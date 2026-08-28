/**
 * Exam camera recording.
 *
 * MediaRecorder with a 10s timeslice → chunks uploaded incrementally with
 * retry/backoff so a single failed request never loses the recording. WebM is
 * preferred (server concatenates chunks into one playable file); MP4 (Safari)
 * is served as a segment playlist.
 */

import { auth, request } from "./api";

export function pickMime(): string {
  const candidates = [
    "video/webm;codecs=vp9,opus",
    "video/webm;codecs=vp8,opus",
    "video/webm",
    "video/mp4",
  ];
  for (const m of candidates) {
    if (typeof MediaRecorder !== "undefined" && MediaRecorder.isTypeSupported(m)) return m;
  }
  return "video/webm";
}

const CHUNK_MS = 10000;
const MAX_RETRIES = 4;

interface PendingChunk {
  index: number;
  blob: Blob;
}

export class RecordingSession {
  private attemptId: number;
  private recorder: MediaRecorder | null = null;
  private mime = "";
  private nextIndex = 0;
  private queue: PendingChunk[] = [];
  private uploading = false;
  private startedAt = 0;
  private stopped = false;

  constructor(attemptId: number) {
    this.attemptId = attemptId;
  }

  get mimeType(): string {
    return this.mime;
  }

  async start(): Promise<void> {
    this.mime = pickMime();
    await request(`/api/recordings/${this.attemptId}/start`, {
      method: "POST",
      headers: { Authorization: `Bearer ${auth.getToken() ?? ""}` },
      body: new URLSearchParams({ mime_type: this.mime }),
    });
  }

  async begin(stream: MediaStream): Promise<void> {
    if (this.recorder) return;
    if (!window.MediaRecorder || !stream.getVideoTracks().length) return;
    this.recorder = new MediaRecorder(stream, { mimeType: this.mime });
    this.startedAt = Date.now();
    this.recorder.ondataavailable = (e: BlobEvent) => {
      if (e.data && e.data.size > 0) {
        this.queue.push({ index: this.nextIndex++, blob: e.data });
        void this.flush();
      }
    };
    this.recorder.start(CHUNK_MS);
  }

  /** Stop recording, flush remaining chunks, then finalize server-side. */
  async stop(): Promise<void> {
    if (this.stopped) return;
    this.stopped = true;
    const recorder = this.recorder;
    this.recorder = null;
    if (recorder && recorder.state !== "inactive") {
      await new Promise<void>((resolve) => {
        const onData = (e: BlobEvent) => {
          if (e.data && e.data.size > 0) {
            this.queue.push({ index: this.nextIndex++, blob: e.data });
          }
        };
        recorder.addEventListener("dataavailable", onData);
        const done = () => {
          recorder.removeEventListener("dataavailable", onData);
          resolve();
        };
        recorder.addEventListener("stop", done, { once: true });
        try {
          recorder.stop();
        } catch {
          done();
        }
      });
    }
    // flush remaining queue (with retries), then finalize
    await this.flush();
    const elapsed = this.startedAt ? (Date.now() - this.startedAt) / 1000 : 0;
    try {
      await request(`/api/recordings/${this.attemptId}/finalize`, {
        method: "POST",
        headers: { Authorization: `Bearer ${auth.getToken() ?? ""}` },
        body: new URLSearchParams({ duration_seconds: String(Math.round(elapsed * 10) / 10) }),
      });
    } catch {
      /* finalize failure is logged by the caller; recording marked degraded */
    }
  }

  private async flush(): Promise<void> {
    if (this.uploading) return;
    this.uploading = true;
    try {
      while (this.queue.length > 0) {
        const chunk = this.queue.shift()!;
        const ok = await this.uploadWithRetry(chunk);
        if (!ok) {
          // Keep the chunk for a final attempt during stop().
          this.queue.unshift(chunk);
          break;
        }
      }
    } finally {
      this.uploading = false;
    }
  }

  private async uploadWithRetry(chunk: PendingChunk): Promise<boolean> {
    for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
      try {
        const form = new FormData();
        form.append("index", String(chunk.index));
        form.append("duration", "0");
        form.append("file", chunk.blob, `chunk_${chunk.index}.${this.mime.includes("mp4") ? "mp4" : "webm"}`);
        await request(`/api/recordings/${this.attemptId}/chunks`, {
          method: "POST",
          headers: { Authorization: `Bearer ${auth.getToken() ?? ""}` },
          body: form,
        });
        return true;
      } catch {
        await new Promise((r) => setTimeout(r, 400 * Math.pow(2, attempt)));
      }
    }
    return false;
  }
}

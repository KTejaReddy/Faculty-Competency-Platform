import { useEffect, useMemo, useRef, useState } from "react";
import {
  Maximize,
  Pause,
  Play,
  RotateCcw,
  RotateCw,
  Video,
  Volume2,
  VolumeX,
} from "lucide-react";
import { api } from "../services/api";
import { Spinner } from "./ui";
import { formatDuration } from "../utils/format";
import type { PlaylistResponse } from "../types";

interface Segment {
  index: number;
  duration: number;
  url: string;
}

export function ExamVideoPlayer({ attemptId, seekTo }: { attemptId: number; seekTo?: number | null }) {
  const [playlist, setPlaylist] = useState<PlaylistResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<PlaylistResponse>(`/api/recordings/admin/video/${attemptId}/playlist`)
      .then(setPlaylist)
      .catch(() => setError("Recording is not available."));
  }, [attemptId]);

  if (error) {
    return (
      <div className="flex flex-col items-center gap-2 rounded-2xl border border-white/10 bg-ink-900/60 py-10 text-center">
        <Video className="h-8 w-8 text-slate-500" />
        <p className="text-sm text-slate-400">{error}</p>
      </div>
    );
  }
  if (!playlist) {
    return (
      <div className="flex items-center justify-center rounded-2xl border border-white/10 bg-ink-900/60 py-12">
        <Spinner className="h-6 w-6" />
      </div>
    );
  }

  return playlist.mode === "single" && playlist.url ? (
    <SinglePlayer url={playlist.url} seekTo={seekTo} />
  ) : (
    <SegmentPlayer segments={playlist.segments ?? []} seekTo={seekTo} />
  );
}

function usePlayerController(videoRef: React.RefObject<HTMLVideoElement | null>) {
  const [playing, setPlaying] = useState(false);
  const [time, setTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [muted, setMuted] = useState(false);
  const [rate, setRate] = useState(1);

  useEffect(() => {
    const v = videoRef.current;
    if (!v) return;
    const onTime = () => setTime(v.currentTime);
    const onDuration = () => setDuration(v.duration || 0);
    const onPlay = () => setPlaying(true);
    const onPause = () => setPlaying(false);
    const onEnded = () => setPlaying(false);
    v.addEventListener("timeupdate", onTime);
    v.addEventListener("loadedmetadata", onDuration);
    v.addEventListener("play", onPlay);
    v.addEventListener("pause", onPause);
    v.addEventListener("ended", onEnded);
    return () => {
      v.removeEventListener("timeupdate", onTime);
      v.removeEventListener("loadedmetadata", onDuration);
      v.removeEventListener("play", onPlay);
      v.removeEventListener("pause", onPause);
      v.removeEventListener("ended", onEnded);
    };
  }, [videoRef]);

  return { playing, time, duration, muted, rate, setPlaying, setTime, setMuted, setRate };
}

function Controls({
  playing,
  time,
  duration,
  muted,
  rate,
  onSeek,
  setMuted,
  setRate,
  videoRef,
}: {
  playing: boolean;
  time: number;
  duration: number;
  muted: boolean;
  rate: number;
  setPlaying: (v: boolean) => void;
  onSeek: (t: number) => void;
  setMuted: (v: boolean) => void;
  setRate: (r: number) => void;
  videoRef: React.RefObject<HTMLVideoElement | null>;
}) {
  return (
    <div className="rounded-b-2xl border-t border-white/10 bg-ink-900/90 px-4 py-3">
      <input
        type="range"
        min={0}
        max={duration || 0}
        step={0.1}
        value={Math.min(time, duration || 0)}
        onChange={(e) => onSeek(Number(e.target.value))}
        className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-white/15 accent-brand-500"
      />
      <div className="mt-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              const v = videoRef.current;
              if (!v) return;
              if (playing) v.pause();
              else void v.play();
            }}
            className="rounded-lg p-1.5 text-slate-300 hover:bg-white/10"
            aria-label={playing ? "Pause" : "Play"}
          >
            {playing ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
          </button>
          <button
            onClick={() => onSeek(Math.max(0, time - 10))}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-white/10"
            aria-label="Back 10s"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
          <button
            onClick={() => onSeek(time + 10)}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-white/10"
            aria-label="Forward 10s"
          >
            <RotateCw className="h-4 w-4" />
          </button>
          <button
            onClick={() => {
              const v = videoRef.current;
              if (!v) return;
              const next = !v.muted;
              v.muted = next;
              setMuted(next);
            }}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-white/10"
            aria-label="Mute"
          >
            {muted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
          </button>
          <span className="font-mono text-xs text-slate-400">
            {formatDuration(time)} <span className="text-slate-600">/</span> {formatDuration(duration)}
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          {[0.5, 1, 1.5, 2].map((r) => (
            <button
              key={r}
              onClick={() => {
                const v = videoRef.current;
                if (v) v.playbackRate = r;
                setRate(r);
              }}
              className={`rounded-md px-2 py-1 text-xs font-semibold transition ${
                rate === r ? "bg-brand-500/25 text-brand-200" : "text-slate-500 hover:text-slate-300"
              }`}
            >
              {r}×
            </button>
          ))}
          <button
            onClick={() => {
              const v = videoRef.current;
              if (v) void v.requestFullscreen?.();
            }}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-white/10"
            aria-label="Fullscreen"
          >
            <Maximize className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

function SinglePlayer({ url, seekTo }: { url: string; seekTo?: number | null }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const ctl = usePlayerController(videoRef);

  useEffect(() => {
    if (seekTo == null) return;
    const v = videoRef.current;
    if (!v) return;
    v.currentTime = Math.min(seekTo, v.duration || seekTo);
    void v.play().catch(() => {});
  }, [seekTo]);

  return (
    <div className="overflow-hidden rounded-2xl border border-white/10 bg-black">
      <video
        ref={videoRef}
        src={url}
        className="aspect-video w-full bg-black"
        muted={ctl.muted}
        playsInline
        controls={false}
      />
      <Controls
        {...ctl}
        videoRef={videoRef}
        onSeek={(t) => {
          const v = videoRef.current;
          if (!v) return;
          v.currentTime = t;
        }}
      />
    </div>
  );
}

/** MP4 (Safari) fallback: plays server-stored segments back-to-back. */
function SegmentPlayer({ segments, seekTo }: { segments: Segment[]; seekTo?: number | null }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [activeIndex, setActiveIndex] = useState(0);
  const offsetRef = useRef(0);
  const ctl = usePlayerController(videoRef);



  const total = useMemo(
    () => segments.reduce((acc, s) => acc + (s.duration || 0), 0),
    [segments]
  );

  const seekToGlobal = (t: number) => {
    const clamped = Math.max(0, Math.min(t, total));
    let acc = 0;
    for (let i = 0; i < segments.length; i++) {
      const segDuration = segments[i].duration || 0;
      if (clamped < acc + segDuration || i === segments.length - 1) {
        setActiveIndex(i);
        offsetRef.current = acc;
        const v = videoRef.current;
        if (v) {
          v.src = segments[i].url;
          v.currentTime = clamped - acc;
        }
        return;
      }
      acc += segDuration;
    }
  };

  useEffect(() => {
    const v = videoRef.current;
    if (!v) return;
    v.src = segments[0]?.url ?? "";
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (seekTo == null) return;
    seekToGlobal(seekTo);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [seekTo]);

  return (
    <div className="overflow-hidden rounded-2xl border border-white/10 bg-black">
      <video
        ref={videoRef}
        className="aspect-video w-full bg-black"
        muted={ctl.muted}
        playsInline
        controls={false}
        onEnded={() => {
          if (activeIndex < segments.length - 1) {
            const next = activeIndex + 1;
            offsetRef.current += segments[activeIndex].duration || 0;
            setActiveIndex(next);
            const v = videoRef.current;
            if (v) {
              v.src = segments[next].url;
              void v.play();
            }
          } else {
            ctl.setPlaying(false);
          }
        }}
      />
      <Controls
        {...ctl}
        duration={total}
        videoRef={videoRef}
        onSeek={seekToGlobal}
        setPlaying={(p) => {
          const v = videoRef.current;
          if (v) {
            if (p) void v.play();
            else v.pause();
          }
        }}
      />
    </div>
  );
}

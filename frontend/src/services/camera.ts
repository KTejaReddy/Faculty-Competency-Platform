/**
 * Camera helpers.
 *
 * IMPORTANT LIMITATION (documented honestly):
 * Browser-level analysis is heuristic image processing, not AI/ML face detection.
 * We measure frame brightness, variance (obstruction) and skin-tone ratio in the
 * center region. A browser cannot detect every physical cheating method (phones,
 * external cameras, OS-level capture). The system provides strong browser-level
 * monitoring, recording and deterrence only.
 */

export interface FrameAnalysis {
  brightness: number; // mean luma 0..255
  variance: number; // pixel variance 0..255
  skinRatio: number; // fraction of skin-tone pixels in the center crop 0..1
}

export type CameraCondition =
  | "OK"
  | "TOO_DARK"
  | "TOO_BRIGHT"
  | "OBSTRUCTED"
  | "DISCONNECTED"
  | "ACCESS_LOST";

export const CONDITION_VIOLATION: Record<CameraCondition, string | null> = {
  OK: null,
  TOO_DARK: "CAMERA_TOO_DARK",
  TOO_BRIGHT: "CAMERA_TOO_BRIGHT",
  OBSTRUCTED: "CAMERA_OBSTRUCTED",
  DISCONNECTED: "CAMERA_DISCONNECTED",
  ACCESS_LOST: "CAMERA_PERMISSION_LOST",
};

const DARK_THRESHOLD = 32;
const BRIGHT_THRESHOLD = 235;
const OBSTRUCT_VARIANCE = 9;
const OBSTRUCT_BRIGHTNESS = 90;
const SKIN_MIN = 0.02;

export async function requestCamera(): Promise<MediaStream> {
  return navigator.mediaDevices.getUserMedia({
    video: {
      width: { ideal: 640 },
      height: { ideal: 480 },
      facingMode: "user",
    },
    audio: false,
  });
}

export function streamCondition(stream: MediaStream | null): CameraCondition {
  if (!stream) return "DISCONNECTED";
  const track = stream.getVideoTracks()[0];
  if (!track) return "DISCONNECTED";
  if (track.readyState === "ended") return "ACCESS_LOST";
  return "OK";
}

/** Analyze the current video frame into brightness / variance / skin ratio. */
export function analyzeFrame(video: HTMLVideoElement, canvas: HTMLCanvasElement): FrameAnalysis | null {
  if (!video.videoWidth || video.videoHeight === 0) return null;
  const w = 96;
  const h = Math.max(1, Math.round((video.videoHeight / video.videoWidth) * w));
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  if (!ctx) return null;
  try {
    ctx.drawImage(video, 0, 0, w, h);
    const data = ctx.getImageData(0, 0, w, h).data;

    let sum = 0;
    let sumSq = 0;
    const centerX0 = Math.floor(w * 0.25);
    const centerX1 = Math.ceil(w * 0.75);
    const centerY0 = Math.floor(h * 0.25);
    const centerY1 = Math.ceil(h * 0.75);
    let skin = 0;
    let skinCount = 0;

    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        const i = (y * w + x) * 4;
        const r = data[i];
        const g = data[i + 1];
        const b = data[i + 2];
        const luma = 0.299 * r + 0.587 * g + 0.114 * b;
        sum += luma;
        sumSq += luma * luma;
        const inCenter = x >= centerX0 && x <= centerX1 && y >= centerY0 && y <= centerY1;
        if (inCenter) {
          // classic skin-tone heuristic (YCbCr-ish thresholds)
          const isSkin = r > 95 && g > 40 && b > 20 && r > g && r > b && r - g > 15 && r - b > 15;
          if (isSkin) skin++;
          skinCount++;
        }
      }
    }
    const n = w * h;
    const brightness = sum / n;
    const variance = sumSq / n - brightness * brightness;
    const skinRatio = skinCount > 0 ? skin / skinCount : 0;
    return { brightness, variance, skinRatio };
  } catch {
    return null;
  }
}

export function classifyFrame(a: FrameAnalysis): CameraCondition {
  if (a.brightness < DARK_THRESHOLD) return "TOO_DARK";
  if (a.brightness > BRIGHT_THRESHOLD) return "TOO_BRIGHT";
  if (a.variance < OBSTRUCT_VARIANCE && a.brightness < OBSTRUCT_BRIGHTNESS) return "OBSTRUCTED";
  return "OK";
}

export interface CameraCheck {
  detected: boolean;
  accessible: boolean;
  faceVisible: boolean;
  lightingOk: boolean;
  unobstructed: boolean;
  brightness: number;
}

export function evaluateCheck(a: FrameAnalysis | null, stream: MediaStream | null): CameraCheck {
  if (!a) {
    return {
      detected: !!stream,
      accessible: false,
      faceVisible: false,
      lightingOk: false,
      unobstructed: false,
      brightness: 0,
    };
  }
  return {
    detected: !!stream,
    accessible: true,
    faceVisible: a.skinRatio >= SKIN_MIN,
    lightingOk: a.brightness >= DARK_THRESHOLD && a.brightness <= BRIGHT_THRESHOLD,
    unobstructed: !(a.variance < OBSTRUCT_VARIANCE && a.brightness < OBSTRUCT_BRIGHTNESS),
    brightness: Math.round(a.brightness),
  };
}

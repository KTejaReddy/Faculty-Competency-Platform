import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { AlertTriangle, Camera, CameraOff, CheckCircle2, RefreshCw, ShieldCheck, Video } from "lucide-react";
import { api } from "../services/api";
import { Card, Spinner } from "../components/ui";
import { useToast } from "../components/Toast";
import { unlockAudio } from "../services/audio";
import {
  analyzeFrame,
  evaluateCheck,
  requestCamera,
  type CameraCheck as CameraCheckState,
} from "../services/camera";
import type { StartExamResponse } from "../types";

const ATTEMPT_KEY = "ftp_attempt";

export function CameraCheck() {
  const { subjectId } = useParams();
  const [params] = useSearchParams();
  const band = params.get("band") ?? "8-12";
  const navigate = useNavigate();
  const { toast } = useToast();

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const [status, setStatus] = useState<"idle" | "requesting" | "live" | "error">("idle");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [check, setCheck] = useState<CameraCheckState | null>(null);
  const [allPass, setAllPass] = useState(false);
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    let alive = true;
    let interval: number | undefined;

    const boot = async () => {
      setStatus("requesting");
      try {
        const stream = await requestCamera();
        if (!alive) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play().catch(() => {});
        }
        setStatus("live");

        interval = window.setInterval(() => {
          if (!videoRef.current || !canvasRef.current) return;
          const analysis = analyzeFrame(videoRef.current, canvasRef.current);
          const c = evaluateCheck(analysis, streamRef.current);
          setCheck(c);
          setAllPass(c.detected && c.accessible && c.faceVisible && c.lightingOk && c.unobstructed);
        }, 500);
      } catch (err) {
        if (!alive) return;
        setStatus("error");
        setErrorMsg(
          err instanceof DOMException && err.name === "NotAllowedError"
            ? "Camera permission was denied. Grant camera access and try again."
            : "No camera was detected or it could not be opened."
        );
      }
    };

    void boot();
    return () => {
      alive = false;
      if (interval) window.clearInterval(interval);
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  const startExam = async () => {
    if (!allPass) return;
    setStarting(true);
    unlockAudio(); // user gesture → unlock the audio context for the buzzer
    try {
      const attempt = await api.post<StartExamResponse>(`/api/exams/start`, {
        subject_id: Number(subjectId),
        experience_band: band,
      });
      localStorage.setItem(ATTEMPT_KEY, JSON.stringify(attempt));
      // Request fullscreen inside the user gesture
      try {
        await document.documentElement.requestFullscreen?.();
      } catch {
        /* fullscreen will be re-requested on first interaction inside the exam */
      }
      navigate("/exam", { replace: true });
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Could not start the exam.";
      toast(msg, "error");
      if (String(msg).toLowerCase().includes("locked") || String(msg).toLowerCase().includes("completed")) {
        navigate("/dashboard");
      }
      setStarting(false);
    }
  };

  const rows: { label: string; pass: boolean | null }[] = [
    { label: "Camera detected", pass: check ? check.detected : null },
    { label: "Camera accessible", pass: check ? check.accessible : null },
    { label: "Face visible", pass: check ? check.faceVisible : null },
    { label: "Lighting acceptable", pass: check ? check.lightingOk : null },
    { label: "Camera unobstructed", pass: check ? check.unobstructed : null },
  ];

  return (
    <div className="mx-auto w-full max-w-3xl px-6 py-10">
      <button onClick={() => navigate(-1)} className="btn-ghost mb-6">
        ← Back
      </button>
      <div className="mb-6 flex items-center gap-2">
        <Camera className="h-5 w-5 text-brand-300" />
        <h1 className="text-2xl font-extrabold tracking-tight text-slate-50">CAMERA VERIFICATION</h1>
      </div>

      {status === "error" ? (
        <Card className="flex flex-col items-center gap-4 p-10 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-rose-500/15 text-rose-400">
            <CameraOff className="h-7 w-7" />
          </div>
          <p className="text-lg font-semibold text-slate-100">Camera unavailable</p>
          <p className="max-w-md text-sm text-slate-400">{errorMsg}</p>
          <button onClick={() => window.location.reload()} className="btn-secondary">
            <RefreshCw className="h-4 w-4" /> Try again
          </button>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          <Card className="overflow-hidden p-0">
            <div className="relative aspect-video bg-black">
              {status !== "live" ? (
                <div className="absolute inset-0 flex items-center justify-center">
                  <Spinner className="h-8 w-8" />
                </div>
              ) : null}
              <video ref={videoRef} muted playsInline className="h-full w-full object-cover" />
              <div className="absolute bottom-3 left-3 flex items-center gap-2">
                <span className="flex items-center gap-1.5 rounded-full bg-black/60 px-3 py-1 text-[11px] font-semibold text-mint-400">
                  <span className="h-2 w-2 animate-pulse rounded-full bg-mint-400" /> LIVE PREVIEW
                </span>
              </div>
            </div>
            <div className="flex items-center justify-between px-4 py-3 text-xs text-slate-400">
              <span>
                Brightness: <span className="font-semibold text-slate-200">{check?.brightness ?? "—"}</span>/255
              </span>
              <span className="flex items-center gap-1.5">
                <Video className="h-3.5 w-3.5" /> Your session will be recorded
              </span>
            </div>
            <canvas ref={canvasRef} className="hidden" />
          </Card>

          <Card className="flex flex-col justify-between p-6">
            <div>
              <p className="mb-4 text-xs font-bold uppercase tracking-widest text-slate-400">Security checks</p>
              <ul className="space-y-3">
                {rows.map((row) => (
                  <li key={row.label} className="flex items-center gap-3 text-sm">
                    {row.pass === null ? (
                      <Spinner className="h-4 w-4" />
                    ) : row.pass ? (
                      <CheckCircle2 className="h-4.5 w-4.5 shrink-0 text-mint-400" />
                    ) : (
                      <AlertTriangle className="h-4.5 w-4.5 shrink-0 text-amber-400" />
                    )}
                    <span className={row.pass ? "text-slate-200" : "text-amber-300"}>{row.label}</span>
                  </li>
                ))}
              </ul>
            </div>
            <button onClick={startExam} disabled={!allPass || starting} className="btn-primary mt-6 w-full py-3">
              {starting ? <Spinner /> : <ShieldCheck className="h-5 w-5" />}
              {allPass ? "I UNDERSTAND — START EXAM" : "WAITING FOR CAMERA CHECKS…"}
            </button>
          </Card>
        </div>
      )}

      <p className="mt-6 text-center text-xs leading-relaxed text-slate-500">
        By starting, you consent to this session being recorded and monitored. Camera checks use
        heuristic image analysis (brightness, obstruction, skin-tone presence) — not AI face
        recognition.
      </p>
    </div>
  );
}

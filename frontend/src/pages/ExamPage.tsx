import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  AlertTriangle,
  Camera,
  CameraOff,
  CheckCircle2,
  ChevronRight,
  CircleDot,
  Maximize,
  ShieldCheck,
  Square,
  Timer as TimerIcon,
} from "lucide-react";
import { api } from "../services/api";
import { useServerTimer } from "../hooks/useServerTimer";
import { ViolationMonitor, type ViolationType } from "../services/violationMonitor";
import { RecordingSession } from "../services/recording";
import { beep, startContinuousTone, stopContinuousTone, unlockAudio } from "../services/audio";
import {
  analyzeFrame,
  classifyFrame,
  requestCamera,
  streamCondition,
  type CameraCondition,
} from "../services/camera";
import { Badge, Modal, Spinner } from "../components/ui";
import { useToast } from "../components/Toast";
import { formatClock } from "../utils/format";
import type { AttemptStatus, ExamQuestion, StartExamResponse, SubmitResponse } from "../types";

const ATTEMPT_KEY = "ftp_attempt";
const CAMERA_GRACE_MS = 5000;
const CRITICAL_CONDITIONS: CameraCondition[] = ["OBSTRUCTED", "TOO_DARK", "DISCONNECTED", "ACCESS_LOST"];

interface Warning {
  id: number;
  title: string;
  detail: string;
}

export function ExamPage() {
  const navigate = useNavigate();
  const { toast } = useToast();

  const [attempt] = useState<StartExamResponse | null>(() => {
    try {
      const raw = localStorage.getItem(ATTEMPT_KEY);
      return raw ? (JSON.parse(raw) as StartExamResponse) : null;
    } catch {
      return null;
    }
  });

  const [current, setCurrent] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number[]>>({});
  const [warning, setWarning] = useState<Warning | null>(null);
  const [cameraState, setCameraState] = useState<CameraCondition>("OK");
  const [cameraLive, setCameraLive] = useState(false);
  const [fullscreenRequired, setFullscreenRequired] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [securityLive, setSecurityLive] = useState(false);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const monitorRef = useRef<ViolationMonitor | null>(null);
  const recordingRef = useRef<RecordingSession | null>(null);
  const answersRef = useRef(answers);
  const currentRef = useRef(current);
  const submittedRef = useRef(false);
  const navigatedRef = useRef(false);

  const timer = useServerTimer(attempt ? attempt.deadline : null);

  const questions: ExamQuestion[] = attempt?.questions ?? [];
  const total = questions.length;
  const currentQuestion = questions[current];
  const answeredCount = Object.keys(answers).length;

  answersRef.current = answers;
  currentRef.current = current;

  const showWarning = useCallback((title: string, detail: string) => {
    setWarning({ id: Date.now(), title, detail });
    beep();
    window.setTimeout(() => setWarning((w) => (w && Date.now() - w.id > 3500 ? null : w)), 4000);
  }, []);

  const reportViolation = useCallback(
    async (type: ViolationType, duration = 0, metadata: Record<string, unknown> = {}) => {
      if (!attempt || submittedRef.current) return;
      try {
        await api.post(`/api/exams/attempts/${attempt.attempt_id}/violations`, {
          type,
          duration_seconds: Math.round(duration * 10) / 10,
          metadata,
        });
      } catch {
        /* best-effort: the frontend still shows the warning */
      }
    },
    [attempt]
  );

  // ------------------------------------------------------------------
  // Boot: camera, recording, monitor, timer sync, fullscreen
  // ------------------------------------------------------------------
  useEffect(() => {
    if (!attempt) {
      navigate("/dashboard", { replace: true });
      return;
    }

    const boot = async () => {
      // sync with the server: authoritative deadline + resume state
      try {
        const status = await api.get<AttemptStatus>(`/api/exams/attempts/${attempt.attempt_id}/status`);
        timer.sync(status.deadline);
        setSecurityLive(true);
        if (status.answers) {
          setAnswers(status.answers);
          if (status.last_position > 0) setCurrent(Math.min(status.last_position, total - 1));
        }
        if (status.status !== "in_progress") {
          finishToComplete(attempt.attempt_id);
          return;
        }
      } catch {
        /* offline: continue with local data */
      }

      // camera
      try {
        const stream = await requestCamera();
        streamRef.current = stream;
        setCameraLive(true);
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          void videoRef.current.play().catch(() => {});
        }
      } catch {
        setCameraLive(false);
        await reportViolation("CAMERA_DISCONNECTED", 0, { reason: "camera unavailable at start" });
        showWarning("CAMERA UNAVAILABLE", "Camera could not be started. This has been recorded.");
      }

      // recording
      if (streamRef.current) {
        const rec = new RecordingSession(attempt.attempt_id);
        recordingRef.current = rec;
        try {
          await rec.start();
          await rec.begin(streamRef.current);
        } catch {
          /* recording is best-effort; never block the exam */
        }
      }

      // violation monitor
      const monitor = new ViolationMonitor();
      monitorRef.current = monitor;
      monitor.onViolation(({ type, duration, metadata }) => {
        void reportViolation(type, duration, metadata);
        const label = type.replace(/_/g, " ").toLowerCase();
        showWarning(`${type.replace(/_/g, " ")} DETECTED`, `This incident has been recorded (${label}).`);
        if (type === "FULLSCREEN_EXIT") setFullscreenRequired(true);
      });
      monitor.attach();

      // fullscreen requirement
      if (!document.fullscreenElement) {
        try {
          await document.documentElement.requestFullscreen();
        } catch {
          setFullscreenRequired(true);
        }
      }
    };

    void boot();
    return () => {
      monitorRef.current?.detach();
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ------------------------------------------------------------------
  // Camera monitoring loop (brightness / obstruction / disconnection)
  // ------------------------------------------------------------------
  const sustainedRef = useRef<{ condition: CameraCondition; since: number } | null>(null);
  const reportedRef = useRef<Set<CameraCondition>>(new Set());

  useEffect(() => {
    if (!attempt || !cameraLive) return;
    const id = window.setInterval(async () => {
      const stream = streamRef.current;
      const cond = streamCondition(stream);
      let condition: CameraCondition = cond;
      if (cond === "OK" && videoRef.current && canvasRef.current) {
        const analysis = analyzeFrame(videoRef.current, canvasRef.current);
        condition = analysis ? classifyFrame(analysis) : "OK";
      }
      setCameraState(condition);

      const now = Date.now();
      if (condition === "OK") {
        sustainedRef.current = null;
        reportedRef.current.clear();
        stopContinuousTone();
        return;
      }

      if (!sustainedRef.current || sustainedRef.current.condition !== condition) {
        sustainedRef.current = { condition, since: now };
      }
      const sustained = now - sustainedRef.current.since >= CAMERA_GRACE_MS;

      if (sustained && !reportedRef.current.has(condition)) {
        reportedRef.current.add(condition);
        const type =
          condition === "TOO_DARK"
            ? "CAMERA_TOO_DARK"
            : condition === "TOO_BRIGHT"
              ? "CAMERA_TOO_BRIGHT"
              : condition === "ACCESS_LOST"
                ? "CAMERA_PERMISSION_LOST"
                : "CAMERA_OBSTRUCTED";
        await reportViolation(type, (now - sustainedRef.current.since) / 1000, { condition });
        showWarning("CAMERA ISSUE DETECTED", "Please restore proper camera visibility.");
        if (CRITICAL_CONDITIONS.includes(condition)) startContinuousTone();
      }
    }, 800);
    return () => window.clearInterval(id);
  }, [attempt, cameraLive, reportViolation, showWarning]);

  // ------------------------------------------------------------------
  // Fullscreen change handling
  // ------------------------------------------------------------------
  useEffect(() => {
    const onFs = () => {
      const active = !!document.fullscreenElement;
      if (!active && submittedRef.current === false) {
        setFullscreenRequired(true);
        void reportViolation("FULLSCREEN_EXIT", 0, {});
        showWarning("FULLSCREEN EXIT DETECTED", "This incident has been recorded.");
      } else if (active) {
        setFullscreenRequired(false);
      }
    };
    document.addEventListener("fullscreenchange", onFs);
    return () => document.removeEventListener("fullscreenchange", onFs);
  }, [reportViolation, showWarning]);

  // ------------------------------------------------------------------
  // Timer warnings + auto submit
  // ------------------------------------------------------------------
  const lastWarningRef = useRef(0);
  useEffect(() => {
    if (!attempt) return;
    const s = timer.seconds;
    if (s === 600 || s === 300 || s === 60) {
      if (s !== lastWarningRef.current) {
        lastWarningRef.current = s;
        toast(`${Math.round(s / 60)} minutes remaining`, "warning");
        beep(660);
      }
    }
    if (timer.expired && !submittedRef.current) {
      void submitExam(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [timer.seconds, timer.expired]);

  // periodic server resync
  useEffect(() => {
    if (!attempt) return;
    const id = window.setInterval(async () => {
      try {
        const status = await api.get<AttemptStatus>(`/api/exams/attempts/${attempt.attempt_id}/status`);
        timer.sync(status.deadline);
        if (status.status !== "in_progress" && !submittedRef.current) {
          finishToComplete(attempt.attempt_id);
        }
      } catch {
        /* transient network error — keep counting locally */
      }
    }, 30000);
    return () => window.clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [attempt]);

  // ------------------------------------------------------------------
  // Answer handling (strict forward navigation)
  // ------------------------------------------------------------------
  const selectOption = (index: number) => {
    if (!currentQuestion) return;
    const key = String(currentQuestion.position);
    const q = currentQuestion;
    let next: number[];
    if (q.question_type === "multiple") {
      const currentChoices = answers[key] ?? [];
      next = currentChoices.includes(index)
        ? currentChoices.filter((i) => i !== index)
        : [...currentChoices, index].sort((a, b) => a - b);
    } else {
      next = [index];
    }
    const updated = { ...answersRef.current, [key]: next };
    setAnswers(updated);
    void api
      .post(`/api/exams/attempts/${attempt!.attempt_id}/answers`, {
        position: currentQuestion.position,
        chosen_options: next,
      })
      .catch(() => {
        toast("Could not save your answer. Retrying…", "warning");
      });
  };

  const goNext = () => {
    if (current < total - 1) setCurrent(current + 1);
  };

  const finishToComplete = (attemptId: number) => {
    if (navigatedRef.current) return;
    navigatedRef.current = true;
    submittedRef.current = true;
    localStorage.removeItem(ATTEMPT_KEY);
    navigate(`/exam/complete?attempt_id=${attemptId}`, { replace: true });
  };

  const submitExam = async (auto = false) => {
    if (!attempt || submittedRef.current) return;
    submittedRef.current = true;
    setSubmitting(true);
    stopContinuousTone();
    if (auto) toast("Time expired — auto submitting.", "warning");

    // finalize recording before submitting
    try {
      await recordingRef.current?.stop();
    } catch {
      /* recording finalize is best-effort */
    }
    monitorRef.current?.detach();
    streamRef.current?.getTracks().forEach((t) => t.stop());

    try {
      const res = await api.post<SubmitResponse>(`/api/exams/attempts/${attempt.attempt_id}/submit`);
      if (res.status === "in_progress") {
        // server returned a fresh in-progress attempt (deadline not passed); ignore
      }
      finishToComplete(attempt.attempt_id);
    } catch {
      setSubmitting(false);
      submittedRef.current = false;
      toast("Submission failed. Check your connection and try again.", "error");
    }
  };

  const reEnterFullscreen = async () => {
    unlockAudio();
    try {
      await document.documentElement.requestFullscreen();
      setFullscreenRequired(false);
    } catch {
      toast("Fullscreen was blocked. Click again to retry.", "warning");
    }
  };

  if (!attempt) return null;
  if (!questions.length) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  const optionLetters = ["A", "B", "C", "D", "E", "F"];
  const choices = answers[String(currentQuestion.position)] ?? [];

  return (
    <div className="flex h-screen flex-col bg-ink-950">
      {/* header */}
      <header className="flex items-center justify-between border-b border-white/10 bg-ink-900/80 px-6 py-3">
        <div className="flex items-center gap-3">
          <span className="hidden text-sm font-bold text-slate-100 sm:block">{attempt.subject_name}</span>
          <Badge tone={timer.seconds <= 300 ? "red" : timer.seconds <= 600 ? "amber" : "brand"}>
            <TimerIcon className="h-3 w-3" /> {formatClock(timer.seconds)}
          </Badge>
        </div>
        <div className="flex items-center gap-3">
          {cameraLive ? (
            <Badge tone="green">
              <Camera className="h-3 w-3" /> CAMERA ACTIVE
            </Badge>
          ) : (
            <Badge tone="red">
              <CameraOff className="h-3 w-3" /> CAMERA OFFLINE
            </Badge>
          )}
          <Badge tone={securityLive ? "green" : "slate"}>
            <ShieldCheck className="h-3 w-3" /> SECURITY {securityLive ? "ACTIVE" : "…"}
          </Badge>
        </div>
      </header>

      {/* warning banner */}
      {warning && (
        <div className="border-b border-rose-500/30 bg-rose-500/15 px-6 py-3" style={{ animation: "flashWarn 0.3s" }}>
          <div className="mx-auto flex max-w-3xl items-center gap-3">
            <AlertTriangle className="h-5 w-5 shrink-0 text-rose-400" />
            <div>
              <p className="text-sm font-bold text-rose-300">{warning.title}</p>
              <p className="text-xs text-rose-300/80">{warning.detail}</p>
            </div>
          </div>
        </div>
      )}

      {fullscreenRequired && (
        <div className="border-b border-amber-400/30 bg-amber-400/10 px-6 py-2.5">
          <div className="mx-auto flex max-w-3xl items-center justify-between gap-3">
            <p className="flex items-center gap-2 text-sm text-amber-300">
              <Maximize className="h-4 w-4" /> Fullscreen is required for this examination.
            </p>
            <button onClick={reEnterFullscreen} className="btn-secondary !py-1.5 text-xs">
              RE-ENTER FULLSCREEN
            </button>
          </div>
        </div>
      )}

      {/* body */}
      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto w-full max-w-3xl px-6 py-8">
          {/* progress */}
          <div className="mb-6">
            <div className="mb-2 flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-400">
              <span>
                QUESTION {current + 1} / {total}
              </span>
              <span>
                {answeredCount} answered
              </span>
            </div>
            <div className="flex gap-1">
              {questions.map((q, i) => {
                const key = String(q.position);
                const answered = !!answers[key];
                return (
                  <div
                    key={q.position}
                    className={`h-1.5 flex-1 rounded-full transition ${
                      i === current ? "bg-brand-400" : answered ? "bg-mint-500/70" : "bg-white/10"
                    }`}
                  />
                );
              })}
            </div>
          </div>

          <div className="card p-7" key={currentQuestion.position}>
            <p className="mb-3 text-[11px] font-bold uppercase tracking-widest text-brand-300">
              {typeLabel(currentQuestion.question_type)}
            </p>
            <p className="text-lg leading-relaxed text-slate-100" style={{ whiteSpace: "pre-wrap" }}>
              {currentQuestion.question_text}
            </p>

            <div className="mt-6 space-y-2.5">
              {currentQuestion.options.map((opt, i) => {
                const selected = choices.includes(i);
                return (
                  <button
                    key={i}
                    onClick={() => selectOption(i)}
                    className={`flex w-full items-start gap-3 rounded-xl border px-4 py-3 text-left text-sm transition ${
                      selected
                        ? "border-brand-400/70 bg-brand-500/15 text-slate-100 ring-1 ring-brand-500/40"
                        : "border-white/10 bg-white/[0.03] text-slate-300 hover:border-white/25 hover:bg-white/[0.06]"
                    }`}
                  >
                    <span
                      className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border text-[11px] font-bold ${
                        selected ? "border-brand-300 bg-brand-500 text-white" : "border-slate-500 text-slate-400"
                      }`}
                    >
                      {optionLetters[i]}
                    </span>
                    <span style={{ whiteSpace: "pre-wrap" }}>{opt}</span>
                  </button>
                );
              })}
            </div>

            {currentQuestion.question_type === "multiple" && (
              <p className="mt-3 flex items-center gap-1.5 text-xs text-slate-500">
                <CircleDot className="h-3.5 w-3.5" /> Multiple options may be correct — select all that apply.
              </p>
            )}
          </div>

          <div className="mt-6 flex items-center justify-between">
            <p className="text-xs text-slate-500">
              {current < total - 1
                ? "You cannot return to previous questions."
                : "This is the last question."}
            </p>
            {current < total - 1 ? (
              <button onClick={goNext} className="btn-primary px-8">
                NEXT <ChevronRight className="h-4 w-4" />
              </button>
            ) : (
              <button onClick={() => setConfirmOpen(true)} className="btn-primary px-8 !bg-mint-600 !shadow-mint-600/20 hover:!bg-mint-500">
                <Square className="h-4 w-4" /> SUBMIT EXAM
              </button>
            )}
          </div>
        </div>
      </main>

      {/* hidden video + canvas for analysis */}
      <video ref={videoRef} muted playsInline className="pointer-events-none fixed -left-[1000px] top-0 h-1 w-1 opacity-0" />
      <canvas ref={canvasRef} className="hidden" />

      {/* camera status strip */}
      <footer className="border-t border-white/10 bg-ink-900/80 px-6 py-2">
        <div className="mx-auto flex max-w-3xl items-center justify-between text-[11px] text-slate-400">
          <span className="flex items-center gap-1.5">
            <span className={`h-2 w-2 rounded-full ${cameraLive ? "bg-mint-400 animate-pulse" : "bg-rose-400"}`} />
            {cameraStateLabel(cameraState)}
          </span>
          <span className="flex items-center gap-1.5">
            <CheckCircle2 className="h-3.5 w-3.5 text-mint-400/70" /> Session is being recorded
          </span>
        </div>
      </footer>

      <Modal
        open={confirmOpen}
        onClose={() => !submitting && setConfirmOpen(false)}
        title="Submit examination?"
      >
        <div className="space-y-4">
          <p className="text-sm text-slate-300">
            You answered <span className="font-bold text-slate-100">{answeredCount}</span> of{" "}
            <span className="font-bold text-slate-100">{total}</span> questions. Once submitted, this
            subject becomes permanently locked and cannot be attempted again.
          </p>
          <div className="flex justify-end gap-3">
            <button className="btn-secondary" disabled={submitting} onClick={() => setConfirmOpen(false)}>
              Keep working
            </button>
            <button className="btn-primary" disabled={submitting} onClick={() => submitExam(false)}>
              {submitting ? <Spinner /> : <Square className="h-4 w-4" />} Submit
            </button>
          </div>
        </div>
      </Modal>
      <style>{`@keyframes flashWarn { from { background: rgba(244,63,94,0.35) } }`}</style>
    </div>
  );
}

function typeLabel(t: string): string {
  return (
    {
      single: "Single Correct",
      multiple: "Multiple Correct",
      assertion_reason: "Assertion / Reason",
      scenario: "Scenario Based",
      code: "Code Based",
      numerical: "Numerical",
      debugging: "Debugging",
    }[t] ?? "Question"
  );
}

function cameraStateLabel(c: CameraCondition): string {
  return (
    {
      OK: "● CAMERA ACTIVE · ENVIRONMENT OK",
      TOO_DARK: "⚠ LIGHTING TOO LOW",
      TOO_BRIGHT: "⚠ LIGHTING TOO HIGH",
      OBSTRUCTED: "⚠ CAMERA OBSTRUCTED",
      DISCONNECTED: "⚠ CAMERA DISCONNECTED",
      ACCESS_LOST: "⚠ CAMERA ACCESS LOST",
    }[c] ?? ""
  );
}

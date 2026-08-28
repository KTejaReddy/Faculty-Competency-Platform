import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowRight, Camera, CheckCircle2, Info, Laptop, MonitorSmartphone } from "lucide-react";
import { api } from "../services/api";
import { Badge, LoadingScreen } from "../components/ui";
import { useToast } from "../components/Toast";
import type { SubjectStatusItem } from "../types";
import { experienceLabel } from "../utils/format";

const BANDS = [
  { band: "1-3", years: "1–3 Years", desc: "Foundational teaching experience" },
  { band: "4-7", years: "4–7 Years", desc: "Established classroom experience" },
  { band: "8-12", years: "8–12 Years", desc: "Senior faculty experience" },
  { band: "13-20", years: "13–20 Years", desc: "Distinguished teaching record" },
  { band: "20+", years: "20+ Years", desc: "Legendary teaching career" },
];

function isSuitableDevice(): { suitable: boolean; width: number; touch: boolean } {
  const width = window.innerWidth;
  const touch = window.matchMedia("(pointer: coarse)").matches;
  return { suitable: width >= 1024 && !touch, width, touch };
}

export function ExamStart() {
  const { subjectId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [subject, setSubject] = useState<SubjectStatusItem | null>(null);
  const [band, setBand] = useState<string | null>(null);
  const device = useMemo(isSuitableDevice, []);

  useEffect(() => {
    api
      .get<SubjectStatusItem[]>("/api/subjects")
      .then((items) => {
        const found = items.find((s) => String(s.subject.id) === subjectId);
        if (!found) {
          toast("Subject not found.", "error");
          navigate("/dashboard");
          return;
        }
        if (found.status === "COMPLETED") {
          toast("This subject is already completed and locked.", "warning");
          navigate("/dashboard");
          return;
        }
        setSubject(found);
      })
      .catch(() => navigate("/dashboard"));
  }, [subjectId, navigate, toast]);

  if (!subject) return <LoadingScreen label="Loading subject…" />;

  const start = () => {
    if (!band) {
      toast("Select your teaching experience to continue.", "warning");
      return;
    }
    navigate(`/subjects/${subjectId}/verify?band=${band}`);
  };

  return (
    <div className="mx-auto w-full max-w-3xl px-6 py-10">
      <button onClick={() => navigate("/dashboard")} className="btn-ghost mb-6">
        ← Back to dashboard
      </button>

      <div className="mb-8">
        <Badge tone="brand">{subject.subject.difficulty_label}</Badge>
        <h1 className="mt-3 text-3xl font-extrabold tracking-tight text-slate-50">{subject.subject.name}</h1>
        <p className="mt-2 text-sm text-slate-400">{subject.subject.description}</p>
        <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-400">
          <span className="chip">{subject.question_count} questions · 1 mark each</span>
          <span className="chip">{subject.duration_minutes} minutes</span>
        </div>
      </div>

      <section>
        <h2 className="text-sm font-bold uppercase tracking-widest text-slate-300">
          SELECT YOUR TEACHING EXPERIENCE
        </h2>
        <p className="mt-1 text-xs text-slate-500">
          Your experience level determines the difficulty distribution of the examination questions.
        </p>
        <div className="mt-4 space-y-3">
          {BANDS.map((b) => (
            <button
              key={b.band}
              onClick={() => setBand(b.band)}
              className={`card flex w-full items-center justify-between p-5 text-left transition ${
                band === b.band
                  ? "border-brand-400/60 bg-brand-500/10 ring-2 ring-brand-500/30"
                  : "hover:border-white/20 hover:bg-white/[0.05]"
              }`}
            >
              <div>
                <p className="font-bold text-slate-100">{b.years}</p>
                <p className="text-xs text-slate-400">{b.desc}</p>
              </div>
              {band === b.band ? (
                <CheckCircle2 className="h-5 w-5 text-brand-300" />
              ) : (
                <ArrowRight className="h-5 w-5 text-slate-600" />
              )}
            </button>
          ))}
        </div>
      </section>

      <section className="mt-8">
        {device.suitable ? (
          <div className="flex items-center gap-3 rounded-xl border border-mint-500/25 bg-mint-500/10 px-4 py-3 text-sm text-mint-400">
            <Laptop className="h-5 w-5 shrink-0" />
            Desktop detected — ideal for the camera, fullscreen and security monitoring.
          </div>
        ) : (
          <div className="flex items-start gap-3 rounded-xl border border-amber-400/25 bg-amber-400/10 px-4 py-3 text-sm text-amber-300">
            <MonitorSmartphone className="mt-0.5 h-5 w-5 shrink-0" />
            <div>
              <p className="font-semibold">Device suitability warning</p>
              <p className="mt-0.5 text-amber-300/80">
                This examination strongly recommends a desktop or laptop with a camera, because of
                fullscreen mode, camera monitoring and security controls. You may continue, but the
                experience will be degraded.
              </p>
            </div>
          </div>
        )}
        <div className="mt-3 flex items-start gap-2 text-xs text-slate-500">
          <Info className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          <p>
            The session will be recorded and monitored. Tab switches, copy/paste attempts, focus
            loss and camera conditions are logged and penalized.
          </p>
        </div>
      </section>

      <div className="mt-8 flex items-center justify-between">
        <p className="text-xs text-slate-500">Selected: {band ? experienceLabel(band) : "none"}</p>
        <button onClick={start} className="btn-primary px-8 py-3" disabled={!band}>
          <Camera className="h-4.5 w-4.5" /> CONTINUE TO CAMERA CHECK
        </button>
      </div>
    </div>
  );
}

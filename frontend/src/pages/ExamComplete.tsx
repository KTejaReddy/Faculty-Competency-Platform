import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { CheckCircle2, EyeOff, Lock, ShieldCheck } from "lucide-react";
import { api } from "../services/api";
import { Card, LoadingScreen } from "../components/ui";
import { formatDuration } from "../utils/format";
import type { ResultResponse } from "../types";

export function ExamComplete() {
  const [params] = useSearchParams();
  const attemptId = params.get("attempt_id");
  const navigate = useNavigate();
  const [result, setResult] = useState<ResultResponse | null>(null);

  useEffect(() => {
    if (!attemptId) {
      navigate("/dashboard");
      return;
    }
    api
      .get<ResultResponse>(`/api/exams/attempts/${attemptId}/result`)
      .then(setResult)
      .catch(() => navigate("/dashboard"));
  }, [attemptId, navigate]);

  if (!result) return <LoadingScreen label="Preparing your results…" />;

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12">
      <div className="w-full max-w-lg">
        <Card className="relative overflow-hidden p-8 text-center">
          <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-mint-500 via-brand-500 to-mint-500" />
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-mint-500/15 ring-8 ring-mint-500/5">
            <CheckCircle2 className="h-9 w-9 text-mint-400" />
          </div>
          <h1 className="mt-5 text-3xl font-extrabold tracking-tight text-slate-50">EXAM COMPLETED</h1>
          <p className="mt-2 text-sm text-slate-400">
            Your examination for <span className="font-semibold text-slate-200">{result.subject_name}</span>{" "}
            has been successfully submitted.
          </p>

          <div className="mt-7 grid grid-cols-3 gap-3">
            <Metric label="Questions" value={String(result.num_questions)} />
            <Metric label="Time Used" value={formatDuration(result.time_used_seconds)} />
            <Metric label="Violations" value={String(result.violations.length ? result.violations.reduce((a, v) => a + v.count, 0) : 0)} />
          </div>

          <div className="mt-7 rounded-2xl border border-white/10 bg-ink-900/60 p-5 text-left">
            <p className="mb-3 text-xs font-bold uppercase tracking-widest text-slate-400">
              Violation Penalties
            </p>
            {result.violations.length === 0 ? (
              <p className="text-sm text-mint-400">No violations recorded. Clean session.</p>
            ) : (
              <ul className="space-y-2.5">
                {result.violations.map((v) => (
                  <li key={v.type} className="flex items-center justify-between text-sm">
                    <span className="text-slate-300">
                      {v.type.replace(/_/g, " ")} × {v.count}
                    </span>
                    <span className="font-semibold text-rose-300">
                      {v.total_penalty > 0 ? "+" : ""}
                      {v.total_penalty}
                    </span>
                  </li>
                ))}
              </ul>
            )}
            <div className="mt-4 flex items-center justify-between border-t border-white/10 pt-3 text-sm font-bold">
              <span className="text-slate-300">TOTAL PENALTY</span>
              <span className="text-rose-300">{result.total_penalty} MARKS</span>
            </div>
          </div>

          <div className="mt-6 flex flex-col items-center gap-3">
            <div className="flex items-center gap-2 rounded-xl border border-brand-400/25 bg-brand-500/10 px-4 py-3 text-sm text-brand-200">
              <EyeOff className="h-4 w-4" /> FINAL SCORE: HIDDEN
            </div>
            <p className="max-w-sm text-xs leading-relaxed text-slate-500">
              Your score is reviewed administratively. Correct answers and explanations are not
              displayed to candidates.
            </p>
          </div>

          <div className="mt-6 flex items-center justify-center gap-2 text-xs text-amber-300">
            <Lock className="h-3.5 w-3.5" /> Subject locked — this examination cannot be attempted again.
          </div>

          <button onClick={() => navigate("/dashboard")} className="btn-primary mt-6 w-full py-3">
            BACK TO DASHBOARD
          </button>
        </Card>

        <p className="mt-5 flex items-center justify-center gap-1.5 text-[11px] text-slate-500">
          <ShieldCheck className="h-3.5 w-3.5" /> All incidents were recorded server-side with timestamps.
        </p>
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
      <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">{label}</p>
      <p className="mt-0.5 text-lg font-bold text-slate-100">{value}</p>
    </div>
  );
}

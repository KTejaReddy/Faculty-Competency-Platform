import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  ArrowLeft,
  Camera,
  CheckCircle2,
  ChevronDown,
  Eye,
  FileSearch,
  ShieldAlert,
  Video,
  XCircle,
} from "lucide-react";
import { api } from "../../services/api";
import { Badge, Card, LoadingScreen } from "../../components/ui";
import { PageHeader } from "../../layouts/AdminLayout";
import { ExamVideoPlayer } from "../../components/ExamVideoPlayer";
import {
  difficultyLabel,
  experienceLabel,
  formatDuration,
  formatTimeOnly,
  parseUtc,
  questionTypeLabel,
} from "../../utils/format";
import type { AdminExamReport, ReportViolation } from "../../types";

export function AdminReport() {
  const { id } = useParams();
  const [report, setReport] = useState<AdminExamReport | null>(null);
  const [videoSeek, setVideoSeek] = useState<number | null>(null);

  useEffect(() => {
    api.get<AdminExamReport>(`/api/admin/attempts/${id}/report`).then(setReport).catch(() => {});
  }, [id]);

  const timeline = useMemo<{ violation: ReportViolation; seconds: number }[]>(() => {
    if (!report) return [];
    const start = parseUtc(report.started_at);
    return report.violations.map((v) => ({
      violation: v,
      seconds: Math.max(0, (parseUtc(v.timestamp) - start) / 1000),
    }));
  }, [report]);

  const playerRef = useRef<HTMLDivElement>(null);
  const seekVideo = (seconds: number) => {
    setVideoSeek(seconds);
    playerRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  };

  if (!report) return <LoadingScreen label="Loading examination report…" />;

  const totalViolations = report.violation_summary.reduce((a, v) => a + v.count, 0);

  return (
    <div>
      <PageHeader title="Examination Report" subtitle={`Attempt #${report.attempt_id}`} />
      <Link to={`/admin/faculty`} className="btn-ghost mb-5 !px-3 !py-1.5 text-xs">
        <ArrowLeft className="h-3.5 w-3.5" /> Faculty list
      </Link>

      {/* Summary */}
      <div className="grid gap-5 lg:grid-cols-3">
        <Card className="p-6 lg:col-span-2">
          <div className="grid grid-cols-2 gap-x-8 gap-y-3 text-sm sm:grid-cols-3">
            <SummaryRow label="Faculty" value={report.faculty_name} />
            <SummaryRow label="Department" value={report.department} />
            <SummaryRow label="Subject" value={report.subject_name} />
            <SummaryRow label="Experience" value={experienceLabel(report.experience_band)} />
            <SummaryRow label="Questions" value={`${report.num_questions}`} />
            <SummaryRow
              label="Status"
              value={<Badge tone={report.status === "auto_submitted" ? "red" : "green"}>{report.status.replace("_", " ").toUpperCase()}</Badge>}
            />
            <SummaryRow label="Time Used" value={`${formatDuration(report.time_used_seconds ?? 0)} / ${formatDuration(report.duration_minutes * 60)}`} />
            <SummaryRow label="Started" value={formatTimeOnly(report.started_at)} />
            <SummaryRow label="Submitted" value={report.submitted_at ? formatTimeOnly(report.submitted_at) : "—"} />
          </div>

          <div className="mt-6 grid grid-cols-4 gap-3 border-t border-white/10 pt-5">
            <ScoreBox label="Correct" value={report.correct} tone="text-mint-400" />
            <ScoreBox label="Incorrect" value={report.incorrect} tone="text-rose-400" />
            <ScoreBox label="Unanswered" value={report.unanswered} tone="text-slate-400" />
            <ScoreBox label="Raw Score" value={`${report.raw_score} / ${report.num_questions}`} tone="text-brand-300" />
          </div>
          <div className="mt-5 flex items-center justify-between rounded-xl border border-white/10 bg-ink-900/60 px-5 py-4">
            <div className="text-sm">
              <p className="font-bold uppercase tracking-wider text-slate-400">Final Score</p>
              <p className="mt-1 text-2xl font-extrabold text-slate-50">
                {report.final_score} <span className="text-base font-semibold text-slate-500">/ {report.num_questions}</span>
              </p>
            </div>
            <div className="text-right text-sm">
              <p className="text-slate-400">
                Penalty: <span className="font-bold text-rose-300">{report.penalty_total}</span>
              </p>
              <p className="mt-1 text-xs text-slate-500">{totalViolations} violations recorded</p>
            </div>
          </div>
        </Card>

        <Card className="flex flex-col p-6">
          <h2 className="mb-4 flex items-center gap-2 text-sm font-bold uppercase tracking-widest text-slate-300">
            <ShieldAlert className="h-4 w-4 text-rose-400" /> Security Report
          </h2>
          {report.violation_summary.length === 0 ? (
            <p className="text-sm text-mint-400">No violations. Clean session.</p>
          ) : (
            <ul className="flex-1 space-y-2.5 text-sm">
              {report.violation_summary.map((v) => (
                <li key={v.type} className="flex items-center justify-between">
                  <span className="text-slate-300">{v.type.replace(/_/g, " ")}</span>
                  <span className="flex items-center gap-2">
                    <span className="text-slate-400">×{v.count}</span>
                    <span className="w-14 text-right font-semibold text-rose-300">{v.total_penalty}</span>
                  </span>
                </li>
              ))}
            </ul>
          )}
          <div className="mt-4 flex items-center justify-between border-t border-white/10 pt-3 text-sm font-bold">
            <span className="text-slate-300">TOTAL PENALTY</span>
            <span className="text-rose-300">{report.penalty_total}</span>
          </div>
        </Card>
      </div>

      {/* Recording */}
      <div ref={playerRef} className="mt-8">
        <h2 className="mb-4 flex items-center gap-2 text-sm font-bold uppercase tracking-widest text-slate-300">
          <Video className="h-4 w-4 text-brand-300" /> Exam Recording
        </h2>
        {report.recording && report.recording.status === "ready" ? (
          <div className="grid gap-5 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <ExamVideoPlayer attemptId={report.attempt_id} seekTo={videoSeek} />
            </div>
            <TimelinePanel timeline={timeline} onSeek={seekVideo} />
          </div>
        ) : (
          <Card className="flex items-center gap-3 p-6 text-sm text-slate-400">
            <Camera className="h-5 w-5 text-slate-500" />
            {report.recording ? "Recording not ready." : "No recording was captured for this attempt."}
          </Card>
        )}
      </div>

      {/* Questions */}
      <div className="mt-10">
        <h2 className="mb-4 flex items-center gap-2 text-sm font-bold uppercase tracking-widest text-slate-300">
          <FileSearch className="h-4 w-4 text-brand-300" /> Question-by-Question
        </h2>
        <div className="space-y-4">
          {report.questions.map((q) => (
            <QuestionCard key={q.position} q={q} />
          ))}
        </div>
      </div>
    </div>
  );
}

function SummaryRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">{label}</p>
      <p className="mt-0.5 font-semibold text-slate-200">{value}</p>
    </div>
  );
}

function ScoreBox({ label, value, tone }: { label: string; value: React.ReactNode; tone: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3 text-center">
      <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">{label}</p>
      <p className={`mt-1 text-xl font-extrabold ${tone}`}>{value}</p>
    </div>
  );
}

function TimelinePanel({
  timeline,
  onSeek,
}: {
  timeline: { violation: ReportViolation; seconds: number }[];
  onSeek: (s: number) => void;
}) {
  if (timeline.length === 0) {
    return (
      <Card className="flex items-center gap-3 p-6 text-sm text-mint-400">
        <CheckCircle2 className="h-5 w-5" /> No security events in this session.
      </Card>
    );
  }
  return (
    <Card className="p-5">
      <h3 className="mb-3 text-xs font-bold uppercase tracking-widest text-slate-400">Security Events</h3>
      <ul className="max-h-72 space-y-2 overflow-y-auto pr-1 text-xs">
        {timeline.map(({ violation: v, seconds }) => (
          <li key={v.id}>
            <button
              onClick={() => onSeek(seconds)}
              className="flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-left transition hover:bg-white/5"
            >
              <span className="font-mono text-slate-500">{formatDuration(seconds)}</span>
              <span className="font-semibold text-rose-300">{v.type.replace(/_/g, " ")}</span>
              <span className="ml-auto flex items-center gap-1 text-slate-500">
                <Eye className="h-3 w-3" /> seek
              </span>
            </button>
          </li>
        ))}
      </ul>
    </Card>
  );
}

function QuestionCard({ q }: { q: AdminExamReport["questions"][number] }) {
  const [open, setOpen] = useState(false);
  const optionLetters = ["A", "B", "C", "D", "E", "F"];
  const correct = new Set(q.correct_options);

  return (
    <Card className="overflow-hidden">
      <button onClick={() => setOpen((o) => !o)} className="flex w-full items-center gap-3 px-5 py-4 text-left">
        {q.is_correct ? (
          <CheckCircle2 className="h-5 w-5 shrink-0 text-mint-400" />
        ) : (
          <XCircle className="h-5 w-5 shrink-0 text-rose-400" />
        )}
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold text-slate-100">
            Q{q.position} <span className="font-normal text-slate-500">· {questionTypeLabel(q.question_type)} · {difficultyLabel(q.difficulty)} · {q.topic}</span>
          </p>
          <p className="mt-0.5 line-clamp-2 text-xs text-slate-400">{q.question_text}</p>
        </div>
        <span className="font-mono text-xs text-slate-500">{q.marks_awarded} / 1</span>
        <ChevronDown className={`h-4 w-4 shrink-0 text-slate-500 transition ${open ? "rotate-180" : ""}`} />
      </button>
      {open && (
        <div className="border-t border-white/5 px-5 py-4">
          <p className="text-sm leading-relaxed text-slate-200" style={{ whiteSpace: "pre-wrap" }}>
            {q.question_text}
          </p>
          <div className="mt-3 space-y-1.5">
            {q.options.map((opt, i) => {
              const isCorrect = correct.has(i);
              const chosen = q.chosen_options.includes(i);
              return (
                <div
                  key={i}
                  className={`flex items-start gap-2.5 rounded-lg border px-3 py-2 text-sm ${
                    isCorrect
                      ? "border-mint-500/40 bg-mint-500/10 text-mint-300"
                      : chosen
                        ? "border-rose-500/40 bg-rose-500/10 text-rose-300"
                        : "border-white/5 text-slate-400"
                  }`}
                >
                  <span className="font-bold">{optionLetters[i]}</span>
                  <span className="flex-1">{opt}</span>
                  {isCorrect && <CheckCircle2 className="h-4 w-4 shrink-0" />}
                  {chosen && !isCorrect && <XCircle className="h-4 w-4 shrink-0" />}
                </div>
              );
            })}
          </div>
          {q.explanation && (
            <div className="mt-3 rounded-xl border border-brand-400/20 bg-brand-500/5 px-4 py-3">
              <p className="text-[10px] font-bold uppercase tracking-widest text-brand-300">Explanation</p>
              <p className="mt-1 text-sm leading-relaxed text-slate-300">{q.explanation}</p>
            </div>
          )}
        </div>
      )}
    </Card>
  );
}

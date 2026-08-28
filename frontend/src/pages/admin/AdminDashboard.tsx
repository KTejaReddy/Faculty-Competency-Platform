import { useEffect, useState } from "react";
import {
  AlertTriangle,
  BookOpenCheck,
  ClipboardCheck,
  FileQuestion,
  Hourglass,
  Users,
} from "lucide-react";
import { api } from "../../services/api";
import { Card, LoadingScreen, StatCard } from "../../components/ui";
import { PageHeader } from "../../layouts/AdminLayout";
import type { AdminStats, Analytics } from "../../types";

export function AdminDashboard() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);

  useEffect(() => {
    api.get<AdminStats>("/api/admin/stats").then(setStats).catch(() => {});
    api.get<Analytics>("/api/admin/analytics").then(setAnalytics).catch(() => {});
  }, []);

  if (!stats || !analytics) return <LoadingScreen label="Loading dashboard…" />;

  const maxSubject = Math.max(1, ...analytics.subject_performance.map((s) => s.avg_score));
  const maxViolation = Math.max(1, ...analytics.violation_distribution.map((v) => v.count));

  return (
    <div>
      <PageHeader title="Admin Dashboard" subtitle="Platform overview and examination analytics." />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard label="Total Faculty" value={stats.total_faculty} icon={<Users className="h-5 w-5" />} />
        <StatCard label="Exams Completed" value={stats.exams_completed} icon={<ClipboardCheck className="h-5 w-5" />} tone="green" />
        <StatCard label="Exams Pending" value={stats.exams_pending} icon={<Hourglass className="h-5 w-5" />} tone="amber" />
        <StatCard label="Total Subjects" value={stats.total_subjects} icon={<BookOpenCheck className="h-5 w-5" />} />
        <StatCard label="Total Questions" value={stats.total_questions} icon={<FileQuestion className="h-5 w-5" />} />
        <StatCard label="Total Violations" value={stats.total_violations} icon={<AlertTriangle className="h-5 w-5" />} tone="red" />
      </div>

      <div className="mt-6 grid gap-5 lg:grid-cols-2">
        <Card className="p-6">
          <div className="mb-5 flex items-center justify-between">
            <h2 className="text-sm font-bold uppercase tracking-widest text-slate-300">Subject Performance</h2>
            <span className="chip text-brand-300">AVG {analytics.average_score}</span>
          </div>
          <div className="space-y-3">
            {analytics.subject_performance.map((s) => (
              <div key={s.subject}>
                <div className="mb-1 flex items-center justify-between text-xs">
                  <span className="truncate text-slate-300">{s.subject}</span>
                  <span className="font-semibold text-slate-400">
                    {s.avg_score} <span className="text-slate-600">/ {s.attempts} exams</span>
                  </span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-white/10">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-brand-500 to-mint-500"
                    style={{ width: `${(s.avg_score / maxSubject) * 100}%` }}
                  />
                </div>
              </div>
            ))}
            {analytics.subject_performance.length === 0 && (
              <p className="text-sm text-slate-500">No completed exams yet.</p>
            )}
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="mb-5 text-sm font-bold uppercase tracking-widest text-slate-300">
            Violation Distribution
          </h2>
          {analytics.violation_distribution.length === 0 ? (
            <p className="text-sm text-slate-500">No violations recorded yet.</p>
          ) : (
            <div className="space-y-3">
              {analytics.violation_distribution.map((v) => (
                <div key={v.type}>
                  <div className="mb-1 flex items-center justify-between text-xs">
                    <span className="text-slate-300">{v.type.replace(/_/g, " ")}</span>
                    <span className="font-semibold text-slate-400">{v.count}</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-white/10">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-rose-500 to-amber-400"
                      style={{ width: `${(v.count / maxViolation) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      <Card className="mt-6 flex items-center justify-between p-6">
        <div>
          <h2 className="text-sm font-bold uppercase tracking-widest text-slate-300">Completion Rate</h2>
          <p className="mt-1 text-xs text-slate-500">
            Share of started examinations that were submitted (including auto-submissions).
          </p>
        </div>
        <div className="relative flex h-24 w-24 items-center justify-center">
          <svg viewBox="0 0 100 100" className="h-24 w-24 -rotate-90">
            <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="10" />
            <circle
              cx="50"
              cy="50"
              r="42"
              fill="none"
              stroke="url(#g)"
              strokeWidth="10"
              strokeLinecap="round"
              strokeDasharray={`${analytics.completion_rate * 2.64} 264`}
            />
            <defs>
              <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#818cf8" />
                <stop offset="100%" stopColor="#34d399" />
              </linearGradient>
            </defs>
          </svg>
          <span className="absolute text-lg font-bold text-slate-100">{analytics.completion_rate}%</span>
        </div>
      </Card>
    </div>
  );
}

import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { AlertTriangle, ArrowLeft, ClipboardList, FileSearch, RefreshCw } from "lucide-react";
import { api } from "../../services/api";
import { Badge, Card, EmptyState, LoadingScreen } from "../../components/ui";
import { PageHeader } from "../../layouts/AdminLayout";
import { experienceLabel, formatDateTime, formatDuration } from "../../utils/format";
import type { AttemptListItem } from "../../types";

export function AdminFacultyDetail() {
  const { id } = useParams();
  const [attempts, setAttempts] = useState<AttemptListItem[] | null>(null);
  const [loadError, setLoadError] = useState(false);

  const load = useCallback(() => {
    setLoadError(false);
    setAttempts(null);
    api
      .get<AttemptListItem[]>(`/api/admin/attempts?faculty_id=${id}`)
      .then(setAttempts)
      .catch(() => setLoadError(true));
  }, [id]);

  useEffect(load, [load]);

  if (loadError) {
    return (
      <div>
        <PageHeader title="Faculty history" subtitle="Examination history for this faculty member." />
        <EmptyState
          icon={<AlertTriangle className="h-6 w-6" />}
          title="Could not load examination history"
          hint="The server returned an error. Try again, or check the API logs."
          action={
            <button onClick={load} className="btn-primary !px-4 !py-2 text-xs">
              <RefreshCw className="h-3.5 w-3.5" /> RETRY
            </button>
          }
        />
      </div>
    );
  }

  if (!attempts) return <LoadingScreen label="Loading faculty history…" />;

  const facultyName = attempts[0]?.faculty_name ?? "Faculty member";
  const department = attempts[0]?.department ?? "";

  return (
    <div>
      <PageHeader title={facultyName} subtitle={department} />
      <Link to="/admin/faculty" className="btn-ghost mb-5 !px-3 !py-1.5 text-xs">
        <ArrowLeft className="h-3.5 w-3.5" /> All faculty
      </Link>

      {attempts.length === 0 ? (
        <EmptyState
          icon={<ClipboardList className="h-6 w-6" />}
          title="No examinations yet"
          hint="This faculty member has not started any examinations."
        />
      ) : (
        <Card className="overflow-x-auto p-0">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-white/10 text-xs uppercase tracking-wider text-slate-500">
                <th className="px-5 py-3.5">Subject</th>
                <th className="px-5 py-3.5">Experience</th>
                <th className="px-5 py-3.5">Status</th>
                <th className="px-5 py-3.5">Started</th>
                <th className="px-5 py-3.5">Time Used</th>
                <th className="px-5 py-3.5">Final Score</th>
                <th className="px-5 py-3.5">Violations</th>
                <th className="px-5 py-3.5 text-right">Report</th>
              </tr>
            </thead>
            <tbody>
              {attempts.map((a) => (
                <tr key={a.id} className="border-b border-white/5 transition hover:bg-white/[0.03]">
                  <td className="px-5 py-3.5 font-semibold text-slate-100">{a.subject_name}</td>
                  <td className="px-5 py-3.5 text-slate-400">{experienceLabel(a.experience_band)}</td>
                  <td className="px-5 py-3.5">
                    <Badge tone={a.status === "in_progress" ? "amber" : a.status === "auto_submitted" ? "red" : "green"}>
                      {a.status.replace("_", " ").toUpperCase()}
                    </Badge>
                  </td>
                  <td className="px-5 py-3.5 text-slate-400">{formatDateTime(a.started_at)}</td>
                  <td className="px-5 py-3.5 text-slate-400">
                    {a.time_used_seconds != null ? formatDuration(a.time_used_seconds) : "—"}
                  </td>
                  <td className="px-5 py-3.5 font-bold text-slate-100">
                    {a.final_score != null ? `${a.final_score} / ${a.raw_score != null ? a.raw_score : "?"}` : "—"}
                  </td>
                  <td className="px-5 py-3.5">
                    <Badge tone={a.violation_count > 0 ? "red" : "green"}>{a.violation_count}</Badge>
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <Link to={`/admin/attempts/${a.id}`} className="btn-secondary !px-3.5 !py-1.5 text-xs">
                      <FileSearch className="h-3.5 w-3.5" /> OPEN
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  );
}

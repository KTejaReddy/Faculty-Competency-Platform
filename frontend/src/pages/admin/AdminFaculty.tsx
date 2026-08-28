import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Eye, Search, Users } from "lucide-react";
import { api } from "../../services/api";
import { Badge, Card, EmptyState, LoadingScreen } from "../../components/ui";
import { PageHeader } from "../../layouts/AdminLayout";
import type { FacultyListItem } from "../../types";

export function AdminFaculty() {
  const [faculty, setFaculty] = useState<FacultyListItem[] | null>(null);
  const [query, setQuery] = useState("");

  useEffect(() => {
    api.get<FacultyListItem[]>("/api/admin/faculty").then(setFaculty).catch(() => {});
  }, []);

  const filtered = useMemo(() => {
    if (!faculty) return [];
    const q = query.trim().toLowerCase();
    if (!q) return faculty;
    return faculty.filter(
      (f) => f.full_name.toLowerCase().includes(q) || f.department.toLowerCase().includes(q)
    );
  }, [faculty, query]);

  if (!faculty) return <LoadingScreen label="Loading faculty…" />;

  return (
    <div>
      <PageHeader title="Faculty" subtitle="All registered faculty and their examination summaries." />

      <div className="relative mb-5 max-w-sm">
        <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
        <input
          className="input !pl-10"
          placeholder="Search by name or department…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon={<Users className="h-6 w-6" />}
          title="No faculty found"
          hint={faculty.length === 0 ? "Faculty accounts appear here after registration." : "Try a different search."}
        />
      ) : (
        <Card className="overflow-x-auto p-0">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-white/10 text-xs uppercase tracking-wider text-slate-500">
                <th className="px-5 py-3.5">Faculty Name</th>
                <th className="px-5 py-3.5">Department</th>
                <th className="px-5 py-3.5">Subjects Completed</th>
                <th className="px-5 py-3.5">Average Score</th>
                <th className="px-5 py-3.5">Total Violations</th>
                <th className="px-5 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((f) => (
                <tr key={f.id} className="border-b border-white/5 transition hover:bg-white/[0.03]">
                  <td className="px-5 py-3.5 font-semibold text-slate-100">{f.full_name}</td>
                  <td className="px-5 py-3.5 text-slate-400">{f.department}</td>
                  <td className="px-5 py-3.5">
                    <Badge tone="brand">{f.subjects_completed}</Badge>
                  </td>
                  <td className="px-5 py-3.5 font-semibold text-slate-200">{f.average_score}</td>
                  <td className="px-5 py-3.5">
                    <Badge tone={f.total_violations > 0 ? "red" : "green"}>{f.total_violations}</Badge>
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <Link to={`/admin/faculty/${f.id}`} className="btn-secondary !px-3.5 !py-1.5 text-xs">
                      <Eye className="h-3.5 w-3.5" /> VIEW
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

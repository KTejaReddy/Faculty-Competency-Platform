import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { FileQuestion, Filter, Pencil, Plus, Search, Trash2 } from "lucide-react";
import { api } from "../../services/api";
import { Badge, Card, EmptyState, LoadingScreen, Modal, Spinner } from "../../components/ui";
import { PageHeader } from "../../layouts/AdminLayout";
import { useToast } from "../../components/Toast";
import { difficultyLabel, questionTypeLabel } from "../../utils/format";
import type { AdminQuestion, Difficulty, QuestionListResponse, QuestionType, Subject } from "../../types";

const DIFFICULTIES: Difficulty[] = ["hard", "very_hard", "expert"];
const TYPES: QuestionType[] = ["single", "multiple", "assertion_reason", "scenario", "code", "numerical", "debugging"];

export function AdminQuestions() {
  const { toast } = useToast();
  const [data, setData] = useState<QuestionListResponse | null>(null);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({ q: "", subject_id: "", difficulty: "", question_type: "", experience: "" });
  const [toDelete, setToDelete] = useState<AdminQuestion | null>(null);
  const [deleting, setDeleting] = useState(false);

  const pageSize = 15;

  const load = () => {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (filters.q) params.set("q", filters.q);
    if (filters.subject_id) params.set("subject_id", filters.subject_id);
    if (filters.difficulty) params.set("difficulty", filters.difficulty);
    if (filters.question_type) params.set("question_type", filters.question_type);
    if (filters.experience) params.set("experience_min", filters.experience);
    api.get<QuestionListResponse>(`/api/admin/questions?${params}`).then(setData).catch(() => {});
  };

  useEffect(load, [page, filters]);
  useEffect(() => {
    api.get<Subject[]>("/api/admin/subjects").then(setSubjects).catch(() => {});
  }, []);

  const totalPages = data ? Math.max(1, Math.ceil(data.total / pageSize)) : 1;
  const subjectName = useMemo(() => {
    const map = new Map(subjects.map((s) => [s.id, s.name]));
    return (id: number) => map.get(id) ?? `#${id}`;
  }, [subjects]);

  const confirmDelete = async () => {
    if (!toDelete) return;
    setDeleting(true);
    try {
      await api.del(`/api/admin/questions/${toDelete.id}`);
      toast("Question deleted.", "success");
      setToDelete(null);
      load();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Delete failed.", "error");
    } finally {
      setDeleting(false);
    }
  };

  if (!data) return <LoadingScreen label="Loading question bank…" />;

  return (
    <div>
      <PageHeader
        title="Question Bank"
        subtitle={`${data.total} questions · ${subjects.length} subjects`}
        actions={
          <Link to="/admin/questions/new" className="btn-primary">
            <Plus className="h-4 w-4" /> Add Question
          </Link>
        }
      />

      <Card className="mb-5 flex flex-wrap items-end gap-3 p-4">
        <div className="flex items-center gap-1.5 self-center text-slate-500">
          <Filter className="h-4 w-4" />
        </div>
        <div className="relative min-w-56 flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <input
            className="input !pl-9"
            placeholder="Search question text…"
            value={filters.q}
            onChange={(e) => {
              setFilters((f) => ({ ...f, q: e.target.value }));
              setPage(1);
            }}
          />
        </div>
        <select
          className="input !w-auto"
          value={filters.subject_id}
          onChange={(e) => {
            setFilters((f) => ({ ...f, subject_id: e.target.value }));
            setPage(1);
          }}
        >
          <option value="">All subjects</option>
          {subjects.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name}
            </option>
          ))}
        </select>
        <select
          className="input !w-auto"
          value={filters.difficulty}
          onChange={(e) => {
            setFilters((f) => ({ ...f, difficulty: e.target.value }));
            setPage(1);
          }}
        >
          <option value="">All difficulties</option>
          {DIFFICULTIES.map((d) => (
            <option key={d} value={d}>
              {difficultyLabel(d)}
            </option>
          ))}
        </select>
        <select
          className="input !w-auto"
          value={filters.question_type}
          onChange={(e) => {
            setFilters((f) => ({ ...f, question_type: e.target.value }));
            setPage(1);
          }}
        >
          <option value="">All types</option>
          {TYPES.map((t) => (
            <option key={t} value={t}>
              {questionTypeLabel(t)}
            </option>
          ))}
        </select>
        <select
          className="input !w-auto"
          value={filters.experience}
          onChange={(e) => {
            setFilters((f) => ({ ...f, experience: e.target.value }));
            setPage(1);
          }}
        >
          <option value="">Any experience</option>
          {[3, 7, 12, 20].map((y) => (
            <option key={y} value={y}>
              Up to {y} yrs
            </option>
          ))}
        </select>
      </Card>

      {data.items.length === 0 ? (
        <EmptyState
          icon={<FileQuestion className="h-6 w-6" />}
          title="No questions match"
          hint="Adjust the filters or add a new question."
          action={
            <Link to="/admin/questions/new" className="btn-secondary">
              <Plus className="h-4 w-4" /> Add Question
            </Link>
          }
        />
      ) : (
        <>
          <Card className="overflow-x-auto p-0">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-white/10 text-xs uppercase tracking-wider text-slate-500">
                  <th className="px-5 py-3.5">Question</th>
                  <th className="px-5 py-3.5">Subject</th>
                  <th className="px-5 py-3.5">Type</th>
                  <th className="px-5 py-3.5">Difficulty</th>
                  <th className="px-5 py-3.5">Exp. Min</th>
                  <th className="px-5 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((q) => (
                  <tr key={q.id} className="border-b border-white/5 transition hover:bg-white/[0.03]">
                    <td className="max-w-md px-5 py-3.5">
                      <p className="line-clamp-2 text-slate-300">{q.question_text}</p>
                      <p className="mt-0.5 text-xs text-slate-500">
                        {q.topic_name} · {q.options.length} options
                      </p>
                    </td>
                    <td className="px-5 py-3.5 text-slate-400">{subjectName(q.subject_id)}</td>
                    <td className="px-5 py-3.5 text-slate-400">{questionTypeLabel(q.question_type)}</td>
                    <td className="px-5 py-3.5">
                      <Badge tone={q.difficulty === "expert" ? "red" : q.difficulty === "very_hard" ? "amber" : "slate"}>
                        {difficultyLabel(q.difficulty)}
                      </Badge>
                    </td>
                    <td className="px-5 py-3.5 text-slate-400">{q.experience_min}</td>
                    <td className="px-5 py-3.5">
                      <div className="flex justify-end gap-1.5">
                        <Link to={`/admin/questions/${q.id}/edit`} className="btn-secondary !px-2.5 !py-1.5">
                          <Pencil className="h-3.5 w-3.5" />
                        </Link>
                        <button onClick={() => setToDelete(q)} className="btn-danger !px-2.5 !py-1.5">
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
          <div className="mt-4 flex items-center justify-between text-sm text-slate-400">
            <span>
              Page {page} of {totalPages} · {data.total} results
            </span>
            <div className="flex gap-2">
              <button className="btn-secondary !py-1.5" disabled={page <= 1} onClick={() => setPage(page - 1)}>
                Previous
              </button>
              <button className="btn-secondary !py-1.5" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
                Next
              </button>
            </div>
          </div>
        </>
      )}

      <Modal open={!!toDelete} onClose={() => setToDelete(null)} title="Delete question?">
        <p className="text-sm text-slate-300">
          This permanently deletes the question. Attempts that already used it keep their stored copy.
        </p>
        <div className="mt-5 flex justify-end gap-3">
          <button className="btn-secondary" onClick={() => setToDelete(null)}>
            Cancel
          </button>
          <button className="btn-danger" disabled={deleting} onClick={confirmDelete}>
            {deleting ? <Spinner /> : <Trash2 className="h-4 w-4" />} Delete
          </button>
        </div>
      </Modal>
    </div>
  );
}

import { useEffect, useMemo, useState, type FormEvent } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Plus, Save, Trash2 } from "lucide-react";
import { api } from "../../services/api";
import { Card, Spinner } from "../../components/ui";
import { useToast } from "../../components/Toast";
import { difficultyLabel, questionTypeLabel } from "../../utils/format";
import type { AdminQuestion, AdminQuestionInput, Difficulty, QuestionType, Subject, Topic } from "../../types";

const DIFFICULTIES: Difficulty[] = ["hard", "very_hard", "expert"];
const TYPES: QuestionType[] = ["single", "multiple", "assertion_reason", "scenario", "code", "numerical", "debugging"];

const EMPTY_OPTIONS = ["", "", "", ""];

export function AdminQuestionEditor() {
  const { id } = useParams();
  const editing = Boolean(id);
  const navigate = useNavigate();
  const { toast } = useToast();

  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [form, setForm] = useState<AdminQuestionInput>({
    subject_id: 0,
    topic_id: 0,
    difficulty: "very_hard",
    experience_min: 1,
    question_type: "single",
    question_text: "",
    options: [...EMPTY_OPTIONS],
    correct_answer: [],
    explanation: "",
  });
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.get<Subject[]>("/api/admin/subjects").then((s) => {
      setSubjects(s);
      if (s.length && !form.subject_id) setForm((f) => ({ ...f, subject_id: s[0].id }));
    });
  }, []);

  useEffect(() => {
    if (editing) {
      api
        .get<{ items: AdminQuestion[]; total: number }>(`/api/admin/questions?page_size=100`)
        .then((res) => {
          const q = res.items.find((x) => String(x.id) === id);
          if (q) {
            setForm({
              subject_id: q.subject_id,
              topic_id: q.topic_id,
              difficulty: q.difficulty,
              experience_min: q.experience_min,
              question_type: q.question_type,
              question_text: q.question_text,
              options: [...q.options, ...EMPTY_OPTIONS].slice(0, 6),
              correct_answer: [...q.correct_answer],
              explanation: q.explanation,
            });
          }
        })
        .catch(() => {});
    }
  }, [editing, id]);

  useEffect(() => {
    if (!form.subject_id) return;
    api.get<Topic[]>(`/api/admin/subjects/${form.subject_id}/topics`).then(setTopics);
  }, [form.subject_id]);

  const optionsCount = useMemo(() => form.options.filter((o) => o.trim() !== "").length, [form.options]);

  const set = (patch: Partial<AdminQuestionInput>) => setForm((f) => ({ ...f, ...patch }));

  const setOption = (i: number, value: string) => {
    const options = [...form.options];
    options[i] = value;
    set({ options });
  };

  const toggleCorrect = (i: number) => {
    const current = [...form.correct_answer];
    if (current.includes(i)) {
      set({ correct_answer: current.filter((x) => x !== i) });
    } else {
      if (form.question_type !== "multiple" && current.length >= 1) current.length = 0;
      current.push(i);
      set({ correct_answer: current });
    }
  };

  const addOption = () => {
    if (form.options.length >= 6) return;
    set({ options: [...form.options, ""] });
  };

  const removeOption = (i: number) => {
    if (form.options.length <= 2) return;
    const options = form.options.filter((_, idx) => idx !== i);
    const correct_answer = form.correct_answer
      .filter((x) => x !== i)
      .map((x) => (x > i ? x - 1 : x));
    set({ options, correct_answer });
  };

  const save = async (e: FormEvent) => {
    e.preventDefault();
    const opts = form.options.filter((o) => o.trim() !== "");
    const payload: AdminQuestionInput = { ...form, options: opts };

    if (!form.subject_id || !form.topic_id) return toast("Select subject and topic.", "warning");
    if (opts.length < 2) return toast("At least 2 non-empty options are required.", "warning");
    if (!form.question_text.trim()) return toast("Question text is required.", "warning");
    if (payload.correct_answer.length === 0) return toast("Select at least one correct option.", "warning");
    if (payload.correct_answer.some((i) => i >= opts.length)) return toast("Correct answer index out of range.", "error");

    setBusy(true);
    try {
      if (editing) {
        await api.put(`/api/admin/questions/${id}`, payload);
        toast("Question updated.", "success");
      } else {
        await api.post("/api/admin/questions", payload);
        toast("Question created.", "success");
      }
      navigate("/admin/questions");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Save failed.", "error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <div className="mb-5">
        <Link to="/admin/questions" className="btn-ghost mb-3 !px-3 !py-1.5 text-xs">
          <ArrowLeft className="h-3.5 w-3.5" /> Question bank
        </Link>
        <h1 className="text-2xl font-extrabold tracking-tight text-slate-50">
          {editing ? "Edit Question" : "Add Question"}
        </h1>
      </div>

      <form onSubmit={save} className="space-y-5">
        <Card className="grid gap-4 p-6 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <label className="label">Subject</label>
            <select
              className="input"
              value={form.subject_id || ""}
              onChange={(e) => set({ subject_id: Number(e.target.value), topic_id: 0 })}
            >
              <option value="">Select subject</option>
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Topic</label>
            <select className="input" value={form.topic_id || ""} onChange={(e) => set({ topic_id: Number(e.target.value) })}>
              <option value="">Select topic</option>
              {topics.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Difficulty</label>
            <select className="input" value={form.difficulty} onChange={(e) => set({ difficulty: e.target.value as Difficulty })}>
              {DIFFICULTIES.map((d) => (
                <option key={d} value={d}>
                  {difficultyLabel(d)}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Min. Experience (years)</label>
            <input
              className="input"
              type="number"
              min={1}
              max={40}
              value={form.experience_min}
              onChange={(e) => set({ experience_min: Number(e.target.value) })}
            />
          </div>
          <div className="sm:col-span-2">
            <label className="label">Question Type</label>
            <select
              className="input"
              value={form.question_type}
              onChange={(e) => {
                const t = e.target.value as QuestionType;
                set({ question_type: t, correct_answer: t === "multiple" ? form.correct_answer : form.correct_answer.slice(0, 1) });
              }}
            >
              {TYPES.map((t) => (
                <option key={t} value={t}>
                  {questionTypeLabel(t)}
                </option>
              ))}
            </select>
          </div>
          <div className="sm:col-span-2">
            <label className="label">Explanation</label>
            <input
              className="input"
              value={form.explanation}
              onChange={(e) => set({ explanation: e.target.value })}
              placeholder="Shown to admins in reports…"
            />
          </div>
        </Card>

        <Card className="p-6">
          <label className="label">Question</label>
          <textarea
            className="input min-h-28 resize-y"
            value={form.question_text}
            onChange={(e) => set({ question_text: e.target.value })}
            placeholder="Write the question text. Use backticks for code blocks."
          />

          <div className="mt-6 flex items-center justify-between">
            <label className="label !mb-0">
              Options ({optionsCount}) {form.question_type === "multiple" ? "— select ALL correct" : "— select the correct one"}
            </label>
            {form.options.length < 6 && (
              <button type="button" onClick={addOption} className="btn-ghost !py-1 text-xs">
                <Plus className="h-3.5 w-3.5" /> Add option
              </button>
            )}
          </div>
          <div className="mt-3 space-y-2.5">
            {form.options.map((opt, i) => {
              const letter = String.fromCharCode(65 + i);
              const isCorrect = form.correct_answer.includes(i);
              return (
                <div key={i} className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={() => toggleCorrect(i)}
                    className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border text-sm font-bold transition ${
                      isCorrect
                        ? "border-mint-500 bg-mint-500/20 text-mint-300"
                        : "border-white/15 text-slate-500 hover:border-white/30"
                    }`}
                    title={isCorrect ? "Marked correct — click to unmark" : "Mark as correct"}
                  >
                    {letter}
                  </button>
                  <input
                    className="input"
                    value={opt}
                    onChange={(e) => setOption(i, e.target.value)}
                    placeholder={`Option ${letter}`}
                  />
                  {form.options.length > 2 && (
                    <button type="button" onClick={() => removeOption(i)} className="shrink-0 text-slate-500 hover:text-rose-400">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  )}
                </div>
              );
            })}
          </div>
          <p className="mt-3 text-xs text-slate-500">
            {form.question_type === "multiple"
              ? "For multiple-correct questions, all correct options must be chosen to earn the mark."
              : "Single-answer questions award 1 mark for the exact correct option."}
          </p>
        </Card>

        <div className="flex justify-end gap-3">
          <Link to="/admin/questions" className="btn-secondary">
            Cancel
          </Link>
          <button className="btn-primary" disabled={busy}>
            {busy ? <Spinner /> : <Save className="h-4 w-4" />} {editing ? "Save Changes" : "Create Question"}
          </button>
        </div>
      </form>
    </div>
  );
}

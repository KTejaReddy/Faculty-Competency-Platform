import { useEffect, useState, type FormEvent } from "react";
import { BookOpenCheck, Plus, Save, Tag } from "lucide-react";
import { api } from "../../services/api";
import { Badge, Card, LoadingScreen, Modal, Spinner } from "../../components/ui";
import { PageHeader } from "../../layouts/AdminLayout";
import { useToast } from "../../components/Toast";
import type { ExamConfig, Subject, Topic } from "../../types";

export function AdminSubjects() {
  const { toast } = useToast();
  const [subjects, setSubjects] = useState<Subject[] | null>(null);
  const [configs, setConfigs] = useState<Record<number, ExamConfig>>({});
  const [topics, setTopics] = useState<Record<number, Topic[]>>({});
  const [createOpen, setCreateOpen] = useState(false);
  const [configFor, setConfigFor] = useState<Subject | null>(null);
  const [busy, setBusy] = useState(false);

  const load = () => {
    api.get<Subject[]>("/api/admin/subjects").then((s) => {
      setSubjects(s);
      api.get<ExamConfig[]>("/api/admin/exam-configs").then((cs) => {
        setConfigs(Object.fromEntries(cs.map((c) => [c.subject_id, c])));
      });
    });
    api.get<Record<string, never>>("/api/admin/analytics").catch(() => {});
  };

  useEffect(load, []);

  const loadTopics = async (subjectId: number) => {
    if (topics[subjectId]) return;
    const t = await api.get<Topic[]>(`/api/admin/subjects/${subjectId}/topics`).catch(() => []);
    setTopics((prev) => ({ ...prev, [subjectId]: t }));
  };

  if (!subjects) return <LoadingScreen label="Loading subjects…" />;

  return (
    <div>
      <PageHeader
        title="Subjects"
        subtitle="Subjects, topics and per-subject examination configuration."
        actions={
          <button onClick={() => setCreateOpen(true)} className="btn-primary">
            <Plus className="h-4 w-4" /> Add Subject
          </button>
        }
      />

      <div className="grid gap-4 lg:grid-cols-2">
        {subjects.map((s) => {
          const cfg = configs[s.id];
          return (
            <Card key={s.id} className="p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-bold text-slate-100">{s.name}</p>
                  <p className="text-xs text-slate-500">
                    {s.code} · {s.difficulty_label}
                  </p>
                </div>
                <Badge tone={cfg?.active ? "green" : "slate"}>{cfg?.active ? "ACTIVE" : "DISABLED"}</Badge>
              </div>
              {cfg && (
                <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                  <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
                    <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">Questions / exam</p>
                    <p className="mt-0.5 text-lg font-bold text-slate-100">{cfg.num_questions}</p>
                  </div>
                  <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
                    <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">Duration</p>
                    <p className="mt-0.5 text-lg font-bold text-slate-100">{cfg.duration_minutes} min</p>
                  </div>
                </div>
              )}
              <div className="mt-4 flex flex-wrap items-center gap-2">
                <button
                  onClick={() => {
                    setConfigFor(s);
                    void loadTopics(s.id);
                  }}
                  className="btn-secondary !px-3 !py-1.5 text-xs"
                >
                  <BookOpenCheck className="h-3.5 w-3.5" /> Exam config & topics
                </button>
                {topics[s.id] && (
                  <span className="chip text-slate-400">
                    <Tag className="h-3 w-3" /> {topics[s.id].length} topics
                  </span>
                )}
              </div>
            </Card>
          );
        })}
      </div>

      {createOpen && (
        <CreateSubjectModal
          onClose={() => setCreateOpen(false)}
          onCreated={() => {
            setCreateOpen(false);
            load();
          }}
        />
      )}

      {configFor && (
        <ConfigModal
          subject={configFor}
          cfg={configs[configFor.id]}
          topics={topics[configFor.id] ?? []}
          busy={busy}
          onClose={() => setConfigFor(null)}
          onSaved={(c) => {
            setConfigs((prev) => ({ ...prev, [c.subject_id]: c }));
            setConfigFor(null);
            toast("Configuration saved.", "success");
          }}
          setBusy={setBusy}
          reloadTopics={() => loadTopics(configFor.id)}
        />
      )}
    </div>
  );
}

function CreateSubjectModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [form, setForm] = useState({ name: "", code: "", description: "" });
  const [busy, setBusy] = useState(false);
  const { toast } = useToast();

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try {
      await api.post("/api/admin/subjects", { ...form, difficulty_label: "Expert Assessment" });
      toast("Subject created.", "success");
      onCreated();
    } catch (err) {
      toast(err instanceof Error ? err.message : "Create failed.", "error");
      setBusy(false);
    }
  };

  return (
    <Modal open onClose={onClose} title="Add Subject">
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className="label">Subject Name</label>
          <input className="input uppercase" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value.toUpperCase() })} placeholder="QUANTUM COMPUTING" />
        </div>
        <div>
          <label className="label">Code</label>
          <input className="input uppercase" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value.toUpperCase() })} placeholder="QC" />
        </div>
        <div>
          <label className="label">Description</label>
          <textarea className="input min-h-20" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        </div>
        <div className="flex justify-end gap-3">
          <button type="button" className="btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button className="btn-primary" disabled={busy}>
            {busy ? <Spinner /> : <Save className="h-4 w-4" />} Create
          </button>
        </div>
      </form>
    </Modal>
  );
}

function ConfigModal({
  subject,
  cfg,
  topics,
  busy,
  onClose,
  onSaved,
  setBusy,
  reloadTopics,
}: {
  subject: Subject;
  cfg: ExamConfig;
  topics: Topic[];
  busy: boolean;
  onClose: () => void;
  onSaved: (c: ExamConfig) => void;
  setBusy: (b: boolean) => void;
  reloadTopics: () => void;
}) {
  const { toast } = useToast();
  const [numQuestions, setNumQuestions] = useState(cfg.num_questions);
  const [duration, setDuration] = useState(cfg.duration_minutes);
  const [active, setActive] = useState(cfg.active);
  const [newTopic, setNewTopic] = useState("");

  const save = async () => {
    setBusy(true);
    try {
      const updated = await api.put<ExamConfig>(`/api/admin/exam-configs/${cfg.id}`, {
        num_questions: numQuestions,
        duration_minutes: duration,
        active,
      });
      onSaved(updated);
    } catch (err) {
      toast(err instanceof Error ? err.message : "Save failed.", "error");
    } finally {
      setBusy(false);
    }
  };

  const addTopic = async () => {
    if (!newTopic.trim()) return;
    try {
      await api.post(`/api/admin/topics?subject_id=${subject.id}`, { name: newTopic.trim().toUpperCase() });
      setNewTopic("");
      reloadTopics();
      toast("Topic added.", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Could not add topic.", "error");
    }
  };

  return (
    <Modal open onClose={onClose} title={subject.name}>
      <div className="space-y-5">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label">Questions per exam</label>
            <input
              className="input"
              type="number"
              min={1}
              max={100}
              value={numQuestions}
              onChange={(e) => setNumQuestions(Number(e.target.value))}
            />
            <p className="mt-1 text-[11px] text-slate-500">Default 40 for production banks.</p>
          </div>
          <div>
            <label className="label">Duration (minutes)</label>
            <input
              className="input"
              type="number"
              min={5}
              max={240}
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
            />
          </div>
        </div>
        <label className="flex items-center gap-2.5 text-sm text-slate-300">
          <input type="checkbox" checked={active} onChange={(e) => setActive(e.target.checked)} className="h-4 w-4 accent-brand-500" />
          Examination active (visible to faculty)
        </label>

        <div>
          <label className="label">Topics</label>
          <div className="flex flex-wrap gap-2">
            {topics.map((t) => (
              <span key={t.id} className="chip text-slate-300">
                <Tag className="h-3 w-3" /> {t.name}
              </span>
            ))}
          </div>
          <div className="mt-3 flex gap-2">
            <input
              className="input"
              value={newTopic}
              onChange={(e) => setNewTopic(e.target.value)}
              placeholder="New topic name"
              onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addTopic())}
            />
            <button onClick={addTopic} className="btn-secondary shrink-0">
              <Plus className="h-4 w-4" />
            </button>
          </div>
        </div>

        <div className="flex justify-end gap-3">
          <button className="btn-secondary" onClick={onClose}>
            Close
          </button>
          <button className="btn-primary" disabled={busy} onClick={save}>
            {busy ? <Spinner /> : <Save className="h-4 w-4" />} Save
          </button>
        </div>
      </div>
    </Modal>
  );
}

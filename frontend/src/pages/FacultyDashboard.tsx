import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  BookOpen,
  CheckCircle2,
  Clock,
  ListChecks,
  Lock,
  LogOut,
  PlayCircle,
  Timer,
} from "lucide-react";
import { api } from "../services/api";
import { useAuth } from "../hooks/useAuth";
import { Badge, Card, EmptyState, LoadingScreen } from "../components/ui";
import type { SubjectStatusItem } from "../types";

export function FacultyDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [subjects, setSubjects] = useState<SubjectStatusItem[] | null>(null);

  useEffect(() => {
    let alive = true;
    api
      .get<SubjectStatusItem[]>("/api/subjects")
      .then((s) => alive && setSubjects(s))
      .catch(() => {});
    return () => {
      alive = false;
    };
  }, []);

  const counts = useMemo(() => {
    if (!subjects) return { available: 0, inProgress: 0, completed: 0 };
    return {
      available: subjects.filter((s) => s.status === "AVAILABLE").length,
      inProgress: subjects.filter((s) => s.status === "IN_PROGRESS").length,
      completed: subjects.filter((s) => s.status === "COMPLETED").length,
    };
  }, [subjects]);

  if (!user) return null;
  if (!subjects) return <LoadingScreen label="Loading your subjects…" />;

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-30 border-b border-white/5 bg-ink-950/80 backdrop-blur-lg">
        <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-600">
              <BookOpen className="h-5 w-5 text-white" />
            </div>
            <span className="text-sm font-bold tracking-wide text-slate-100">FACULTY DASHBOARD</span>
          </div>
          <button onClick={() => { logout(); navigate("/"); }} className="btn-ghost">
            <LogOut className="h-4 w-4" /> Sign out
          </button>
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl px-6 py-8">
        <section className="card relative mb-8 overflow-hidden p-8">
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-brand-400/60 to-transparent" />
          <p className="text-xs font-semibold uppercase tracking-widest text-slate-400">Welcome,</p>
          <h1 className="mt-1 text-3xl font-extrabold tracking-tight text-slate-50">{user.full_name}</h1>
          <p className="mt-1 text-sm text-slate-400">
            Department: <span className="font-semibold text-slate-200">{user.department}</span>
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <Badge tone="brand">{counts.available} available</Badge>
            <Badge tone="amber">{counts.inProgress} in progress</Badge>
            <Badge tone="green">{counts.completed} completed</Badge>
          </div>
        </section>

        {subjects.length === 0 ? (
          <EmptyState
            icon={<BookOpen className="h-6 w-6" />}
            title="No subjects available"
            hint="Subjects appear here once the administrator enables them."
          />
        ) : (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {subjects.map((item) => (
              <SubjectCard key={item.subject.id} item={item} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

function SubjectCard({ item }: { item: SubjectStatusItem }) {
  const status = item.status;

  if (status === "COMPLETED") {
    return (
      <Card className="flex flex-col p-6 opacity-90">
        <div className="flex items-center gap-2">
          <CheckCircle2 className="h-5 w-5 text-mint-400" />
          <Badge tone="green">✓ COMPLETED</Badge>
        </div>
        <h3 className="mt-4 text-lg font-bold leading-snug text-slate-100">{item.subject.name}</h3>
        <div className="mt-2 space-y-1 text-sm text-slate-400">
          <p className="flex items-center gap-2">
            <ListChecks className="h-4 w-4" /> {item.question_count} Questions
          </p>
          <p className="flex items-center gap-2">
            <Timer className="h-4 w-4" /> {item.duration_minutes} minutes
          </p>
        </div>
        <div className="mt-5 flex items-center gap-2 rounded-xl border border-amber-400/25 bg-amber-400/10 px-3.5 py-2.5 text-sm text-amber-300">
          <Lock className="h-4 w-4 shrink-0" />
          This subject cannot be attempted again.
        </div>
      </Card>
    );
  }

  return (
    <Card className="group flex flex-col p-6 transition hover:border-brand-400/30 hover:bg-white/[0.06]">
      <div className="flex items-center justify-between">
        <Badge tone={status === "IN_PROGRESS" ? "amber" : "brand"}>
          {status === "IN_PROGRESS" ? <Clock className="h-3 w-3" /> : <BookOpen className="h-3 w-3" />}
          {status === "IN_PROGRESS" ? "IN PROGRESS" : "AVAILABLE"}
        </Badge>
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          {item.subject.difficulty_label}
        </span>
      </div>
      <h3 className="mt-4 text-lg font-bold leading-snug text-slate-100">{item.subject.name}</h3>
      <p className="mt-1 line-clamp-2 text-sm text-slate-400">{item.subject.description}</p>
      <div className="mt-3 space-y-1 text-sm text-slate-400">
        <p className="flex items-center gap-2">
          <ListChecks className="h-4 w-4" /> {item.question_count} Questions
        </p>
        <p className="flex items-center gap-2">
          <Timer className="h-4 w-4" /> {item.duration_minutes} minutes · 1 mark each
        </p>
      </div>
      <div className="mt-5">
        <Link to={`/subjects/${item.subject.id}/start`} className="btn-primary w-full">
          {status === "IN_PROGRESS" ? (
            <>
              <PlayCircle className="h-4.5 w-4.5" /> RESUME TEST
            </>
          ) : (
            <>
              <PlayCircle className="h-4.5 w-4.5" /> START TEST
            </>
          )}
        </Link>
      </div>
    </Card>
  );
}

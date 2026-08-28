import {
  ArrowRight,
  BookOpenCheck,
  Camera,
  FileSearch,
  Fingerprint,
  GraduationCap,
  ShieldCheck,
  Timer,
  UserRound,
} from "lucide-react";
import { Link, Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

const FEATURES = [
  {
    icon: <BookOpenCheck className="h-5 w-5" />,
    title: "Expert-Level Examinations",
    text: "40 difficult, subject-based MCQs drawn from a curated, static question bank — no AI, no question generation.",
  },
  {
    icon: <Timer className="h-5 w-5" />,
    title: "Server-Authoritative Timing",
    text: "A 60-minute examination clock enforced by the server. The client timer is only a display.",
  },
  {
    icon: <Camera className="h-5 w-5" />,
    title: "Camera Monitoring & Recording",
    text: "Mandatory camera verification, live environment monitoring and full-session recording, securely stored.",
  },
  {
    icon: <ShieldCheck className="h-5 w-5" />,
    title: "Anti-Cheating Monitoring",
    text: "Tab switches, copy/paste, fullscreen exits and camera conditions are detected, logged and penalized.",
  },
  {
    icon: <FileSearch className="h-5 w-5" />,
    title: "Complete Admin Reports",
    text: "Full exam reports, violation timelines, question-level answers and camera recordings for authorized admins.",
  },
  {
    icon: <Fingerprint className="h-5 w-5" />,
    title: "Role-Based Security",
    text: "Password-only accounts, hashed credentials, JWT sessions, rate-limited logins and subject locking.",
  },
];

export function Landing() {
  const { user } = useAuth();
  if (user) return <Navigate to={user.role === "admin" ? "/admin" : "/dashboard"} replace />;

  return (
    <div className="min-h-screen">
      <header className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-6">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-600 shadow-lg shadow-brand-600/30">
            <GraduationCap className="h-5 w-5 text-white" />
          </div>
          <span className="text-sm font-bold tracking-wide text-slate-100">
            FACULTY <span className="text-brand-300">ASSESSMENT</span>
          </span>
        </div>
        <Link to="/admin/login" className="text-sm text-slate-400 transition hover:text-slate-200">
          Admin portal →
        </Link>
      </header>

      <main className="mx-auto w-full max-w-6xl px-6">
        <section className="grid items-center gap-12 py-16 lg:grid-cols-2">
          <div>
            <div className="chip mb-5 border-brand-400/30 bg-brand-500/10 text-brand-300">
              <ShieldCheck className="h-3.5 w-3.5" /> SECURE EXAMINATION PLATFORM
            </div>
            <h1 className="text-4xl font-extrabold leading-tight tracking-tight text-slate-50 sm:text-5xl">
              Faculty Competency{" "}
              <span className="bg-gradient-to-r from-brand-300 via-brand-400 to-mint-400 bg-clip-text text-transparent">
                Testing Platform
              </span>
            </h1>
            <p className="mt-5 max-w-lg text-lg leading-relaxed text-slate-400">
              Difficult, subject-based MCQ examinations for faculty — with live camera monitoring,
              full-session recording, violation penalties and permanent subject locking.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/register" className="btn-primary px-6 py-3">
                <UserRound className="h-4.5 w-4.5" /> Create Faculty Account
              </Link>
              <Link to="/login" className="btn-secondary px-6 py-3">
                Faculty Login <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
            <p className="mt-6 text-xs leading-relaxed text-slate-500">
              Generic and reusable for any educational institution. No external authentication, no
              AI — every question, rule and penalty is managed through the application.
            </p>
          </div>

          <div className="card relative overflow-hidden p-6">
            <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-brand-400/60 to-transparent" />
            <p className="text-xs font-semibold uppercase tracking-widest text-slate-400">Examination flow</p>
            <ol className="mt-4 space-y-3 text-sm text-slate-300">
              {[
                "Create a faculty account (name, department, password)",
                "Log in and browse available subjects",
                "Select your teaching experience level",
                "Pass the camera security verification",
                "Answer 40 difficult MCQs within 60 minutes",
                "View violations & penalties after submission",
                "Subject becomes permanently locked",
              ].map((step, i) => (
                <li key={step} className="flex items-center gap-3">
                  <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-500/20 text-xs font-bold text-brand-300">
                    {i + 1}
                  </span>
                  {step}
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section className="grid gap-4 pb-20 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((f) => (
            <div key={f.title} className="card group p-5 transition hover:border-brand-400/30 hover:bg-white/[0.06]">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-500/15 text-brand-300 transition group-hover:bg-brand-500/25">
                {f.icon}
              </div>
              <h3 className="mt-4 font-semibold text-slate-100">{f.title}</h3>
              <p className="mt-1.5 text-sm leading-relaxed text-slate-400">{f.text}</p>
            </div>
          ))}
        </section>
      </main>

      <footer className="border-t border-white/5 py-8 text-center text-xs text-slate-600">
        Faculty Competency Testing Platform · Run locally: backend on :8100, frontend on :5173
      </footer>
    </div>
  );
}

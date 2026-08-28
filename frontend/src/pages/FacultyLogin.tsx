import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { GraduationCap, Lock, LogIn } from "lucide-react";
import { loginFaculty } from "../services/api";
import { useAuth } from "../hooks/useAuth";
import { useToast } from "../components/Toast";
import { Spinner } from "../components/ui";

export function FacultyLogin() {
  const { login } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!fullName.trim() || !password) {
      setError("All fields are required.");
      return;
    }
    setBusy(true);
    try {
      const user = await login(() => loginFaculty({ full_name: fullName, password }));
      navigate(user.role === "admin" ? "/admin" : "/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed.");
      toast(err instanceof Error ? err.message : "Login failed.", "error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <AuthShell
      title="FACULTY LOGIN"
      subtitle="Sign in with your registered full name and password."
    >
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className="label">Full Name</label>
          <input
            className="input uppercase"
            placeholder="KATTA TEJA REDDY"
            value={fullName}
            onChange={(e) => setFullName(e.target.value.toUpperCase())}
            autoComplete="username"
          />
        </div>
        <div>
          <label className="label">Password</label>
          <input
            className="input"
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
          />
        </div>
        {error && (
          <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-2.5 text-sm text-rose-300">
            {error}
          </div>
        )}
        <button className="btn-primary w-full py-3" disabled={busy}>
          {busy ? <Spinner /> : <LogIn className="h-4.5 w-4.5" />} LOGIN
        </button>
      </form>
      <p className="mt-6 text-center text-sm text-slate-400">
        New faculty?{" "}
        <Link to="/register" className="font-semibold text-brand-300 hover:text-brand-200">
          Create an account
        </Link>
      </p>
    </AuthShell>
  );
}

export function AuthShell({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <div className="mb-8 flex flex-col items-center text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-500 to-brand-600 shadow-xl shadow-brand-600/30">
            <GraduationCap className="h-7 w-7 text-white" />
          </div>
          <h1 className="mt-5 text-2xl font-extrabold tracking-tight text-slate-50">{title}</h1>
          <p className="mt-2 text-sm text-slate-400">{subtitle}</p>
        </div>
        <div className="card relative overflow-hidden p-7">
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-brand-400/60 to-transparent" />
          {children}
        </div>
        <div className="mt-6 flex items-center justify-center gap-2 text-xs text-slate-500">
          <Lock className="h-3.5 w-3.5" /> Passwords are hashed. No external authentication.
        </div>
      </div>
    </div>
  );
}

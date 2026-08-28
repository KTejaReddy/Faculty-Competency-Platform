import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ShieldCheck } from "lucide-react";
import { adminLogin } from "../services/api";
import { useAuth } from "../hooks/useAuth";
import { useToast } from "../components/Toast";
import { Spinner } from "../components/ui";

export function AdminLogin() {
  const { login } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await login(() => adminLogin({ username, password }));
      navigate("/admin");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Login failed.";
      setError(msg);
      toast(msg, "error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-ink-700 to-ink-800 ring-1 ring-white/15">
            <ShieldCheck className="h-7 w-7 text-brand-300" />
          </div>
          <h1 className="mt-5 text-2xl font-extrabold tracking-tight text-slate-50">ADMIN PORTAL</h1>
          <p className="mt-2 text-sm text-slate-400">Restricted access. Administrator credentials required.</p>
        </div>
        <form onSubmit={submit} className="card relative space-y-4 overflow-hidden p-7">
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-brand-400/60 to-transparent" />
          <div>
            <label className="label">Username</label>
            <input
              className="input uppercase"
              value={username}
              onChange={(e) => setUsername(e.target.value.toUpperCase())}
              autoComplete="username"
            />
          </div>
          <div>
            <label className="label">Password</label>
            <input
              className="input"
              type="password"
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
            {busy ? <Spinner /> : <ShieldCheck className="h-4.5 w-4.5" />} SIGN IN
          </button>
        </form>
        <p className="mt-6 text-center text-sm text-slate-500">
          <Link to="/" className="hover:text-slate-300">
            ← Back to home
          </Link>
        </p>
      </div>
    </div>
  );
}

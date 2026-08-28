import { useEffect, useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { CheckCircle2, UserPlus } from "lucide-react";
import { api, registerFaculty } from "../services/api";
import { useAuth } from "../hooks/useAuth";
import { useToast } from "../components/Toast";
import { Spinner } from "../components/ui";
import type { Department } from "../types";
import { AuthShell } from "./FacultyLogin";

const PASSWORD_MIN = 8;

export function FacultyRegister() {
  const { login } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [department, setDepartment] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [departments, setDepartments] = useState<Department[]>([]);
  const [busy, setBusy] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    api.get<Department[]>("/api/departments").then(setDepartments).catch(() => {});
  }, []);

  const validate = (): boolean => {
    const next: Record<string, string> = {};
    const normalized = fullName.trim().toUpperCase().replace(/\s+/g, " ");
    if (normalized.length < 3) next.fullName = "Enter your full name.";
    else if (normalized.split(" ").length < 2) next.fullName = "Enter at least first and last name.";
    if (!department) next.department = "Select a department.";
    if (password.length < PASSWORD_MIN) next.password = `Minimum ${PASSWORD_MIN} characters.`;
    if (confirmPassword !== password) next.confirmPassword = "Passwords do not match.";
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setBusy(true);
    try {
      const user = await login(() =>
        registerFaculty({ full_name: fullName, department, password, confirm_password: confirmPassword })
      );
      toast(`Account created. Welcome, ${user.full_name}!`, "success");
      navigate("/dashboard");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Registration failed.";
      toast(msg, "error");
      setErrors({ form: msg });
    } finally {
      setBusy(false);
    }
  };

  return (
    <AuthShell
      title="CREATE FACULTY ACCOUNT"
      subtitle="Your full name is stored in uppercase. Choose a strong password (min. 8 characters)."
    >
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className="label">Full Name</label>
          <input
            className="input uppercase"
            placeholder="katta teja reddy → KATTA TEJA REDDY"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            autoComplete="name"
          />
          {errors.fullName && <FieldError msg={errors.fullName} />}
        </div>
        <div>
          <label className="label">Department</label>
          <select className="input" value={department} onChange={(e) => setDepartment(e.target.value)}>
            <option value="">Select your department</option>
            {departments.map((d) => (
              <option key={d.code} value={d.name}>
                {d.name}
              </option>
            ))}
          </select>
          {errors.department && <FieldError msg={errors.department} />}
        </div>
        <div>
          <label className="label">Password</label>
          <input
            className="input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="new-password"
          />
          {errors.password && <FieldError msg={errors.password} />}
        </div>
        <div>
          <label className="label">Confirm Password</label>
          <input
            className="input"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            autoComplete="new-password"
          />
          {errors.confirmPassword && <FieldError msg={errors.confirmPassword} />}
        </div>
        {errors.form && (
          <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-2.5 text-sm text-rose-300">
            {errors.form}
          </div>
        )}
        <button className="btn-primary w-full py-3" disabled={busy}>
          {busy ? <Spinner /> : <UserPlus className="h-4.5 w-4.5" />} CREATE ACCOUNT
        </button>
      </form>
      <div className="mt-5 flex items-center gap-2 text-xs text-slate-500">
        <CheckCircle2 className="h-4 w-4 text-mint-400" />
        Your name is normalized to uppercase and checked for duplicate accounts.
      </div>
      <p className="mt-4 text-center text-sm text-slate-400">
        Already registered?{" "}
        <Link to="/login" className="font-semibold text-brand-300 hover:text-brand-200">
          Log in
        </Link>
      </p>
    </AuthShell>
  );
}

function FieldError({ msg }: { msg: string }) {
  return <p className="mt-1 text-xs text-rose-400">{msg}</p>;
}

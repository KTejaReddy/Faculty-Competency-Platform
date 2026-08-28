import { Link } from "react-router-dom";
import { Compass } from "lucide-react";

export function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 px-4">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-white/5 text-slate-400">
        <Compass className="h-7 w-7" />
      </div>
      <h1 className="text-3xl font-extrabold text-slate-100">404 — Page not found</h1>
      <p className="text-sm text-slate-400">The page you are looking for does not exist.</p>
      <Link to="/" className="btn-primary mt-2">
        Back to home
      </Link>
    </div>
  );
}

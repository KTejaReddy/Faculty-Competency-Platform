import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { TokenResponse, User } from "../types";
import { auth } from "../services/api";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  login: (fn: () => Promise<TokenResponse>) => Promise<User>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => auth.getUser());
  const [token, setToken] = useState<string | null>(() => auth.getToken());

  useEffect(() => {
    const onUnauthorized = () => {
      setUser(null);
      setToken(null);
    };
    window.addEventListener("ftp:unauthorized", onUnauthorized);
    return () => window.removeEventListener("ftp:unauthorized", onUnauthorized);
  }, []);

  const login = useCallback(async (fn: () => Promise<TokenResponse>): Promise<User> => {
    const res = await fn();
    auth.setSession(res.access_token, res.user);
    setToken(res.access_token);
    setUser(res.user);
    return res.user;
  }, []);

  const logout = useCallback(() => {
    auth.clear();
    setUser(null);
    setToken(null);
  }, []);

  const value = useMemo(() => ({ user, token, login, logout }), [user, token, login, logout]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}

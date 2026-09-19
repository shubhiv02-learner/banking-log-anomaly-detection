import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useNavigate } from "@tanstack/react-router";

import { api } from "@/lib/api/client";
import {
  clearSession,
  getStoredUser,
  setSession,
  type AuthUser,
} from "@/lib/auth-storage";
import { AuthContext } from "@/lib/auth-context";

export function AuthProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate();
  const [user, setUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    setUser(getStoredUser());
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const result = await api.login(email, password);
      setSession(result.access_token, result.user);
      setUser(result.user);
      await navigate({ to: "/" });
    },
    [navigate],
  );

  const logout = useCallback(() => {
    clearSession();
    setUser(null);
    void navigate({ to: "/login" });
  }, [navigate]);

  const value = useMemo(
    () => ({ user, login, logout }),
    [user, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

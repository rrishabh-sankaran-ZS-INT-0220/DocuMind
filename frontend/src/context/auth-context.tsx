"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";
import { apiClient } from "@/lib/api";

const TOKEN_KEY = "documind_access_token";

type User = {
  id: string;
  email: string;
  full_name?: string | null;
};

type AuthContextValue = {
  user: User | null;
  accessToken: string | null;
  setAccessToken: (token: string | null) => void;
  loading: boolean;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [accessToken, setAccessTokenState] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Persist token to localStorage and update state
  const setAccessToken = (token: string | null) => {
    setAccessTokenState(token);
    if (token) {
      localStorage.setItem(TOKEN_KEY, token);
    } else {
      localStorage.removeItem(TOKEN_KEY);
    }
  };

  // Hydrate token from localStorage on first render (client only)
  useEffect(() => {
    const stored = localStorage.getItem(TOKEN_KEY);
    if (stored) {
      setAccessTokenState(stored);
    } else {
      // No token stored -- stop loading immediately
      setLoading(false);
    }
  }, []);

  // Fetch current user whenever accessToken changes
  useEffect(() => {
    if (!accessToken) {
      setUser(null);
      setLoading(false);
      return;
    }

    let cancelled = false;

    const fetchMe = async () => {
      try {
        const res = await apiClient.get("/auth/me", {
          headers: { Authorization: "Bearer " + accessToken },
        });
        if (!cancelled) setUser(res.data);
      } catch {
        if (!cancelled) {
          setUser(null);
          setAccessToken(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchMe();

    return () => {
      cancelled = true;
    };
  }, [accessToken]);

  // Attach request interceptor -- eject the old one when accessToken changes
  // to prevent interceptors from stacking up across re-renders.
  useEffect(() => {
    const requestId = apiClient.interceptors.request.use((config) => {
      if (accessToken) {
        config.headers = config.headers ?? {};
        config.headers["Authorization"] = "Bearer " + accessToken;
      }
      return config;
    });

    return () => {
      apiClient.interceptors.request.eject(requestId);
    };
  }, [accessToken]);

  // Attach response interceptor once -- redirect to /login on 401
  useEffect(() => {
    const responseId = apiClient.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error?.response?.status === 401) {
          setAccessToken(null);
          window.location.replace("/login");
        }
        return Promise.reject(error);
      }
    );

    return () => {
      apiClient.interceptors.response.eject(responseId);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <AuthContext.Provider value={{ user, accessToken, setAccessToken, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

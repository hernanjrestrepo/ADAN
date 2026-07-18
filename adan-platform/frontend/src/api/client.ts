/** Typed API client - BP-0007. Generado a mano contra los contratos reales del backend
 * (contracts/openapi/); se reemplaza por generacion automatica cuando WO-002 estabilice
 * el contrato de agentes. */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8020";

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface HealthResponse {
  status: string;
  uptime_seconds: number;
}

class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
  }
}

function getToken(): string | null {
  return localStorage.getItem("adan_token");
}

export function setToken(token: string | null): void {
  if (token) localStorage.setItem("adan_token", token);
  else localStorage.removeItem("adan_token");
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken();
  const headers = new Headers(init?.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const resp = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  if (!resp.ok) {
    const body = await resp.json().catch(() => ({ message: resp.statusText }));
    throw new ApiError(resp.status, body.message ?? body.detail ?? "Request failed");
  }
  return resp.json() as Promise<T>;
}

export const api = {
  health: () => request<HealthResponse>("/health"),

  login: async (email: string, password: string): Promise<TokenResponse> => {
    const form = new URLSearchParams();
    form.set("username", email);
    form.set("password", password);
    return request<TokenResponse>("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form,
    });
  },

  register: (email: string, password: string, display_name?: string) =>
    request<TokenResponse>("/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, display_name }),
    }),
};

export { ApiError };

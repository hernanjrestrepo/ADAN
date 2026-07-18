import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

import { api, ApiError, setToken } from "../api/client";

export function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const { access_token } = await api.login(email, password);
      setToken(access_token);
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error de conexión");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm rounded-lg border border-adan-border bg-adan-surface p-8"
      >
        <h1 className="mb-1 text-2xl font-semibold">ADÁN</h1>
        <p className="mb-6 text-sm text-adan-muted">Sistema Operativo Empresarial</p>

        <label className="mb-1 block text-sm text-adan-muted" htmlFor="email">
          Correo
        </label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="mb-4 w-full rounded border border-adan-border bg-adan-bg px-3 py-2 text-adan-text outline-none focus:border-adan-primary"
        />

        <label className="mb-1 block text-sm text-adan-muted" htmlFor="password">
          Contraseña
        </label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="mb-6 w-full rounded border border-adan-border bg-adan-bg px-3 py-2 text-adan-text outline-none focus:border-adan-primary"
        />

        {error && <p className="mb-4 text-sm text-red-400">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded bg-adan-primary py-2 font-medium text-white disabled:opacity-50"
        >
          {loading ? "Entrando..." : "Entrar"}
        </button>
      </form>
    </div>
  );
}

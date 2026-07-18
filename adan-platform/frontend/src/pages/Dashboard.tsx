import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { api, HealthResponse, setToken } from "../api/client";

export function Dashboard() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth(null));
  }, []);

  function logout() {
    setToken(null);
    navigate("/login");
  }

  return (
    <div className="min-h-screen p-8">
      <header className="mb-8 flex items-center justify-between">
        <h1 className="text-xl font-semibold">ADÁN — Workspace</h1>
        <button onClick={logout} className="text-sm text-adan-muted hover:text-adan-text">
          Cerrar sesión
        </button>
      </header>

      <div className="rounded-lg border border-adan-border bg-adan-surface p-6">
        <h2 className="mb-2 text-sm text-adan-muted">Estado de la API</h2>
        {health ? (
          <p className="text-adan-success">
            {health.status} · {health.uptime_seconds}s activo
          </p>
        ) : (
          <p className="text-adan-warning">Sin conexión con la API</p>
        )}
      </div>
    </div>
  );
}

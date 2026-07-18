import { FormEvent, useEffect, useRef, useState } from "react";

import { api, EjecucionAgente, EjecucionStatus } from "../api/client";

const DIAGNOSTICO_AGENT_ID = "diagnostico-nivel-1";
const POLL_INTERVAL_MS = 1500;

function statusColor(status: EjecucionStatus): string {
  switch (status) {
    case "completed":
      return "text-adan-success";
    case "failed":
      return "text-red-400";
    case "cancelled":
      return "text-adan-muted";
    default:
      return "text-adan-warning";
  }
}

export function Agents() {
  const [userInput, setUserInput] = useState("");
  const [current, setCurrent] = useState<EjecucionAgente | null>(null);
  const [history, setHistory] = useState<EjecucionAgente[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const pollRef = useRef<number | null>(null);

  function loadHistory() {
    api.listRuns().then(setHistory).catch(() => setHistory([]));
  }

  useEffect(() => {
    loadHistory();
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current);
    };
  }, []);

  function pollExecution(executionId: string) {
    if (pollRef.current) window.clearInterval(pollRef.current);
    pollRef.current = window.setInterval(async () => {
      try {
        const result = await api.getRun(executionId);
        setCurrent(result);
        if (["completed", "failed", "cancelled"].includes(result.status)) {
          if (pollRef.current) window.clearInterval(pollRef.current);
          loadHistory();
        }
      } catch {
        if (pollRef.current) window.clearInterval(pollRef.current);
      }
    }, POLL_INTERVAL_MS);
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!userInput.trim()) return;
    setSubmitting(true);
    setCurrent(null);
    try {
      const { execution_id } = await api.runAgent(DIAGNOSTICO_AGENT_ID, userInput);
      setCurrent({
        id: execution_id,
        agent_id: DIAGNOSTICO_AGENT_ID,
        status: "pending",
        user_input: userInput,
        final_output: null,
        error: null,
      });
      pollExecution(execution_id);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen p-8">
      <h1 className="mb-6 text-xl font-semibold">Agente de Diagnóstico — Nivel 1</h1>

      <form onSubmit={handleSubmit} className="mb-8 rounded-lg border border-adan-border bg-adan-surface p-6">
        <label className="mb-2 block text-sm text-adan-muted" htmlFor="user-input">
          Cuéntale a ADÁN tu problema de negocio
        </label>
        <textarea
          id="user-input"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          rows={4}
          className="mb-4 w-full rounded border border-adan-border bg-adan-bg px-3 py-2 text-adan-text outline-none focus:border-adan-primary"
        />
        <button
          type="submit"
          disabled={submitting}
          className="rounded bg-adan-primary px-4 py-2 font-medium text-white disabled:opacity-50"
        >
          {submitting ? "Enviando..." : "Diagnosticar"}
        </button>
      </form>

      {current && (
        <div
          data-testid="current-execution"
          className="mb-8 rounded-lg border border-adan-border bg-adan-surface p-6"
        >
          <h2 className="mb-2 text-sm text-adan-muted">Ejecución en curso</h2>
          <p className={`mb-2 font-medium ${statusColor(current.status)}`}>{current.status}</p>
          {current.final_output && (
            <pre className="whitespace-pre-wrap text-sm text-adan-text">{current.final_output}</pre>
          )}
          {current.error && <p className="text-sm text-red-400">{current.error}</p>}
        </div>
      )}

      <div className="rounded-lg border border-adan-border bg-adan-surface p-6">
        <h2 className="mb-4 text-sm text-adan-muted">Historial de ejecuciones</h2>
        <ul className="space-y-3">
          {history.map((run) => (
            <li key={run.id} className="border-b border-adan-border pb-3 last:border-0">
              <p className={`text-sm font-medium ${statusColor(run.status)}`}>{run.status}</p>
              <p className="truncate text-sm text-adan-muted">{run.user_input}</p>
            </li>
          ))}
          {history.length === 0 && <p className="text-sm text-adan-muted">Sin ejecuciones todavía.</p>}
        </ul>
      </div>
    </div>
  );
}

import { FormEvent, useState } from "react";

import { api, HybridResult, KGTraverseResult } from "../api/client";

export function KGExplorer() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<HybridResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [detail, setDetail] = useState<KGTraverseResult | null>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  async function handleSearch(e: FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setSearching(true);
    setDetail(null);
    setSelectedNodeId(null);
    try {
      const hits = await api.hybridQuery(query);
      setResults(hits);
    } finally {
      setSearching(false);
    }
  }

  async function showDetail(nodeId: string) {
    setSelectedNodeId(nodeId);
    const traverse = await api.getNodeTraverse(nodeId, 2);
    setDetail(traverse);
  }

  return (
    <div className="min-h-screen p-8">
      <h1 className="mb-6 text-xl font-semibold">Explorador del Knowledge Graph</h1>

      <form onSubmit={handleSearch} className="mb-8 flex gap-2">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Buscar en el conocimiento (semántico + grafo)..."
          className="flex-1 rounded border border-adan-border bg-adan-surface px-3 py-2 text-adan-text outline-none focus:border-adan-primary"
        />
        <button
          type="submit"
          disabled={searching}
          className="rounded bg-adan-primary px-4 py-2 font-medium text-white disabled:opacity-50"
        >
          {searching ? "Buscando..." : "Buscar"}
        </button>
      </form>

      <div className="grid grid-cols-2 gap-6">
        <div className="rounded-lg border border-adan-border bg-adan-surface p-6">
          <h2 className="mb-4 text-sm text-adan-muted">Resultados</h2>
          <ul className="space-y-3">
            {results.map((r, i) => (
              <li key={i} className="border-b border-adan-border pb-3 last:border-0">
                <span
                  className={`mr-2 rounded px-2 py-0.5 text-xs ${
                    r.origen === "semantico" ? "bg-adan-primary/20 text-adan-primary" : "bg-adan-warning/20 text-adan-warning"
                  }`}
                >
                  {r.origen}
                </span>
                <span className="text-sm">{r.contenido}</span>
                {r.nodo_id && (
                  <button
                    onClick={() => showDetail(r.nodo_id!)}
                    className="ml-2 text-xs text-adan-primary underline"
                  >
                    ver conexiones
                  </button>
                )}
              </li>
            ))}
            {results.length === 0 && <p className="text-sm text-adan-muted">Sin resultados todavía.</p>}
          </ul>
        </div>

        <div className="rounded-lg border border-adan-border bg-adan-surface p-6">
          <h2 className="mb-4 text-sm text-adan-muted">
            {selectedNodeId ? "Nodos y relaciones conectadas" : "Selecciona un resultado para ver sus conexiones"}
          </h2>
          {detail && (
            <div>
              <p className="mb-2 text-xs text-adan-muted">{detail.nodos.length} nodos, {detail.aristas.length} relaciones</p>
              <ul className="space-y-2">
                {detail.nodos.map((n) => (
                  <li key={n.id} className="text-sm">
                    <span className="text-adan-muted">[{n.tipo}]</span> {n.nombre}
                  </li>
                ))}
              </ul>
              {detail.aristas.length > 0 && (
                <ul className="mt-4 space-y-1 border-t border-adan-border pt-4 text-xs text-adan-muted">
                  {detail.aristas.map((a) => (
                    <li key={a.id}>
                      {a.origen_id.slice(0, 8)}... —{a.tipo_relacion}→ {a.destino_id.slice(0, 8)}...
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

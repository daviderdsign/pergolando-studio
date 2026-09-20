"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export function NewDraftForm() {
  const router = useRouter();
  const [tenantId, setTenantId] = useState("");
  const [nomeAzienda, setNomeAzienda] = useState("");
  const [template, setTemplate] = useState<"vuoto" | "vision" | "brera">("vuoto");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const res = await fetch("/api/drafts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tenantId, nomeAzienda, template }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "Errore sconosciuto");
      router.push(`/drafts/${data.draft.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="new-draft-form">
      <label>
        Tenant id
        <input
          value={tenantId}
          onChange={(e) => setTenantId(e.target.value.trim())}
          placeholder="es. rossi-pergole"
          required
        />
      </label>
      <label>
        Nome azienda
        <input
          value={nomeAzienda}
          onChange={(e) => setNomeAzienda(e.target.value)}
          placeholder="es. Rossi Pergole S.r.l."
          required
        />
      </label>
      <label>
        Parti da
        <select value={template} onChange={(e) => setTemplate(e.target.value as typeof template)}>
          <option value="vuoto">Bundle vuoto</option>
          <option value="vision">Template Vision (sotto-modello singolo)</option>
          <option value="brera">Template Brera (multi-variante)</option>
        </select>
      </label>
      <button type="submit" disabled={submitting}>
        {submitting ? "Creazione…" : "Crea bozza"}
      </button>
      {error && <p className="error">{error}</p>}
    </form>
  );
}

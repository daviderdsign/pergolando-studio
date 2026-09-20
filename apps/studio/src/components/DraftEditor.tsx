"use client";

import { useState } from "react";
import type { Draft } from "@/lib/storage";
import type { ValidationReport } from "@/lib/validate-bundle";

interface Props {
  initialDraft: Draft;
}

export function DraftEditor({ initialDraft }: Props) {
  const [draft, setDraft] = useState(initialDraft);
  const [databaseText, setDatabaseText] = useState(JSON.stringify(initialDraft.database, null, 2));
  const [priceMatricesText, setPriceMatricesText] = useState(
    JSON.stringify(initialDraft.priceMatrices, null, 2),
  );
  const [jsonError, setJsonError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [report, setReport] = useState<ValidationReport | null>(null);
  const [validating, setValidating] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [exportResult, setExportResult] = useState<{ version: string; downloadUrl: string } | null>(
    null,
  );
  const [changelogNote, setChangelogNote] = useState("");

  async function saveJson() {
    setJsonError(null);
    let database: unknown;
    let priceMatrices: unknown;
    try {
      database = JSON.parse(databaseText);
      priceMatrices = JSON.parse(priceMatricesText);
    } catch (err) {
      setJsonError(`JSON non valido: ${err instanceof Error ? err.message : String(err)}`);
      return;
    }
    setSaving(true);
    try {
      const res = await fetch(`/api/drafts/${draft.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ database, priceMatrices }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      setDraft(data.draft);
      setReport(null);
      setExportResult(null);
    } catch (err) {
      setJsonError(err instanceof Error ? err.message : String(err));
    } finally {
      setSaving(false);
    }
  }

  async function uploadPdf(file: File) {
    setUploading(true);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`/api/drafts/${draft.id}/upload`, { method: "POST", body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      setDraft(data.draft);
    } catch (err) {
      alert(err instanceof Error ? err.message : String(err));
    } finally {
      setUploading(false);
    }
  }

  async function uploadLetterhead(file: File) {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`/api/drafts/${draft.id}/letterhead`, { method: "POST", body: form });
    const data = await res.json();
    if (!res.ok) {
      alert(data.error);
      return;
    }
    setDraft(data.draft);
  }

  async function runValidation() {
    setValidating(true);
    try {
      const res = await fetch(`/api/drafts/${draft.id}/validate`, { method: "POST" });
      const data = await res.json();
      setReport(data.report);
    } finally {
      setValidating(false);
    }
  }

  async function runExport() {
    setExporting(true);
    try {
      const res = await fetch(`/api/drafts/${draft.id}/export`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ changelogNote }),
      });
      const data = await res.json();
      if (!res.ok) {
        setReport(data.report ?? report);
        alert(data.error);
        return;
      }
      setExportResult(data);
    } finally {
      setExporting(false);
    }
  }

  return (
    <main className="page">
      <p>
        <a href="/">&larr; Bozze</a>
      </p>
      <h1>{draft.nomeAzienda}</h1>
      <p className="muted">tenant: {draft.tenantId}</p>

      <section>
        <h2>1. Ingest PDF (STU-1)</h2>
        <input
          type="file"
          accept="application/pdf"
          disabled={uploading}
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) void uploadPdf(file);
          }}
        />
        {uploading && <p className="muted">Estrazione in corso…</p>}
        {draft.extractedText && (
          <details>
            <summary>Testo estratto ({draft.extractedText.length} caratteri)</summary>
            <pre className="extracted-text">{draft.extractedText}</pre>
          </details>
        )}
        {draft.tableCandidates && draft.tableCandidates.length > 0 && (
          <details>
            <summary>
              Blocchi tabellari candidati ({draft.tableCandidates.length}) — da verificare manualmente,
              non ancora affidabili
            </summary>
            {draft.tableCandidates.map((tc, i) => (
              <div key={i}>
                <p className="muted">Pagina {tc.page}</p>
                <pre className="extracted-text">
                  {tc.rows.map((r) => r.join(" | ")).join("\n")}
                </pre>
              </div>
            ))}
          </details>
        )}
      </section>

      <section>
        <h2>2-4. Mappatura nello schema del bundle (STU-2/3/4)</h2>
        <p className="muted">
          Correggi manualmente ciò che l&apos;estrazione automatica non prende bene — la revisione
          umana è obbligatoria prima dell&apos;export.
        </p>
        <div className="editor-grid">
          <label>
            catalog/database.json
            <textarea
              value={databaseText}
              onChange={(e) => setDatabaseText(e.target.value)}
              spellCheck={false}
              rows={24}
            />
          </label>
          <label>
            catalog/price_matrices.json
            <textarea
              value={priceMatricesText}
              onChange={(e) => setPriceMatricesText(e.target.value)}
              spellCheck={false}
              rows={24}
            />
          </label>
        </div>
        {jsonError && <p className="error">{jsonError}</p>}
        <button onClick={saveJson} disabled={saving}>
          {saving ? "Salvataggio…" : "Salva mappatura"}
        </button>
      </section>

      <section>
        <h2>5. Validazione (STU-5)</h2>
        <button onClick={runValidation} disabled={validating}>
          {validating ? "Validazione…" : "Valida"}
        </button>
        {report && <ValidationReportView report={report} />}
      </section>

      <section>
        <h2>6. Branding (STU-6)</h2>
        <label>
          Carta intestata (PDF o SVG)
          <input
            type="file"
            accept="application/pdf,image/svg+xml"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) void uploadLetterhead(file);
            }}
          />
        </label>
        {draft.letterheadFileName && <p className="muted">Caricata: {draft.letterheadFileName}</p>}
      </section>

      <section>
        <h2>7. Export bundle (STU-7)</h2>
        <label>
          Nota changelog
          <input value={changelogNote} onChange={(e) => setChangelogNote(e.target.value)} />
        </label>
        <button onClick={runExport} disabled={exporting || (report !== null && !report.passed)}>
          {exporting ? "Export…" : "Esporta bundle"}
        </button>
        {report && !report.passed && (
          <p className="error">Valida con successo prima di esportare.</p>
        )}
        {exportResult && (
          <p>
            Bundle versione <strong>{exportResult.version}</strong> esportato.{" "}
            <a href={exportResult.downloadUrl}>Scarica zip</a>
          </p>
        )}
      </section>
    </main>
  );
}

function ValidationReportView({ report }: { report: ValidationReport }) {
  return (
    <div className={`report ${report.passed ? "report-ok" : "report-fail"}`}>
      <p>
        <strong>{report.passed ? "✓ Validazione superata" : "✗ Validazione non superata"}</strong>
      </p>
      {report.schemaErrors.length > 0 && (
        <div>
          <h3>Errori di schema</h3>
          <ul>
            {report.schemaErrors.map((e, i) => (
              <li key={i}>{e}</li>
            ))}
          </ul>
        </div>
      )}
      {report.coherenceIssues.length > 0 && (
        <div>
          <h3>Coerenza matrici</h3>
          <ul>
            {report.coherenceIssues.map((issue, i) => (
              <li key={i} className={issue.severity === "error" ? "error" : "warning"}>
                [{issue.matrice}] {issue.message}
              </li>
            ))}
          </ul>
        </div>
      )}
      {report.smokeTests.length > 0 && (
        <div>
          <h3>Test motore di pricing (smoke test)</h3>
          <ul>
            {report.smokeTests.map((t, i) => (
              <li key={i} className={t.ok ? "ok" : "error"}>
                {t.sottoModello} / {t.varianteMontaggio}:{" "}
                {t.ok ? `OK — ${t.prezzoTotaleEur} EUR` : t.error}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

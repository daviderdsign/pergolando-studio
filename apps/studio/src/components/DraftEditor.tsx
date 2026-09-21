"use client";

import { useState } from "react";
import type { Draft, DraftTheme } from "@/lib/storage";
import type { ValidationReport } from "@/lib/validate-bundle";
import type { AssetManifestEntry } from "@pergolando/shared/schema";
import { apiPath } from "@/lib/base-path";

const TIPO_LABELS: Record<AssetManifestEntry["tipo"], string> = {
  foto: "Foto",
  rendering: "Rendering",
  altro: "Altro",
};

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
  const [uploadingLogo, setUploadingLogo] = useState(false);
  const [uploadingAsset, setUploadingAsset] = useState(false);
  const [assetTipo, setAssetTipo] = useState<AssetManifestEntry["tipo"]>("foto");
  const [assetProdotto, setAssetProdotto] = useState("");
  const [assetSottoModello, setAssetSottoModello] = useState("");
  const [assetVariante, setAssetVariante] = useState("");
  const [assetColore, setAssetColore] = useState("");
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
      const res = await fetch(apiPath(`/api/drafts/${draft.id}`), {
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
      const res = await fetch(apiPath(`/api/drafts/${draft.id}/upload`), { method: "POST", body: form });
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
    const res = await fetch(apiPath(`/api/drafts/${draft.id}/letterhead`), { method: "POST", body: form });
    const data = await res.json();
    if (!res.ok) {
      alert(data.error);
      return;
    }
    setDraft(data.draft);
  }

  async function uploadLogo(file: File) {
    setUploadingLogo(true);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(apiPath(`/api/drafts/${draft.id}/logo`), { method: "POST", body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      setDraft(data.draft);
    } catch (err) {
      alert(err instanceof Error ? err.message : String(err));
    } finally {
      setUploadingLogo(false);
    }
  }

  async function uploadAsset(file: File) {
    setUploadingAsset(true);
    try {
      const form = new FormData();
      form.append("file", file);
      form.append("tipo", assetTipo);
      if (assetProdotto) form.append("prodotto", assetProdotto);
      if (assetSottoModello) form.append("sotto_modello", assetSottoModello);
      if (assetVariante) form.append("variante_montaggio", assetVariante);
      if (assetColore) form.append("colore", assetColore);
      const res = await fetch(apiPath(`/api/drafts/${draft.id}/assets`), { method: "POST", body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      setDraft(data.draft);
    } catch (err) {
      alert(err instanceof Error ? err.message : String(err));
    } finally {
      setUploadingAsset(false);
    }
  }

  async function deleteAsset(assetPath: string) {
    const res = await fetch(apiPath(`/api/drafts/${draft.id}/assets?path=${encodeURIComponent(assetPath)}`), {
      method: "DELETE",
    });
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
      const res = await fetch(apiPath(`/api/drafts/${draft.id}/validate`), { method: "POST" });
      const data = await res.json();
      setReport(data.report);
    } finally {
      setValidating(false);
    }
  }

  async function runExport() {
    setExporting(true);
    try {
      const res = await fetch(apiPath(`/api/drafts/${draft.id}/export`), {
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

        <label>
          Logo (PNG, SVG, JPEG o WebP)
          <input
            type="file"
            accept="image/png,image/svg+xml,image/jpeg,image/webp"
            disabled={uploadingLogo}
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) void uploadLogo(file);
            }}
          />
        </label>
        {uploadingLogo && <p className="muted">Caricamento…</p>}
        {draft.logoFileName && <p className="muted">Caricato: {draft.logoFileName}</p>}
      </section>

      <section>
        <h2>6b. Immagini prodotto (foto, rendering)</h2>
        <p className="muted">
          Facoltativo — foto e rendering dei modelli, associabili a prodotto/sotto-modello/variante/colore.
          Non ancora usate dal motore di calcolo, verranno esportate nel bundle come materiale di riferimento.
        </p>
        <div className="asset-upload-fields">
          <label>
            Tipo
            <select
              value={assetTipo}
              onChange={(e) => setAssetTipo(e.target.value as AssetManifestEntry["tipo"])}
            >
              <option value="foto">Foto</option>
              <option value="rendering">Rendering</option>
              <option value="altro">Altro</option>
            </select>
          </label>
          <label>
            Prodotto (opz.)
            <input value={assetProdotto} onChange={(e) => setAssetProdotto(e.target.value)} />
          </label>
          <label>
            Sotto-modello (opz.)
            <input value={assetSottoModello} onChange={(e) => setAssetSottoModello(e.target.value)} />
          </label>
          <label>
            Variante montaggio (opz.)
            <input value={assetVariante} onChange={(e) => setAssetVariante(e.target.value)} />
          </label>
          <label>
            Colore (opz.)
            <input value={assetColore} onChange={(e) => setAssetColore(e.target.value)} />
          </label>
          <label>
            File (PNG, JPEG o WebP)
            <input
              type="file"
              accept="image/png,image/jpeg,image/webp"
              disabled={uploadingAsset}
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) void uploadAsset(file);
                e.target.value = "";
              }}
            />
          </label>
        </div>
        {uploadingAsset && <p className="muted">Caricamento…</p>}
        {draft.assets && draft.assets.length > 0 && (
          <ul className="asset-list">
            {draft.assets.map((a) => (
              <li key={a.path}>
                <span>
                  [{TIPO_LABELS[a.tipo]}] {a.path.split("/").pop()}
                  {a.prodotto ? ` — ${a.prodotto}` : ""}
                  {a.sotto_modello ? ` / ${a.sotto_modello}` : ""}
                  {a.variante_montaggio ? ` / ${a.variante_montaggio}` : ""}
                  {a.colore ? ` / ${a.colore}` : ""}
                </span>
                <button type="button" onClick={() => void deleteAsset(a.path)}>
                  Rimuovi
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h2>6c. Anteprima App Venditore</h2>
        <p className="muted">
          Come apparirà indicativamente la pagina di accesso del venditore per questo cliente —
          logo e colore primario del tema attuale. Non è l&apos;app reale (che richiede un
          deployment a sé per ogni cliente), solo un&apos;anteprima per valutare il branding prima
          di esportare.
        </p>
        <VenditorePreview draftId={draft.id} logoFileName={draft.logoFileName} theme={draft.theme} />
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
            <a href={apiPath(exportResult.downloadUrl)}>Scarica zip</a>
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

/**
 * Self-contained mockup of the App Venditore login page, styled with the
 * draft's current theme — not a live embed of the real app (each tenant is
 * its own deployment, there's nothing running yet for an in-progress draft),
 * just enough to judge the branding before exporting.
 */
function VenditorePreview({
  draftId,
  logoFileName,
  theme,
}: {
  draftId: string;
  logoFileName?: string;
  theme: DraftTheme;
}) {
  const primario = theme.palette.primario || "#111827";

  return (
    <div className="venditore-preview">
      <div className="venditore-preview-topbar">
        {logoFileName && (
          <img src={apiPath(`/api/drafts/${draftId}/logo`)} alt={theme.nome_azienda} />
        )}
        <span className="venditore-preview-lang">IT EN</span>
      </div>
      <div className="venditore-preview-body">
        <h3>Accesso venditore</h3>
        <label>
          Email
          <input type="email" disabled placeholder="venditore@esempio.it" />
        </label>
        <label>
          Password
          <input type="password" disabled placeholder="••••••••" />
        </label>
        <button type="button" disabled style={{ background: primario }}>
          Accedi
        </button>
      </div>
    </div>
  );
}

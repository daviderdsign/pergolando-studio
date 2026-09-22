import type { Draft } from "./storage";
import { listBundleVersions } from "./storage";

const WEIGHTS = {
  catalogoPdf: 15,
  mappatura: 25,
  logo: 15,
  cartaIntestata: 10,
  esportato: 35,
} as const;

function hasMappatura(database: unknown): boolean {
  if (!database || typeof database !== "object") return false;
  const prodotto = (database as Record<string, unknown>).prodotto;
  return Boolean(prodotto && typeof prodotto === "object" && Object.keys(prodotto).length > 0);
}

/**
 * Percentuale di completamento indicativa per le card di progetto in
 * dashboard — un'euristica, non un requisito di business formale. Pesi
 * documentati qui sopra: "esportato" pesa di più perché è l'unico passaggio
 * che garantisce che la validazione sia stata superata almeno una volta
 * (il risultato della validazione non è persistito sul Draft).
 */
export async function draftProgress(draft: Draft): Promise<number> {
  let score = 0;
  if (draft.extractedText) score += WEIGHTS.catalogoPdf;
  if (hasMappatura(draft.database)) score += WEIGHTS.mappatura;
  if (draft.logoFileName) score += WEIGHTS.logo;
  if (draft.letterheadFileName) score += WEIGHTS.cartaIntestata;
  const versions = await listBundleVersions(draft.tenantId);
  if (versions.length > 0) score += WEIGHTS.esportato;
  return Math.min(100, score);
}

export interface ProjectSummary {
  id: string;
  nomeAzienda: string;
  tenantId: string;
  logoFileName?: string;
  progress: number;
}

export async function summarizeDrafts(drafts: Draft[]): Promise<ProjectSummary[]> {
  return Promise.all(
    drafts.map(async (d) => ({
      id: d.id,
      nomeAzienda: d.nomeAzienda,
      tenantId: d.tenantId,
      logoFileName: d.logoFileName,
      progress: await draftProgress(d),
    })),
  );
}

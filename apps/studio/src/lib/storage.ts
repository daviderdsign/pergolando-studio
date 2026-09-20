import { mkdir, readFile, readdir, writeFile, rm } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import { randomUUID } from "node:crypto";

/**
 * Local-disk, per-draft storage for the Studio MVP (STU-1..STU-7). No
 * multi-tenant isolation is needed here — Studio is a single-operator
 * internal tool (see PRD: "Utente: noi... Mai il venditore, mai il cliente
 * finale"). Multi-tenant isolation is an App Venditore concern.
 */

const STORAGE_ROOT = path.join(process.cwd(), "storage");
const UPLOADS_DIR = path.join(STORAGE_ROOT, "uploads");
const BUNDLES_DIR = path.join(STORAGE_ROOT, "bundles");

export interface DraftTheme {
  nome_azienda: string;
  logo_path?: string;
  palette: {
    primario: string;
    secondario?: string;
    testo?: string;
    sfondo?: string;
  };
}

export interface Draft {
  id: string;
  tenantId: string;
  nomeAzienda: string;
  createdAt: string;
  updatedAt: string;
  /** Raw text extracted from an uploaded PDF, if any (STU-1). */
  extractedText?: string;
  /** Best-effort table candidate blocks flagged for manual review (STU-2). */
  tableCandidates?: TableCandidate[];
  /** The catalog database the operator is editing (STU-3/STU-4). */
  database: unknown;
  /** The price matrices the operator is editing. */
  priceMatrices: unknown;
  theme: DraftTheme;
  letterheadFileName?: string;
}

export interface TableCandidate {
  page: number;
  rows: string[][];
}

async function ensureDirs() {
  await mkdir(UPLOADS_DIR, { recursive: true });
  await mkdir(BUNDLES_DIR, { recursive: true });
}

function draftDir(draftId: string): string {
  return path.join(UPLOADS_DIR, draftId);
}

function draftFile(draftId: string): string {
  return path.join(draftDir(draftId), "draft.json");
}

export async function createDraft(input: {
  tenantId: string;
  nomeAzienda: string;
  database?: unknown;
  priceMatrices?: unknown;
}): Promise<Draft> {
  await ensureDirs();
  const now = new Date().toISOString();
  const draft: Draft = {
    id: randomUUID(),
    tenantId: input.tenantId,
    nomeAzienda: input.nomeAzienda,
    createdAt: now,
    updatedAt: now,
    database: input.database ?? {},
    priceMatrices: input.priceMatrices ?? {},
    theme: { nome_azienda: input.nomeAzienda, palette: { primario: "#1a1a1a" } },
  };
  await mkdir(draftDir(draft.id), { recursive: true });
  await writeFile(draftFile(draft.id), JSON.stringify(draft, null, 2), "utf-8");
  return draft;
}

export async function getDraft(draftId: string): Promise<Draft | null> {
  const file = draftFile(draftId);
  if (!existsSync(file)) return null;
  return JSON.parse(await readFile(file, "utf-8")) as Draft;
}

export async function saveDraft(draft: Draft): Promise<void> {
  draft.updatedAt = new Date().toISOString();
  await writeFile(draftFile(draft.id), JSON.stringify(draft, null, 2), "utf-8");
}

export async function listDrafts(): Promise<Draft[]> {
  await ensureDirs();
  const ids = existsSync(UPLOADS_DIR) ? await readdir(UPLOADS_DIR) : [];
  const drafts = await Promise.all(ids.map((id) => getDraft(id)));
  return drafts
    .filter((d): d is Draft => d !== null)
    .sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));
}

export async function deleteDraft(draftId: string): Promise<void> {
  await rm(draftDir(draftId), { recursive: true, force: true });
}

export async function saveUploadedPdf(draftId: string, bytes: Buffer, fileName: string): Promise<string> {
  await mkdir(draftDir(draftId), { recursive: true });
  const dest = path.join(draftDir(draftId), fileName);
  await writeFile(dest, bytes);
  return dest;
}

export async function saveLetterhead(draftId: string, bytes: Buffer, fileName: string): Promise<string> {
  await mkdir(draftDir(draftId), { recursive: true });
  const dest = path.join(draftDir(draftId), fileName);
  await writeFile(dest, bytes);
  return dest;
}

export function draftUploadPath(draftId: string, fileName: string): string {
  return path.join(draftDir(draftId), fileName);
}

/** Bundle export destinations — one immutable, versioned folder per tenant+version (per PRD). */
export async function bundleExportDir(tenantId: string, version: string): Promise<string> {
  const dir = path.join(BUNDLES_DIR, tenantId, version);
  await mkdir(dir, { recursive: true });
  return dir;
}

export async function listBundleVersions(tenantId: string): Promise<string[]> {
  const tenantDir = path.join(BUNDLES_DIR, tenantId);
  if (!existsSync(tenantDir)) return [];
  return (await readdir(tenantDir)).sort();
}

export { BUNDLES_DIR };

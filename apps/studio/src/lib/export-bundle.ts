import { writeFile, mkdir, readFile, copyFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import AdmZip from "adm-zip";
import { CURRENT_SCHEMA_VERSION } from "@pergolando/bundle-schema";
import { bundleExportDir, listBundleVersions, draftUploadPath, type Draft } from "./storage";

/**
 * STU-7: exports an immutable, versioned bundle folder (manifest.json,
 * catalog/*.json, branding/*) per the PRD's bundle contract, and a zip of
 * it for download. A version bump happens on every export — bundles are
 * never modified in place.
 */

function nextVersion(existing: string[]): string {
  if (existing.length === 0) return "0.1.0";
  const latest = existing[existing.length - 1]!;
  const parts = latest.split(".").map(Number);
  const patch = (parts[2] ?? 0) + 1;
  return `${parts[0] ?? 0}.${parts[1] ?? 0}.${patch}`;
}

export async function exportBundle(
  draft: Draft,
  changelogNote: string,
): Promise<{ version: string; dir: string; zipPath: string }> {
  const existingVersions = await listBundleVersions(draft.tenantId);
  const version = nextVersion(existingVersions);
  const dir = await bundleExportDir(draft.tenantId, version);

  const manifest = {
    tenant_id: draft.tenantId,
    nome_azienda: draft.nomeAzienda,
    bundle_version: version,
    data_export: new Date().toISOString(),
    schema_version: CURRENT_SCHEMA_VERSION,
  };

  await mkdir(path.join(dir, "catalog"), { recursive: true });
  await mkdir(path.join(dir, "branding"), { recursive: true });

  await writeFile(path.join(dir, "manifest.json"), JSON.stringify(manifest, null, 2), "utf-8");
  await writeFile(
    path.join(dir, "catalog", "database.json"),
    JSON.stringify(draft.database, null, 2),
    "utf-8",
  );
  await writeFile(
    path.join(dir, "catalog", "price_matrices.json"),
    JSON.stringify(draft.priceMatrices, null, 2),
    "utf-8",
  );
  await writeFile(
    path.join(dir, "branding", "theme.json"),
    JSON.stringify(draft.theme, null, 2),
    "utf-8",
  );

  if (draft.letterheadFileName) {
    const src = draftUploadPath(draft.id, draft.letterheadFileName);
    if (existsSync(src)) {
      await copyFile(src, path.join(dir, "branding", draft.letterheadFileName));
    }
  }

  const changelogPath = path.join(path.dirname(dir), "CHANGELOG.md");
  const prevChangelog = existsSync(changelogPath) ? await readFile(changelogPath, "utf-8") : "# Changelog\n\n";
  const entry = `## ${version} — ${manifest.data_export}\n\n${changelogNote || "(nessuna nota)"}\n\n`;
  await writeFile(changelogPath, prevChangelog + entry, "utf-8");

  const zip = new AdmZip();
  zip.addLocalFolder(dir);
  const zipPath = path.join(path.dirname(dir), `${draft.tenantId}-${version}.zip`);
  zip.writeZip(zipPath);

  return { version, dir, zipPath };
}

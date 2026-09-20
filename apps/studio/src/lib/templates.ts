import { readFile } from "node:fs/promises";
import path from "node:path";

/**
 * "Start from Vision/Brera as template" (per the Fase 0/1 plan) — these are
 * the two already-validated reference catalogs, useful as a starting shape
 * when onboarding the next real catalog.
 */

const FIXTURES_DIR = path.join(process.cwd(), "..", "..", "fixtures");

export type TemplateName = "vision" | "brera";

export async function loadTemplate(name: TemplateName): Promise<{
  database: unknown;
  priceMatrices: unknown;
}> {
  const dir = path.join(FIXTURES_DIR, name);
  const [database, priceMatrices] = await Promise.all([
    readFile(path.join(dir, "database.json"), "utf-8"),
    readFile(path.join(dir, "price_matrices.json"), "utf-8"),
  ]);
  return {
    database: JSON.parse(database),
    priceMatrices: JSON.parse(priceMatrices),
  };
}

export function emptyDatabaseTemplate(): unknown {
  return {
    prodotto: {
      nome: "Nuovo prodotto",
      categoria: "",
      categoria_en: "",
      brevetti: [],
      made_in: "Italy",
      colori: {
        struttura_e_lame: { standard: [], con_supplemento: [] },
        parti_plastiche: { opzioni: [] },
      },
    },
    sotto_modelli: {},
  };
}

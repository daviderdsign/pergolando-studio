import { PergolaEngine } from "@pergolando/shared/pricing-engine";
import type { CatalogDatabase, PriceMatrices } from "@pergolando/shared/schema";

/**
 * STU-5c: a smoke test, not exhaustive regression — for every
 * sotto_modello x variante_montaggio in the draft, builds one representative
 * mid-range configuration and runs it through the shared pricing engine.
 * Catches the most common mapping mistakes (wrong matrice_prezzi_ref, a
 * price matrix missing entirely, malformed per-moduli tables) before export.
 */

export interface SmokeTestResult {
  sottoModello: string;
  varianteMontaggio: string;
  ok: boolean;
  prezzoTotaleEur?: number;
  error?: string;
}

function nomeCompleto(c: { ral?: string | null; nome_it: string }): string {
  return c.ral ? `${c.ral} ${c.nome_it}` : c.nome_it;
}

export function runSmokeTests(db: CatalogDatabase, priceMatrices: PriceMatrices): SmokeTestResult[] {
  const results: SmokeTestResult[] = [];
  const engine = PergolaEngine.fromDatabase(db, priceMatrices);

  const strutturaColori = [
    ...db.prodotto.colori.struttura_e_lame.standard,
    ...db.prodotto.colori.struttura_e_lame.con_supplemento,
  ];
  const coloreStruttura = strutturaColori[0] ? nomeCompleto(strutturaColori[0]) : undefined;
  const colorePlastica = db.prodotto.colori.parti_plastiche.opzioni[0]?.nome_it;

  for (const [smKey, sm] of Object.entries(db.sotto_modelli)) {
    const opzioni = sm.opzioni_tecniche_lama ?? sm.opzioni_tecniche;
    const primaOpzioneEntry = opzioni ? Object.entries(opzioni)[0] : undefined;

    for (const [varianteKey, variante] of Object.entries(sm.varianti_montaggio)) {
      const label = `${smKey} / ${varianteKey}`;
      if (!coloreStruttura || !colorePlastica || !primaOpzioneEntry) {
        results.push({
          sottoModello: smKey,
          varianteMontaggio: varianteKey,
          ok: false,
          error: `${label}: colori o opzioni tecniche mancanti, impossibile costruire un caso di prova.`,
        });
        continue;
      }
      const [opzioneNome, opzioneDati] = primaOpzioneEntry;
      const altezza = Math.max(1, sm.vincoli_dimensionali.H_max_cm - 1);

      let pRichiesta: number;
      let lRichiesta: number;

      if (variante.orientamento_crescita === "L" && variante.L_max_per_n_moduli) {
        const moduli = Object.keys(variante.L_max_per_n_moduli)
          .map(Number)
          .sort((a, b) => a - b);
        const nModuli = moduli[0]!;
        const lMaxTotale = Math.min(
          variante.L_max_per_n_moduli[String(nModuli)]!,
          opzioneDati.L_max_cm * nModuli,
        );
        lRichiesta = Math.max(1, Math.floor(lMaxTotale / 2));
        pRichiesta = sm.vincoli_dimensionali.P_min_cm;
      } else if (variante.orientamento_crescita === "P" && variante.P_max_per_n_moduli) {
        const moduli = Object.keys(variante.P_max_per_n_moduli)
          .map(Number)
          .sort((a, b) => a - b);
        const nModuli = moduli[0]!;
        const pMaxTotale = variante.P_max_per_n_moduli[String(nModuli)]!;
        pRichiesta = Math.max(1, Math.floor(pMaxTotale / 2));
        lRichiesta = Math.max(1, Math.floor(opzioneDati.L_max_cm / 2));
      } else {
        results.push({
          sottoModello: smKey,
          varianteMontaggio: varianteKey,
          ok: false,
          error: `${label}: dati dimensionali mancanti o incoerenti con orientamento_crescita.`,
        });
        continue;
      }

      try {
        const cfg = engine.configura({
          sottoModello: smKey,
          varianteMontaggio: varianteKey,
          pRichiestaCm: pRichiesta,
          lRichiestaCm: lRichiesta,
          coloreStruttura,
          colorePlastica,
          altezzaMontantiCm: altezza,
          opzioneTecnica: opzioneNome,
        });
        results.push({
          sottoModello: smKey,
          varianteMontaggio: varianteKey,
          ok: true,
          prezzoTotaleEur: cfg.prezzo_totale_eur,
        });
      } catch (err) {
        results.push({
          sottoModello: smKey,
          varianteMontaggio: varianteKey,
          ok: false,
          error: err instanceof Error ? err.message : String(err),
        });
      }
    }
  }

  return results;
}

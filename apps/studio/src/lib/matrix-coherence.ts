/**
 * STU-5b: matrix coherence checks (missing rows/columns, non-monotonic
 * prices, range outliers) — a best-effort sanity net, not a replacement for
 * the operator's own read of the catalog.
 */

export interface CoherenceIssue {
  matrice: string;
  severity: "error" | "warning";
  message: string;
}

interface MatriceRigaLike {
  P_riferimento: number;
  prezzi_per_L: Record<string, number>;
}

export function checkPriceMatrices(priceMatrices: Record<string, MatriceRigaLike[]>): CoherenceIssue[] {
  const issues: CoherenceIssue[] = [];

  for (const [nome, righe] of Object.entries(priceMatrices)) {
    if (righe.length === 0) {
      issues.push({ matrice: nome, severity: "error", message: "La matrice non ha righe." });
      continue;
    }

    const pValues = righe.map((r) => r.P_riferimento);
    const duplicates = pValues.filter((p, i) => pValues.indexOf(p) !== i);
    if (duplicates.length > 0) {
      issues.push({
        matrice: nome,
        severity: "error",
        message: `P_riferimento duplicato: ${[...new Set(duplicates)].join(", ")}.`,
      });
    }

    const allColumns = new Set<string>();
    for (const r of righe) for (const col of Object.keys(r.prezzi_per_L)) allColumns.add(col);

    for (const r of righe) {
      const missing = [...allColumns].filter((c) => !(c in r.prezzi_per_L));
      if (missing.length > 0) {
        issues.push({
          matrice: nome,
          severity: "warning",
          message: `Riga P_riferimento=${r.P_riferimento}: colonne mancanti rispetto alle altre righe: ${missing.join(", ")}.`,
        });
      }
    }

    const sortedByP = [...righe].sort((a, b) => a.P_riferimento - b.P_riferimento);
    for (const r of sortedByP) {
      const cols = Object.keys(r.prezzi_per_L)
        .map(Number)
        .sort((a, b) => a - b);
      for (let i = 1; i < cols.length; i++) {
        const prev = r.prezzi_per_L[String(cols[i - 1])]!;
        const curr = r.prezzi_per_L[String(cols[i])]!;
        if (curr < prev) {
          issues.push({
            matrice: nome,
            severity: "warning",
            message: `Riga P_riferimento=${r.P_riferimento}: prezzo non crescente tra L=${cols[i - 1]} (${prev}) e L=${cols[i]} (${curr}).`,
          });
        }
      }
    }

    for (const col of allColumns) {
      let prevPrice: number | undefined;
      for (const r of sortedByP) {
        const price = r.prezzi_per_L[col];
        if (price === undefined) continue;
        if (prevPrice !== undefined && price < prevPrice) {
          issues.push({
            matrice: nome,
            severity: "warning",
            message: `Colonna L=${col}: prezzo non crescente tra P_riferimento=${r.P_riferimento} e la riga precedente.`,
          });
        }
        prevPrice = price;
      }
    }

    const allPrices = righe.flatMap((r) => Object.values(r.prezzi_per_L));
    const mean = allPrices.reduce((s, v) => s + v, 0) / allPrices.length;
    const stddev = Math.sqrt(
      allPrices.reduce((s, v) => s + (v - mean) ** 2, 0) / allPrices.length,
    );
    const outliers = allPrices.filter((v) => stddev > 0 && Math.abs(v - mean) > 4 * stddev);
    if (outliers.length > 0) {
      issues.push({
        matrice: nome,
        severity: "warning",
        message: `Valori fuori range statistico (>4 dev.std dalla media ${mean.toFixed(0)}): ${outliers.join(", ")}.`,
      });
    }
  }

  return issues;
}

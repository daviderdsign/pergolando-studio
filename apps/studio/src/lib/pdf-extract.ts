import { getDocument } from "pdfjs-dist/legacy/build/pdf.mjs";
import type { TableCandidate } from "./storage";

/**
 * STU-1 (reliable): raw text extraction, page by page.
 * STU-2 (best-effort): groups text items into rows by y-coordinate and
 * flags rows that look numeric-heavy as price-table candidates. This is
 * NOT trusted as a finished price matrix — per the PRD, automatic table
 * extraction on a catalog like Brera still needed human correction, so
 * this only produces candidates for the mapping editor to review, never
 * writes directly into catalog/price_matrices.json.
 */

interface TextItem {
  str: string;
  transform: number[];
}

const NUMERIC_TOKEN = /^[\d.,]+$/;

export async function extractPdf(bytes: Uint8Array): Promise<{
  text: string;
  tableCandidates: TableCandidate[];
}> {
  const doc = await getDocument({ data: bytes }).promise;

  const pageTexts: string[] = [];
  const tableCandidates: TableCandidate[] = [];

  for (let pageNum = 1; pageNum <= doc.numPages; pageNum++) {
    const page = await doc.getPage(pageNum);
    const content = await page.getTextContent();
    const items = content.items as TextItem[];

    const rows = groupIntoRows(items);
    pageTexts.push(rows.map((r) => r.map((t) => t.str).join(" ")).join("\n"));

    const candidateRows = rows
      .map((r) => r.map((t) => t.str.trim()).filter(Boolean))
      .filter((r) => looksLikeTableRow(r));

    if (candidateRows.length >= 2) {
      tableCandidates.push({ page: pageNum, rows: candidateRows });
    }
  }

  return { text: pageTexts.join("\n\n--- page break ---\n\n"), tableCandidates };
}

function groupIntoRows(items: TextItem[]): TextItem[][] {
  const Y_TOLERANCE = 2;
  const sorted = [...items].sort((a, b) => b.transform[5]! - a.transform[5]!);

  const rows: TextItem[][] = [];
  for (const item of sorted) {
    const y = item.transform[5]!;
    const currentRow = rows[rows.length - 1];
    const lastY = currentRow?.[0]?.transform[5];
    if (currentRow && lastY !== undefined && Math.abs(lastY - y) <= Y_TOLERANCE) {
      currentRow.push(item);
    } else {
      rows.push([item]);
    }
  }
  for (const row of rows) {
    row.sort((a, b) => a.transform[4]! - b.transform[4]!);
  }
  return rows;
}

function looksLikeTableRow(tokens: string[]): boolean {
  if (tokens.length < 3) return false;
  const numericCount = tokens.filter((t) => NUMERIC_TOKEN.test(t)).length;
  return numericCount / tokens.length >= 0.5;
}

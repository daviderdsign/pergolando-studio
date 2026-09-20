import { NextResponse } from "next/server";
import { readFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import { BUNDLES_DIR } from "@/lib/storage";

interface Params {
  params: Promise<{ tenantId: string; version: string }>;
}

export async function GET(_req: Request, { params }: Params) {
  const { tenantId, version } = await params;
  const zipPath = path.join(BUNDLES_DIR, tenantId, `${tenantId}-${version}.zip`);
  if (!existsSync(zipPath)) {
    return NextResponse.json({ error: "Bundle non trovato." }, { status: 404 });
  }
  const bytes = await readFile(zipPath);
  return new NextResponse(new Uint8Array(bytes), {
    headers: {
      "Content-Type": "application/zip",
      "Content-Disposition": `attachment; filename="${tenantId}-${version}.zip"`,
    },
  });
}

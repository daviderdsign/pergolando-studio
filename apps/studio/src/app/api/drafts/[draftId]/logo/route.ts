import { readFile } from "node:fs/promises";
import { extname } from "node:path";
import { NextRequest, NextResponse } from "next/server";
import { getDraft, saveDraft, saveLogo, draftUploadPath } from "@/lib/storage";

interface Params {
  params: Promise<{ draftId: string }>;
}

const ALLOWED_TYPES = new Set(["image/png", "image/svg+xml", "image/jpeg", "image/webp"]);

const CONTENT_TYPES: Record<string, string> = {
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
};

/** Serves the currently uploaded logo — used by the Studio preview panel. */
export async function GET(_req: NextRequest, { params }: Params) {
  const { draftId } = await params;
  const draft = await getDraft(draftId);
  if (!draft?.logoFileName) {
    return NextResponse.json({ error: "Nessun logo caricato." }, { status: 404 });
  }

  const bytes = await readFile(draftUploadPath(draftId, draft.logoFileName));
  const contentType = CONTENT_TYPES[extname(draft.logoFileName).toLowerCase()] ?? "application/octet-stream";
  return new NextResponse(new Uint8Array(bytes), {
    headers: { "Content-Type": contentType },
  });
}

/** STU-6: upload the tenant's logo (used as theme.logo_path for the App Venditore). */
export async function POST(req: NextRequest, { params }: Params) {
  const { draftId } = await params;
  const draft = await getDraft(draftId);
  if (!draft) return NextResponse.json({ error: "Draft non trovato." }, { status: 404 });

  const form = await req.formData();
  const file = form.get("file");
  if (!(file instanceof File)) {
    return NextResponse.json({ error: "Campo 'file' mancante o non valido." }, { status: 400 });
  }
  if (!ALLOWED_TYPES.has(file.type)) {
    return NextResponse.json({ error: "Il logo deve essere PNG, SVG, JPEG o WebP." }, { status: 400 });
  }

  const bytes = Buffer.from(await file.arrayBuffer());
  await saveLogo(draftId, bytes, file.name);
  draft.logoFileName = file.name;
  draft.theme = { ...draft.theme, logo_path: `branding/${file.name}` };
  await saveDraft(draft);

  return NextResponse.json({ draft });
}

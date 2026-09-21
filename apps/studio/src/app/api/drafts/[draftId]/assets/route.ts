import { rm } from "node:fs/promises";
import { NextRequest, NextResponse } from "next/server";
import { getDraft, saveDraft, saveAssetFile, draftAssetPath } from "@/lib/storage";
import type { AssetManifestEntry } from "@pergolando/shared/schema";

interface Params {
  params: Promise<{ draftId: string }>;
}

const ALLOWED_TYPES = new Set(["image/png", "image/jpeg", "image/webp"]);
const ALLOWED_TIPI = new Set(["foto", "rendering", "altro"]);

/** Product photos/renderings — populates the assets/ placeholder the bundle schema reserves for Fase 5. */
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
    return NextResponse.json({ error: "L'immagine deve essere PNG, JPEG o WebP." }, { status: 400 });
  }

  const tipo = String(form.get("tipo") ?? "foto");
  if (!ALLOWED_TIPI.has(tipo)) {
    return NextResponse.json({ error: "Tipo non valido (foto, rendering, altro)." }, { status: 400 });
  }

  const bytes = Buffer.from(await file.arrayBuffer());
  await saveAssetFile(draftId, bytes, file.name);

  const entry: AssetManifestEntry = {
    path: `assets/${file.name}`,
    tipo: tipo as AssetManifestEntry["tipo"],
    prodotto: optionalString(form.get("prodotto")),
    sotto_modello: optionalString(form.get("sotto_modello")),
    variante_montaggio: optionalString(form.get("variante_montaggio")),
    colore: optionalString(form.get("colore")),
  };

  draft.assets = [...(draft.assets ?? []), entry];
  await saveDraft(draft);

  return NextResponse.json({ draft });
}

export async function DELETE(req: NextRequest, { params }: Params) {
  const { draftId } = await params;
  const draft = await getDraft(draftId);
  if (!draft) return NextResponse.json({ error: "Draft non trovato." }, { status: 404 });

  const { searchParams } = new URL(req.url);
  const assetPath = searchParams.get("path");
  if (!assetPath) {
    return NextResponse.json({ error: "Parametro 'path' mancante." }, { status: 400 });
  }

  const fileName = assetPath.split("/").pop();
  if (fileName) {
    await rm(draftAssetPath(draftId, fileName), { force: true });
  }
  draft.assets = (draft.assets ?? []).filter((a) => a.path !== assetPath);
  await saveDraft(draft);

  return NextResponse.json({ draft });
}

function optionalString(v: FormDataEntryValue | null): string | undefined {
  if (typeof v !== "string" || v.trim() === "") return undefined;
  return v;
}

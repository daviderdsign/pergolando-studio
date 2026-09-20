import { NextRequest, NextResponse } from "next/server";
import { getDraft, saveDraft, saveUploadedPdf } from "@/lib/storage";
import { extractPdf } from "@/lib/pdf-extract";

interface Params {
  params: Promise<{ draftId: string }>;
}

/** STU-1: upload a catalog PDF, extract raw text + best-effort table candidates. */
export async function POST(req: NextRequest, { params }: Params) {
  const { draftId } = await params;
  const draft = await getDraft(draftId);
  if (!draft) return NextResponse.json({ error: "Draft non trovato." }, { status: 404 });

  const form = await req.formData();
  const file = form.get("file");
  if (!(file instanceof File)) {
    return NextResponse.json({ error: "Campo 'file' mancante o non valido." }, { status: 400 });
  }
  if (file.type !== "application/pdf") {
    return NextResponse.json({ error: "Il file deve essere un PDF." }, { status: 400 });
  }

  const bytes = Buffer.from(await file.arrayBuffer());
  await saveUploadedPdf(draftId, bytes, file.name);

  const { text, tableCandidates } = await extractPdf(new Uint8Array(bytes));
  draft.extractedText = text;
  draft.tableCandidates = tableCandidates;
  await saveDraft(draft);

  return NextResponse.json({ draft });
}

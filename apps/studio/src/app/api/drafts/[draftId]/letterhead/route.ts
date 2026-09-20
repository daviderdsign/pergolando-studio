import { NextRequest, NextResponse } from "next/server";
import { getDraft, saveDraft, saveLetterhead } from "@/lib/storage";

interface Params {
  params: Promise<{ draftId: string }>;
}

/** STU-6: upload the tenant's letterhead (PDF or SVG). */
export async function POST(req: NextRequest, { params }: Params) {
  const { draftId } = await params;
  const draft = await getDraft(draftId);
  if (!draft) return NextResponse.json({ error: "Draft non trovato." }, { status: 404 });

  const form = await req.formData();
  const file = form.get("file");
  if (!(file instanceof File)) {
    return NextResponse.json({ error: "Campo 'file' mancante o non valido." }, { status: 400 });
  }
  if (file.type !== "application/pdf" && file.type !== "image/svg+xml") {
    return NextResponse.json({ error: "La carta intestata deve essere PDF o SVG." }, { status: 400 });
  }

  const bytes = Buffer.from(await file.arrayBuffer());
  await saveLetterhead(draftId, bytes, file.name);
  draft.letterheadFileName = file.name;
  await saveDraft(draft);

  return NextResponse.json({ draft });
}

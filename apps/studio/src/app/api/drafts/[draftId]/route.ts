import { NextRequest, NextResponse } from "next/server";
import { deleteDraft, getDraft, saveDraft } from "@/lib/storage";

interface Params {
  params: Promise<{ draftId: string }>;
}

export async function GET(_req: NextRequest, { params }: Params) {
  const { draftId } = await params;
  const draft = await getDraft(draftId);
  if (!draft) return NextResponse.json({ error: "Draft non trovato." }, { status: 404 });
  return NextResponse.json({ draft });
}

export async function PUT(req: NextRequest, { params }: Params) {
  const { draftId } = await params;
  const draft = await getDraft(draftId);
  if (!draft) return NextResponse.json({ error: "Draft non trovato." }, { status: 404 });

  const body = (await req.json()) as Partial<{
    database: unknown;
    priceMatrices: unknown;
    theme: typeof draft.theme;
    nomeAzienda: string;
  }>;

  if (body.database !== undefined) draft.database = body.database;
  if (body.priceMatrices !== undefined) draft.priceMatrices = body.priceMatrices;
  if (body.theme !== undefined) draft.theme = body.theme;
  if (body.nomeAzienda !== undefined) draft.nomeAzienda = body.nomeAzienda;

  await saveDraft(draft);
  return NextResponse.json({ draft });
}

export async function DELETE(_req: NextRequest, { params }: Params) {
  const { draftId } = await params;
  await deleteDraft(draftId);
  return NextResponse.json({ ok: true });
}

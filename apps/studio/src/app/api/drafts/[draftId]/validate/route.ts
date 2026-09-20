import { NextRequest, NextResponse } from "next/server";
import { getDraft } from "@/lib/storage";
import { validateDraft } from "@/lib/validate-bundle";

interface Params {
  params: Promise<{ draftId: string }>;
}

/** STU-5: schema validation + matrix coherence + pricing-engine smoke tests. */
export async function POST(_req: NextRequest, { params }: Params) {
  const { draftId } = await params;
  const draft = await getDraft(draftId);
  if (!draft) return NextResponse.json({ error: "Draft non trovato." }, { status: 404 });

  const report = validateDraft(draft);
  return NextResponse.json({ report });
}

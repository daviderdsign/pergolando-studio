import { NextRequest, NextResponse } from "next/server";
import { getDraft } from "@/lib/storage";
import { validateDraft } from "@/lib/validate-bundle";
import { exportBundle } from "@/lib/export-bundle";

interface Params {
  params: Promise<{ draftId: string }>;
}

/** STU-7: export is blocked until validation passes (mandatory human review gate). */
export async function POST(req: NextRequest, { params }: Params) {
  const { draftId } = await params;
  const draft = await getDraft(draftId);
  if (!draft) return NextResponse.json({ error: "Draft non trovato." }, { status: 404 });

  const report = validateDraft(draft);
  if (!report.passed) {
    return NextResponse.json(
      { error: "Validazione non superata: impossibile esportare.", report },
      { status: 422 },
    );
  }

  const body = (await req.json().catch(() => ({}))) as { changelogNote?: string };
  const result = await exportBundle(draft, body.changelogNote ?? "");

  return NextResponse.json({
    version: result.version,
    downloadUrl: `/api/bundles/${draft.tenantId}/${result.version}/download`,
  });
}

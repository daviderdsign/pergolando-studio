import { NextRequest, NextResponse } from "next/server";
import { createDraft, listDrafts } from "@/lib/storage";
import { loadTemplate, emptyDatabaseTemplate, type TemplateName } from "@/lib/templates";

export async function GET() {
  const drafts = await listDrafts();
  return NextResponse.json({ drafts });
}

export async function POST(req: NextRequest) {
  const body = (await req.json()) as {
    tenantId?: string;
    nomeAzienda?: string;
    template?: TemplateName | "vuoto";
  };

  if (!body.tenantId || !body.nomeAzienda) {
    return NextResponse.json({ error: "tenantId e nomeAzienda sono obbligatori." }, { status: 400 });
  }

  let database: unknown = emptyDatabaseTemplate();
  let priceMatrices: unknown = {};
  if (body.template === "vision" || body.template === "brera") {
    const tpl = await loadTemplate(body.template);
    database = tpl.database;
    priceMatrices = tpl.priceMatrices;
  }

  const draft = await createDraft({
    tenantId: body.tenantId,
    nomeAzienda: body.nomeAzienda,
    database,
    priceMatrices,
  });

  return NextResponse.json({ draft }, { status: 201 });
}

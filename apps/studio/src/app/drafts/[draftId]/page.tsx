import { notFound } from "next/navigation";
import { getDraft } from "@/lib/storage";
import { DraftEditor } from "@/components/DraftEditor";

interface Props {
  params: Promise<{ draftId: string }>;
}

export default async function DraftPage({ params }: Props) {
  const { draftId } = await params;
  const draft = await getDraft(draftId);
  if (!draft) notFound();

  return <DraftEditor initialDraft={draft} />;
}

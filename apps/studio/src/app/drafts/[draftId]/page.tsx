import { notFound } from "next/navigation";
import { getDraft, listDrafts } from "@/lib/storage";
import { summarizeDrafts } from "@/lib/draft-progress";
import { DraftEditor } from "@/components/DraftEditor";

interface Props {
  params: Promise<{ draftId: string }>;
}

export default async function DraftPage({ params }: Props) {
  const { draftId } = await params;
  const draft = await getDraft(draftId);
  if (!draft) notFound();

  const allDrafts = await listDrafts();
  const projects = await summarizeDrafts(allDrafts);

  return <DraftEditor initialDraft={draft} projects={projects} />;
}

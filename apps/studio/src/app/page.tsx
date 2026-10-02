import { listDrafts } from "@/lib/storage";
import { summarizeDrafts } from "@/lib/draft-progress";
import { NewDraftForm } from "@/components/NewDraftForm";
import { StudioShell } from "@/components/StudioShell";
import { ProjectRow } from "@/components/ProjectRow";

// The draft list changes constantly (new drafts, edits) — without this,
// `next build` prerenders it once as static HTML and every deploy serves a
// frozen snapshot from whatever storage/uploads/ looked like at build time.
export const dynamic = "force-dynamic";

export default async function HomePage() {
  const drafts = await listDrafts();
  const projects = await summarizeDrafts(drafts);

  return (
    <StudioShell>
      <ProjectRow items={projects} />

      <section className="studio-section">
        <h2 className="section-title">Nuovo progetto</h2>
        <NewDraftForm />
      </section>
    </StudioShell>
  );
}

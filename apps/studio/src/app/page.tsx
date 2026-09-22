import { listDrafts } from "@/lib/storage";
import { summarizeDrafts } from "@/lib/draft-progress";
import { NewDraftForm } from "@/components/NewDraftForm";
import { StudioShell } from "@/components/StudioShell";
import { ProjectRow } from "@/components/ProjectRow";
import { apiPath } from "@/lib/base-path";

// The draft list changes constantly (new drafts, edits) — without this,
// `next build` prerenders it once as static HTML and every deploy serves a
// frozen snapshot from whatever storage/uploads/ looked like at build time.
export const dynamic = "force-dynamic";

export default async function HomePage() {
  const drafts = await listDrafts();
  const projects = await summarizeDrafts(drafts);
  const mostRecent = drafts[0];
  const heroAsset = mostRecent?.assets?.[0];
  const heroImageUrl = heroAsset
    ? apiPath(`/api/drafts/${mostRecent.id}/assets?path=${encodeURIComponent(heroAsset.path)}`)
    : undefined;

  return (
    <StudioShell heroImageUrl={heroImageUrl}>
      {projects.length > 0 && <ProjectRow items={projects} currentId={mostRecent?.id} />}

      <section className="studio-section">
        <h2 className="section-title">Nuovo progetto</h2>
        <NewDraftForm />
      </section>
    </StudioShell>
  );
}

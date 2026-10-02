import Link from "next/link";
import { apiPath } from "@/lib/base-path";
import type { ProjectSummary } from "@/lib/draft-progress";
import { PergolandoLogo } from "./PergolandoLogo";

interface Props {
  items: ProjectSummary[];
  /** The project shown below the logo in the brand card on the detail page. Omitted on the dashboard, where the card is just the Pergolando logo with no back arrow. */
  currentId?: string;
}

/**
 * The row shown at the top of both the dashboard and the project detail
 * page: a fixed-size grey brand card on the left (same on every page — only
 * the gap to its right grows as the viewport widens, the card itself never
 * does), a 2-column grid of the other projects on the right ("Nuovo
 * progetto" always the last cell). On the detail page the card also shows
 * the open project's name/logo + progress below the logo (the back arrow
 * lives in the header instead — see StudioShell).
 */
export function ProjectRow({ items, currentId }: Props) {
  const current = currentId ? items.find((i) => i.id === currentId) : undefined;
  const gridItems = current ? items.filter((i) => i.id !== current.id) : items;

  return (
    <div className="project-row">
      <div className="project-brand-card">
        <PergolandoLogo className="project-brand-card-logo" />
        {current && (
          <div className="project-card-body">
            {current.logoFileName ? (
              <img
                src={apiPath(`/api/drafts/${current.id}/logo`)}
                alt={current.nomeAzienda}
                className="project-card-logo"
              />
            ) : (
              <span className="project-card-name">{current.nomeAzienda}</span>
            )}
            <span className="project-card-progress">{current.progress}%</span>
          </div>
        )}
      </div>

      <nav className="project-grid" aria-label="Progetti in corso">
        {gridItems.map((item) => (
          <Link key={item.id} href={`/drafts/${item.id}`} className="project-grid-item">
            {item.logoFileName ? (
              <img
                src={apiPath(`/api/drafts/${item.id}/logo`)}
                alt={item.nomeAzienda}
                className="project-grid-logo"
              />
            ) : (
              <span className="project-grid-name">{item.nomeAzienda}</span>
            )}
            <span className="project-grid-progress">Sviluppo app {item.progress}%</span>
          </Link>
        ))}
        <Link href="/" className="project-grid-item project-grid-new">
          Nuovo progetto
        </Link>
      </nav>
    </div>
  );
}

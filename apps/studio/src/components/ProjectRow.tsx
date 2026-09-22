import Link from "next/link";
import { apiPath } from "@/lib/base-path";
import type { ProjectSummary } from "@/lib/draft-progress";

interface Props {
  items: ProjectSummary[];
  /** The project shown as the featured card — the one open, or the most recent on the dashboard. */
  currentId?: string;
}

/**
 * The row of in-progress projects shown at the top of both the dashboard and
 * the project detail page — the current project as a featured card, the
 * rest as a plain list, "Nuovo progetto" always last.
 */
export function ProjectRow({ items, currentId }: Props) {
  const current = items.find((i) => i.id === currentId) ?? items[0];
  const others = items.filter((i) => i.id !== current?.id);

  return (
    <nav className="project-row" aria-label="Progetti in corso">
      {current && (
        <div className="project-card">
          <span className="project-card-kicker">Pergolando</span>
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
        </div>
      )}
      {others.map((item) => (
        <Link key={item.id} href={`/drafts/${item.id}`} className="project-row-item">
          <span className="project-row-name">{item.nomeAzienda}</span>
          <span className="project-row-progress">Sviluppo app {item.progress}%</span>
        </Link>
      ))}
      <Link href="/" className="project-row-new">
        Nuovo progetto
      </Link>
    </nav>
  );
}

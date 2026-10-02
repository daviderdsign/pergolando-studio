import type { ReactNode } from "react";
import Link from "next/link";
import { PergolandoLogo } from "./PergolandoLogo";
import { PergolandoMark } from "./PergolandoMark";

// Generic Pergolando brand photo — shown on the dashboard (no single project
// is "open" there, so there's nothing project-specific to show) and as a
// fallback on the detail page until that project has its own product photo
// uploaded. Swap public/hero-fallback.jpg for the real asset when available;
// until then this is simply a 404'd background-image (harmless — the dark
// panel underneath still shows).
const FALLBACK_HERO = "/hero-fallback.jpg";

interface Props {
  children: ReactNode;
  /** URL of an uploaded product asset to show as the hero photo — falls back to FALLBACK_HERO when the current context has none. */
  heroImageUrl?: string;
  /** Shows a bold back arrow at the top-left of the header, e.g. "/" on the project detail page. Omitted on the dashboard, which has nothing to go back to. */
  backHref?: string;
}

/**
 * Shared page chrome (header, content well, hero band, footer) used by both
 * the dashboard and the project detail page — see the graphic reference in
 * D:\Lavori\App\Pagina_Studio_nuovo.pdf and Pagina_Studio_Cliente.pdf.
 */
export function StudioShell({ children, heroImageUrl, backHref }: Props) {
  return (
    <>
      <header className="studio-header">
        {backHref ? (
          <Link href={backHref} className="studio-header-back" aria-label="Torna ai progetti">
            &larr;
          </Link>
        ) : (
          <span />
        )}
        <PergolandoMark className="studio-header-mark" />
      </header>
      <main className="studio-content">{children}</main>
      <div
        className="studio-hero"
        style={{ backgroundImage: `url(${heroImageUrl ?? FALLBACK_HERO})` }}
        aria-hidden="true"
      />
      <footer className="studio-footer">
        <PergolandoLogo className="studio-footer-logo" />
        <PergolandoMark className="studio-footer-mark" />
      </footer>
    </>
  );
}

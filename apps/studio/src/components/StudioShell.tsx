import type { ReactNode } from "react";
import { PergolandoLogo } from "./PergolandoLogo";

interface Props {
  children: ReactNode;
  /** URL of an uploaded product asset to show as the hero photo — falls back to a plain dark panel when none exists yet. */
  heroImageUrl?: string;
}

/**
 * Shared page chrome (header, content well, hero band, footer) used by both
 * the dashboard and the project detail page — see the graphic reference in
 * D:\Lavori\App\Pagina_Studio_nuovo.pdf and Pagina_Studio_Cliente.pdf.
 */
export function StudioShell({ children, heroImageUrl }: Props) {
  return (
    <>
      <header className="studio-header">
        <PergolandoLogo className="studio-header-logo" />
      </header>
      <main className="studio-content">{children}</main>
      <div
        className="studio-hero"
        style={heroImageUrl ? { backgroundImage: `url(${heroImageUrl})` } : undefined}
        aria-hidden="true"
      />
      <footer className="studio-footer">
        <PergolandoLogo className="studio-footer-logo" />
      </footer>
    </>
  );
}

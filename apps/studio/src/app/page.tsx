import Link from "next/link";
import { listDrafts } from "@/lib/storage";
import { NewDraftForm } from "@/components/NewDraftForm";

// The draft list changes constantly (new drafts, edits) — without this,
// `next build` prerenders it once as static HTML and every deploy serves a
// frozen snapshot from whatever storage/uploads/ looked like at build time.
export const dynamic = "force-dynamic";

export default async function HomePage() {
  const drafts = await listDrafts();

  return (
    <main className="page">
      <h1>Pergolando Studio</h1>
      <p className="subtitle">
        Trasforma un catalogo PDF di un produttore in un bundle pronto per l&apos;App Venditore.
      </p>

      <section>
        <h2>Nuovo bundle</h2>
        <NewDraftForm />
      </section>

      <section>
        <h2>Bozze in corso</h2>
        {drafts.length === 0 ? (
          <p className="muted">Nessuna bozza ancora.</p>
        ) : (
          <ul className="draft-list">
            {drafts.map((d) => (
              <li key={d.id}>
                <Link href={`/drafts/${d.id}`}>
                  <strong>{d.nomeAzienda}</strong>
                  <span className="muted"> — {d.tenantId}</span>
                </Link>
                <span className="muted"> · aggiornato {new Date(d.updatedAt).toLocaleString("it-IT")}</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}

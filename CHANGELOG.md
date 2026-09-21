# Changelog

Storico ad alto livello del lavoro svolto sul progetto Pergolando (Studio, App Venditore, deploy NAS), dall'inizio. Ogni repo (`pergolando-shared`, `pergolando-backend`, `pergolando-frontend`) ha comunque la propria cronologia Git dettagliata — qui teniamo un riassunto per fase/sessione.

## Fase 0 — Motore di calcolo condiviso (bundle schema + pricing engine)

- Letto il PRD e i file prototipo (`vision_database_v2.json`, `pergola_engine.py`, `brera_price_matrices.json`, `brera_database.json`, `vision_price_matrices.json`).
- Creato lo schema Zod del "bundle" (manifest, catalog/database, price_matrices, theme, assets) e portato in TypeScript il motore di calcolo prezzi Python (`pergola_engine.py` → `PergolaEngine`), con test di regressione a partire dai casi già validati (golden cases) su Vision e Brera.

## Fase 1 — Studio MVP (catalogazione)

- Costruita la prima versione di Studio (Next.js): creazione bozza (tenant id, nome azienda, template Vision/Brera/vuoto), upload PDF con estrazione testo/righe candidate, editor per mappare manualmente `database.json`/`price_matrices.json`, validazione (schema + coerenza matrici + smoke test motore), upload carta intestata, export bundle in zip versionato.
- Verificato a mano il flusso completo Brera: template → validazione → export.

## Fase 2 — App Venditore (architettura multi-tenant)

- Decisione architetturale (confermata con l'utente): **un deployment per cliente** (container/DB separati), non multi-tenant a livello di riga — ogni App Venditore serve un solo bundle, caricato via variabili d'ambiente (`BUNDLE_PATH`, `DATABASE_URL`).
- Creato il repo `pergolando-shared` (pacchetto `@pergolando/shared`, distribuito come git-dependency via tag, es. `v0.1.0`) per non duplicare schema e motore di calcolo tra Studio e App Venditore.
- Creati i repo `pergolando-backend` (NestJS + Prisma + SQLite, Argon2id, sessioni server-side, rate limiting, Pino) e `pergolando-frontend` (Next.js, i18n IT/EN, Playwright+axe-core), con Git Flow (`main`/`develop`) su entrambi.
- Prima slice funzionante: registrazione/login/logout venditore + caricamento bundle a boot + primo step del wizard (dati cliente, scelta prodotto/sotto-modello/variante).

## Fase C — Deploy Docker sul NAS (verifica end-to-end)

- Guidato il deploy reale sul NAS self-hosted, con l'utente che eseguiva i comandi in prima persona.
- Problemi affrontati e risolti:
  - Toolchain di compilazione mancante per moduli nativi (`better-sqlite3`, `argon2`) → aggiunti `python3 make g++` al Dockerfile.
  - Prisma 7: split di configurazione (`prisma.config.ts` per la CLI, driver adapter `@prisma/adapter-better-sqlite3` a runtime).
  - Spazio disco NAS esaurito → migrazione del `data-root` di Docker su un volume più grande.
  - Il primo volume scelto per la migrazione era NTFS (`fuseblk`), che non supporta i permessi Unix reali → ha rotto un container Postgres preesistente e non correlato (`x_rdsign-db-1`); risolto rifacendo la migrazione sul vero volume RAID ext4 (`/dev/md127`) e verificando che tutti i 12 container preesistenti fossero di nuovo sani.
  - Crash-loop a runtime di `pnpm exec prisma migrate deploy` (bloccato dal gate di sicurezza pnpm sulle build git-dependency) → risolto chiamando direttamente `node_modules/.bin/prisma migrate deploy`, bypassando pnpm a runtime.
  - Cloudflare Tunnel: interfaccia cambiata rispetto alla documentazione nota (route ora sotto Networking → Tunnels → Routes).
  - Certificato Universal SSL di Cloudflare copre un solo livello di sottodominio → rinominato l'hostname API da `api.pergolando.rdsign-app.it` (due livelli, nessun certificato valido) a `pergolando-api.rdsign-app.it` (un livello).
- **Verificato funzionante end-to-end** sul dominio pubblico reale `pergolando.rdsign-app.it`.

## Fase D — Registrazione con conferma email + recupero password (2026-09-20)

- **Backend**: flusso completo di verifica email via codice a 6 cifre (invio SMTP, TTL, tentativi massimi, cooldown reinvio) e recupero password con lo stesso meccanismo a codice. Nuovi endpoint: `verify-email`, `resend-verification`, `forgot-password`, `reset-password`. Nuova tabella `VerificationCode`, nuovo `MailService` (nodemailer, fallback a log se SMTP non configurato). Test unitari ed e2e aggiornati/aggiunti, tutti verdi. Mergiato in `main`/`develop` e pushato.
- **Frontend**: nuove pagine `/verify-email` (inserimento codice + reinvio) e `/forgot-password` (richiesta codice → nuova password). Login e registrazione aggiornati per instradare verso questi flussi. Mergiato in `main`/`develop` e pushato.
- **Verifica end-to-end**: testato in locale e poi sul NAS in produzione, inclusa la ricezione reale dell'email SMTP con codice.
- **Problemi affrontati durante il deploy NAS**:
  - Codice sul NAS non aggiornato (repo backend/frontend fermi a un commit precedente) → risolto con `git pull`.
  - Spazio esaurito su `/` (disco di sistema, 19G) durante la build Docker, nonostante il `data-root` di Docker fosse già stato spostato sul volume RAID grande in Fase C — causa: **containerd** ha una propria directory di stato (`/var/lib/containerd`) separata dal `data-root` di Docker, rimasta sul disco piccolo. Soluzione applicata: `docker builder prune -af` + `docker image prune -af` per liberare spazio subito; lo spostamento strutturale di containerd sul volume grande resta da pianificare (tocca tutti i container del NAS, non solo Pergolando).
  - Cancellazione di un account di test già registrato sul NAS tramite script diretto sul database (nessun endpoint di cancellazione account ancora previsto).

## Fase E — Studio: primo progetto reale "Flag" (Arquati) + upload logo/immagini (2026-09-20)

- Creato in Studio un progetto a partire dal PDF listino prezzi reale Arquati Privilege (prodotto **Flag**, tenda a caduta con guide, varianti 2/3/4 guide).
- Estratto e mappato manualmente `catalog/database.json` e `catalog/price_matrices.json` (prezzi per larghezza × sporgenza, 3 tabelle) a partire dal testo estratto dal PDF — validazione superata (schema + coerenza matrici + smoke test motore prezzi).
- **Nota aperta**: gli accessori a supplemento del listino (Trave Laterale, Angolare Laterale, Struttura Timpano, Guida aggiuntiva, ecc.) sono documentati nel bundle ma **non ancora prezzati dal motore di calcolo** — il motore gestisce solo il prezzo base della struttura. Da valutare se estendere lo schema/motore condiviso per supportarli.
- **Nota aperta**: `H_max_cm` e `passo_lama_cm` nel bundle Flag sono placeholder (il listino non li specifica per questo prodotto) — da confermare con l'ufficio tecnico Arquati prima di un uso in produzione.
- **Prodotto Skipper** (stesso catalogo Arquati, tenda a caduta verticale) non incluso in questo bundle — richiederà un bundle/tenant a sé, coerente con l'architettura "un prodotto per bundle".
- Aggiunta a Studio una nuova funzionalità: upload **logo** (sezione Branding) e upload **foto/rendering prodotto** (nuova sezione, con tag opzionali prodotto/sotto-modello/variante/colore). L'export del bundle ora copia automaticamente logo e immagini e genera `assets/manifest.json`. Verificato end-to-end con file di prova, poi ripulito.
- Modifiche non ancora committate su Git a fine sessione (`apps/studio/src/lib/storage.ts`, `apps/studio/src/lib/export-bundle.ts`, `apps/studio/src/components/DraftEditor.tsx`, nuove route `api/drafts/[draftId]/logo`, `api/drafts/[draftId]/assets`).

## Rimasto in sospeso

- Pubblicare Studio su un indirizzo del NAS (es. `pergolando.rdsign-app.it/studio`) — oggi Studio esiste solo come dev server locale, mai containerizzato né deployato.
- Committare le modifiche Studio (logo/immagini) elencate sopra.
- Decidere se estendere il motore di calcolo per prezzare gli accessori Flag a supplemento.
- Spostare la directory di stato di containerd sul volume RAID grande del NAS (intervento a livello di sistema, da pianificare con calma).
- Progetto API Google (Gemini/rendering fotorealistico) — menzionato ma esplicitamente rimandato, non ancora iniziato.

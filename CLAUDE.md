# Pergolando

Monorepo "Studio" del progetto Pergolando: cataloghi/prezzi/branding per l'app venditore
white-label. Contiene `apps/studio` (Next.js, questo repo) e workspace condivisi
(`pergolando-shared`). `pergolando-backend` e `pergolando-frontend` sono repo **separati**,
clonati come cartelle sorelle a questa (vedi `docker-compose.dev.yml` per i dettagli di
deploy locale, `deploy/nas/README.md` per il deploy reale sul NAS).

La cartella `3d/` contiene la pipeline di generazione 3D parametrica della pergola (Blender
headless) — vedi `3d/NOTES.md` per tutti i dettagli tecnici (convenzioni geometriche,
architettura, costanti di calibrazione, bug trovati) e `CHANGELOG.md` per la cronologia
per fase. **Se il lavoro in corso riguarda il modello 3D/Blender, leggi `3d/NOTES.md` prima
di qualunque altra cosa** — è tenuto aggiornato apposta per riprendere una sessione lunga
senza perdere contesto.

## Stato attuale (aggiornato 2026-09-27)

Lavoro in corso: riscrittura di `3d/generate_flag.py` con la nuova **architettura a perno
fisso** (Guida/Telo/Frangivento/Tettuccio/Supporto ruotano rigidamente insieme attorno a un
perno fisico reale, invece del vecchio sistema a offset per-pezzo). Dettagli completi,
formule e bug risolti: sezione "Architettura a perno fisso" in `3d/NOTES.md`.

**Verificato ieri sera**: riproduzione esatta a dimensioni di riferimento; render coerente
su più combinazioni L/SP/H/Δh (inclusi test dal vivo con Davide in Blender); Tettuccio
(nervature) simmetrico e senza buchi a L=300 e L=500.

**Prossimo passo esplicito**: Davide ha detto *"domani continuiamo con i primi rendering"* —
quindi si parte da lì, non da zero. Prima di procedere, controllare la sezione "Da fare,
prossima sessione" in fondo a `3d/NOTES.md` (in particolare: `Tettuccio_Lato_Dx/Sx` che
Davide stava cancellando a mano, e `setup_camera_from_pnp` da riverificare dopo il cambio
di convenzione degli assi).

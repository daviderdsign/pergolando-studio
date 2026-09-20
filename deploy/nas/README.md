# Deploy su NAS — un tenant di App Venditore

Guida passo-passo per mettere online un tenant (venditore) su un sottodominio dedicato, usando
una cartella dedicata sul NAS. **Verificata end-to-end il 2026-09-20** (login → wizard → catalogo
caricato) su `pergolando.rdsign-app.it`, dopo aver risolto una serie di problemi reali — vedi la
sezione **Problemi già affrontati** in fondo prima di aprire un ticket con te stesso alle 2 di notte.

## 0. Prerequisiti sul NAS

- Docker + Docker Compose (v2, il comando `docker compose`, non `docker-compose`).
- Accesso SSH o terminale al NAS.
- `git` disponibile (per clonare i repo — pubblici, nessun token necessario).
- **Spazio libero vero** sul filesystem dove vive `/var/lib/docker` (o la cartella dati di Docker
  che hai configurato). Una build di NestJS + Next.js con toolchain nativa richiede diversi GB
  temporanei. Se il disco di sistema del NAS è piccolo (es. 19G), sposta la cartella dati di
  Docker su un volume grande **prima** di iniziare — vedi "Spazio disco" più sotto.
- Quel volume deve essere un **filesystem Linux vero** (ext4/btrfs/xfs), non NTFS/exFAT montato
  via FUSE — altrimenti Docker non può gestire i permessi Unix dei volumi (i container con dati
  che richiedono ownership specifico, tipo Postgres, si rifiutano di partire). Controlla con
  `df -T <punto-di-mount>`: se il tipo è `fuseblk`, non va bene.

## 1. Struttura della cartella

Nella cartella dedicata sul NAS, clona i due repo applicativi e copia questi file di deploy:

```bash
cd /path/alla/cartella/Pergolando

git clone https://github.com/daviderdsign/pergolando-backend.git
git clone https://github.com/daviderdsign/pergolando-frontend.git
```

Poi copia in questa stessa cartella i file da `deploy/nas/` di questo repo
(`docker-compose.yml`, `backend.env.example`, `.env.example`) — sono quelli che stai leggendo ora.
**Copiali di nuovo se questo repo cambia** — non c'è `git pull` automatico per questi file, vanno
ricopiati a mano ogni volta (è quello che ci ha fatto perdere tempo la prima volta: un
`docker-compose.yml` sul NAS rimasto indietro rispetto a correzioni fatte qui).

Risultato atteso:

```
Pergolando/
├── docker-compose.yml
├── backend.env.example  -> copialo in backend.env e compilalo
├── .env.example          -> copialo in .env e compilalo (TUNNEL_TOKEN)
├── bundle/                (lo crei al passo 2)
├── pergolando-backend/
└── pergolando-frontend/
```

## 2. Il bundle del tenant

Serve un bundle esportato da Studio (manifest.json, catalog/, branding/) — per il primo test puoi
usare quello di prova già generato (Brera demo), altrimenti quello del cliente reale una volta
pronto in Studio.

Copia il **contenuto** della cartella versione del bundle (non la cartella del tenant intera, e
non l'intero albero `storage/bundles/`) dentro `Pergolando/bundle/` sul NAS:

```bash
scp -r apps/studio/storage/bundles/brera-demo/0.1.0/* utente@nas:/path/alla/cartella/Pergolando/bundle/
```

Verifica che dentro `bundle/` ci siano `manifest.json`, `catalog/`, `branding/` **direttamente**,
non annidati in un'altra sottocartella:

```bash
find bundle -maxdepth 1
```

## 3. File d'ambiente

```bash
cp backend.env.example backend.env
cp .env.example .env
```

`backend.env` è già compilato per il dominio scelto — non serve modificarlo a meno che tu non usi
un altro dominio.

`.env` invece va compilato con `TUNNEL_TOKEN` dopo il passo 4.

## 4. Cloudflare Tunnel

L'interfaccia di Cloudflare è cambiata più volte negli ultimi mesi — se questi nomi non
corrispondono esattamente a quello che vedi, cerca "Tunnels" nella barra di ricerca del
dashboard, non fidarti ciecamente di questi screenshot testuali.

1. Dashboard Cloudflare → **Networking → Tunnels → Create Tunnel** → dai un nome al tunnel.
2. Nella schermata di setup dell'ambiente, scegli **Docker** come connettore — Cloudflare mostra
   un comando `docker run` con un token lungo dopo `--token`. Copia solo quel token.
3. Incolla il token in `.env`:
   ```
   TUNNEL_TOKEN=eyJ...
   ```
4. Apri il tuo tunnel (Networking → Tunnels → seleziona il tunnel) e vai sul tab **Routes**.
   Seleziona **Add route → Published application** e aggiungi **due route separate** (due
   sottodomini sullo stesso tunnel):

   | Hostname | Service |
   | --- | --- |
   | `<tenant>.tuodominio.it` | `http://frontend:3000` |
   | `<tenant>-api.tuodominio.it` | `http://backend:3001` |

   **Importante — usa un sottodominio a un solo livello per l'API** (`<tenant>-api.tuodominio.it`,
   non `api.<tenant>.tuodominio.it`): il certificato SSL universale di Cloudflare copre solo
   `*.tuodominio.it` (un livello), non due livelli annidati. Un hostname come
   `api.pergolando.rdsign-app.it` non ha un certificato valido e fallisce con
   `ERR_SSL_VERSION_OR_CIPHER_MISMATCH` — non si risolve aspettando, serve
   "Advanced Certificate Manager" (a pagamento) oppure, più semplice, evitare l'annidamento.

   `backend`/`frontend` sono i nomi dei servizi Docker Compose — funzionano come hostname perché
   `cloudflared` è nella stessa rete Docker.
5. Ogni route creata così genera automaticamente il record DNS corrispondente, di **tipo
   "Tunnel"** (non un CNAME manuale) — se per qualche motivo il DNS non si crea da solo, non
   aggiungere un CNAME a mano puntato a `<tunnel-uuid>.cfargotunnel.com`: cancella e ricrea la
   route dal tab Routes del tunnel, così Cloudflare genera il record giusto.

Con due sottodomini invece di un percorso condiviso, frontend e backend sono tecnicamente due
origin diversi per il browser: è lo stesso meccanismo CORS già usato e verificato in sviluppo
locale (lì porte diverse, qui sottodomini diversi) — `CORS_ORIGIN` in `backend.env` e
`NEXT_PUBLIC_API_URL` nel build del frontend sono già impostati di conseguenza in questi file
(aggiorna `NEXT_PUBLIC_API_URL` in `docker-compose.yml` se cambi dominio).

## 5. Avvio

```bash
docker compose up --build -d
docker compose logs -f
```

Cose da controllare nei log:

- `backend`: deve loggare `"Loaded bundle for tenant ..."` e `"Nest application successfully
  started"`, **senza** ripetersi in loop. Se riparte in continuazione, guarda l'errore esatto —
  vedi "Problemi già affrontati" sotto, li abbiamo praticamente visti tutti.
- `cloudflared`: deve loggare connessioni stabilite (`Registered tunnel connection`) e il blocco
  `SUMMARY: Environment is healthy`.

## 6. Verifica

Da un browser qualsiasi (anche da telefono, fuori dalla rete del NAS):

```
https://<tenant>.tuodominio.it
```

Deve apparire la pagina di login. Registra un venditore, accedi, verifica che il wizard carichi
il catalogo del bundle. Se cambi `NEXT_PUBLIC_API_URL` dopo un primo tentativo fallito, ricorda
che è "cotto" nel bundle JS in fase di build — serve `docker compose up --build -d frontend`, non
solo un restart, e conviene forzare un hard-reload nel browser (la vecchia versione può restare
in cache).

## 7. Sullo smartphone

Nessun passo aggiuntivo: essendo dietro Cloudflare Tunnel con dominio e HTTPS veri, è un normale
sito web. Il layout attuale non ha ancora breakpoint specifici per mobile stretti: se la prima
verifica su telefono mostra problemi di layout (in particolare `.field-grid` a due colonne nel
wizard), è la prossima cosa da sistemare, non un bug bloccante.

## Aggiornare il tenant dopo un cambio

```bash
cd pergolando-backend && git pull && cd ..
cd pergolando-frontend && git pull && cd ..
docker compose up --build -d
```

## Un secondo tenant

Copia l'intera cartella in una nuova cartella dedicata, cambia il bundle in `bundle/`, il dominio
in `backend.env`/`NEXT_PUBLIC_API_URL` nel `docker-compose.yml`, crea un secondo tunnel Cloudflare
con un secondo sottodominio (schema `<tenant>.tuodominio.it` / `<tenant>-api.tuodominio.it`), e
usa `docker compose -p <tenant> up -d` (il flag `-p` dà un nome di progetto diverso così i
container e i volumi non si mescolano con gli altri tenant).

## Problemi già affrontati

Tutti reali, incontrati nel primo deploy — se ricapitano su un secondo tenant o un altro NAS, la
causa è quasi certamente la stessa:

- **`ERR_PNPM_GIT_DEP_PREPARE_NOT_ALLOWED` in fase di build**: pnpm blocca per default gli script
  di build di dipendenze git come `@pergolando/shared`. Già risolto nei `pnpm-workspace.yaml` di
  entrambi i repo (`allowBuilds`) — se ricompare dopo un aggiornamento della dipendenza condivisa,
  il messaggio d'errore di pnpm indica la chiave esatta da aggiungere.
- **`better-sqlite3` fallisce con "Could not find any Python installation"**: l'immagine
  `node:24-slim` non ha Python/compilatore C++. Già risolto nel `Dockerfile` del backend
  (`python3 make g++`).
- **`No space left on device` durante la build**: il disco dove vive `/var/lib/docker` è troppo
  pieno/piccolo. Vedi "Spazio disco" sotto.
- **Container `backend` in crash-loop dopo un avvio riuscito**, con
  `ERR_PNPM_IGNORED_BUILDS` nei log: il comando di avvio usava `pnpm exec prisma migrate deploy`,
  che ri-verifica le dipendenze ad ogni riavvio e non trova `pnpm-lock.yaml`/`pnpm-workspace.yaml`
  nell'immagine finale. Già corretto nel `docker-compose.yml`: si chiama
  `node_modules/.bin/prisma` direttamente.
- **`Error: ENOENT ... /app/bundle/manifest.json`**: il bundle non è nella cartella giusta —
  vedi passo 2, il contenuto della versione va copiato direttamente in `bundle/`, non annidato.
- **Pagina irraggiungibile con `ERR_NAME_NOT_RESOLVED`, poi `Error 1033`**: il DNS non si era
  creato aggiungendo la route (o si era creato come CNAME manuale invece che record "Tunnel").
  Soluzione: cancella la route e ricreala dal tab Routes del tunnel (passo 4, punto 5).
- **`ERR_SSL_VERSION_OR_CIPHER_MISMATCH` solo sul sottodominio API**: hostname a due livelli
  (`api.<tenant>.tuodominio.it`) non coperto dal certificato wildcard. Usa un sottodominio a un
  livello (`<tenant>-api.tuodominio.it`) — vedi passo 4.
- **Il frontend continua a chiamare il dominio sbagliato dopo aver corretto
  `NEXT_PUBLIC_API_URL`**: è "cotto" nel bundle JS a build time, non un env var runtime — serve
  ricostruire (`docker compose up --build -d frontend`) e spesso anche un hard-reload del browser
  per scartare la versione in cache.

### Spazio disco

Se `/var/lib/docker` è su un disco piccolo (es. il disco di sistema), spostalo su un volume più
grande **prima** di fare build ripetute:

```bash
systemctl stop docker
mkdir -p /percorso/volume-grande/docker-data
rsync -aHAX --info=progress2 /var/lib/docker/ /percorso/volume-grande/docker-data/
cat > /etc/docker/daemon.json <<'EOF'
{ "data-root": "/percorso/volume-grande/docker-data" }
EOF
systemctl start docker
```

Verifica con `docker info | grep "Docker Root Dir"` e controlla che **tutti** i container
preesistenti (non solo Pergolando) siano ancora `Up` con `docker ps -a` prima di cancellare la
vecchia copia in `/var/lib/docker`. Se un container con volumi (es. Postgres) va in crash-loop con
"wrong ownership" dopo lo spostamento, il volume target non supporta i permessi Unix reali
(controlla con `stat` su un file del volume — se il proprietario non cambia dopo un `chown`
esplicito, il filesystem è il problema, non i permessi) — sposta invece su un volume ext4/btrfs
vero.

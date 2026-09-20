# Deploy su NAS — un tenant di App Venditore

Guida passo-passo per mettere online il primo tenant (venditore) su
`pergolando.rdsign-app.it`, usando la cartella "Pergolando" già creata sul NAS.

Questi file **non testati end-to-end** su hardware reale in questa sessione
(Docker non era disponibile nell'ambiente in cui sono stati scritti) — la
prima esecuzione va seguita con attenzione, non lanciata alla cieca.

## 0. Prerequisiti sul NAS

- Docker + Docker Compose (v2, il comando `docker compose`, non `docker-compose`).
- Accesso SSH o terminale al NAS.
- `git` disponibile (per clonare i repo — pubblici, nessun token necessario).

## 1. Struttura della cartella

Nella cartella "Pergolando" già creata sul NAS, entra e clona i due repo
applicativi e copia questi file di deploy:

```bash
cd /path/alla/cartella/Pergolando

git clone https://github.com/daviderdsign/pergolando-backend.git
git clone https://github.com/daviderdsign/pergolando-frontend.git
```

Poi copia in questa stessa cartella i file da `deploy/nas/` di questo repo
(`docker-compose.yml`, `backend.env.example`, `.env.example`) — sono quelli
che stai leggendo ora.

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

Serve un bundle esportato da Studio (manifest.json, catalog/, branding/) —
per il primo test puoi usare quello di prova già generato (Brera demo),
altrimenti quello del cliente reale una volta pronto in Studio.

Copia la cartella del bundle esportato (es. da
`apps/studio/storage/bundles/<tenant>/<versione>/` sul tuo PC) dentro
`Pergolando/bundle/` sul NAS — via `scp`, condivisione file del NAS, o
`rsync`:

```bash
scp -r apps/studio/storage/bundles/brera-demo/0.1.0/* utente@nas:/path/alla/cartella/Pergolando/bundle/
```

## 3. File d'ambiente

```bash
cp backend.env.example backend.env
cp .env.example .env
```

`backend.env` è già compilato per `pergolando.rdsign-app.it` — non serve
modificarlo a meno che tu non usi un altro dominio.

`.env` invece va compilato con `TUNNEL_TOKEN` dopo il passo 4.

## 4. Cloudflare Tunnel

L'interfaccia di Cloudflare è cambiata più volte negli ultimi mesi — se questi
nomi non corrispondono esattamente a quello che vedi, cerca "Tunnels" nella
barra di ricerca del dashboard, non fidarti ciecamente di questi screenshot
testuali.

1. Dashboard Cloudflare → **Networking → Tunnels → Create Tunnel** → nome
   `pergolando`.
2. Nella schermata di setup dell'ambiente, scegli **Docker** come
   connettore — Cloudflare mostra un comando `docker run` con un token
   lungo dopo `--token`. Copia solo quel token.
3. Incolla il token in `.env`:
   ```
   TUNNEL_TOKEN=eyJ...
   ```
4. Apri il tuo tunnel (Networking → Tunnels → seleziona `pergolando`) e
   vai sul tab **Routes**. Seleziona **Add route → Published application**
   e aggiungi **due route separate** (due sottodomini sullo stesso tunnel,
   non due regole sullo stesso hostname — più semplice e più affidabile
   del routing per-percorso, che nella UI attuale non è chiaramente
   esposto):

   | Hostname | Service |
   | --- | --- |
   | `pergolando.rdsign-app.it` | `http://frontend:3000` |
   | `api.pergolando.rdsign-app.it` | `http://backend:3001` |

   `backend`/`frontend` sono i nomi dei servizi Docker Compose — funzionano
   come hostname perché `cloudflared` è nella stessa rete Docker.
5. Ogni route creata così genera automaticamente anche il record DNS
   corrispondente sotto `rdsign-app.it` — non serve aggiungerlo a mano.

Con due sottodomini invece di un percorso condiviso, frontend e backend sono
tecnicamente due origin diversi per il browser: è lo stesso meccanismo CORS
già usato e verificato in sviluppo locale (lì porte diverse, qui sottodomini
diversi) — `CORS_ORIGIN` in `backend.env` e `NEXT_PUBLIC_API_URL` nel build
del frontend sono già impostati di conseguenza in questi file.

## 5. Avvio

```bash
docker compose up --build -d
docker compose logs -f
```

Cose da controllare nei log:

- `backend`: deve loggare `"Loaded bundle for tenant ..."` e
  `"Nest application successfully started"`. Se si ferma prima, quasi
  sempre è `BUNDLE_PATH` vuoto/sbagliato o il bundle non valido.
- `cloudflared`: deve loggare connessioni stabilite (`Registered tunnel
  connection`), senza errori di autenticazione sul token.

## 6. Verifica

Dal NAS stesso:

```bash
curl http://localhost:3001/api/v1/health
```

Da un browser qualsiasi (anche da telefono, fuori dalla rete del NAS):

```
https://pergolando.rdsign-app.it
```

Deve apparire la pagina di login. Registra un venditore, accedi, verifica
che il wizard carichi il catalogo del bundle.

## 7. Sullo smartphone

Nessun passo aggiuntivo: essendo dietro Cloudflare Tunnel con dominio e
HTTPS veri, è un normale sito web — si apre da Safari/Chrome sul telefono
come qualsiasi altra pagina. Il layout attuale non ha ancora breakpoint
specifici per mobile stretti: se la prima verifica su telefono mostra
problemi di layout (in particolare `.field-grid` a due colonne nel
wizard), è la prossima cosa da sistemare, non un bug bloccante.

## Aggiornare il tenant dopo un cambio

```bash
cd pergolando-backend && git pull && cd ..
cd pergolando-frontend && git pull && cd ..
docker compose up --build -d
```

## Un secondo tenant

Copia l'intera cartella `Pergolando/` in una nuova cartella (es.
`Pergolando-clienteB/`), cambia il bundle in `bundle/`, il dominio in
`backend.env`/`NEXT_PUBLIC_API_URL` nel `docker-compose.yml`, crea un
secondo tunnel Cloudflare con un secondo subdominio, e usa
`docker compose -p pergolando-clienteb up -d` (il flag `-p` dà un nome di
progetto diverso così i container e i volumi non si mescolano con il primo
tenant).

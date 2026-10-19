# Demo 3 - estrazione automatica dei listini

Carica PDF con testo selezionabile, CSV e immagini. Premi Estrai listino e foto. Controlla ogni tabella confrontandola con la pagina originale: modello/variante, unità, larghezza/profondità, prezzi e condizioni. Conferma e salva. Il preventivo usa solo tabelle confermate, con scelta esplicita fra misure esatte e fascia superiore. Non estrapola prezzi e conserva come non disponibili le celle vuote. I dati delle altre due demo non vengono cambiati.

I documenti, il testo, le foto e le tabelle restano in IndexedDB su quel browser/dispositivo. Cambiando browser o dispositivo non sono disponibili automaticamente. Esportazione JSON disponibile. Nessuna pubblicazione del catalogo aziendale e nessun collegamento a magazzino/ordini implementato. Il preventivo PDF è scaricabile; invio email tramite backend esistente, dopo accesso e con SMTP configurato.

Limiti: OCR delle scansioni non ancora implementato; XLS/XLSX da esportare in CSV. Le regole su motori, IVA, montaggio, colori, numero moduli e supplementi non vengono dedotte automaticamente dal testo: vanno verificate e inserite esplicitamente. Il riconoscimento geometrico produce candidate, non garantisce che ogni tabella di un catalogo sia stata rilevata. Limite 250 pagine per analisi; foto estratte fino a 100/25MB, 12 per pagina.

Il menu delle Demo 1/2 e delle sezioni Demo 3 contiene Home - scegli una demo in un gruppo separato.

Verifiche: compilazione Next.js; parser numeri europei, celle mancanti, inversione assi, mm/cm e prezzi fuori tabella; tutte le 416 celle della matrice Vision confrontate con database verificato; catalogo Arquati 40 pagine: 5 tabelle candidate dopo filtraggio dei falsi positivi. Browser: estrazione Vision, 13 immagini, conferma/salvataggio, preventivo L300/P310 e PDF A4 orizzontale di 4 pagine.

## Aggiornare il NAS

Il pacchetto include anche le modifiche precedenti alle tre demo, prospettiva e navigazione. Copiarlo nella cartella principale del progetto NAS. Fare prima un backup dei sorgenti modificati. Non contiene .env, backend.env o database e non elimina account.

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker run --rm -v "$PWD":/work -w /work python:3.12-alpine python -m zipfile -e Pergolando-ChatGPT-listini-automatici-2026-10-08.zip .
docker compose up -d --build backend frontend
```

Aprire https://pergolando.rdsign-app.it/demo/catalogo e ricaricare la pagina. La configurazione del backend continua a stare in backend.env; .env nella radice contiene il token del tunnel. PDF.js viene installato dalle dipendenze e il suo worker viene copiato automaticamente durante pnpm run build, senza CDN o API key.

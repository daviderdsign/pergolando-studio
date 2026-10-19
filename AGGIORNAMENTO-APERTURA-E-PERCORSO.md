# Apertura pratica, ordine grafico e percorso della commessa

## Interfaccia

- Uniformati spazi di campi e pulsanti (16 px), separazioni fra riquadri (24 px), margini interni e larghezze.
- Intestazione allineata alla colonna dei contenuti, lingua con stile coerente fra pagine, caselle di conferma sulla stessa riga del testo.
- Percorso fisso in basso, escluso dalla configurazione iniziale e dall’accesso pubblico: 1 Pratica, 2 Prodotti, 3 Offerta, 4 Trattativa, 5 Ordini, 6 Posa, 7 Consegna, 8 Assistenza. Su telefono sono visibili i numeri e il nome della fase corrente; su desktop anche le etichette.
- Punti verdi solo sulla base dei dati salvati. Linea verde fra punti adiacenti completati; anello sulla fase visualizzata. Si può tornare alle schermate disponibili. Ordini, posa e portale assistenza mostrano «in preparazione», senza simulare operazioni inesistenti.
- Avanzamento ricalcolato sul server, senza caricare immagini o interi preventivi nella barra. Registrazione pratica, prodotti attivi, revisione offerta, conferma rivenditore e consegna sono i riferimenti attuali. Consegna usa lo stato già presente nel conto economico, non sostituisce il futuro modulo collaudo.

## Punto 2 — Apertura della pratica

Nuova pratica → /pratiche/nuova. Campi: nome commessa, eventuale azienda cliente, referente, email, telefono, indirizzo cliente, indirizzo intervento distinto, richiesta/vincoli/misure preliminari in nota. Salva e passa alla scelta dei prodotti.

Foto e PDF del sopralluogo possono essere aggiunti alla creazione e in seguito dalla scheda /pratiche/:id/apertura. PDF, PNG, JPEG: fino a 8 MB ciascuno, 50 file o 50 MB complessivi per pratica. Download autenticato, controllo del formato, deduplicazione e rimozione con conferma. Non è un archivio antivirus; i file non vengono eseguiti dal server.

Se un caricamento fallisce, la pratica resta disponibile e si può riprovare senza duplicarla. I dati si modificano dalla scheda; lo storico delle modifiche è conservato nelle attività. I precedenti preventivi restano immutati. Gli allegati e le note di sopralluogo sono interni e non sono inclusi automaticamente nell’offerta pubblica. Nome commessa, azienda cliente e luogo dell’intervento entrano nelle nuove revisioni PDF.

Anche il vecchio ingresso /progetto senza pratica conduce alla nuova apertura. Con un ID pratica il configuratore continua a funzionare normalmente, compresi gli elementi già salvati. Esistenti dati e cataloghi restano conservati.

## Installazione NAS

Backup del database/volume. Copiare i contenuti di Aggiornamento nella directory del progetto, conservando percorsi ed evitando .env, backend.env e volumi.

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build backend frontend && docker compose restart gateway
docker compose ps
```

Nuova migrazione additiva 20261015230000_case_opening (campi pratica, chiave di creazione e tabella allegati), applicata all’avvio backend. Il pacchetto include anche la precedente prima configurazione. Non usare migrate reset.

Aprire https://pergolando.rdsign-app.it/pratiche e scegliere Nuova pratica. Se richiesto, completare prima le impostazioni del rivenditore.

## Verifiche

Build backend/frontend e TypeScript. Tredici test backend su database temporanei, comprese privacy degli allegati, duplicati, accessi, revisioni e migrazioni. Chromium: apertura con interruzione upload/recupero, ritorno ai punti, progresso reale, sfondo verde effettivo, allineamenti riquadri e nessuna eccedenza orizzontale a 320/390 px. Controllo anche su desktop e PDF con commessa/indirizzo intervento. Configurazione iniziale e percorso preventivo verificati con API simulate. Nessun invio email reale o aggiornamento automatico del NAS.

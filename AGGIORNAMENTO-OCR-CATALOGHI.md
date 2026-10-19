# Lettura OCR dei cataloghi

Il nuovo OCR legge le pagine scansionate dei PDF nel browser, in italiano e inglese. Non richiede servizi Blender/GeoCalib o programmi aggiuntivi sul NAS.

## Uso

Aprire Cataloghi e listini → Importa un listino. La modalità predefinita applica OCR alle pagine con poco testo selezionabile. Per un PDF misto o con solo intestazioni selezionabili scegliere «Tutte le pagine». Ripetere l'estrazione del documento già caricato: le vecchie analisi non vengono rielaborate da sole.

Il primo utilizzo scarica i modelli linguistici dal CDN Tesseract (serve connessione). Le pagine sono elaborate sul dispositivo; su smartphone mantenere aperta la pagina. Cataloghi molto lunghi possono richiedere tempo. Il limite attuale è 250 pagine per analisi.

L'OCR può sbagliare cifre, decimali o celle: confrontare le tabelle con l'anteprima, controllare le condizioni e svolgere i test del catalogo prima dell'approvazione. La confidenza OCR non certifica i prezzi. Le foto singole restano importate come immagini, senza OCR.

## NAS

Copiare il contenuto di Aggiornamento nella directory del progetto mantenendo i percorsi. Conservare .env, backend.env e volumi.

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build frontend
docker compose restart gateway
```

Il pacchetto è cumulativo: se non è ancora stato installato l'aggiornamento del percorso unico, ricostruire anche il backend secondo le istruzioni precedenti. Nessuna nuova migrazione per questo OCR.

## Verifiche

Build e TypeScript; prova Chromium con PDF contenente solo immagine, prezzi e dimensioni della matrice verificati. Resta il collaudo sul catalogo reale e sul telefono.

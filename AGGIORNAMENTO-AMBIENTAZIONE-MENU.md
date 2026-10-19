# Aggiornamento ambientazione e menu fasi — 7 ottobre 2026

## Risultato
- Menu compatto «Vai a una fase» nell'intestazione, con accesso alle fasi disponibili.
- Tornare indietro conserva il progetto. Cambiare misure, modello o accessori invalida preventivo, disegni e immagine; il nuovo calcolo usa i dati aggiornati.
- Analisi di sei linee (due per fronte, verticali e profondità). Ciascuna può essere corretta con lente 4× o rimossa.
- Sagoma con dimensioni effettive dal preventivo. X, sollevamento e Z si spostano separatamente; la maniglia posteriore permette una rotazione da -25° a +25°.
- Zero fisso sulla foto. Spostamento e rotazione non cambiano il preventivo.
- Scala stimata se non si fornisce una misura. Per misurare una cornice in alto occorre indicare anche la sua altezza dal pavimento. Una misura non valida produce un avviso e usa la stima.
- Focale e centro ottico vengono trasmessi automaticamente fino a Blender; nessun pulsante di esportazione viene mostrato al venditore.

## Installazione sul NAS
Copia lo ZIP nella cartella /home/davideromeo/Pergolando-chatgpt con WinSCP. Non sostituire .env: lo ZIP non contiene password, token, database o configurazioni personali.

Da PuTTY:

```sh
cd /home/davideromeo/Pergolando-chatgpt
tar -czf "backup-ambientazione-$(date +%Y%m%d-%H%M%S).tar.gz" pergolando-frontend/src/app/prova pergolando-frontend/src/lib/camera-geometry.ts pergolando-backend/src/perspective pergolando-backend/src/scene3d
```

Se unzip è disponibile:

```sh
unzip -o Pergolando-ChatGPT-ambientazione-menu-2026-10-07.zip
```

Altrimenti, usa il container Python ufficiale:

```sh
docker run --rm -v "$PWD":/work -w /work python:3.12-alpine python -m zipfile -e Pergolando-ChatGPT-ambientazione-menu-2026-10-07.zip .
```

Poi:

```sh
docker compose up -d --build backend frontend
docker compose ps
```

Il servizio prospettiva sul PC è già stato aggiornato e riavviato. Le copie Python e Blender nello ZIP servono anche a mantenere coerente la cartella NAS per il successivo trasferimento del rendering. Se stai invece eseguendo GeoCalib su un altro host, aggiorna e riavvia quel servizio con questi stessi file. Non cambiare l'indirizzo pubblico o il tunnel Cloudflare.

## Prova finale
Apri https://pergolando.rdsign-app.it/prova e aggiorna la pagina dopo il deployment.
1. Compila il progetto e calcola il preventivo.
2. Carica la foto: controlla sei linee e sagoma. Se manca una direzione, segna entrambi gli estremi delle linee mancanti.
3. Eventualmente aggiungi la misura di uno dei quattro bordi orizzontali; lascia altezza 0 solo se è a terra.
4. Conferma, sposta sui tre assi, ruota e crea l'immagine.
5. Dal menu torna a Misure e accessori. Cambia una dimensione, calcola nuovamente e verifica la nuova sagoma e il nuovo rendering.

## Verifiche eseguite sul PC
- Compilazione frontend di produzione e backend completate.
- Tre test di integrazione: scala metrica, invarianza all'ordine degli estremi, sei bordi automatici distinti sulla foto di prova.
- API GeoCalib reali: sei linee riconosciute in 3,61 s sul PC e camera completa restituita.
- Rendering Eevee riuscito con Brera e Flag usando i nuovi intrinseci.
- Prova browser dei controlli, inclusa traslazione verticale indipendente.

La nuova pagina di prova locale /ambientazione-test e le foto di verifica non sono incluse in questo aggiornamento pubblico.

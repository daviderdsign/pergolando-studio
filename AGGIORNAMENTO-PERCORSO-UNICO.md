# Percorso unico Pergolando — 15 ottobre 2026

## Cambiamento principale
Eliminata la scelta delle tre demo. Dopo l’accesso si apre Pratiche clienti, il centro del lavoro del rivenditore. Da qui si creano nuove pratiche o si riprendono quelle esistenti.

Percorso commerciale attuale:

Dati cliente → Catalogo e modello → Misure/accessori → Preventivo → Ambientazione facoltativa → Offerta unica/revisioni/PDF → Email e pagina cliente → Accettazione con codice email → Verifica tecnica del rivenditore.

Cataloghi e listini sono un’area del medesimo ambiente: importazione → correzione → prove → approvazione della versione → utilizzo nelle pratiche. Non sono più una terza demo.

Il conto economico, le note, i richiami e le comunicazioni restano collegati alla stessa pratica. Incassi verificati, ordini ai produttori, consegne, posa e assistenza completi rimangono i blocchi successivi dello schema generale: non sono stati simulati con pulsanti non funzionanti.

## Comportamenti
- La nuova pratica viene creata sul server dopo il primo passaggio dei dati cliente. Le configurazioni prodotto vengono salvate al preventivo o proseguendo all’offerta.
- Un solo percorso per prodotti preconfigurati e listini approvati, con moduli di configurazione appropriati al prodotto. Nessuna scelta tra versione completa e versione senza 3D.
- L’ambientazione è facoltativa e appare solo per le configurazioni che dispongono del modello. I servizi di rendering non bloccano il passaggio dal preventivo all’offerta.
- «Continua all’offerta unica» salva la riga; se disponibili salva anche ambientazione e viste tecniche. Se il salvataggio delle immagini fallisce, non abbandona la schermata con un errore nascosto.
- Si possono salvare le viste tecniche già pronte anche senza aver fatto l’ambientazione. Non si attende indefinitamente Blender per aprire l’offerta; le viste non ancora disponibili non vengono inventate o incluse come definitive.
- PDF, invio email, accettazione e comunicazioni fanno capo all’offerta unica della pratica. Eliminata dal percorso normale la vecchia consegna di un PDF isolato per singolo prodotto.
- Nel catalogo importato non compare più il comando per generare/inviare un preventivo da una bozza locale non approvata, né il selettore foto che non archiviava la foto nell’offerta unica. Le foto estratte restano consultabili nell’area catalogo; il loro impiego automatico nel PDF unico è ancora da completare.
- Menu a tendina sul telefono, logo con O barrate e selettore IT/EN conservati. Le nuove aree non ancora tradotte interamente restano da completare nel piano generale.

## Indirizzi e compatibilità
- Ingresso dopo login: /pratiche.
- Nuovo progetto/configurazione: /progetto.
- Archivio listini: /cataloghi.
- Importazione: /cataloghi/importa.
- Configurazione da listino: /cataloghi/preventivo?catalog=ID.
- Vecchio /demo porta alle pratiche; /prova e /wizard portano al progetto unico; /demo/catalogo e /demo/catalogo/preventivo portano alle nuove aree cataloghi.
- I reindirizzamenti conservano i parametri della pratica/prodotto/catalogo. I vecchi parametri demo non selezionano più flussi diversi. Le bozze locali esistenti conservano la vecchia chiave IndexedDB per non perdere documenti già caricati.

## Installazione sul NAS
Fare backup del database/volume. Copiare Aggiornamento nella cartella del progetto, mantenendo i percorsi e senza sostituire .env, backend.env o volumi.

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build backend frontend
docker compose restart gateway
```

Questo blocco cambia il frontend e la navigazione, senza nuove migrazioni. Il pacchetto cumulativo conserva quelle dei blocchi precedenti: migrate deploy applicherà quelle mancanti. Non usare migrate reset.

## Verifiche
TypeScript e build di produzione frontend superati. Test automatico Chromium con viewport mobile e API simulate: ingresso senza demo, creazione della pratica una sola volta, preventivo anche con servizi rendering indisponibili, passaggio all’offerta unica, riga da catalogo approvato nella stessa pratica e compatibilità dei vecchi link. Verificati i ritorni dopo login e il rifiuto di destinazioni esterne. Home mobile renderizzata e controllata visivamente; anteprima in output/workflow/home-unificata-mobile.png.

Nessuna email o rendering reale avviato nel test. Il collaudo effettivo sul NAS resta da eseguire dopo la copia. Per il collaudo si parte da /pratiche, senza scegliere una demo.

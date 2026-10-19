# Revisione riservata al cliente e conferma del rivenditore

Nota successiva: AGGIORNAMENTO-VERIFICA-EMAIL-CLIENTE.md aggiunge il codice monouso per le nuove accettazioni e supera il limite OTP descritto sotto. Le accettazioni precedenti restano storiche.

## Aggiornamento sul NAS
Salvare prima una copia del database/volume. Copiare il contenuto di Aggiornamento mantenendo i percorsi, senza sostituire backend.env, .env o i volumi.

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build backend frontend
docker compose restart gateway
```

La migrazione 20261014230000_proposal_invitations aggiunge i collegamenti riservati e i riferimenti all’offerta accettata/confermata nella pratica. Il backend la applica con migrate deploy; non usare migrate reset.

## Come provarlo
1. Pratiche → Offerta unica, revisioni e PDF → salvare una revisione con validità futura e condizioni complete.
2. Nella revisione premere «Crea collegamento cliente». Copiare il collegamento completo e aprirlo sul telefono, anche senza accesso venditore.
3. La pagina mostra la revisione congelata: prodotti, importi, condizioni, immagini disponibili e PDF scaricabile. Le modifiche successive alla pratica non cambiano questa revisione.
4. Il cliente indica nome ed email, legge la dichiarazione e preme «Accetta e richiedi conferma». Se il preventivo ha già un’email, viene richiesta la stessa.
5. Il rivenditore preme «Aggiorna stato cliente» nella revisione oppure ricarica la pagina. La pratica indica «Accettazione da verificare».
6. Dopo il controllo tecnico può confermare o rifiutare. Il rifiuto richiede una motivazione, visibile anche al cliente, e consente di preparare una nuova proposta. La conferma è conservata e la pratica viene indicata come confermata.

## Gestione dei collegamenti
- Ogni collegamento contiene un segreto casuale nel frammento URL, dopo #. Non cancellare quella parte quando lo si copia. Il database conserva solo l’hash del segreto; il collegamento completo viene mostrato alla creazione.
- Durata di accesso 30 giorni; l’accettazione è comunque bloccata dopo la data di validità della revisione. Le date di scadenza del preventivo sono considerate fino a fine giornata UTC.
- Una nuova pubblicazione revoca i collegamenti precedenti non accettati della stessa pratica. Il rivenditore può revocarli manualmente.
- Una richiesta già accettata non può essere cancellata tramite revoca: viene confermata o rifiutata, conservando lo storico. Finché è pendente o confermata non si può pubblicare un’altra proposta per la stessa pratica.
- Il collegamento permette di leggere dati e immagini della sola revisione condivisa. Va trasmesso esclusivamente al cliente. Le risposte pubbliche non vengono memorizzate in cache; il token di accesso è oscurato nei log delle richieste backend.

## Limiti e contabilità
L’identità dichiarata dal cliente non viene verificata con OTP: non è stata implementata una firma digitale. Questa è una richiesta di accettazione con dichiarazione, nominativo, email, data e revisione conservati, seguita dalla verifica del rivenditore.

Il collegamento va condiviso manualmente: in questo blocco non è stato aggiunto l’invio email della revisione unica e non sono state spedite email di prova. Nessun pagamento è attivato. Acconti e saldi spettano al rivenditore; la conferma non genera incassi né duplica ricavi nel conto economico. Gli inserimenti economici restano nel modulo manuale esistente. Nessun ordine ai produttori viene inviato da questi pulsanti.

Per modificare una proposta già confermata servirà il successivo flusso esplicito di variante/annullamento; in questa versione la decisione finale è bloccata. Il portale è per ora in italiano.

## Verifiche locali
Compilazione backend, controllo TypeScript e build frontend. Test su database temporaneo per migrazioni, isolamento fra venditori, hash dei token, rotazione/revoca, scadenze, accesso limitato alle immagini della revisione, dichiarazione, coerenza email, accettazione, conferma/rifiuto, immutabilità dell’offerta e assenza di scritture economiche automatiche. Ripetuti tutti i test delle pratiche, conto economico, cataloghi e prodotti importati. Il collaudo effettivo sul NAS resta da eseguire dopo la copia.

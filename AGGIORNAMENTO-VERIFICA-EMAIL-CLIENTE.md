# Verifica email cliente con codice monouso — 15 ottobre 2026

## Installazione
Fare backup del database/volume, poi copiare Aggiornamento sul NAS mantenendo i percorsi. Non sostituire backend.env, .env o volumi.

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build backend frontend
docker compose restart gateway
```

Migrazione additiva: 20261015180000_offer_email_codes. Aggiunge i codici e la data emailVerifiedAt alle accettazioni; applicata da migrate deploy, senza reset del database.

## Percorso cliente
1. Aprire il collegamento della proposta ricevuto dal rivenditore, leggere prodotti, PDF e condizioni.
2. Inserire nome ed email; se la revisione contiene un indirizzo, deve essere lo stesso.
3. Premere «Invia codice di verifica email» e controllare la casella e lo spam.
4. Inserire il codice di sei cifre, confermare la dichiarazione e premere «Accetta e richiedi conferma».
5. Il rivenditore vede la data di verifica email insieme alla richiesta e procede con la verifica tecnica/conferma o il rifiuto come prima.

L’email con codice parte soltanto quando il cliente preme il pulsante. Richiede lo stesso SMTP già configurato; non è un messaggio in coda da reinviare automaticamente. In caso di invio incerto il codice eventualmente ricevuto può essere utilizzato.

## Regole
- Codice casuale a sei cifre, conservato soltanto come hash Argon2; mai restituito dall’API o registrato nello storico.
- Durata 10 minuti, massimo 5 tentativi di verifica per codice. Anche le verifiche corrette consumano un tentativo.
- Almeno 60 secondi tra gli invii e massimo 5 invii complessivi per collegamento cliente. Oltre il limite occorre un nuovo collegamento del rivenditore, che revoca i precedenti non accettati.
- Un nuovo codice sostituisce il precedente. Il codice è legato al collegamento e all’email; cambiarli non consente di riutilizzarlo.
- Il consumo del codice e la registrazione dell’accettazione avvengono nella stessa transazione. Codici errati consumano tentativi anche se l’accettazione non viene salvata.
- Token revocati, offerta scaduta o codice scaduto impediscono la nuova accettazione.
- Se nella vecchia revisione manca l’email, viene verificata la casella dichiarata da chi possiede il collegamento: per associare in anticipo il destinatario compilare l’anagrafica prima di creare la revisione.
- Le accettazioni precedenti restano storiche, con data verifica vuota e indicazione esplicita. Non vengono trasformate retroattivamente in accettazioni verificate.

Il codice verifica l’accesso alla casella, non l’identità personale del nominativo dichiarato. Non viene introdotta una firma digitale. L’accesso di lettura alla pagina e al PDF continua a dipendere dal collegamento riservato: il codice è richiesto per la nuova accettazione, non per aprire la pagina.

Non aggiunge pagamenti o ordini ai produttori. Collaudo sul NAS ancora rinviato: test locali con SMTP simulato, nessuna email reale inviata. Restano varianti dopo conferma e verifica dell’incasso al rivenditore prima degli ordini.

20 ottobre: il codice non è più obbligatorio per default nell’accettazione delle offerte; vedere AGGIORNAMENTO-OFFERTA-TRATTATIVA-DISEGNI.md. La verifica degli account rimane separata.

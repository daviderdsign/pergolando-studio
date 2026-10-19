# Notifiche della trattativa — 15 ottobre 2026

## Installazione e prova
Salvare una copia del database/volume, poi copiare il contenuto di Aggiornamento sul NAS mantenendo i percorsi. Non sostituire backend.env, .env o volumi.

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build backend frontend
docker compose restart gateway
```

Migrazione additiva: 20261015120000_case_notifications. Il backend la applica con migrate deploy; non usare migrate reset.

1. Creare una revisione e un collegamento cliente.
2. Il cliente accetta: viene registrata nella stessa transazione una notifica destinata all’email dell’account venditore proprietario della pratica.
3. Il rivenditore conferma o rifiuta: viene registrata una comunicazione all’email dichiarata dal cliente nell’accettazione, con la nota del rivenditore quando presente.
4. Aprire Pratiche → Offerta unica → Comunicazioni della trattativa, quindi Aggiorna comunicazioni.
5. Il backend controlla la coda ogni 30 secondi. Senza configurazione SMTP i messaggi restano in coda; il backend deve rimanere acceso.

## Esiti e affidabilità
La registrazione della notifica è atomica rispetto all’accettazione/decisione. L’invio SMTP avviene successivamente: un errore non annulla la decisione del cliente o del rivenditore.

Un solo evento per tipo e collegamento: ripetere la richiesta non crea notifiche duplicate. Stati: PENDING, SENDING, SMTP_ACCEPTED, FAILED, UNKNOWN. SMTP_ACCEPTED indica soltanto accettazione da parte del server email, non consegna o lettura.

Errori e risultati incerti non vengono ripetuti automaticamente. Dopo aver controllato la casella, il proprietario può selezionare la conferma e rimettere la singola notifica in coda. Vengono conservati destinatario, messaggio, data e numero di tentativi; è conservato l’ultimo esito, non un dettaglio separato di ogni tentativo SMTP.

Al riavvio gli invii rimasti SENDING diventano UNKNOWN, per evitare duplicati automatici. Il worker è pensato per l’attuale singola istanza backend per rivenditore, non per più repliche concorrenti. Se il destinatario manca, lo stato è FAILED/MISSING_RECIPIENT: non viene simulato un invio riuscito.

Le email di notifica non contengono segreti dei collegamenti cliente né allegati: il PDF versionato viene inviato con il flusso offerta già implementato. Nessuna password o credenziale viene salvata nella coda.

## Perimetro attuale
Sono completate notifiche di accettazione, conferma/rifiuto e relativo storico. Rimangono da sviluppare editor anagrafico cliente, verifica OTP, varianti/annullamenti dopo conferma, attività e richiami della trattativa, pagamenti e verifica incassi. Nessun ricavo, pagamento o ordine al produttore viene creato da queste notifiche.

Il collaudo NAS richiesto resta rinviato. Test locali con SMTP simulato, nessuna email reale inviata. Build backend e frontend superate, test notifiche e regressione degli altri otto script superati.

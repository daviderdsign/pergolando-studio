# Invio email della revisione unica — 15 ottobre 2026

## Installazione sul NAS
Fare una copia del database/volume, quindi copiare il contenuto di Aggiornamento mantenendo i percorsi. Non sostituire backend.env, .env o i volumi.

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build backend frontend
docker compose restart gateway
```

La migrazione aggiuntiva 20261015090000_proposal_deliveries crea lo storico invii con le copie dei PDF. Viene applicata dal migrate deploy del backend. Non usare migrate reset.

## Prova dal telefono
1. Pratiche → Offerta unica → selezionare una revisione con email cliente e validità futura.
2. Creare il collegamento cliente. Un nuovo collegamento revoca quelli precedenti non accettati della stessa pratica, anche se già spediti via email: evitare di rigenerarlo dopo l’invio senza necessità.
3. «Prepara email e PDF»: il destinatario è quello della revisione, non un indirizzo arbitrario digitato per l’invio. Se nella pratica manca l’email, aprire Dati cliente, note e richiami, correggere l’anagrafica e creare una nuova revisione. Le revisioni precedenti restano invariate.
4. Controllare il messaggio e scaricare il PDF da verificare. Il documento deriva dalla revisione immutabile e dalle immagini in essa referenziate; immagini mancanti impediscono la preparazione.
5. Selezionare la conferma di controllo e premere «Invia email al cliente».
6. Consultare lo storico e scaricare la copia archiviata, identica nei byte a quella passata al servizio SMTP.

## Stati e richieste ripetute
- SMTP_ACCEPTED: il server email ha accettato il destinatario; non prova consegna o lettura.
- FAILED: errore certo di configurazione/autenticazione, connessione iniziale o destinatario rifiutato.
- UNKNOWN: timeout o altro esito non determinabile; controllare la casella prima di un eventuale nuovo tentativo.
- SENDING: tentativo avviato e non ancora completato. Se il processo viene interrotto può restare in questo stato: aggiornare gli esiti e verificare la casella.

La stessa richiesta non viene inviata due volte, anche se il browser ripete la chiamata. Un nuovo tentativo richiede una nuova preparazione esplicita. Un invio SENDING recente blocca per due minuti un secondo tentativo con chiave diversa; trascorso questo tempo non avviene alcun reinvio automatico.

## Configurazione
Usare SMTP_HOST, SMTP_PORT, SMTP_SECURE, SMTP_USER, SMTP_PASS e SMTP_FROM già configurati nel backend.env del deployment. Nessuna credenziale è stata copiata nel pacchetto di aggiornamento.

Il collegamento nell’email usa per impostazione predefinita https://pergolando.rdsign-app.it. Per un altro deployment impostare PUBLIC_APP_URL con l’origine HTTPS pubblica, senza percorsi; non usare l’indirizzo locale del telefono o del PC. PUBLIC_APP_URL va nel backend.env runtime e richiede la ricreazione del container backend. Non è obbligatorio aggiungerlo per il dominio attuale.

## Dati conservati e limiti
- Revisione, destinatario, oggetto, corpo con segreto del link oscurato, hash dello snapshot e del PDF, copia allegato, stato, data, codice errore sintetico e message-id quando disponibile.
- Il token del collegamento non viene archiviato in chiaro nello storico. Per questo un nuovo tentativo dopo ricaricamento della pagina richiede un nuovo collegamento, con la conseguente revoca dei precedenti non accettati.
- PDF generato nel browser dallo stesso componente usato per il download, sulla revisione salvata. Il backend verifica proprietà, revisione/hash, collegamento attivo, conferma del venditore, struttura base e dimensione del file. Non analizza semanticamente il testo del PDF per certificare che coincida con lo snapshot; la verifica dell’allegato resta esplicita nell’anteprima.
- Limite PDF circa 8 MB, anche in base al limite della richiesta base64. Gli allegati aumentano la dimensione del database e dei backup.
- Nessuna verifica automatica di consegna/bounce o lettura, nessun worker con reinvio automatico. Restano da aggiungere notifiche al rivenditore per l’accettazione e conferme email al cliente.
- Nessun pagamento, ordine al produttore o scrittura economica automatica viene generato dall’invio.

## Verifiche locali
Test con SMTP simulato: nessuna email reale spedita. Verificati hash/revisione, allegato archiviato, isolamento, configurazione mancante, token revocato, errori certi/incerti, ripetizione e concorrenza senza duplicati. Ripetuti i test delle pratiche, conto economico, cataloghi, prodotti importati e pagina cliente. Compilazione backend e build frontend. Resta il collaudo SMTP effettivo sul NAS tramite il pulsante dell’app.

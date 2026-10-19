# Invio email ordini ricambi — 16 ottobre 2026

## Percorso operativo

Pratica → Assistenza → ticket → intervento → Ordini ricambi al fornitore → singolo ordine → «Invio ordine ricambi via email».

1. Inserire l’indirizzo email verificato del fornitore: non viene ricavato dal nome dell’azienda.
2. Aprire l’anteprima. Si vedono mittente configurato, destinatario, oggetto, testo e nome dell’allegato. Il PDF scaricabile nell’ordine è quello originale già archiviato.
3. Verificare destinatario, messaggio e PDF, poi selezionare la conferma esplicita e premere «Invia email ordine ricambi».
4. Consultare lo storico degli esiti. Dopo l’accettazione SMTP l’ordine passa a «Invio registrato»; la conferma delle condizioni da parte del produttore e gli arrivi restano operazioni distinte.

Il testo richiede conferma di codici, quantità, disponibilità, condizioni di fornitura e data di consegna. Il riferimento univoco dell’ordine resta uguale anche in un eventuale invio ripetuto, per chiarire al fornitore che si tratta dello stesso ordine. Non vengono aggiunti prezzi o condizioni presunte.

Cambiare il destinatario invalida l’anteprima e la conferma. Il server verifica anche impronta del PDF, contenuto dell’ordine, revisione dell’intervento e mittente configurato. Un’anteprima superata non consente l’invio. Per interventi a pagamento deve essere ancora presente il preventivo accettato corrispondente ai ricambi.

## Stati e verifiche

- **Invio in corso**: tentativo registrato prima di contattare SMTP. Richieste concorrenti e retry della stessa richiesta non generano due spedizioni.
- **Accettata dal server email**: il server SMTP ha accettato il destinatario. Questo non prova la consegna in casella, la lettura o l’accettazione commerciale del fornitore.
- **Invio non riuscito**: fallimento con esito noto, per esempio autenticazione o destinatario rifiutato. Si può riprovare soltanto dopo una nuova anteprima e conferma; il tentativo precedente rimane nello storico.
- **Esito incerto**: timeout, connessione interrotta o processo interrotto. Nessun reinvio automatico. Prima di procedere occorre verificare con il fornitore.

Per un esito incerto il rivenditore può registrare, con data, riferimento e nota, che il fornitore conferma la ricezione oppure la mancata ricezione. La verifica resta associata al tentativo originario e non riscrive l’esito SMTP come se fosse stato certo.

La ricezione confermata registra l’invio e impedisce una seconda spedizione dall’app. La mancata ricezione verificata consente soltanto di preparare una nuova anteprima: non spedisce nulla. Prima di un nuovo invio occorre concordarlo con il fornitore, perché un messaggio iniziale potrebbe arrivare in ritardo. Le informazioni della verifica sono dichiarazioni del rivenditore, non una lettura automatica della casella del produttore.

Il sistema riduce i reinvii involontari ma non può garantire la consegna esattamente una volta attraverso SMTP. Una eventuale accettazione tardiva dopo una verifica manuale viene evidenziata nello storico con `LATE_ACCEPTANCE_AFTER_CHECK`: va riconciliata con il fornitore usando lo stesso riferimento d’ordine.

## Protezioni e storico

Durante un invio in corso o un esito incerto non riconciliato sono bloccate le modifiche operative all’ordine, incluso l’annullamento. Il PDF resta consultabile. Un ordine già registrato come inviato esternamente non può essere spedito nuovamente dalla funzione email.

Ogni tentativo conserva destinatario, mittente, oggetto, testo, nome e impronta dell’allegato, esito, codice tecnico, riferimento SMTP se disponibile e verifica manuale. Non vengono archiviate credenziali SMTP in queste righe. Dati e operazioni sono riservati al rivenditore proprietario della pratica.

All’avvio del backend e ogni 30 secondi si controllano i tentativi interrotti: quelli rimasti in corso oltre cinque minuti diventano incerti, senza reinvio. I tentativi ancora attivi nello stesso processo non vengono classificati come interrotti. Lo storico nel browser si aggiorna periodicamente e può essere ricaricato manualmente.

La connessione persa viene trattata come esito incerto anche nell’invio degli ordini principali ai produttori, evitando di considerarla automaticamente un fallimento sicuramente non consegnato.

Questo blocco non genera costi, incassi, ordini aggiuntivi o notifiche al cliente. Usa il trasporto SMTP già configurato nel backend. Le email di test sono simulate: nessun messaggio reale è stato spedito durante lo sviluppo.

## Aggiornamento NAS

Pacchetto cumulativo nella cartella Aggiornamento. Eseguire prima backup di database e allegati; copiare i file mantenendo i percorsi, senza sostituire .env/backend.env.

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build backend frontend && docker compose restart gateway
```

Migrazione additiva `20261017000000_support_part_order_mail`. Nessun tentativo creato per gli ordini preesistenti; nessun invio avviene per effetto dell’aggiornamento. Nessun deploy NAS eseguito dalla sessione.

## Verifiche e seguito

Test locali con trasporto SMTP simulato: anteprima, allegato e mittente, proprietà dei dati, SMTP assente, revisione/impronta, invio concorrente idempotente, fallimento certo, esiti incerti, verifiche ricevuto/non ricevuto, retry esplicito, blocco modifiche e recupero interruzioni senza spedizione automatica. Regressioni ordini ricambi, interventi, notifiche e ricavi assistenza eseguite.

Prossimo blocco: documenti e fatture dei fornitori riferiti ai ricambi, con verifica degli importi e collegamento al consuntivo senza duplicare i costi. Restano acquisizione automatica dalle caselle email, ripartizioni documenti, resi, magazzino, carta intestata del PDF, EN e collaudo completo sul NAS con SMTP reale.

Collaudo mobile con API simulate superato a 320/390 px: anteprima senza invio, conferma esplicita, modifica del destinatario che invalida l’anteprima, esito incerto che blocca le modifiche, verifica documentata con il fornitore e storico. Screenshot controllato in output/support/email-ordine-ricambi-mobile.png. Build backend/frontend completate; nessuna email reale o chiamata IA.


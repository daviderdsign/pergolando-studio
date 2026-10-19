# Preventivi assistenza — 16 ottobre 2026

## Percorso rivenditore

In Pratica → Assistenza → ticket → Interventi e ricambi, salvare un intervento «Da organizzare» con copertura «A pagamento». Aprire «Preventivi assistenza · voci di vendita» e inserire descrizioni, quantità (anche frazionarie a due decimali), prezzi unitari netti, IVA per voce, scadenza e condizioni. Tutti gli importi sono espliciti: nessuna tariffa, aliquota o regola di garanzia viene presunta.

La verifica del rivenditore consente di emettere il PDF A4 orizzontale. Il documento e i dati commerciali sono archiviati come versione immutabile. Il totale imponibile viene arrotondato al centesimo per voce; l’IVA si calcola per voce e i totali si sommano. Una nuova versione sostituisce la precedente e richiede nuova approvazione. Controlli di revisione impediscono di emettere su una versione già superata.

Il PDF usa la ragione sociale salvata nella configurazione; in sua assenza identifica l’account del rivenditore tramite email. Il layout attuale è di base: l’applicazione della carta intestata personalizzata a questo documento resta da estendere. I caratteri non rappresentabili nel font del PDF generano un messaggio esplicito, senza sostituzioni silenziose.

## Decisione del cliente

Il cliente vede i preventivi della propria richiesta nel portale riservato, scarica il PDF e può accettare o rifiutare dopo aver confermato la lettura della specifica versione. Il rivenditore può registrare una decisione ricevuta altrove, indicando obbligatoriamente il riferimento (per esempio email, data o documento). Non si tratta di firma digitale e il riferimento testuale non sostituisce l’archiviazione dell’originale da parte del rivenditore.

Il rivenditore può ritirare un preventivo ancora in attesa. Un preventivo scaduto non può essere accettato; la scadenza è indicata come fine giornata UTC. Dopo l’accettazione la scadenza non annulla la decisione già registrata.

Emissione e decisione aggiungono un evento alla conversazione e accodano le notifiche già previste. Nessuna email reale è stata inviata durante lo sviluppo. Per ricevere l’avviso e accedere al documento, il cliente deve avere un accesso assistenza valido. Le note interne, le giacenze dichiarate e i costi effettivi non vengono pubblicati nel preventivo o nelle API pubbliche.

## Intervento e conto economico

Un intervento a pagamento richiede un preventivo accettato corrispondente alla copertura e ai ricambi previsti prima di confermare l’appuntamento o completare il lavoro. Cambiando codici, descrizioni, quantità necessarie o fornitori, serve una nuova versione accettata. Disponibilità e consumi sono invece dati operativi.

Le rettifiche dei soli costi di interventi già completati restano possibili a parità di copertura e ricambi, anche per dati antecedenti a questa migrazione. Non si obbliga a ricreare un’accettazione storica non registrata.

L’accettazione non genera ricavi, fatture, pagamenti, ordini al produttore o chiusure automatiche del ticket. I costi effettivi continuano a essere registrati dal consuntivo dell’intervento. Ordini dei ricambi, ricavi assistenza e relativo incasso richiedono ancora il proprio flusso esplicito.

## Aggiornamento NAS e verifiche

File cumulativi nella cartella Aggiornamento. Eseguire prima backup di database e allegati; copiare mantenendo i percorsi e senza sostituire .env/backend.env.

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build backend frontend && docker compose restart gateway
```

Migrazione additiva `20261016235930_support_quotes`. Nessun deploy NAS eseguito.

Verifiche locali: build backend/frontend, calcoli e IVA, versioni e revisioni, accessi per rivenditore/cliente, revoca, approvazione esplicita, riferimenti manuali, blocco degli interventi non approvati, protezione dei costi e PDF archiviato. Test browser con API simulate su 320/390 px. PDF di prova renderizzato e controllato visivamente in `output/support/preventivo-assistenza.pdf`; schermate di prova nella stessa cartella.

Prossimo blocco: richiesta/ordine ricambi al produttore collegato all’intervento, disponibilità e arrivi verificati, adozione guidata dei costi manuali. Restano anche carta intestata, traduzione EN e collaudo end-to-end sul NAS.

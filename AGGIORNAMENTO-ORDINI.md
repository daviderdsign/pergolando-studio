# Preparazione ordini — 16 ottobre 2026

Aggiunta /pratiche/:id/ordini e API autenticata /cases/:id/orders. Il rivenditore assegna ogni prodotto della revisione confermata a un produttore e verifica codice, quantità e specifiche. Salvataggio immutabile raggruppato per produttore, senza dedurre codici o ragioni sociali dal marchio. Non include prezzi di vendita cliente nel documento del produttore.

Controlli server: proprietà, proposta confermata, acconto effettivo verificato al netto dei rimborsi, cataloghi importati ancora approvati e con hash coerente, corrispondenza esatta delle righe, revisione concorrente, conferma esplicita e retry idempotente. Un solo insieme di ordini per revisione; varianti/rettifiche successive da sviluppare. Nessun costo o movimento finanziario creato.

Questo blocco prepara documenti interni: NON invia email o ordini esterni, non produce ancora PDF di acquisto, non gestisce conferme/arrivi parziali. Questi sono i prossimi passi. Il collaudo reale dei cataloghi resta pendente per credito API esaurito: nessuna nuova chiamata eseguita.

Migrazione additiva 20261016180000_supplier_orders: fare backup database prima del deploy. Build backend, controllo TypeScript frontend e test ordini/acconti locali passati. Nessun collaudo NAS o prova UI reale eseguiti per questo blocco.

## PDF e invio esplicito — completato nel codice il 16 ottobre

Per ogni produttore: PDF A4 verticale multipagina generato dal server con riferimento ordine, dati del rivenditore conservati dalla revisione offerta (se disponibili), codice, quantità e specifiche verificate. Non esporta il prezzo di vendita né il JSON commerciale completo. I PDF originali già archiviati negli invii vengono restituiti identici. Modello documentale essenziale: non applica ancora la carta intestata PDF personalizzata; caratteri fuori dall’alfabeto supportato producono errore esplicito.

Email produttore inserita dal rivenditore, anteprima, PDF scaricabile e consenso specifico prima dell’invio. Il server ricontrolla proposta confermata, cataloghi e acconto; collega il consenso a destinatario e snapshot tramite hash. Invio SMTP dal server, allegato archiviato, storico esiti, retry idempotente. SMTP_ACCEPTED non significa consegna o conferma d’ordine del produttore. Esiti incerti o processi interrotti restano bloccati da ulteriori invii; riconciliazione esplicita di questi esiti da sviluppare. Errori sicuramente falliti permettono una nuova anteprima e un nuovo tentativo.

Migrazione aggiuntiva 20261016200000_supplier_order_delivery. Backup database prima di aggiornare il NAS. Nessuna email reale spedita durante lo sviluppo; trasporto e API simulati nei test. Build backend/frontend superate, test ordini/acconti/setup e Chromium mobile 320/390 px superati; PDF di prova su tre pagine renderizzato e controllato. Nessun deploy NAS eseguito.

Prossimo blocco: conferme produttori (prezzi di acquisto, riferimenti, date), documenti originali e arrivi parziali; poi collegamento versionato al conto economico, senza doppio conteggio. Non ancora implementati invio tramite portali/API dei produttori, riconciliazione email, varianti di ordini già preparati, stato Ordini completato nel percorso e gestione di invii incerti.

Il rivenditore ha comunicato di avere creato il progetto Google dedicato, ricaricato e configurato la chiave. Disponibilità reale API ancora da verificare dall’app/NAS: nessuna chiamata IA aggiuntiva effettuata in questo blocco.

## Conferme produttori e arrivi parziali — 16 ottobre

Nella pagina ordini, per ogni produttore: conferma con riferimento originale, data documento, totale acquisto al netto IVA, eventuale data promessa (vuota se non comunicata), nota di verifica e collegamento facoltativo a un allegato originale della pratica. Per caricare nuovi documenti si usa ancora la sezione allegati della pratica. L’email accettata da SMTP non crea automaticamente una conferma.

Arrivi: totale cumulativo ricevuto per ciascuna riga, da zero alla quantità ordinata. Richiede prima una conferma del produttore; nessuna somma automatica degli inserimenti. Nuove registrazioni possono correggere i totali precedenti con riferimento e motivo, mantenendo tutte le versioni. Stesso criterio per aggiornamenti di costo e data promessa. Stato completo soltanto quando tutte le righe del singolo ordine sono ricevute; non dichiara automaticamente posa/consegna finale della commessa.

Server: accessi del proprietario, gruppo/riga appartenenti all’ordine, date reali, costo netto esplicito, quantità intere entro l’ordinato, revisione concorrente e retry idempotente. Eventi immutabili con autore e data. Gli allegati collegati sono protetti dalla cancellazione anche tramite vincolo DB. Nessun costo, ricavo o pagamento creato automaticamente in questo blocco: integrazione economica versionata resta il prossimo punto, per evitare duplicazioni tra conferme e fatture.

Migrazione additiva 20261016220000_supplier_order_events: backup database prima del deploy. Build backend/frontend, test ordini, conferme/arrivi, acconti e setup passati; Chromium con API simulate a 320/390 px, screenshot verificato. Nessun invio reale, chiamata IA o deploy NAS eseguito.

Restano riconciliazione email automatica, integrazione conto economico/fatture, quantità per componenti e accessori interni alla riga, annullamento/modifica ordini commerciali già preparati, pianificazione posa e gestione dei resi. La rettifica di quantità ricevuta non invia un reso al produttore. L’interfaccia di questo blocco è in italiano; traduzione EN da completare.

## Collegamento costi ordini / conto economico — 16 ottobre

Le nuove conferme verificate alimentano una voce SUPPLIER prevista, identificata da ordine e produttore. Nuove conferme sostituiscono il precedente valore previsto. Dopo una fattura, una conferma successiva resta nello storico ma non sovrascrive il costo effettivo né ricalcola il budget storico.

Operazione Fattura / rettifica del totale fatturato nella pagina Ordini: richiede originale allegato alla stessa pratica, riferimento, data, nota e totale netto IVA cumulativo attribuito a quell’ordine. Include le fatture precedenti e le note di credito; il nuovo valore SOSTITUISCE il precedente, non si somma. Stato parziale/definitivo scelto esplicitamente. In caso di documento relativo a più ordini, il rivenditore deve verificare e attribuire il totale di ciascun ordine; nessuna ripartizione automatica presunta. Sono ammessi totali cumulativi da zero a 1.000.000 euro: un saldo netto negativo richiede una gestione dedicata, non è interpretato automaticamente.

Gli effettivi parziali mantengono il consuntivo provvisorio anche se viene spuntata la completezza dei costi. La fattura definitiva richiede comunque la verifica finale dei costi della pratica. Incassi, uscite, consegna e assistenza restano indipendenti. Nessuna fattura crea automaticamente un pagamento, nessun acconto aumenta i ricavi.

Prima del primo collegamento: possibilità di scegliere una voce manuale SUPPLIER attiva da sostituire, invece di duplicarla. Se non esiste, il rivenditore conferma che il costo è distinto. Nessun abbinamento per somiglianza del nome. Le voci già collegate all’ordine non sono modificabili attraverso il modulo manuale; conferme e fatture usano una catena di sostituzioni con evento originale, autore e data. Copia deduplicata del documento nel conto economico. Controlli e scrittura di evento/voce/revisioni nella stessa transazione; retry idempotenti.

Le conferme storiche anteriori a questo aggiornamento NON vengono riversate automaticamente, per evitare doppioni con voci manuali esistenti: nuova conferma verificata o fattura dalla pagina Ordini, scegliendo l’eventuale voce già inserita. Messaggio dedicato in interfaccia.

Migrazione additiva 20261016230000_order_costs. Backend/frontend compilati; test aggiornati su database temporanei per conferma, fattura parziale/definitiva, rettifica/nota di credito, sostituzione manuale, documenti e separazione dalla cassa. Controlli mobile con API simulate a 320/390 px. Nessuna chiamata IA, email reale, migrazione del database locale operativo o deploy NAS.

Prossimo blocco: pianificazione posa (squadra, date, disponibilità e verifica materiali/cantiere), checklist e successivo verbale di consegna/collaudo. Acquisizione automatica delle email, fatture elettroniche/partite fiscali, riconciliazione bancaria e traduzione EN non completate.

# Ripresa — 16 ottobre 2026, conversione PDF

Ultimo obiettivo: conversione di tutti i contenuti commerciali dei PDF in regole, con domande al rivenditore per ogni ambiguità. Vincolo fondamentale dell’utente: MAI inventare prezzi, condizioni o limiti; se non chiaro, chiedere o spiegare perché non implementato. Non promettere infallibilità al 100% della lettura IA.

Software implementato: job background, originali/hash/pagine, motore dichiarativo senza eval, opzioni/formule/vincoli/base IVA, configuratore e ricalcolo server; domande e risposte salvate per catalogo/revisione con autore/data, riconversione e prove manuali. Blocchi di copertura, evidenze e test. Migrazione 20261016150000_catalog_conversion e dipendenza pdf-lib nel lockfile. Documentazione AGGIORNAMENTO-CONVERSIONE-PDF.md.

Build e sei test backend più tre verifiche Chromium con API simulate passati. Prova reale VISION NON validata: proposte non eseguibili sono state respinte; richieste del provider hanno dato errori, ultimo HTTP 402 credito prepagato esaurito. Interrotte le chiamate reali. Non dichiarare conversione completa di un catalogo reale. Nessun catalogo approvato automaticamente, nessun deploy NAS. Aggiornamento cumulativo da copiare dopo backup DB, preservando ambienti.

Prossimi passi:
1. Ripristinare disponibilità/credito del servizio IA prima di altre chiamate reali, senza ripetizioni automatiche indiscriminate.
2. Installare e collaudare sul NAS il flusso con PDF originali completi: conversione, domande, risposte, regole, preventivi generati e riscontro sul listino. Modello configurabile via CATALOG_CONVERSION_MODEL; default gemini-3.1-pro-preview; chiave dedicata oppure GEMINI_API_KEY già esistente nel vero backend.env.
3. Chiudere tutte le lacune reali, aggiungere estensioni del motore se necessarie. Solo poi proseguire con gli ordini separati per produttore. Pratiche, offerta e acconti già implementati.

Regole societarie confermate: acconti/saldi al rivenditore, abbonamento Pergolando separato; più prodotti/marchi; cataloghi validati dal rivenditore; manodopera ore × costo squadra; assistenza indipendente da fatture tardive.

Aggiornamento successivo: prima preparazione ordini implementata mentre il collaudo PDF resta sospeso. Vedere AGGIORNAMENTO-ORDINI.md. Prossimo: PDF acquisto/anteprima e invio esplicito, poi conferme e consegne. Non dichiarare modulo ordini completo.
Criterio API confermato: elaborazioni ordinarie deterministiche, IA tramite API solo dove serve interpretazione autonoma per il rivenditore.


ULTIMO PUNTO: PDF e invio esplicito ordini ai produttori implementati; vedere AGGIORNAMENTO-ORDINI.md. Schema/migrazione supplier_order_delivery, nuove route e componente SupplierOrderSend. Nessuna email reale. Prossimo: conferme produttori e arrivi parziali, poi conto economico senza duplicati. Carta intestata personalizzata e riconciliazione invii incerti restano da sviluppare. Utente riferisce credito Google ripristinato e chiave configurata sul NAS, non verificato dal codice locale; nessuna nuova chiamata reale eseguita.


ULTIMO BLOCCO COMPLETATO: conferme produttori e arrivi parziali manuali, UI nella pagina ordini. SupplierOrderEvent append-only, revisioni, quantità cumulative e documenti protetti. Migrazione 20261016220000_supplier_order_events. Test e build locali passati; nessun deploy, email reale o chiamata IA. Prossimo punto: costo confermato per produttore nel conto economico con sostituzione/versionamento delle fatture, senza duplicazioni. Vedere AGGIORNAMENTO-ORDINI.md. EN ancora da completare.


ULTIMO BLOCCO: collegamento costi ordini/contabilità di commessa. Nuove conferme -> PLANNED; fatture/retifiche -> totale ACTUAL cumulativo sostitutivo, originale obbligatorio, stato costPending per parziali. Sostituzione esplicita di manuali, protezione voci collegate, nessun movimento cassa. Migrazione 20261016230000_order_costs. Vecchie conferme non importate senza verifica. Prossimo punto: pianificazione posa, materiali/cantiere/squadra, checklist e collaudo. Vedere AGGIORNAMENTO-ORDINI.md. Build/test locali; nessun deploy NAS.


ULTIMO BLOCCO COMPLETATO: pianificazione posa /pratiche/:id/posa. Stati, squadra/date/mezzi, controlli server su ordini/materiali/cantiere e conflitti, storico e retry. Migrazione 20261016233000_installation_planning. Vedere AGGIORNAMENTO-POSA.md. Test locali e mobile superati; nessun deploy NAS/email reale/API IA. Prossimo: checklist posa, foto, verbale consegna/collaudo e riserve, poi assistenza/notifiche. Percorso Posa collegato; non è chiusura del lavoro.


ULTIMO BLOCCO: checklist e verbale consegna /pratiche/:id/consegna. CaseHandover e CaseHandoverFile, PDF con foto archiviato, riserve/esiti, arrivi completi per senza riserve, protezione allegati e stato consegna gestito dal verbale. Migrazione 20261016235000_handovers. Build/test backend/mobile/PDF passati. Vedere AGGIORNAMENTO-CONSEGNA.md. Prossimo: invito portale assistenza, accesso cliente, ticket/foto/responsabile e notifiche. Firma e carta intestata personalizzata per verbale ancora da estendere. Nessun deploy/email/API IA.


ULTIMO BLOCCO: assistenza /pratiche/:id/assistenza e portale /assistenza#token. Accesso capability 30gg revocabile/email vincolata, hash nel DB e header redatto, invito SMTP esplicito, ticket/foto/risposte e gestione interna, niente note/costi nel pubblico. Migrazione 20261016235900_support. Build e test locali/mobile passati; nessuna email reale/IA/deploy. Vedere AGGIORNAMENTO-ASSISTENZA.md. Prossimo: notifiche automatiche ticket e risposte con storico esiti, poi interventi/ricambi. Account cliente password/OTP ed EN non implementati.


ULTIMO BLOCCO: notifiche automatiche assistenza. enqueueSupportNotification nelle transazioni ticket/eventi; SupportNotificationsService worker 30s, storico tentativi e recupero SENDING oltre 5min come UNKNOWN. Cancellazione su email/accesso cambiati, retry solo FAILED verificati, niente token/note nei messaggi. UI SupportNotifications nella pagina assistenza. Migrazione 20261016235910_support_notifications. Vedere AGGIORNAMENTO-NOTIFICHE-ASSISTENZA.md. Build e test locali/mobile passati; nessuna email reale/IA/deploy. Prossimo: interventi e ricambi collegati ai ticket. Riconciliazione UNKNOWN, bounce, preferenze ed EN restano da completare.



## 16 ottobre — Interventi e ricambi assistenza
Interventi per ticket, appuntamenti/squadre e conflitti con pose, ricambi dichiarati e utilizzati, ore × costo squadra, consuntivi con sostituzioni e protezione costi gestiti. Importi proposti separati da ricavi/incassi; note interne e messaggi pubblici distinti. Migrazione support_works. Vedere AGGIORNAMENTO-INTERVENTI.md. Test backend e browser mobile passati; nessun deploy NAS o invio reale. Prossimo: preventivo assistenza/ricambi, adozione guidata dei costi manuali e collaudo NAS.




## 16 ottobre — Preventivi assistenza
Voci commerciali esplicite con prezzi e IVA, PDF A4 orizzontale archiviato per versione, storico/sostituzioni e controllo revisioni. Accettazione/rifiuto dal portale cliente o registrazione del rivenditore con riferimento obbligatorio; ritiro delle offerte in attesa. Interventi a pagamento vincolati alla versione accettata e ai ricambi previsti. Nessun ricavo/incasso/ordine automatico. Migrazione support_quotes; vedere AGGIORNAMENTO-PREVENTIVI-ASSISTENZA.md. Verifiche locali backend/frontend/mobile/PDF eseguite; nessun deploy NAS o invio reale. Prossimo: ordini ricambi collegati agli interventi, arrivi e adozione guidata dei costi manuali. Carta intestata del nuovo PDF ed EN ancora da estendere.



## 16 ottobre — Ordini ricambi assistenza
Ordini per fornitore dai ricambi salvati, PDF A4 orizzontale archiviato, registrazione di invio esterno, conferme e arrivi cumulativi con rettifiche esplicite e storico. Quantità attive limitate al fabbisogno; copertura e ricambi protetti da cambi incoerenti. Richiesta accettata prima di acquisti per interventi a pagamento. Nessun aggiornamento automatico delle disponibilità, costo, incasso o email al fornitore. Migrazione support_part_orders; vedere AGGIORNAMENTO-ORDINI-RICAMBI.md. Test locali backend e PDF eseguiti; nessun deploy NAS o invio reale. Prossimo: adozione guidata costi manuali e riconciliazione economica assistenza. Trasmissione SMTP, fatture/ricambi, resi, magazzino, carta intestata ed EN da estendere.



## 16 ottobre — Riconciliazione economica assistenza
Collegamenti guidati delle voci manuali a manodopera, ricambi e altri costi; riconciliazione anche di doppioni scoperti dopo il consuntivo. Originali e storico conservati, conteggio unico, blocco del riutilizzo e revisione economica controllata. Riepilogo assistenza nel conto/CSV e blocco della dichiarazione di costi completi con interventi pendenti, senza bloccare consegna o assistenza. Migrazione support_cost_reconciliation; vedere AGGIORNAMENTO-RICONCILIAZIONE-ASSISTENZA.md. Build e test locali backend/mobile passati; nessun deploy NAS, invio reale o chiamata IA. Prossimo: ricavi e incassi assistenza collegati alla versione commerciale accettata. Ripartizione fatture, SMTP ricambi ed EN ancora da estendere.



## 16 ottobre — Ricavi, incassi e rimborsi assistenza
Registrazioni esplicite su intervento a pagamento completato e preventivo accettato: ricavo cumulativo netto, incassi/rimborsi effettivi IVA inclusa, riferimenti/metodi, adozione manuale e correzioni con storico. Residuo ed eccedenze visibili senza automatismi. Incassi assistenza esclusi dall’acconto originale e dai requisiti economici degli ordini; riepilogo conto e CSV aggiornati. Migrazione support_settlements. Vedere AGGIORNAMENTO-RICAVI-INCASSI-ASSISTENZA.md. Test locali backend/mobile eseguiti; nessuna operazione bancaria, email reale, IA o deploy NAS. Prossimo: invio SMTP ordini ricambi con anteprima e storico. Fatturazione, ripartizioni, acquisizione documenti, resi, magazzino, carta intestata ed EN restano da estendere.



## 16 ottobre — Email ordini ricambi
Anteprima di mittente/destinatario, testo e PDF archiviato; invio SMTP esplicito con impronta del contenuto e tentativo registrato prima della spedizione. Storico, retry dei fallimenti verificati, blocco degli esiti incerti e verifica documentata con il fornitore; recupero interruzioni senza reinvio automatico. Modifiche ordine protette durante invii pendenti. Connessione persa classificata incerta anche negli ordini principali. Migrazione support_part_order_mail. Vedere AGGIORNAMENTO-EMAIL-ORDINI-RICAMBI.md. Test SMTP simulati eseguiti; nessuna email reale o deploy NAS. Prossimo: fatture/documenti fornitori per ricambi e collegamento al consuntivo senza duplicazioni. Acquisizione automatica, ripartizioni, resi, magazzino, carta intestata ed EN restano da estendere.


## 16 ottobre — Documenti e fatture ricambi
Originali archiviati, dati netti verificati manualmente, quote su costi ricambi già consuntivati senza nuove voci economiche. Controlli limiti, revisioni, accessi e idempotenza; rettifiche con storico. Collegamenti a costi sostituiti segnalati e da ricontrollare prima della chiusura economica, senza bloccare consegna/assistenza. Migrazione support_part_documents. Build backend/frontend e test locali database/mobile/regressioni passati; nessuna email reale, IA o deploy NAS. Vedere AGGIORNAMENTO-DOCUMENTI-RICAMBI.md. Prossimo: resi e note di credito dei ricambi, con verifica esplicita e rettifica dei costi; acquisizione automatica documenti, magazzino, ripartizioni tra pratiche ed EN ancora da estendere.

## 16 ottobre — Resi e note di credito ricambi
Resi cumulativi separati dagli arrivi, limiti verificati, rettifiche e storico; annullamento dopo reso completo. Note di credito originali collegate a fattura e riduzione verificata del costo consuntivato, senza sottrazione duplicata né rimborso automatico. Quote limitate, revisioni e riferimenti protetti. Migrazione support_part_returns. Vedere AGGIORNAMENTO-RESI-NOTE-CREDITO.md. Build e test locali backend/mobile superati; nessun deploy NAS, SMTP reale o IA. Prossimo: collaudo sul NAS del flusso completo prima di altri moduli. Restano acquisizione email, magazzino, ripartizione tra pratiche, carta intestata completa ed EN.

## 16 ottobre — Chiarezza punto 4 e verifica acconti
Il punto 4 apriva correttamente Gestione ma mostrava subito il modulo cliente, confondendolo con il punto 1. Ora apre una pagina «Trattativa e acconto», con collegamenti a conferma tecnica e incassi; anagrafica raccolta in una sezione richiudibile. Nella pagina pagamenti nuovo movimento preselezionato per verifica, pulsante «Verifica questo movimento» nello storico e collegamento esplicito al prerequisito della conferma tecnica. Nessuna verifica automatica o modifica ai controlli economici. Build frontend superata. Da copiare e ricompilare sul NAS, non ancora distribuito. Il precedente deploy risulta avviato dai log NAS forniti dal rivenditore; collaudo funzionale in corso.

## 19 ottobre — Allineamento GitHub
Verificati i quattro repository esistenti, tutti pubblici, e recuperati i riferimenti remoti senza divergenze da integrare. Aggiornamenti del pacchetto venditore salvati su rami codex/github-alignment-2026-10-19; codice runtime escluso da credenziali, database, cache, pacchetti di consegna e nuove foto del laboratorio. Aggiunto GITHUB.md per struttura, versionamento e distribuzione separata dal NAS. Shared: build e 35 test passati; backend: build e 24 test passati. La dipendenza shared resta fissata a v0.3.0, senza modificare tag o lockfile. Stato delle pubblicazioni e dei controlli remoti da consultare nelle pull request. Nessun deploy NAS in questa sessione.

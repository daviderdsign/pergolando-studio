# Piano Pergolando aggiornato

## Decisioni confermate
- Percorso unico: ingresso su Pratiche clienti, cataloghi come area di preparazione e ambientazione facoltativa nella pratica. Eliminate le tre demo dalla navigazione.
- Un ambiente per rivenditore; cataloghi multipli caricati e verificati dal rivenditore con test guidati.
- Pratica multi-prodotto e multi-marchio.
- Il rivenditore incassa acconti e saldi; Pergolando ha un rapporto di abbonamento separato.
- Manodopera: ore effettive × costo orario squadra.
- Abbonamento Pergolando escluso dal riparto di commessa; altre spese generali separate dal margine diretto.
- Assistenza abilitabile alla consegna/collaudo, senza aspettare fatture del produttore.

## Prima apertura — Rapporto con Pergolando (prima versione di prova implementata)

Percorso: registrazione → verifica email → dati del rivenditore e del soggetto autorizzato → condizioni e abbonamento Pergolando → configurazione attività/carta intestata/cataloghi → uso operativo.

- Pagina dedicata alle condizioni B2B del servizio, scaricabili prima dell’accettazione. Definire piano, prezzo/IVA, periodicità, rinnovo, disdetta, scadenze, eventuali consumi IA/rendering, sospensione, esportazione e trattamento dati a fine rapporto. Nessun addebito implicito con un semplice consenso generico; eventuale ordine/pagamento separato ed esplicito.
- Chiarire obblighi del rivenditore: diritti sui cataloghi/loghi/foto caricati, verifica dei prezzi estratti e delle regole, misure e fattibilità tecnica, approvazione prima di inviare offerte o ordini. Immagini IA e rendering hanno funzione illustrativa; non sostituiscono verifiche tecniche.
- Definire obblighi e limiti di responsabilità di Pergolando, assistenza, disponibilità del servizio e backup; eventuale manleva circoscritta a violazioni imputabili al rivenditore. Nessun esonero assoluto o promessa di eliminare ogni responsabilità. Testi e forma di accettazione da validare da un legale, comprese le approvazioni specifiche eventualmente richieste.
- Distinguere accettazione contrattuale, approvazioni specifiche, presa visione dell’informativa privacy ed eventuale accordo sul trattamento dei dati dei clienti. Marketing e usi facoltativi dei dati separati, non preselezionati e non necessari per procedere.
- Registrare lato server identità/account e azienda, autorità dichiarata del firmatario, versione/testo o hash dei documenti, data/ora e azioni di accettazione; rendere disponibile una copia. Non assumere che una checkbox costituisca da sola forma valida per ogni clausola.
- Bloccare lato backend le funzioni operative se manca l’accordo obbligatorio; permettere consultazione documenti, gestione account e uscita. Gli aggiornamenti contrattuali richiedono un flusso tracciato coerente con il contratto, senza alterare lo storico.
- Separare sempre l’abbonamento Pergolando dagli acconti e saldi delle commesse, incassati dal rivenditore.
- Stato: pagina e registro delle conferme implementati in modalità di prova, con controllo lato backend. Clausole definitive, privacy, approvazioni specifiche e pagamento dell’abbonamento rimangono da definire e validare legalmente.

## Prima apertura — Carta intestata del rivenditore (prima versione implementata)

La preparazione iniziale include una sezione «Carta intestata e documenti», modificabile in seguito nelle impostazioni del rivenditore.

- Due alternative: caricare un PDF già predisposto oppure creare la carta intestata nell’app con logo, ragione sociale, recapiti e diciture in intestazione/piè di pagina.
- PDF caricato: anteprima, controllo formato/orientamento e area utile per i contenuti; evitare deformazioni, tagli del logo e sovrapposizioni. Gestire modelli A4 orizzontale e verticale secondo il tipo di documento, senza forzare un modello verticale nel preventivo orizzontale.
- Editor interno: caricamento logo, testi, disposizione semplice, margini e anteprima con un documento di esempio. Salvataggio sul server come modello riutilizzabile del rivenditore, non soltanto nel browser.
- Scelta della carta intestata predefinita per tutti i documenti generati; eventuali varianti per formato e prima pagina/pagine successive. Le condizioni contrattuali restano dati del documento, non soltanto testo decorativo sullo sfondo.
- Anteprima e conferma prima dell’attivazione. La carta intestata può essere cambiata in seguito; i PDF già emessi restano identici e le revisioni devono mantenere il riferimento alla versione grafica usata.
- Ambito: preventivi e relativi allegati prodotti dall’app; in seguito ordini, verbali, consegna/collaudo e assistenza. I documenti originali ricevuti da produttori restano inalterati.
- Stato: editor/logo e PDF A4 orizzontale implementati, salvataggio server, anteprima/export e integrazione versionata nelle offerte esistenti. Da estendere a orientamento verticale, varianti prima pagina/seguito e futuri documenti dei moduli ancora da sviluppare.

## Prima configurazione operativa

Realizzata /impostazioni: rapporto di prova Pergolando → dati aziendali → carta intestata → parametri commerciali → cataloghi/email/rendering → riepilogo. Nuove tabelle, controllo backend e ingresso guidato. Le impostazioni propongono i valori nelle nuove offerte e il costo squadra nel conto economico. Documentazione: AGGIORNAMENTO-PRIMA-CONFIGURAZIONE.md. Restano contratto commerciale definitivo e pagamento, estensione documenti futuri e traduzione EN completa.

## Punto 2 — Apertura pratica e percorso (implementato, da collaudare sul NAS)

/Pratiche → Nuova pratica con nome commessa, azienda/referente, recapiti, indirizzi separati e note del sopralluogo. Allegati PDF/PNG/JPEG autenticati e limitati, deduplicazione, ripresa senza seconda pratica, modifica audit e vecchie offerte preservate. Nuova migrazione 20261015230000_case_opening. Percorso inferiore numerato da Pratica ad Assistenza, con stato reale e ritorno alle funzioni presenti; impostazioni iniziali escluse, moduli futuri indicati come tali. UI uniformata su griglia di spaziature; verifiche mobile 320/390 px e desktop. Dettagli in AGGIORNAMENTO-APERTURA-E-PERCORSO.md.

## Blocchi realizzati nel codice, da collaudare sul NAS
1. Archivio e salvataggio pratiche multi-prodotto; prezzi ricalcolati sul backend, accessi per proprietario.
2. Conto economico manuale: ricavi previsti/confermati, costi previsti/effettivi, manodopera, spese generali, margini, cassa separata, storico sostituzioni, documenti originali, stato consegna e abilitabilità assistenza, CSV.

3. Modifica ed esclusione reversibile delle righe; revisioni immutabili e PDF multi-prodotto con sconto sui prodotti, posa, trasporto, IVA e acconto confermati dal venditore. Ambientazioni e viste tecniche possono ora essere salvate per riga e incluse nelle revisioni. Restano dati tecnici commerciali completi, invio versionato e accettazione.

## Prossimi blocchi e dipendenze
4. Cataloghi sul server con originali, versioni, test manuali e approvazione bloccata. Prodotti importati collegati alle pratiche multi-prodotto, ricalcolo server, modifica dal catalogo originale e offerta unica con i prodotti preconfigurati. Accesso dalla scelta catalogo del progetto unico; per gli importati il percorso resta senza 3D. OCR browser aggiunto e collaudato su PDF raster; da completare regole tecniche e supplementi automatici.
5. Ruoli del rivenditore e condivisione autorizzata delle pratiche, archivio attività e scadenze. Realizzati anagrafica cliente con storico, note e richiami manuali con completamento/riapertura; restano ruoli/condivisione e avvisi automatici delle scadenze.
6. Realizzato il primo flusso dell’offerta al cliente: collegamento riservato revocabile, revisione e PDF, richiesta di accettazione registrata, conferma tecnica/rifiuto del rivenditore. Aggiunti anteprima email/PDF, invio SMTP esplicito, storico esiti e copie degli allegati. Aggiunte notifiche transazionali di accettazione al venditore e conferma/rifiuto al cliente, coda SMTP e storico esiti. Aggiunto editor anagrafico con storico e conservazione dei dati nelle vecchie revisioni. Aggiunta verifica della casella email con codice monouso prima della nuova accettazione (non verifica dell’identità personale). Da completare: varianti dopo conferma, pagamento al rivenditore e verifica incasso prima degli ordini. Nessun incasso o ricavo viene creato automaticamente dal nuovo flusso.
7. Ordini separati per produttore e gestione di conferme, consegne e arrivi parziali.
8. Lettura email del rivenditore: acquisizione originali, estrazione e proposta di abbinamento a produttore/ordine/pratica. Dati dubbi o duplicati richiedono verifica; fatture/rettifiche sostituiscono i precedenti valori senza doppio conteggio.
9. Pianificazione posa, checklist, foto, verbale e collaudo.
10. Portale assistenza con invito cliente al collaudo, ticket e ricambi; indipendente dalla chiusura economica.
11. Report economici PDF/Excel, margini aggregati, pipeline e flussi finanziari, notifiche a destinatari autorizzati. Abbonamento rivenditore/Pergolando in area separata.
12. Consolidamento infrastruttura VPS/RunPod, backup, monitoraggio, audit e carico concorrente.

Le funzioni dimostrative (rendering, IA, cataloghi) non equivalgono a collaudo commerciale completo.

## Punto 3 — Configurazione prodotti (implementato 15 ottobre)

Area dedicata della pratica per cataloghi predisposti e approvati, ricerca, configurazione di più prodotti/marchi, riepilogo, modifica ed esclusione/ripristino. Salvataggi ricalcolati dal server e risultati precedenti invalidati. Blocco dei prodotti dopo accettazione/conferma, offerte storiche immutate. I listini importati mantengono verifiche manuali e supplementi espliciti: regole tecniche generali e varianti dopo conferma da estendere. Build e test locali superati; collaudo NAS ancora da eseguire. Dettagli in AGGIORNAMENTO-CONFIGURAZIONE-PRODOTTI.md.

## Offerta unica — Consolidamento del 16 ottobre

Riepilogo multiprodotto, anteprima economica coerente con gli arrotondamenti server, verifica condizioni da rinnovare dopo modifiche, revisioni con totali storici e aggiornamento stato dopo esiti cliente. Blocco server delle revisioni dopo accettazione/conferma, retry concorrenti idempotenti. Restano varianti definitive, registrazione/verifica incasso e ordini separati per produttore. Vedere AGGIORNAMENTO-OFFERTA-UNICA.md. Nessun deploy NAS eseguito da questa sessione.

## Acconto al rivenditore — Implementato 16 ottobre
Registrazione e verifica manuale incassi/rimborsi, acconto dalla revisione confermata, parziali, revoche e rettifiche, storico con autore. Riutilizzata la cassa, senza doppio ricavo. Migrazione payment_checks, pagina collegata all’offerta. Vedere AGGIORNAMENTO-ACCONTI.md. Prossimo blocco: ordini per produttore con verifica economica e tecnica ricalcolata sul server prima dell’autorizzazione, poi conferme/consegne. Nessun deploy NAS eseguito.

## Priorità aggiornata — Copertura integrale del catalogo
Il rivenditore controlla preventivi generati dal sistema, non costruisce i casi. Sequenza implementata con almeno cinque preventivi calcolabili e tutti i casi di copertura; non basta per approvare se restano opzioni non automatizzate. Nuove approvazioni PDF/condizioni non strutturate bloccate. Prossimo lavoro prioritario: inventario completo delle opzioni da ogni fonte/pagina, conversione a regole di prezzo/fattibilità, interfaccia configurazione e generazione di test per ogni regola e combinazione critica. Conversione completa NON ancora implementata; non presentare l’importazione tabelle come catalogo completo. Vedere AGGIORNAMENTO-VALIDAZIONE-CATALOGHI.md.

## Conversione commerciale PDF — 16 ottobre, software implementato / collaudo reale pendente
Flusso background, formule/opzioni/vincoli, base IVA, fonti/pagine e test di copertura collegati al configuratore. Chiarimenti del rivenditore versionati e limitati al catalogo; cambio risposta richiede riconversione. Non inventare prezzi, limiti o significati: dati mancanti, ambigui, non supportati o senza riscontro devono essere esplicitati e bloccare l’approvazione. Nessuna promessa di lettura IA infallibile. Verifiche locali passate; prova reale non conclusa, servizio HTTP 402 credito esaurito. Vedere AGGIORNAMENTO-CONVERSIONE-PDF.md. Riprendere il collaudo sui documenti completi dopo ripristino credito, prima degli ordini. Nessun deploy NAS.

## Preparazione ordini — 16 ottobre
Implementati raggruppamento per produttore, codici/quantità/specifiche verificati dal rivenditore, snapshot e controlli server. Restano PDF acquisto, invio esplicito, conferme e arrivi parziali. Collaudo reale conversione cataloghi sempre pendente. Vedere AGGIORNAMENTO-ORDINI.md.


## Invio ordini — 16 ottobre
PDF multipagina server, anteprima destinatario/testo, consenso, SMTP esplicito e archivio implementati. Nessun invio automatico; SMTP accettato distinto da conferma produttore. Restano conferme, arrivi parziali, riconciliazione esiti incerti e integrazione costi. Vedere AGGIORNAMENTO-ORDINI.md.


## Conferme e arrivi — 16 ottobre
Implementate registrazioni manuali delle conferme (costo netto/data promessa) e quantità ricevute cumulative per ogni riga, con rettifiche e storico. Allegati originali collegabili e protetti. Restano acquisizione email, costi integrati e fatture, pianificazione posa. Vedere AGGIORNAMENTO-ORDINI.md.


## Costi integrati — 16 ottobre
Collegamento transazionale conferme/fatture al conto economico, per ordine/produttore. Totali cumulativi sostitutivi e stato parziale, documenti e adozione di voci manuali verificata; nessun doppio costo o movimento cassa automatico. Restano acquisizione email e pianificazione posa/checklist/collaudo. Vedere AGGIORNAMENTO-ORDINI.md.


## Pianificazione posa — 16 ottobre
Implementati provvisorio/confermato/annullato, squadra e mezzi, durata, verifiche materiali e cantiere, disponibilità e accordo cliente, conflitti fra pose confermate e storico. Restano checklist, foto, verbale/collaudo, calendario risorse strutturato, notifiche e assistenza. Vedere AGGIORNAMENTO-POSA.md.


## Consegna e verbali — 16 ottobre
Checklist generale, foto, verbale PDF immutabile con revisioni e riserve implementati; consegna separata dalla chiusura economica. Restano checklist tecniche specifiche, firma, personalizzazione carta intestata e invio, portale assistenza/ticket. Vedere AGGIORNAMENTO-CONSEGNA.md.


## Assistenza — 16 ottobre
Accesso cliente tramite link riservato, invito esplicito, ticket con foto/risposte e gestione interna implementati. Consegna separata dai costi e accessi revocabili. Restano notifiche automatiche, interventi e ricambi, eventuale account/OTP, EN e collaudo NAS. Vedere AGGIORNAMENTO-ASSISTENZA.md.


## Notifiche assistenza — 16 ottobre
Implementati avvisi automatici transazionali, worker SMTP, storico tentativi, controlli destinatario/accesso e retry verificato dei fallimenti; nessun reinvio degli esiti incerti. Restano riconciliazione avanzata, interventi/ricambi e relative componenti economiche. Vedere AGGIORNAMENTO-NOTIFICHE-ASSISTENZA.md.



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

## Esito finale — 19 ottobre 2026
Tutti e quattro i repository sono integrati su main tramite pull request. Backend: CI test e Docker passati (run 39232847639); frontend: lint, TypeScript, build, tre test browser accessibilità/IT-EN e Docker passati (run 39233893547). Shared: build e 35 test locali superati. Le revisioni coordinate sono nel manifest JSON di allineamento.
Corretti conflitto della versione pnpm, configurazione ESLint frontend mancante nel checkout autonomo, diciture obsolete dei test di accesso e contrasto della dicitura iniziale. Nessun controllo disabilitato per forzare un esito verde. Restano warning di lint backend non bloccanti. Credenziali e dati operativi esclusi dai nuovi commit, senza riscrittura della cronologia. Backup locale Blender identico al sorgente originale verificato e mantenuto fuori da Git. Nessun deploy NAS eseguito. Prossimo lavoro: continuare il collaudo funzionale sul NAS; GitHub non sostituisce la verifica della commessa completa.

## 20 ottobre — Offerta, trattativa, accettazione semplice e disegni
Separati punto 3 (preparazione/revisioni/PDF) e punto 4 (invio, risposta, conferma tecnica, richiami e acconti). Anteprima cliente facoltativa; stato e prossima azione espliciti, aggiornamento stato cliente ogni 15 secondi. Codice email non obbligatorio per default, riattivabile tramite OFFER_EMAIL_VERIFICATION_REQUIRED; dichiarazione, revisione e timestamp conservati, emailVerifiedAt resta nullo senza effettivo codice. Ricevuta al cliente e notifica al rivenditore in coda idempotente. Account e conferme tecniche/economiche invariati. Recupero automatico delle viste mancanti in Prodotti/Offerta e archiviazione con controllo versione; salvataggi parziali preservano gli altri allegati. Revisioni precedenti immutabili. Vedere AGGIORNAMENTO-OFFERTA-TRATTATIVA-DISEGNI.md. Nessuna migrazione o distribuzione NAS automatica. Collaudo con API/SMTP simulati, nessuna decisione o email reale sulla pratica aperta.

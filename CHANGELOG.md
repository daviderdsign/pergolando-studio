# Changelog

## 16 ottobre 2026 — Conversione commerciale PDF e domande al rivenditore

- Flusso background su originali PDF/CSV, regole con fonti/pagine, opzioni e formule dichiarative, vincoli e base IVA. Configuratore dinamico e ricalcolo server, senza supplementi manuali nei nuovi cataloghi convertiti.
- Domande su dati mancanti o regole non esercitabili; risposte conservate con autore/data nel singolo catalogo e convertite in una nuova revisione. Nessun completamento probabilistico dei dati.
- Blocchi per copertura, evidenze, limiti, segnalazioni, differenze e casi di prova mancanti. Formule non supportate restano esplicitamente non applicate. La lettura IA non è infallibile e richiede riscontro e validazione manuale.
- Migrazione catalog_conversion e pdf-lib; build, sei test backend e tre collaudi Chromium simulati superati.
- Collaudo reale NON completato: proposte non eseguibili respinte e servizio IA infine HTTP 402, credito prepagato esaurito. Chiamate reali interrotte. Nessun catalogo reale approvato e nessun deploy NAS. Priorità: ripristino credito e collaudo della conversione, senza dichiarare completezza universale.

## 16 ottobre 2026 — Preventivi di prova generati dal sistema

- Il sistema costruisce e calcola i casi; il rivenditore li confronta e conferma uno alla volta. Minimo cinque calcolabili distinti e tutti i casi richiesti per tabelle, fascia e limiti.
- Conferme versionate con autore/data/nota; differenze e modifiche impongono una nuova revisione. Foglio informativo disponibile e testo conservato nell’approvazione, senza promessa di esonero assoluto di responsabilità.
- Requisito precisato: tutte le opzioni del catalogo devono diventare regole automatiche. Questa conversione semantica dei PDF NON è ancora implementata. Nuove approvazioni PDF/condizioni non strutturate bloccate anche dopo cinque prove; precedenti versioni storiche inalterate.
- Migrazione additiva catalog_trials. Build, quattro test backend e collaudo Chromium mobile superati. Nessun deploy NAS. Priorità successiva: motore completo opzioni/vincoli e copertura delle regole, prima di proseguire con gli ordini.

## 16 ottobre 2026 — Acconti e verifica incassi del rivenditore

- Nuova pagina /pratiche/:id/pagamenti collegata dall’offerta; movimenti nella cassa esistente e verifica separata di accrediti/rimborsi cliente.
- Acconto richiesto dalla revisione confermata, importi parziali e disponibilità verificata al netto dei rimborsi, per il futuro modulo ordini.
- Registro verifiche/revoche con autore, data, riferimento e nota; rettifiche da riverificare, accessi e retry protetti. Nessun doppio ricavo.
- Migrazione additiva 20261016090000_payment_checks. Nessun pagamento eseguito, riconciliazione bancaria automatica o ordine inviato.
- Build, cinque test backend e due verifiche Chromium superati. Aggiornamento da installare e collaudare sul NAS.

## 16 ottobre 2026 — Consolidamento offerta unica

- Riepilogo prodotti attivi/esclusi, anteprima in centesimi di sconto/posa/trasporto/IVA/totale/acconto/saldo, ritorno a prodotti e trattativa.
- Conferma del venditore azzerata dopo cambi delle condizioni, ricaricamento e salvataggio. Parametri iniziali protetti da sovrascrittura tardiva durante la compilazione.
- Revisioni con totali e validità storici; aggiornamento del contesto dopo esiti cliente. PDF e invio esplicito esistenti mantenuti.
- Nuove revisioni bloccate dopo accettazione/conferma anche sul backend; retry concorrenti della stessa richiesta senza duplicazione. Varianti dopo conferma restano da realizzare.
- Build backend/frontend e TypeScript superati; sei test backend e tre verifiche Chromium passati. Nessuna nuova migrazione e nessun incasso/ordine automatico. Installazione e collaudo sul NAS ancora da eseguire.

## 15 ottobre 2026 — Fine sessione e ripresa

Punto 3 completato e verificato. Stato, limiti, installazione NAS e prossime attività salvati in RIPRESA-DOMANI.md. Sessione fermata su richiesta dell’utente; nessun deploy NAS eseguito.

## 15 ottobre 2026 — Punto 3: prodotti della pratica

- Nuova area /pratiche/:id/prodotti: cataloghi predisposti e importati approvati, ricerca, riepilogo multiprodotto/marchio, modifica, esclusione e ripristino. Collegata all’apertura e al punto 2 del percorso inferiore.
- Configuratori collegati al contesto della pratica, pulsante per salvare e aggiungere un altro prodotto, prezzi restituiti dal server. Risultati asincroni precedenti ignorati dopo un cambio di parametri.
- Mutazioni dei prodotti bloccate lato server dopo accettazione o conferma. Revisioni offerte immutate; varianti post-conferma ancora da implementare.
- Retry concorrenti di inserimento senza doppio incremento economico. Nessuna modifica ai listini o nuova migrazione in questo blocco.
- Build superate, 14 script backend e tre verifiche Chromium con API simulate. Layout prodotti controllato a 320/390 px. Pacchetto cumulativo Aggiornamento da installare e collaudare sul NAS.

## 15 ottobre 2026 — Allineamenti, percorso della commessa e apertura pratica completa

- Spaziature condivise 16/24 px, card e intestazioni allineate, campi/pulsanti coerenti, checkbox in riga e selettore lingua uniforme. Sistemati anche sovrapposizione clic/linea e contrasto dei punti verdi nel percorso.
- Nuovo percorso inferiore a otto punti, senza fase di impostazioni: Pratica, Prodotti, Offerta, Trattativa, Ordini, Posa, Consegna, Assistenza. Avanzamento da dati server reali; ritorno alle schermate disponibili. Moduli futuri esplicitamente in preparazione. Endpoint compatto progress e aggiornamento dopo salvataggi.
- Punto 2: /pratiche/nuova e /pratiche/:id/apertura, nome commessa/azienda, anagrafica, luogo intervento separato, note e allegati del sopralluogo. Creazione idempotente e ripresa dopo errori di caricamento.
- Allegati autenticati PDF/PNG/JPEG con firme, limiti, hash/deduplicazione, download e conferma rimozione. Nessuna diffusione automatica di note/allegati interni al cliente.
- Migrazione additiva campi pratica, creationKey per proprietario e tabella case_files. Modifiche anagrafiche in storico; revisioni offerta immutate. Nuove revisioni con nome commessa, azienda cliente e luogo intervento nel PDF.
- Build superate, 13 test backend, Chromium mobile/desktop con recupero upload e navigazione, allineamenti e assenza di scroll orizzontale 320/390 px. Verde e collegamenti verificati. PDF renderizzato e controllato.
- Pacchetto cumulativo Aggiornamento pronto, ancora da installare sul NAS. Prossimo blocco: consolidamento configurazione prodotti/varianti e percorso commerciale; ordini/posa/assistenza completa restano da realizzare.

## 15 ottobre 2026 — Prima configurazione operativa del rivenditore

- Nuova pagina /impostazioni con sei sezioni: rapporto Pergolando, dati aziendali, carta intestata, parametri commerciali, cataloghi/servizi e riepilogo. Accessibile anche dal menu.
- Rapporto iniziale marcato come configurazione di prova, senza addebiti: documenti versionati/hash, conferma dell’account e rappresentante, copia scaricabile, conservazione storica. Contratto commerciale definitivo/privacy e pagamento abbonamento restano da completare con revisione legale.
- Migrazione additiva dealer_setup/dealer_agreements, profilo per account del rivenditore, concorrenza e validazioni server. Ingresso guidato frontend e controllo backend prima delle operazioni; nessuna cancellazione dei dati esistenti.
- Dati aziendali, condizioni/IBAN e parametri netti/percentuali/validità salvati sul server; nuovi preventivi precompilati e costo orario squadra proposto nel conto economico. I cataloghi non cambiano prezzo.
- Carta intestata con logo/testi o PDF singola pagina A4 orizzontale; originale conservato, anteprima raster, margini, PDF carta e documento di esempio. Revisioni nuove con copia grafica e dati aziendali, senza parametri interni riservati. Vecchie revisioni immutate.
- Checklist di cataloghi approvati o controllo manuale dei predisposti. Verifica SMTP e invio esplicito all’account autenticato; controllo Blender/GeoCalib facoltativo. Nessun servizio rendering necessario alla preventivazione.
- Build superate, dodici test backend, avvio Nest su DB temporaneo, collaudo Chromium mobile completo e regressione percorso unico. Email simulate, PDF renderizzato e verificato visivamente.
- Aggiornamento cumulativo preparato per NAS, ancora da installare. Limiti: pagina nuova in italiano, carta A4 orizzontale, futuri documenti e firma/pagamenti contrattuali da estendere.

## 15 ottobre 2026 — Specifica rapporto contrattuale Pergolando

- Prevista pagina dopo registrazione/verifica email per condizioni B2B, abbonamento, obblighi del rivenditore, diritti sui materiali e responsabilità; testi e modalità di accettazione da revisione legale.
- Separati accettazione, eventuali approvazioni specifiche, privacy e consensi facoltativi; previsto registro versionato server e blocco operativo fino al completamento degli adempimenti obbligatori.
- Abbonamento Pergolando separato dagli incassi del rivenditore. Nessun addebito, nuova clausola effettiva o modifica software introdotti in questo blocco di progettazione.

## 15 ottobre 2026 — Specifica carta intestata nella prima apertura

- Aggiunto al piano il requisito PDF caricato oppure editor con logo e diciture, salvataggio sul server e scelta predefinita per i documenti del rivenditore.
- Previsti anteprima, margini, varianti di orientamento, versionamento grafico e conservazione dei PDF già emessi.
- Verifica codice: disponibile branding del bundle, non ancora carta intestata personalizzabile. Aggiornamento progettuale, nessuna implementazione o deploy in questo blocco.

## 15 ottobre 2026 — Correzione configurazione pnpm per NAS

- Rimossa la riga segnaposto duplicata tesseract.js in pnpm-workspace.yaml, aggiunta dall’installazione delle dipendenze. Manteniamo una sola voce false: il postinstall opzionale non serve al motore OCR.
- Corretti sorgente e pacchetto Aggiornamento; entrambi verificati con parser YAML. Il precedente build locale non rilevava il file perché avviato direttamente con Node, mentre Docker lo legge tramite pnpm.


## 15 ottobre 2026 — Eliminazione cataloghi dall’archivio

- Aggiunto tasto Elimina catalogo con conferma esplicita e annullamento nell’archivio, per bozze e versioni approvate.
- DELETE autenticato, limitato al proprietario e alla revisione visualizzata: cataloghi cambiati nel frattempo non vengono eliminati.
- Eliminazione logica tramite stato DELETED: catalogo nascosto e non utilizzabile per nuovi prezzi/prodotti. Dati, originali e prove conservati; pratiche e offerte già salvate rimangono immutate. Modifiche successive a quei prodotti richiedono un catalogo disponibile. Nessuna cancellazione fisica o nuova migrazione.
- Backend build, frontend TypeScript/build; test cataloghi con eliminazione bozze/approvati, isolamento proprietario, revisione obsoleta, storico conservato e prezzo bloccato. Superata anche la regressione prodotti importati.
- File inclusi nell’aggiornamento cumulativo per NAS: ricostruire backend e frontend. Sito pubblico non ancora aggiornato automaticamente.

## 15 ottobre 2026 — OCR per i cataloghi scansionati

- Aggiunta lettura Tesseract.js 6.0.1 in italiano e inglese, sul dispositivo del venditore, senza inviare le pagine a un servizio OCR esterno.
- Automatica sulle pagine con meno di 80 caratteri alfanumerici estraibili; modalità tutte le pagine per PDF misti e opzione senza OCR. La soglia non identifica ogni scansione parziale: usare tutte le pagine quando necessario.
- Rendering PDF limitato a 2600 pixel sul lato lungo e un solo worker sequenziale per contenere memoria; coordinate delle parole riportate nello spazio PDF per riconoscere le matrici esistenti.
- Motore/worker serviti dall'app; modelli linguistici scaricati al primo utilizzo dal CDN predefinito Tesseract e memorizzati dal browser. Richiesta connessione al primo uso. Non serve Blender/GeoCalib né installare Tesseract sul NAS.
- Conservati anteprima originale, testo, metodo e confidenza OCR nelle pagine esportate. Segnalazioni per letture OCR/fallite; nessuna conferma o approvazione automatica delle tabelle. Controllo manuale e test catalogo invariati.
- Annullamento e timeout, rilascio worker/canvas; eventuali errori OCR conservano il testo originario e segnalano la pagina. OCR delle foto caricate separatamente non compreso.
- Verifiche: TypeScript e build frontend; Chromium con PDF raster generato, matrice 2×2 letta con prezzi corretti e tabella non approvata. Nessuna prova ancora sul PDF reale dell'utente o sul NAS.
- Aggiornamento cumulativo nella cartella Aggiornamento; copiare e ricostruire il frontend sul NAS. Nessuna migrazione database o modifica alle credenziali.

## 15 ottobre 2026 — Unificazione: eliminate le tre demo

- Richiesta dell’utente: usare un unico progetto secondo lo schema generale condiviso, senza scelta fra tre demo.
- Accesso → Pratiche clienti. Nuova pratica, cataloghi/listini e progetti esistenti nello stesso ambiente, con menu compatto e lingue conservate.
- /progetto per la configurazione; /cataloghi/importa e /cataloghi/preventivo per i listini del rivenditore. Vecchi indirizzi compatibili con reindirizzamenti e conservazione del contesto.
- Rimosse le diramazioni demo dal configuratore. Pratica creata dopo i dati cliente; prodotti salvati al preventivo. Ambientazione facoltativa, documenti/revisioni/invio nell’offerta unica.
- Passaggio all’offerta con salvataggio delle immagini e delle viste già disponibili, anche sole viste senza rendering; nessun blocco commerciale per rendering non disponibile.
- Rimosso il percorso normale di PDF/email isolati dei singoli prodotti. Importazione → verifica → catalogo approvato → pratica → offerta comune.
- Ritirati i componenti di scelta demo, mantenendo compatibilità con import e bozze locali precedenti. Nessuna modifica al motore prezzi o ai dati/migrazioni backend in questo blocco.
- TypeScript/build frontend superati. Test Chromium mobile con API simulate: nuova pratica senza duplicati, preventivo senza rendering, offerta comune, prodotto importato, redirect con contesto e destinazione login sicura. Home controllata visivamente.
- Aggiornamento cumulativo di 83 file verificati. Istruzioni: AGGIORNAMENTO-PERCORSO-UNICO.md. Collaudo NAS da iniziare dall’ingresso /pratiche dopo copia e rebuild.
- Restano i blocchi già elencati nel piano: varianti, incasso, ordini, consegne, posa e assistenza completi. Il percorso unico non dichiara già realizzate le parti mancanti dello schema.

---

## 15 ottobre 2026 — Codice monouso per l’email cliente

- Nuove accettazioni della proposta subordinate a un codice di sei cifre inviato all’email del cliente. La lettura tramite collegamento riservato resta invariata.
- Scadenza 10 minuti; massimo 5 verifiche per codice, 60 secondi tra invii e 5 invii per collegamento. Codici conservati con hash Argon2, mai restituiti dalle API.
- Vincolo a email/collegamento e consumo nella stessa transazione dell’accettazione. I tentativi errati restano conteggiati anche se l’accettazione viene rifiutata.
- Il nuovo codice sostituisce il precedente. Revoca/scadenza del collegamento impedisce accettazione e richiesta codice. Un esito SMTP incerto non provoca reinvii automatici; il codice eventualmente ricevuto resta utilizzabile.
- Data emailVerifiedAt conservata e visibile al rivenditore. Le vecchie accettazioni non sono retroattivamente verificate.
- Il codice prova l’accesso alla casella, non l’identità personale: nessuna firma digitale implementata.
- Migrazione additiva 20261015180000_offer_email_codes.
- Build backend/frontend e tutti gli undici test superati. Il nuovo test-offer-email-code.cjs usa hash e verifica reali con SMTP simulato; i test precedenti della macchina stati/notifiche isolano il verificatore con uno stub. Nessuna email reale inviata.
- Aggiornamento cumulativo: 75 file verificati, inclusi istruzioni AGGIORNAMENTO-VERIFICA-EMAIL-CLIENTE.md e questo changelog. Collaudo NAS ancora rinviato.
- Prossimi blocchi: varianti dopo conferma e verifica dell’incasso al rivenditore prima degli ordini; ruoli e automazione dei richiami restano nel piano.

---

## 15 ottobre 2026 — Anagrafica, note e richiami della trattativa

- Nuova pagina /pratiche/[id]/gestione, collegata dall’archivio e dall’offerta unica.
- Modifica di nome/cognome, email, telefono e indirizzo con controllo versione e storico prima/dopo.
- Le offerte già salvate, gli invii e le accettazioni non vengono modificati; le nuove revisioni usano l’anagrafica aggiornata.
- Note immutabili, richiami con scadenza, completamento e riapertura con storico. Nessuna email o notifica push programmata per i richiami.
- Migrazione additiva 20261015150000_case_management.
- Build backend/frontend e dieci script di test superati; nessuna email reale. Collaudo NAS ancora rinviato.
- Pacchetto cumulativo Aggiornamento: 72 file verificati; istruzioni in AGGIORNAMENTO-GESTIONE-PRATICHE.md.
- Prossimi blocchi: verifica identità cliente/OTP, varianti dopo conferma, verifica dell’incasso al rivenditore; ruoli/condivisione e avvisi automatici dei richiami restano aperti.

---

## 15 ottobre 2026 — Notifiche e gestione degli esiti della trattativa

- Su richiesta dell’utente, proseguito lo sviluppo senza attendere il collaudo sul NAS.
- Notifica al venditore proprietario dopo accettazione cliente; email al cliente dopo conferma o rifiuto del rivenditore, con eventuale nota.
- Coda persistente registrata nella stessa transazione della decisione; worker ogni 30 secondi. Invio fallito non annulla la decisione commerciale.
- Deduplicazione per collegamento/tipo evento, esiti SMTP distinti e ripetizione soltanto esplicita dopo verifica della casella. Gli invii interrotti diventano incerti al riavvio.
- Nuova sezione Comunicazioni della trattativa nell’offerta unica. Conservati messaggi, destinatari, ultimo esito e contatore tentativi; non uno storico separato di ciascun tentativo SMTP.
- Separato il trasporto SMTP condiviso in proposal-mail.transport.ts; evitati cicli tra servizi.
- Nuova migrazione 20261015120000_case_notifications. Configurazione SMTP invariata.
- Build backend/frontend e tutti i nove script di test superati, incluso test-notifications.cjs. SMTP simulato: nessuna email reale inviata.
- Pacchetto Aggiornamento cumulativo: 67 file verificati. Nota operativa: AGGIORNAMENTO-NOTIFICHE-TRATTATIVA.md.
- Collaudo NAS ancora rinviato. Restano editor cliente, OTP, attività/richiami, varianti dopo conferma e verifica incasso prima degli ordini.

---

## 15 ottobre 2026 — Ripresa: email delle revisioni e storico invii

- Ripreso il lavoro dal checkpoint del 14 ottobre. Non è ancora confermato il deploy sul NAS degli ultimi blocchi.
- Aggiunti preparazione e controllo di destinatario, messaggio e PDF della revisione immutabile, seguiti dal pulsante esplicito «Invia email al cliente».
- Destinatario ricavato dalla revisione; collegamento cliente verificato sul server. La UI genera il PDF dalla revisione e dalle immagini salvate; il backend controlla proprietà, snapshot/hash, collegamento, formato base e dimensione. Il contenuto semantico del PDF non viene certificato dal backend.
- Storico per revisione: destinatario, oggetto, testo con segreto oscurato, hash dello snapshot/PDF, copia allegato, date, message-id e stato.
- Stati SMTP_ACCEPTED, FAILED, UNKNOWN, SENDING. L’accettazione SMTP non equivale a consegna o lettura.
- Richieste ripetute non reinviano la stessa email. Timeout incerti non generano reinvii automatici; un nuovo tentativo richiede una nuova preparazione e verifica della casella.
- Copia archiviata del PDF scaricabile con accesso del proprietario. Nessun token cliente in chiaro nello storico invii.
- Nuova migrazione additiva: `20261015090000_proposal_deliveries`.
- Configurazione SMTP esistente in backend.env. PUBLIC_APP_URL opzionale; valore predefinito https://pergolando.rdsign-app.it. Nessuna credenziale modificata o inclusa nel pacchetto.
- Test SMTP simulato, nessuna email reale inviata. Test invii superato e regressione completa degli altri sette script superata; controllo TypeScript, compilazione backend e build di produzione frontend superati.
- Documentazione: `AGGIORNAMENTO-EMAIL-OFFERTE.md`. Aggiornamento cumulativo di 61 file verificati (include questo changelog) da copiare sul NAS; mantenere backend.env, .env e volumi, fare prima il backup del database, poi rebuild backend/frontend e restart gateway.

### Prossima ripartenza

1. Collaudare sul NAS il flusso completo e un invio esplicito dal telefono con SMTP reale; verificare allegato e collegamento ricevuti.
2. Aggiungere notifiche di accettazione al rivenditore e conferma/rifiuto al cliente, con esiti tracciati.
3. Editor dei dati cliente, OTP, varianti dopo conferma e verifica dell’incasso al rivenditore restano da completare prima degli ordini ai produttori.
4. Gli altri blocchi del piano (ruoli, ordini, consegne, posa, assistenza, report e traduzioni) restano aperti.

La sezione del 14 ottobre sotto è storica: il limite «invio email della revisione unica non presente» è superato da questo blocco. Notifiche automatiche e verifica di consegna restano assenti.

---

## 14 ottobre 2026 — Chiusura giornata e punto di ripartenza

**Stato:** sviluppo locale completato per i blocchi descritti sotto, test e build superati. Gli ultimi aggiornamenti sono preparati per il NAS; non risulta confermato in questa sessione che siano già stati copiati, compilati e collaudati sul dominio pubblico. Non considerare il sito pubblico automaticamente aggiornato.

Questa sezione è il riferimento attuale per riprendere il lavoro. Le sezioni precedenti conservate più sotto sono cronologia storica e possono descrivere architetture o limiti successivamente superati.

### Decisioni del progetto da mantenere

- Un ambiente separato per ogni rivenditore, con più cataloghi/marchi secondo i suoi contratti.
- Una pratica può contenere più prodotti e più marchi, con un’unica offerta al cliente.
- I cataloghi estratti devono essere verificati manualmente dal rivenditore con prove prima dell’approvazione.
- Acconti e saldi della commessa sono del rivenditore. L’abbonamento a Pergolando è un rapporto separato e non viene ripartito sulle commesse.
- Manodopera interna: ore effettive della squadra × costo orario della squadra.
- Margine diretto della commessa distinto dall’eventuale quota di altre spese generali; incassi e pagamenti separati dal risultato economico.
- L’assistenza deve poter partire alla consegna/collaudo anche se una fattura del produttore arriva dopo.
- L’app venditore deve restare semplice da usare sul telefono. I prodotti importati senza modello 3D seguono il percorso senza ambientazione.

### Modifiche realizzate

**1. Pratiche multi-prodotto e multi-marchio**

- Archivio `/pratiche`, dati cliente e righe prodotto persistenti sul backend.
- Prezzi dei prodotti preconfigurati ricalcolati sul server al salvataggio.
- Modifica con controllo versione, esclusione reversibile e ripristino delle righe.
- Accesso limitato al proprietario della pratica; non ancora condivisione tra account diversi dello stesso rivenditore.

**2. Conto economico della commessa**

- Ricavi e costi previsti/effettivi, produttori, trasporto, trasferte, altri costi e manodopera.
- Calcolo ore × costo orario squadra; spese generali separate dal margine diretto.
- Acconti, saldi e uscite nel flusso di cassa senza doppio conteggio dei ricavi/costi.
- Storico delle sostituzioni, allegati originali e deduplicazione dei documenti.
- Costi incompleti segnalati come provvisori; consegna indipendente dalla chiusura economica.
- Esportazione CSV. Inserimento ancora manuale, senza lettura automatica della casella email.

**3. Offerta unica, revisioni e immagini**

- Revisioni immutabili dell’offerta con prodotti, sconto sui prodotti, posa, trasporto, IVA, acconto, saldo, validità e condizioni.
- PDF A4 orizzontale multi-prodotto.
- Salvataggio esplicito dell’ambientazione finale e delle tre viste tecniche disponibili per riga prodotto.
- Le revisioni mantengono le immagini salvate in quel momento; cambiare il prodotto invalida le immagini correnti della riga, senza modificare le vecchie offerte.
- Non viene ancora salvata l’intera sessione fotografica: foto originale, punti e camera non sono ripristinabili come sessione di lavoro.

**4. Cataloghi del rivenditore sul server**

- Archivio `/cataloghi`, originali conservati, versioni e bozze modificabili.
- Upload degli originali in blocchi con verifica SHA-256 e ripresa del caricamento.
- Prove manuali per ogni tabella: minimo, massimo, un altro prezzo e un caso fuori intervallo. La regola della fascia superiore richiede una prova specifica.
- Modifiche a tabelle o originali invalidano le prove precedenti.
- Approvazione esplicita del rivenditore e blocco della versione approvata; nuove modifiche tramite nuova versione.
- L’approvazione descrive i controlli del rivenditore, non certifica automaticamente ogni combinazione possibile.
- L’estrazione resta nel browser: PDF con testo e CSV; OCR, lettura nativa Excel e regole tecniche/supplementi automatici non aggiunti.

**5. Prodotti importati nelle pratiche**

- Da una pratica esistente: «Aggiungi da un catalogo approvato».
- Accesso anche dalla scelta catalogo delle Demo 1/2, conservando la pratica e passando al percorso senza 3D.
- Prezzo base ricalcolato dal backend sulla versione approvata; supplementi espliciti del venditore distinti nelle voci.
- Conservati catalogo/versione/hash, tabella/pagina, regola dimensionale, misure e colore.
- Modifica dal catalogo originale, esclusione/ripristino e inclusione nell’offerta unica insieme a Flag/Brera.
- I prodotti importati non generano automaticamente modello Blender, disegni tecnici o foto nel PDF unico.

**6. Ultimo blocco completato: pagina riservata al cliente**

- Dalla revisione dell’offerta: «Crea collegamento cliente».
- Pagina `/offerta#<segreto>` accessibile senza login venditore: revisione congelata, prodotti, condizioni, immagini e download PDF.
- Segreto casuale: nel database è conservato solo l’hash. Il collegamento completo appare alla creazione.
- Accesso per 30 giorni; accettazione bloccata dopo la validità dell’offerta. Scadenza dell’offerta considerata fino a fine giornata UTC.
- Nuovo collegamento revoca quelli precedenti non accettati della stessa pratica; revoca manuale disponibile.
- Registrazione della richiesta del cliente con nominativo, email, dichiarazione e data. Se presente nell’offerta, l’email deve coincidere.
- Il rivenditore usa «Aggiorna stato cliente», quindi conferma dopo verifica tecnica oppure rifiuta con motivazione e riapre la trattativa.
- Stato pratica: bozza / accettazione da verificare / confermata.
- Una proposta già confermata non è modificabile tramite questo flusso; varianti e annullamenti dopo conferma restano da implementare.
- Nessuna scrittura automatica di ricavi o incassi, nessun ordine ai produttori.
- **Non ancora presenti:** invio email della revisione unica, notifiche automatiche, OTP per l’identità cliente, firma digitale e pagamenti online. Il link va condiviso manualmente. Pagina cliente attualmente in italiano.

### Verifiche eseguite oggi

- Generazione client Prisma, compilazione backend NestJS, controllo TypeScript e build di produzione Next.js superati.
- Test su database SQLite temporanei: `test-cases.cjs`, `test-finance.cjs`, `test-proposals.cjs`, `test-media.cjs`, `test-dealer-catalogs.cjs`, `test-imported-cases.cjs`, `test-invitations.cjs`.
- Coperti isolamento, prezzi server, richieste ripetute, versioni, revisioni immutabili, originali/checksum, approvazione cataloghi, token/revoca/scadenza, immagini autorizzate, accettazione/conferma/rifiuto e assenza di ricavi/incassi duplicati.
- Verificata anche l’accettazione ripetuta/contemporanea dello stesso collegamento.
- PDF dimostrativi delle revisioni verificati anche visivamente nel precedente blocco immagini.
- Nessuna email reale, pagamento, ordine a produttori o nuova generazione IA eseguiti durante questi test.

### Aggiornamento pronto e configurazione da preservare

- Cartella di lavoro: `D:/Lavori/App/Pergolando_chatgpt`.
- Cartella `Aggiornamento`: **55 file cumulativi**, ricopiati dai sorgenti e verificati tramite hash. Il presente changelog resta nella cartella principale, non aggiunto al pacchetto.
- Destinazione NAS: `/home/davideromeo/Pergolando-chatgpt`.
- Copiare il contenuto di Aggiornamento mantenendo i percorsi, dopo backup del database/volume.
- Non sostituire `.env`, `backend.env` o i volumi. Non usare `prisma migrate reset`.
- Il backend del pacchetto NAS esegue `prisma migrate deploy` all’avvio.
- Migrazioni additive incluse: `20261014090000_customer_cases`, `20261014120000_case_finance`, `20261014150000_case_proposals`, `20261014180000_case_media`, `20261014210000_dealer_catalogs`, `20261014230000_proposal_invitations`.
- `.env` principale: token tunnel. Configurazione applicativa nel `backend.env` principale; i file `.env.example` non sono configurazione runtime.
- Dominio pubblico: `https://pergolando.rdsign-app.it`.
- Ultimi indirizzi concordati per i servizi sul PC: GeoCalib `http://192.168.1.118:8090`, Blender `http://192.168.1.118:8080`; disponibilità da ricontrollare alla ripresa, non verificata in questo blocco.

Comandi NAS dopo la copia:

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build backend frontend
docker compose restart gateway
```

Documentazione dettagliata: `PIANO-PERGOLANDO.md`, `AGGIORNAMENTO-CONTO-ECONOMICO.md`, `AGGIORNAMENTO-PRATICHE-OFFERTE.md`, `AGGIORNAMENTO-IMMAGINI-PRATICA.md`, `AGGIORNAMENTO-CATALOGHI.md`, `AGGIORNAMENTO-PRODOTTI-IMPORTATI.md`, `AGGIORNAMENTO-OFFERTA-CLIENTE.md`.

### Da dove ripartire domani

1. Verificare se i 55 file sono stati copiati sul NAS; se no, fare backup, copia, rebuild e controllo dei log/migrazioni.
2. Collaudare dal telefono una pratica mista: prodotto preconfigurato + prodotto da catalogo approvato → revisione unica → PDF → collegamento cliente → richiesta di accettazione → conferma/rifiuto del rivenditore.
3. Prossimo blocco proposto: invio email della revisione unica con PDF e collegamento, storico degli invii/esiti e notifiche al rivenditore. Usare la revisione immutabile e non ricostruirla dai dati correnti della pratica.
4. Completare verifica identità cliente/OTP e gestione delle varianti dopo conferma; poi verifica dell’incasso al rivenditore prima dell’avvio degli ordini. Eventuali pagamenti online richiedono ancora la scelta/configurazione del fornitore e del conto del rivenditore.
5. Restano nel piano: ruoli e condivisione autorizzata, attività/scadenze, ordini separati per produttore, conferme e consegne, acquisizione email/documenti, posa/collaudo, portale assistenza e report economici aggregati.
6. Completare traduzioni IT/EN dei nuovi moduli e il collaudo commerciale; non considerare i test locali equivalenti al collaudo sul NAS.

**Pausa richiesta dall’utente a fine giornata. Nessun ulteriore sviluppo avviato dopo questo salvataggio.**

---

Storico ad alto livello del lavoro svolto sul progetto Pergolando (Studio, App Venditore, deploy NAS), dall'inizio. Ogni repo (`pergolando-shared`, `pergolando-backend`, `pergolando-frontend`) ha comunque la propria cronologia Git dettagliata — qui teniamo un riassunto per fase/sessione.

## Fase 0 — Motore di calcolo condiviso (bundle schema + pricing engine)

- Letto il PRD e i file prototipo (`vision_database_v2.json`, `pergola_engine.py`, `brera_price_matrices.json`, `brera_database.json`, `vision_price_matrices.json`).
- Creato lo schema Zod del "bundle" (manifest, catalog/database, price_matrices, theme, assets) e portato in TypeScript il motore di calcolo prezzi Python (`pergola_engine.py` → `PergolaEngine`), con test di regressione a partire dai casi già validati (golden cases) su Vision e Brera.

## Fase 1 — Studio MVP (catalogazione)

- Costruita la prima versione di Studio (Next.js): creazione bozza (tenant id, nome azienda, template Vision/Brera/vuoto), upload PDF con estrazione testo/righe candidate, editor per mappare manualmente `database.json`/`price_matrices.json`, validazione (schema + coerenza matrici + smoke test motore), upload carta intestata, export bundle in zip versionato.
- Verificato a mano il flusso completo Brera: template → validazione → export.

## Fase 2 — App Venditore (architettura multi-tenant)

- Decisione architetturale (confermata con l'utente): **un deployment per cliente** (container/DB separati), non multi-tenant a livello di riga — ogni App Venditore serve un solo bundle, caricato via variabili d'ambiente (`BUNDLE_PATH`, `DATABASE_URL`).
- Creato il repo `pergolando-shared` (pacchetto `@pergolando/shared`, distribuito come git-dependency via tag, es. `v0.1.0`) per non duplicare schema e motore di calcolo tra Studio e App Venditore.
- Creati i repo `pergolando-backend` (NestJS + Prisma + SQLite, Argon2id, sessioni server-side, rate limiting, Pino) e `pergolando-frontend` (Next.js, i18n IT/EN, Playwright+axe-core), con Git Flow (`main`/`develop`) su entrambi.
- Prima slice funzionante: registrazione/login/logout venditore + caricamento bundle a boot + primo step del wizard (dati cliente, scelta prodotto/sotto-modello/variante).

## Fase C — Deploy Docker sul NAS (verifica end-to-end)

- Guidato il deploy reale sul NAS self-hosted, con l'utente che eseguiva i comandi in prima persona.
- Problemi affrontati e risolti:
  - Toolchain di compilazione mancante per moduli nativi (`better-sqlite3`, `argon2`) → aggiunti `python3 make g++` al Dockerfile.
  - Prisma 7: split di configurazione (`prisma.config.ts` per la CLI, driver adapter `@prisma/adapter-better-sqlite3` a runtime).
  - Spazio disco NAS esaurito → migrazione del `data-root` di Docker su un volume più grande.
  - Il primo volume scelto per la migrazione era NTFS (`fuseblk`), che non supporta i permessi Unix reali → ha rotto un container Postgres preesistente e non correlato (`x_rdsign-db-1`); risolto rifacendo la migrazione sul vero volume RAID ext4 (`/dev/md127`) e verificando che tutti i 12 container preesistenti fossero di nuovo sani.
  - Crash-loop a runtime di `pnpm exec prisma migrate deploy` (bloccato dal gate di sicurezza pnpm sulle build git-dependency) → risolto chiamando direttamente `node_modules/.bin/prisma migrate deploy`, bypassando pnpm a runtime.
  - Cloudflare Tunnel: interfaccia cambiata rispetto alla documentazione nota (route ora sotto Networking → Tunnels → Routes).
  - Certificato Universal SSL di Cloudflare copre un solo livello di sottodominio → rinominato l'hostname API da `api.pergolando.rdsign-app.it` (due livelli, nessun certificato valido) a `pergolando-api.rdsign-app.it` (un livello).
- **Verificato funzionante end-to-end** sul dominio pubblico reale `pergolando.rdsign-app.it`.

## Fase D — Registrazione con conferma email + recupero password (2026-09-20)

- **Backend**: flusso completo di verifica email via codice a 6 cifre (invio SMTP, TTL, tentativi massimi, cooldown reinvio) e recupero password con lo stesso meccanismo a codice. Nuovi endpoint: `verify-email`, `resend-verification`, `forgot-password`, `reset-password`. Nuova tabella `VerificationCode`, nuovo `MailService` (nodemailer, fallback a log se SMTP non configurato). Test unitari ed e2e aggiornati/aggiunti, tutti verdi. Mergiato in `main`/`develop` e pushato.
- **Frontend**: nuove pagine `/verify-email` (inserimento codice + reinvio) e `/forgot-password` (richiesta codice → nuova password). Login e registrazione aggiornati per instradare verso questi flussi. Mergiato in `main`/`develop` e pushato.
- **Verifica end-to-end**: testato in locale e poi sul NAS in produzione, inclusa la ricezione reale dell'email SMTP con codice.
- **Problemi affrontati durante il deploy NAS**:
  - Codice sul NAS non aggiornato (repo backend/frontend fermi a un commit precedente) → risolto con `git pull`.
  - Spazio esaurito su `/` (disco di sistema, 19G) durante la build Docker, nonostante il `data-root` di Docker fosse già stato spostato sul volume RAID grande in Fase C — causa: **containerd** ha una propria directory di stato (`/var/lib/containerd`) separata dal `data-root` di Docker, rimasta sul disco piccolo. Soluzione applicata: `docker builder prune -af` + `docker image prune -af` per liberare spazio subito; lo spostamento strutturale di containerd sul volume grande resta da pianificare (tocca tutti i container del NAS, non solo Pergolando).
  - Cancellazione di un account di test già registrato sul NAS tramite script diretto sul database (nessun endpoint di cancellazione account ancora previsto).

## Fase E — Studio: primo progetto reale "Flag" (Arquati) + upload logo/immagini (2026-09-20)

- Creato in Studio un progetto a partire dal PDF listino prezzi reale Arquati Privilege (prodotto **Flag**, tenda a caduta con guide, varianti 2/3/4 guide).
- Estratto e mappato manualmente `catalog/database.json` e `catalog/price_matrices.json` (prezzi per larghezza × sporgenza, 3 tabelle) a partire dal testo estratto dal PDF — validazione superata (schema + coerenza matrici + smoke test motore prezzi).
- **Nota aperta**: gli accessori a supplemento del listino (Trave Laterale, Angolare Laterale, Struttura Timpano, Guida aggiuntiva, ecc.) sono documentati nel bundle ma **non ancora prezzati dal motore di calcolo** — il motore gestisce solo il prezzo base della struttura. Da valutare se estendere lo schema/motore condiviso per supportarli.
- **Nota aperta**: `H_max_cm` e `passo_lama_cm` nel bundle Flag sono placeholder (il listino non li specifica per questo prodotto) — da confermare con l'ufficio tecnico Arquati prima di un uso in produzione.
- **Prodotto Skipper** (stesso catalogo Arquati, tenda a caduta verticale) non incluso in questo bundle — richiederà un bundle/tenant a sé, coerente con l'architettura "un prodotto per bundle".
- Aggiunta a Studio una nuova funzionalità: upload **logo** (sezione Branding) e upload **foto/rendering prodotto** (nuova sezione, con tag opzionali prodotto/sotto-modello/variante/colore). L'export del bundle ora copia automaticamente logo e immagini e genera `assets/manifest.json`. Verificato end-to-end con file di prova, poi ripulito.
- Modifiche non ancora committate su Git a fine sessione (`apps/studio/src/lib/storage.ts`, `apps/studio/src/lib/export-bundle.ts`, `apps/studio/src/components/DraftEditor.tsx`, nuove route `api/drafts/[draftId]/logo`, `api/drafts/[draftId]/assets`).

## Fase F — Pipeline 3D parametrica Flag in Blender (in corso)

- Pivot rispetto all'idea iniziale di rendering fotorealistico via Gemini/Nano Banana (Fase E, "Nota aperta"): dopo aver verificato un limite reale di accuratezza sull'AI image generation statica, deciso di costruire prima un **modello 3D parametrico reale** (Blender, competenza pregressa dell'utente), da collegare in un secondo momento a una pipeline di compositing su foto reali (OpenCV + ControlNet) — quest'ultima parte resta solo concordata concettualmente, non implementata.
- Collegato Blender a Claude Code via **BlenderMCP** (sessione interattiva, stesso file `.blend` condiviso in tempo reale — l'utente vede/corregge dal vivo nel proprio Blender).
- Resa completamente parametrica la geometria del modello Flag (`3d/flag.blend`): montanti, travi, guide (con inclinazione calcolata via Pitagora sui parametri reali L/P/Δh), supporti, frangivento (spaziatura e conteggio dinamici), tettuccio (pattern di nervature rigenerato per periodo misurato), telo, timpano/trave laterale opzionali. Implementate entrambe le varianti di fissaggio (autoportante a 4 pilastri / a parete-soffitto) come collection Blender alternative.
- Validato con un primo test end-to-end su dimensioni reali diverse da quelle di riferimento (560×450cm, Δh 60cm) — la logica generalizza correttamente; poi riportato allo stato di riferimento 3x3 per assorbire nuovi file `.fbx` inviati dall'utente (pezzi ridisegnati, nuovi elementi opzionali).
- Dettagli tecnici (convenzioni assi, costanti di calibrazione, tecniche per pezzo, bug reali incontrati e relative fix) documentati in `3d/NOTES.md`, per continuità tra sessioni.
- **Nota aperta**: due elementi nuovi (`Pilastrino_intermedio`, `Skipper`) importati ma non ancora spiegati/lavorati.
- **Obiettivo finale non ancora iniziato**: formalizzare tutto in uno script headless invocabile dal backend con i parametri reali del preventivo, per generare export GLB/USDZ automaticamente.

## Fase G — App Venditore: pipeline "componi su foto reale" (in corso)

Pipeline concordata in 6 passi per inserire il modello 3D nella foto reale del cliente: 1) foto scattata dal venditore, 2) tocco di punti di riferimento sulla foto, 3) OpenCV calcola la prospettiva, 4) il modello 3D viene posizionato/renderizzato con quella prospettiva, 5) estrazione di una mappa strutturale (bordi/profondità), 6) foto + mappa → API ControlNet ospitata → immagine finale fotorealistica. Si procede in ordine, un passo alla volta.

- **Passo 1** (`pergolando-frontend`): nuova sezione nel wizard per scattare/caricare la foto del luogo di installazione (solo stato locale per ora, nessuna persistenza).
- **Passo 2** (`pergolando-frontend`): nuovo componente `FotoRiferimentoPunti` — il venditore tocca 4 punti sulla foto, in ordine fisso (piede anteriore sinistro/destro, posteriore sinistro/destro), con marker numerati rimovibili. Bug reale trovato e corretto durante il test: tap ravvicinati si sovrascrivevano per una race condition su stato React non aggiornato — risolto con aggiornamento funzionale dello stato.
- **Passo 3** (`pergolando-backend`): nuovo endpoint `POST /catalog/perspective` — usa OpenCV (`@techstark/opencv-js`, build WASM, **non** binding nativi: niente compilazione C++ da gestire in Docker, a differenza di `better-sqlite3`/`argon2` in Fase C) per risolvere la posa della camera (`solvePnP`) dai 4 punti e riproiettare i 4 angoli del piano del tetto sulla foto. Il frontend disegna il risultato come overlay SVG (wireframe) sopra la foto — prova visiva concreta che la pipeline geometrica funziona, ancora prima che esista il vero compositing 3D del passo 4.
- **Approssimazione dichiarata**: senza calibrazione reale della fotocamera, si assume un campo visivo orizzontale plausibile (60°, tipico di uno smartphone) — non è una misura reale, è un'assunzione ragionevole per una foto singola non calibrata.
- Verificato end-to-end in locale (login reale, calcolo preventivo reale, foto sintetica di test, 4 punti simulati, overlay renderizzato correttamente).
- **Passo 4** (`3d/generate_flag.py`, nuovo): prerequisito indispensabile — trascritto tutto il lavoro di parametrizzazione interattiva della Fase F in uno **script Blender headless riutilizzabile** (`build_pergola(L, P, H, deltaH, fissaggio)`), che apre `flag.blend` in background, applica tutte le tecniche validate finora, e renderizza. **Non scrive mai su `flag.blend`** — solo render/export. Aggiunta anche la conversione della posa camera calcolata al passo 3 (OpenCV `rvec`/`tvec`) in un transform camera Blender.
  - Scoperta durante la stesura: le costanti di calibrazione per-pezzo si semplificano algebricamente a un'unica formula universale (`P_cm - 300`) per lo spostamento in profondità.
  - Bug reale trovato e corretto: la logica del Telo riusava la pendenza vecchia della guida invece di quella nuova (mascherato durante il lavoro interattivo perché lì si aggiornava un pezzo alla volta).
  - **Verificato con render headless**: dimensione di riferimento (riproduce l'originale), dimensione diversa (450×350, generalizza correttamente), variante a parete (corretto, niente pilastri posteriori), e — verifica numerica precisa — una posa camera reale calcolata dal passo 3 riproietta i piedi del modello esattamente dove erano stati "toccati" in input (scarto di 1-2px su 1200).
- **Passo 4 collegato al backend/frontend**: nuovo endpoint `POST /catalog/render3d` (`pergolando-backend`) — chiama Blender come processo esterno (`child_process.execFile`, argomenti passati come array, mai una stringa di shell) con la posa camera del passo 3, e restituisce il PNG trasparente. Nel wizard, nuovo bottone "Genera anteprima 3D" che lo mostra sovrapposto alla foto (stesso schema dell'overlay SVG del passo 3).
  - **Verificato end-to-end dal vivo**: login reale, preventivo reale, foto di test, 4 punti, prospettiva calcolata, anteprima 3D generata e composita correttamente sulla foto — le gambe del modello atterrano esattamente nei punti toccati.
  - **Due semplificazioni dichiarate, da rivedere con l'utente**: (1) il campo `deltaHCm` (la salita del lato posteriore per lo scolo dell'acqua) non è ancora raccolto dal wizard come valore reale — stimato come 12% della sporgenza, in attesa di chiarire se coincide con "Altezza per calcolo inclinazione H1" o è un campo a sé; (2) il wizard offre solo fissaggio "a parete"/"a soffitto" (nessuna opzione autoportante) — entrambi oggi mappati sulla variante Blender "parete" (niente pilastri posteriori).
  - **Non ancora fatto**: Blender non è installato nel Docker del NAS (richiesto solo per il deploy in produzione, non per lo sviluppo locale) — **da decidere con l'utente**; materiali/colori reali nel render (oggi tutto grigio di debug); Timpano/Trave_Laterale restano esclusi (non ancora parametrizzati per L/P/H arbitrari).
- **Decisione architetturale su dove vive Blender**: Blender serve solo a costruire la mappa strutturale (profondità/edge) per il passo 5-6 della pipeline — non deve inventare forme, quel compito resta di Nano Banana/ControlNet. Non esiste una build "ridotta" ufficiale di Blender, quindi la scelta è stata isolarlo in un **container/servizio separato** (`pergolando-blender-service`, nuovo package) piuttosto che installarlo dentro l'immagine Docker del backend principale — così il backend resta leggero e il "blast radius" di questa dipendenza (~300MB) resta contenuto. Lo spazio su disco del NAS non è il vincolo (RAID con ~270GB liberi dopo lo spostamento dei dati NAS), la separazione è per igiene dell'immagine.
  - `pergolando-blender-service`: servizio HTTP minimale in Node (`node:http`, senza dipendenze esterne) che espone `POST /render3d` e invoca Blender headless (`execFile`, argomenti in array, mai stringa di shell) su `3d/generate_flag.py`, restituendo il PNG in base64. `Dockerfile` scarica la build ufficiale Linux di Blender (5.2.2, pinnata) nell'immagine; monta `3d/` come volume di sola lettura (uno script/modello aggiornato non richiede rebuild dell'immagine).
  - `pergolando-backend`: `Scene3dService` riscritto da chiamata locale (`execFile`) a **client HTTP** del nuovo servizio (`BLENDER_SERVICE_URL`, opzionale — 503 se assente, stesso pattern di `GEMINI_API_KEY`).
  - `docker-compose.dev.yml`: nuovo servizio `blender`, wiring di `depends_on`/`BLENDER_SERVICE_URL` sul `backend`.
  - **Verificato end-to-end in locale** (backend → servizio Blender via HTTP → Blender → immagine, per entrambe le varianti di fissaggio, autoportante e a parete).
  - **Non ancora verificato**: build Docker reale (`Dockerfile` del nuovo servizio + `docker-compose.dev.yml`) — **Docker non disponibile in questo ambiente di sviluppo**, va testata da Davide o in un ambiente con Docker prima del deploy sul NAS, in particolare l'elenco esatto delle librerie condivise Debian richieste da Blender headless.
- **Passo 5 (mappa di profondità) — solo lo script, non ancora collegato**: `generate_flag.py` ha ora una modalità `render_depth_map` che produce la vera mappa strutturale per ControlNet (non il render "debug" a colori usato finora) — depth pass di Blender normalizzato via Map Range, mascherato con l'alpha per azzerare lo sfondo. Scoperte reali (API del compositor cambiata in Blender 5.x, verificate empiricamente): `scene.node_tree` non esiste più, sostituito da `scene.compositing_node_group` (un vero node group, richiede `interface.new_socket` + `NodeGroupOutput`); i nodi `CompositorNodeMath`/`CompositorNodeMapRange`/`CompositorNodeComposite` non esistono più nel compositor, funzionano gli equivalenti `ShaderNode*`. **Non ancora esposto**: né `Scene3dService`/`RenderScene3dDto` né il wizard sanno ancora richiedere questa modalità — resta da collegare a un endpoint/UI (passo 6, il compositing ControlNet vero e proprio, non è ancora iniziato).
- **Riscrittura completa di `generate_flag.py` — architettura a "perno fisso" (2026-09-27)**: il sistema precedente (ogni pezzo spostato con una formula di offset propria, calibrata a mano) continuava a rompersi in modo imprevedibile su dimensioni diverse da quella di riferimento (Frangivento troppo vicino alla Guida, Tettuccio che la intersecava, scarti che crescevano con le dimensioni). Su proposta di Davide: **Guida, Telo, tutti i Frangivento, Tettuccio e Supporto ora ruotano insieme, rigidamente, attorno a un unico perno fisico reale** — il foro di una "zanca" di aggancio visibile sulla Guida stessa, trovato per clustering dei vertici (stabile a 176 vertici entro 4-5cm) e confermato identico su due file preparati indipendentemente da Davide. Una rotazione pura preserva per costruzione ogni relazione tra i pezzi, eliminando la classe intera di bug del sistema a offset.
  - **Cambio di convenzione degli assi**: l'origine del mondo (Y=0) è stata spostata una volta per tutte al punto più posteriore di `Aggancio_Parete` (il bracket a parete) — prima era un punto "centrato" arbitrario. La profondità (SP) ora misura sempre da lì; il retro della pergola è fisso nello spazio, solo il fronte si allontana con SP.
  - **Nomenclatura reale del venditore, ora documentata**: il modulo d'ordine usa L (larghezza), SP (profondità — il nostro `P_cm`), P (altezza frontale — il nostro `H_cm`), H (altezza posteriore), H1 (H−P — il nostro `deltaH_cm`). Non ancora rinominato nello script per non toccare il contratto wizard/backend prima di aggiornarli insieme, ma documentato in `3d/NOTES.md` per evitare confusione nei test.
  - **Verificato**: riproduzione esatta (scarto zero) a dimensioni di riferimento; render headless coerente a L=400/SP=400/H=200/Δh=50; test dal vivo con Davide su L=550/SP=480 (altezza frontale 220, posteriore 270) — confermato corretto.
  - **Bug reali trovati e corretti durante la riscrittura**: object transform (`location`) e coordinate dei vertici sono due spazi diversi — ignorare una `location` residua (retaggio del sistema vecchio) rompeva la rotazione; due pezzi (`Frangivento_Iniziale_Finale`/`_Finale`) condividevano lo stesso datablock mesh nel file (stesso pezzo fisico installato alle due estremità, per design) e modificarne uno corrompeva l'altro; la larghezza di alcuni pezzi veniva applicata due volte (una assoluta via stretch, una relativa via shift) sommandosi per errore.
  - **Bug reale nelle nervature del Tettuccio**: `bmesh.ops.delete` per vertici cancella a cascata anche le facce collegate — con la mesh non perfettamente simmetrica (~2cm di differenza reale tra i due lati), la soglia di taglio cadeva dentro una faccia grande solo a destra, cancellandola tutta e lasciando un buco visibile. Risolto allargando il margine di sicurezza della soglia di taglio; e semplificato su indicazione di Davide (le nervature possono estendersi sotto le facce di chiusura senza problemi, quindi il loro raggio si calcola dal bordo esterno vero, non da cosa sopravvive al taglio).
  - **Non ancora fatto**: `setup_camera_from_pnp` (pipeline foto reale, passi 3-4) non è stata riverificata dopo il cambio di convenzione degli assi; Timpano/Trave_Laterale/Pilastrino_intermedio/Skipper restano esclusi.

- **Passo 6 — compositing fotorealistico su foto reale via Gemini (2026-09-28)**:
  - **Architettura reale** (diversa da quanto concordato): il passo 6 originale nel piano era "mappa strutturale → ControlNet ospitato → immagine finale". ControlNet è un meccanismo di Stable Diffusion e non esiste nell'API Gemini — questa assunzione era rimasta implicita senza essere mai verificata. Decisione: **tenere Gemini** (qualità estetica superiore, latenza bassa, costo inferiore) e migliorare la tecnica di conditioning tramite immagini di riferimento multiple e parametri di generazione.
  - **`RenderFinaleService`** (`pergolando-backend`): nuovo servizio `POST /catalog/render-finale` che orchestra il passo 6 — riceve la foto reale + la sagoma grigia (render geometrico del passo 4), aggiunge fino a 3 render isolati puliti dello stesso modello da angolazioni diverse (`isometrico`, `laterale`, `dall_alto` via `Scene3dService`), e chiama Gemini con tutto questo come contesto visivo + prompt. I render di riferimento sono **best-effort**: se `Scene3dService` non è raggiungibile, il ciclo salta quell'angolo e procede ugualmente.
  - **Shading FLAT per i render di riferimento** (`3d/generate_flag.py`): i render isolati usano Workbench FLAT (niente sole, niente ombre) invece del renderer di default. Motivazione: la luce direzionale proiettava ombre sulle nervature del Tettuccio che — a bassa risoluzione — erano visivamente indistinguibili da gap tra lamelle bioclimatiche, fornendo a Gemini un segnale visivo sbagliato. Con FLAT, la geometria appare esattamente com'è, senza artefatti di illuminazione.
  - **Prompt rinforzato** (`prompt.ts`, funzione `buildCompositePrompt`): aggiunti vincoli espliciti dopo test in cui Gemini allucinava coerentemente: (1) "NON è una pergola bioclimatica" subito dopo il nome prodotto; (2) paragrafo dedicato alla continuità del telo ("UNA SOLA superficie continua e sigillata, senza fessure…"); (3) trave anteriore rafforzata ("NON un tubo, rullo, tamburo o cassonetto cilindrico"); (4) vincolo esplicito sul tettuccio in `buildCompositePrompt` ("UNICO pannello continuo e piatto… NON è un tetto a lamelle/doghe orientabili"). La stessa checklist strutturale è condivisa anche da `buildRenderPrompt` (render isolato, passo 5b) via `structuralChecklist()`.
  - **`temperature: 0.2, topP: 0.8`** nel `generateContent` di `render-finale.service.ts` — fix decisivo. Prima del fix, i parametri di default (temperature ~1.0) lasciavano il modello libero di scivolare verso il suo prior ("pergola bioclimatica" è il tipo più frequente nei dataset di addestramento): rullo avvolgitore, tetto a lamelle, luci a filo. Con temperature 0.2 il campionamento è molto meno "creativo" e il modello rimane ancorato alle immagini di riferimento — confermato via confronto visivo: nessun rullo, nessuna luce, tetto continuo piatto, carrelli visibili sulla trave anteriore (dettaglio del prodotto reale, non un'invenzione).
  - **Scoperta sul vocabolario**: i carrelli/supporti in plastica sulla trave anteriore (un dettaglio costruttivo reale e corretto del modello) erano stati inizialmente scambiati per un'allucinazione. Dopo confronto con le foto di riferimento, confermati come dettaglio autentico — il prompt è stato aggiornato per descriverli esplicitamente e non confonderli con un "rullo continuo".
  - **Risultato**: il render finale a temperature 0.2 non allucinava né rullo né lamelle né luci; la struttura corrispondeva alle immagini di riferimento. Test eseguito una sola volta — la stabilità statistica (2-3 run) è ancora da verificare.
  - **`Tettuccio_Lato_Dx/Sx`**: confermato rimosso manualmente da Davide da `flag.blend` — le mesh erano ancora nella scena ma il codice che le generava era già stato eliminato nella sessione precedente; Davide ha completato la pulizia a mano, verificato via query headless.

## Rimasto in sospeso

- Pubblicare Studio su un indirizzo del NAS (es. `pergolando.rdsign-app.it/studio`) — oggi Studio esiste solo come dev server locale, mai containerizzato né deployato.
- Committare le modifiche Studio (logo/immagini) elencate sopra.
- Decidere se estendere il motore di calcolo per prezzare gli accessori Flag a supplemento.
- Spostare la directory di stato di containerd sul volume RAID grande del NAS (intervento a livello di sistema, da pianificare con calma).
- **Passo 6 — stabilità**: eseguire 2-3 render-finale aggiuntivi a temperature 0.2 per confermare che il risultato corretto non sia un campione fortunato di un modello non deterministico.
- **Passo 6 — fixture di test realistica**: creare una coppia foto/sagoma con la pergola effettivamente posizionata contro una parete reale (la fixture attuale `abs_position_render.png`+`1.jpg` ha la silhouette isolata sul prato, Gemini deve inventarsi il contesto ogni run — confronti cross-run rumorosi).
- **`setup_camera_from_pnp`**: riverificare la conversione OpenCV→Blender della posa camera dopo il cambio di convenzione degli assi introdotto nella riscrittura a perno fisso.
- **`prompt.spec.ts`** (`pergolando-backend`): test pre-esistente che cerca stringhe "DA SOTTO"/"TRE" non più presenti nel prompt attuale — da aggiornare separatamente.









## 16 ottobre — Preparazione ordini per produttore
Pagina ordini, raggruppamento con dati verificati dal rivenditore, snapshot e blocchi server su proposta/acconto/cataloghi. Migrazione supplier_orders. Test ordini/acconti e compilazione locali passati. Invio esterno, PDF di acquisto e arrivi ancora da sviluppare. Vedere AGGIORNAMENTO-ORDINI.md.


## 16 ottobre — PDF e invio ordini ai produttori
PDF server multipagina senza prezzi cliente, anteprima email e invio esplicito, archivio allegati e storico SMTP; blocchi su invio duplicato/incerto e stato economico/tecnico. Migrazione supplier_order_delivery. Test locali con SMTP simulato e mobile superati. Nessun invio reale/deploy. Conferme e arrivi ancora da implementare.


## 16 ottobre — Conferme produttori e arrivi parziali
Conferme con riferimento, costo netto verificato e data promessa; quantità ricevute cumulative per riga, rettifiche e storico con autore. Allegati originali protetti, controlli server/revisioni/retry. Migrazione supplier_order_events. Test locali e mobile superati; nessun costo automatico o deploy NAS. Prossimo: collegamento versionato al conto economico.


## 16 ottobre — Costi ordini nel conto economico
Conferme previste e fatture cumulative effettive collegate per ordine/produttore; aggiornamenti sostitutivi e storico, stato parziale/definitivo e documento originale. Sostituzione esplicita delle voci manuali, blocco delle modifiche fuori ordine. Cassa e assistenza separate. Migrazione order_costs. Test locali superati; nessun deploy NAS.


## 16 ottobre — Pianificazione posa
Appuntamento provvisorio/confermato/annullato con squadra, orari, durata e mezzi; verifiche materiali/cantiere e cliente, conflitti squadra, storico e riconferma su condizioni cambiate. Migrazione installation_planning. Build/test backend e mobile superati. Nessuna notifica reale o deploy NAS.


## 16 ottobre — Checklist e verbali consegna
Pagina consegna, controlli generali obbligatori con note, esiti con/senza riserve o lavori non completati, foto nel PDF e originali protetti. Revisioni immutabili e stato consegna separato dai costi; gestione attraverso verbale dopo prima registrazione. Migrazione handovers. Build/test e mobile superati; PDF renderizzato. Nessun deploy o invio reale.


## 16 ottobre — Portale assistenza e ticket
Accessi riservati revocabili dopo consegna, invito email esplicito e stato SMTP, richieste con foto, risposte e riapertura. Gestione stato/priorità/responsabile, note interne separate dal messaggio pubblico, storico e concorrenza. Migrazione support. Test backend/mobile passati; nessuna email reale o deploy NAS.


## 16 ottobre — Notifiche automatiche assistenza
Coda transazionale ticket/risposte/cambi stato, avvisi minimi senza note interne o token, worker SMTP e storico tentativi. Verifica destinatari/accesso prima dell’invio, retry esplicito dei fallimenti e blocco degli esiti incerti. UI storico/retry e indicazioni al cliente. Migrazione support_notifications. Build/test backend/mobile passati, nessuna email reale o deploy NAS.



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

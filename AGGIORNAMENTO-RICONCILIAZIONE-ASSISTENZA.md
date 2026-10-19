# Riconciliazione dei costi assistenza — 16 ottobre 2026

## Collegamenti espliciti

Pratica → Assistenza → ticket → intervento → Consuntivo interno → Collegamenti al conto economico.

La schermata mostra separatamente il consuntivo da registrare, il costo già gestito dall’intervento e le voci manuali attive dello stesso tipo disponibili per il collegamento: manodopera, ricambi usati e altri costi diretti. Non associa documenti o importi in base a probabilità, nomi o somiglianze.

Il rivenditore seleziona una voce manuale soltanto se è interamente riferita a quel costo dell’intervento. La schermata esplicita l’importo precedente e la differenza rispetto al nuovo consuntivo. I valori non vengono sommati. Occorre verificare nuovamente sia i costi sia il salvataggio. I collegamenti si applicano al completamento o alla rettifica del consuntivo.

Il collegamento è possibile anche quando il consuntivo è già stato registrato e il doppione viene scoperto dopo. In questo caso la nuova voce sostituisce il costo gestito precedente e riconcilia anche la voce manuale scelta. Entrambi gli originali rimangono nello storico; solo il nuovo consuntivo è conteggiato. La voce manuale consumata non può essere riutilizzata da un altro intervento, da un ordine o da una rettifica manuale.

Si può riconciliare una voce per tipo in ciascun salvataggio. Per più voci dello stesso tipo procedere con rettifiche successive, verificando ogni collegamento. Non è prevista la ripartizione automatica di una fattura fra più lavori o fra più tipi di costo: non selezionare una fattura condivisa come se appartenesse interamente a questo intervento.

## Originali, revisioni e storico

L’eventuale documento collegato alla voce manuale viene mantenuto sul costo dell’intervento; alle rettifiche successive il collegamento resta disponibile. Gli originali sono consultabili nella schermata e nell’archivio documenti del conto economico. Lo storico dei consuntivi distingue le voci conteggiate da quelle sostituite e segnala i collegamenti di riconciliazione.

Una nuova rettifica parte senza riproporre automaticamente i vecchi collegamenti manuali: le voci già riconciliate non sono nuovamente selezionabili. La nuova interfaccia verifica anche la revisione economica letta; se il conto cambia prima del completamento, serve aggiornare i collegamenti e rileggerli. La lettura delle voci e della revisione avviene in una transazione coerente.

Le previsioni originarie restano distinguibili dal consuntivo. Una successiva voce prevista duplicata, riconciliata come tale, non crea una seconda previsione dello stesso costo. Non viene modificato l’importo di una fattura originale.

## Conto economico e chiusura

Nel conto compare un riepilogo assistenza con costi effettivi gestiti dagli interventi, interventi completati e interventi ancora da organizzare/eseguire. Questi costi sono già inclusi nei costi diretti: il riepilogo non li aggiunge una seconda volta. Storico e CSV identificano i collegamenti con l’assistenza e le voci manuali riconciliate.

La creazione di un intervento e i successivi aggiornamenti riaprono la verifica economica della pratica. Finché esistono interventi PLANNED o CONFIRMED non si può dichiarare che tutti i costi siano completi. Il controllo è anche sul server, con revisione e transazione. Gli interventi annullati non sono pendenti; i loro ordini devono comunque essere riconciliati secondo le regole già presenti.

La consegna e l’accesso assistenza rimangono indipendenti dal conto provvisorio. Acconti, incassi, ricavi e spese generali non vengono generati o modificati da questi collegamenti. L’abbonamento Pergolando continua a non essere ripartito sulle commesse.

## Aggiornamento NAS

Pacchetto cumulativo nella cartella Aggiornamento. Prima fare backup del database e degli allegati; poi copiare mantenendo i percorsi senza sostituire .env o backend.env.

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build backend frontend && docker compose restart gateway
```

Migrazione `20261016235950_support_cost_reconciliation`: riferimento economico aggiuntivo e indice univoco; le pratiche già dichiarate economicamente complete ma con interventi pendenti tornano da verificare, incrementando la revisione. Nessun costo originale cancellato. Nessun deploy NAS eseguito in questo blocco.

## Verifiche e seguito

Build backend/frontend; test su database temporaneo per adozione iniziale, doppione tardivo, totale unico, successive correzioni, originali, accessi, revisione economica, mancato riutilizzo della voce, previsioni e chiusura con interventi pendenti. Regressioni conto economico, interventi, preventivi, ordini ricambi e tracciamento ordini passate. Test browser con API simulate a 320/390 px: scelta del collegamento, verifica importi, salvataggio e riepilogo conto. Screenshot in output/support/riconciliazione-costi-mobile.png e conto-assistenza-mobile.png.

Nessuna email reale, chiamata IA o modifica del database operativo eseguita. Prossimo blocco: ricavi e incassi degli interventi di assistenza, con registrazione esplicita e collegamento alla versione commerciale accettata. Restano trasmissione SMTP ordini ricambi, acquisizione/riconciliazione fatture produttori, ripartizione documenti, resi, magazzino, carta intestata, EN e collaudo completo sul NAS.

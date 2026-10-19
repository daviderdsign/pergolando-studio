# Cataloghi — prove generate e copertura delle regole

Aggiornamento 16 ottobre 2026. Requisito corretto dall’utente: non basta verificare la griglia. Ogni opzione descritta nel catalogo deve essere rappresentata nel configuratore e nel calcolo automatico. I cinque preventivi sono un minimo di controllo, non una copertura sufficiente da soli.

## Implementato

- Il sistema genera dimensioni e risultati di prova sui dati strutturati, senza chiedere al rivenditore di inventare il test o inserire prima un prezzo atteso.
- Campioni distribuiti sulle celle disponibili, prova fascia superiore e caso fuori intervallo per ogni tabella. Almeno cinque configurazioni calcolabili distinte complessive, e tutti i casi generati, devono essere confermati manualmente uno alla volta.
- Il rivenditore confronta risultato e condizioni con il documento originale; può segnalare una differenza. Una differenza blocca l’approvazione e richiede correzione dati e nuova revisione. Nessuna autoapprovazione al quinto clic.
- Conferme con autore/data/nota, legate alla revisione. Modifiche a tabelle/originali invalidano la sequenza corrente, preservando lo storico.
- Foglio informativo apribile/scaricabile, copia del testo e autore conservati nell’approvazione. La verifica non viene presentata come esonero assoluto di responsabilità: eventuali condizioni contrattuali definitive richiedono revisione legale distinta.

## Limite importante: conversione completa dei PDF ancora da realizzare

L’attuale estrattore legge tabelle, testo e foto, ma non converte ancora tutte le note commerciali in un insieme completo di regole (colori, accessori, motori, supplementi, quantità, incompatibilità, vincoli, eccezioni, ecc.). Non dichiarare questa funzione completa.

Per le **nuove approvazioni** il backend ora blocca cataloghi PDF, pagine testuali, segnalazioni irrisolte e note riconosciute come condizioni/opzioni non strutturate, anche con cinque prove corrette. È un blocco prudenziale e visibile, non un analizzatore semantico completo. Cataloghi semplici di sole matrici CSV possono essere validati se privi di queste lacune e con tutte le prove conformi. Le versioni precedentemente approvate non vengono riscritte né revocate automaticamente; restano storiche, con i limiti del precedente motore.

Il lavoro successivo prioritario è quindi la conversione completa dei cataloghi, prima degli ordini: inventario di tutte le opzioni con fonte/pagina, regole strutturate di prezzo e fattibilità, collegamento al configuratore, casi generati che coprano ciascuna regola e combinazioni critiche, revisione manuale del rivenditore. Il numero di prove deve aumentare oltre cinque quando necessario. Non affidare al rivenditore il calcolo manuale degli extra come soluzione definitiva.

## Installazione e prove

Migrazione additiva 20261016120000_catalog_trials: campi di generazione/revisione nei controlli e testo/autore dell’approvazione. Fare backup DB e conservare ambienti prima di copiare Aggiornamento sul NAS, poi ricostruire backend/frontend e riavviare gateway.

Build backend/frontend superate; quattro test backend (nuove prove, cataloghi, prodotti importati, configurazione iniziale) e test Chromium mobile con API simulate superati. Verificati sequenza, cinque calcolabili più limite, isolamento, revisioni, storico, differenze e blocco di copertura anche lato server. Nessun deploy NAS eseguito.

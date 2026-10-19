# Pianificazione posa — 16 ottobre 2026

Nuova pagina /pratiche/:id/posa, raggiungibile dalla strada inferiore e dagli ordini. Squadra identificata dal nome normalizzato, data/ora e durata, mezzi/attrezzature, nota operativa. Tre stati: provvisorio, confermato, annullato; tutte le registrazioni conservate con autore e data. Spostamenti e annullamenti non cancellano gli appuntamenti precedenti.

Il provvisorio richiede offerta confermata e ordini della relativa revisione inviati (SMTP accettato) o confermati dal produttore. La conferma richiede anche indirizzo cantiere esplicito, conferme produttori e materiali già ricevuti oppure data promessa precedente al giorno di posa. Una consegna prevista lo stesso giorno richiede prima la registrazione degli arrivi effettivi. Nessuna affidabilità viene dedotta automaticamente: il rivenditore deve verificare consegne, cantiere, disponibilità di squadra/mezzi e accordo con il cliente.

Controllo di sovrapposizione con altre pose confermate dello stesso rivenditore e con lo stesso nome squadra (maiuscole e spazi normalizzati). Intervalli adiacenti consentiti. I provvisori non impegnano in modo esclusivo la squadra. Non è un calendario anagrafico delle risorse né un collegamento a calendari esterni: nomi diversi per la stessa squadra non sono automaticamente riconosciuti; mezzi e attrezzature restano una verifica manuale.

Cambio di indirizzo/offerta o rettifiche materiali che rendono insufficienti le condizioni fanno apparire la necessità di riconfermare, conservando il vecchio evento. Una prenotazione confermata da ricontrollare continua a occupare la squadra fino ad annullamento/riprogrammazione. Nessuna fattura o completezza economica richiesta per la posa; nessun costo/ora effettiva creato da un appuntamento.

Orari inseriti nel fuso del dispositivo, memorizzati con istanti UTC e durata. Revisioni concorrenti e retry idempotenti, proprietà verificata sul server. Nessuna notifica al cliente o sincronizzazione calendario automatica in questo blocco.

Migrazione additiva 20261016233000_installation_planning. Fare backup DB prima del deploy. Build backend/frontend e test su database temporaneo superati, compresi sovrapposizioni, stati, retry, materiali e cambi cantiere; test ordini/costi/setup passati. Chromium con API simulate a 320/390 px e screenshot verificato. Nessun deploy NAS, email reale, chiamata IA o migrazione del database operativo locale.

Prossimo blocco: checklist di posa, foto e documenti, verbale di consegna/collaudo ed eventuali riserve; poi attivazione assistenza e notifiche esplicite. La voce Posa nel percorso apre ora la pianificazione, ma non viene segnata come lavoro concluso da una semplice prenotazione. Interfaccia di questo blocco in italiano, traduzione EN da completare.

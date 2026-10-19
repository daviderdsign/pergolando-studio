# Interventi e ricambi assistenza — 16 ottobre 2026

Nella pratica, in Assistenza, ogni ticket contiene «Interventi e ricambi», riservato al rivenditore. Si possono creare più interventi, registrare squadra, appuntamento e durata, copertura da valutare/garanzia/a pagamento, materiali necessari, disponibili e utilizzati. La disponibilità è dichiarata dal rivenditore: non esiste ancora un magazzino sincronizzato.

## Controlli e costi

- Conferma appuntamento con squadra, data completa di fuso orario, durata, disponibilità materiali e accordo del cliente verificati.
- Controllo sovrapposizioni della medesima squadra con altre pose e interventi confermati. Gli intervalli adiacenti sono ammessi.
- Completamento solo dopo conferma: data effettiva, ore, costo orario della squadra, altri costi e quantità/costi dei ricambi usati espliciti. Gli zeri devono essere dichiarati.
- Manodopera = ore effettive × costo orario squadra. Ricambi = quantità usate × costo unitario. Costi netti IVA nel conto economico, anche per interventi in garanzia.
- Tre voci gestite dall’intervento: manodopera, ricambi, altri costi. Le rettifiche sostituiscono le precedenti, con storico; non sommano nuovamente i medesimi costi. La chiusura economica torna provvisoria.
- Il conto e gli ordini non possono rettificare direttamente le voci gestite da un intervento.
- Il servizio accetta collegamenti espliciti a costi manuali attivi dello stesso tipo; nell’interfaccia corrente si deve verificare di non avere già registrato manualmente gli stessi costi. La selezione guidata dei costi preesistenti resta da aggiungere.
- Un intervento completato può essere corretto, ma non annullato per far sparire costi sostenuti. Un ritorno richiede un nuovo intervento.
- Importo proposto al cliente separato: non crea ricavo, fattura né incasso. Preventivo assistenza e accettazione sono il prossimo blocco.

Il completamento non chiude automaticamente il ticket e non modifica la consegna. Solo un messaggio pubblico esplicito viene aggiunto alla conversazione e accoda un avviso al cliente; appuntamento, note, ricambi e costi restano interni. Storico revisioni consultabile dal rivenditore.

## Installazione NAS

Pacchetto cumulativo in Aggiornamento. Prima eseguire backup del database e dei file caricati, quindi copiare i file conservando i percorsi. Non sostituire .env o backend.env.

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build backend frontend && docker compose restart gateway
```

Nuova migrazione additiva `20261016235920_support_works` (interventi/eventi e riferimento nei costi). Il normale avvio del backend applica le migrazioni secondo la configurazione Docker esistente.

## Verifiche locali

Build backend e frontend, controllo TypeScript; database temporaneo con tutte le migrazioni. Test interventi, assistenza, notifiche, posa, conto economico e tracciamento ordini passati. Test browser con API simulate: creazione/modifica intervento, ricambi e larghezze 320/390 px; screenshot in output/support/interventi-mobile.png. Nessun invio email reale, chiamata IA o deploy sul NAS eseguiti.

Restano: adozione costi manuali guidata, preventivo assistenza e ordine ricambi, magazzino reale, calendario aggregato, traduzione EN e collaudo con dati reali sul NAS. Nessuna regola di garanzia o tariffa è stata presunta.

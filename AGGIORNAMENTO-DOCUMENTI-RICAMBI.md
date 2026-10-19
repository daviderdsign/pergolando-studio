# Documenti e fatture ricambi — 16 ottobre 2026

## Disponibile
In Pratiche → Assistenza → Intervento → Ordini ricambi → singolo ordine: «Documenti e fatture ricambi».
- Caricamento originale PDF/PNG/JPEG (massimo 3 MB), conservato nell’archivio economico della pratica e scaricabile con accesso del rivenditore.
- Tipo, riferimento, data, totale netto e motivazione inseriti e verificati dal rivenditore. Nessuna estrazione o attribuzione automatica degli importi.
- Fatture collegabili tramite quota netta a un costo ricambi ACTUAL attivo dello stesso intervento. La quota non crea alcuna voce economica e non registra un pagamento: il costo rimane quello del consuntivo.
- Somma quote limitata sia dal netto del medesimo originale sia dal costo collegato; stessa identità documentale coerente tra ordini. Verifica esplicita del fornitore a cura del rivenditore.
- Rettifiche con storico immutabile, controllo della revisione economica, protezione accessi e richieste ripetute.
- Se il costo collegato viene sostituito, il collegamento è segnalato come da verificare e impedisce la dichiarazione finale di costi completi finché non viene rettificato. Consegna e portale cliente restano indipendenti.

## Limiti espliciti
Le quote documentano costi già registrati, non sono un nuovo motore di valorizzazione del magazzino. Una fattura con merce non utilizzata non va attribuita integralmente ai ricambi consumati. Il netto non attribuito resta senza ripartizione automatica. Note di credito, resi, ripartizioni tra pratiche e acquisizione automatica dalle email richiedono il prossimo blocco. Nessun documento viene trasmesso al cliente da questa sezione. L’interfaccia inglese è ancora da completare per questo modulo.

## Verifiche locali
Build backend e frontend superate. Test su database temporaneo: accessi, date, originali, importi fuori limite, revisioni, idempotenza, rettifiche e costo invariato. Regressioni conto economico, riconciliazione e ordini/email ricambi superate. Browser con API simulate a 320/390 px: quota, conferma obbligatoria e invalidazione dopo modifica; nessuna email reale, chiamata IA o modifica al database operativo.

## NAS
Copiare il contenuto cumulativo di Aggiornamento nella cartella /home/davideromeo/Pergolando-chatgpt dopo il backup del database e degli originali. Nessun file .env è incluso.
Nuova migrazione: 20261017001000_support_part_documents. Il normale avvio del backend applica le migrazioni.

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build backend frontend && docker compose restart gateway
```

Da collaudare sul NAS: caricamento/scaricamento originale reale, fattura tardiva su intervento completato, rettifica quota e successiva correzione del consuntivo. Non ancora distribuito da questa sessione.

Estensione successiva: resi e note di credito implementati come descritto in AGGIORNAMENTO-RESI-NOTE-CREDITO.md; sostituisce il limite precedente sulle note di credito degli interventi.

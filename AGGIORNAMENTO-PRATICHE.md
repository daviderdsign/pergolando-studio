# Primo blocco: pratiche cliente multi-prodotto

14 ottobre 2026

## Installazione NAS
Il contenuto di Aggiornamento va copiato nella cartella principale del progetto sul NAS, mantenendo le sottocartelle. Non sostituire backend.env, .env o il volume dati.
Prima dell’installazione conserva un backup del database del backend. La migrazione aggiunge due tabelle e non modifica quelle esistenti.

```
docker compose up -d --build backend frontend
docker compose restart gateway
```
Il comando di avvio del backend già previsto nel pacchetto NAS esegue prisma migrate deploy. Verifica che il backend sia Up; se fallisce, leggere docker compose logs --tail=80 backend. Non usare migrate reset.

## Prova
1. Accedi e apri la home Demo: è presente Apri l’archivio pratiche.
2. Avvia Demo 1 o 2, inserisci cliente, configura Flag e calcola.
3. Premi Salva prodotto nella pratica e apri l’archivio.
4. Premi Aggiungi un prodotto e scegli Pratic Brera: i dati cliente vengono ripresi.
5. Calcola e salva. La pratica contiene entrambe le righe e il totale prodotti.
6. Riapri l’archivio da un altro dispositivo con lo stesso account: i dati arrivano dal server.

## Perimetro di questo blocco
Ogni installazione è già dedicata a un rivenditore; le pratiche sono per ora riservate all’account venditore che le ha create. Non è ancora presente il ruolo di responsabile con accesso condiviso.
I prezzi vengono ricalcolati sul backend prima di essere registrati. Il salvataggio ripetuto della stessa operazione non aggiunge un secondo prodotto.
Sono registrati configurazione, prezzo e impronta del catalogo prodotti. L’impronta non è ancora un sistema di versionamento completo del listino e delle matrici prezzi.
L’archivio mostra le ultime 100 pratiche. Il totale prodotti non è un’offerta definitiva e non aggiunge automaticamente posa, trasporto, sconti o IVA.
Non sono ancora implementati modifica/eliminazione delle righe salvate, PDF complessivo multi-prodotto, allegati e immagini persistenti, revisioni commerciali, validazione autonoma dei cataloghi, pagamenti o abbonamenti.
Il PDF e il rendering attuali restano riferiti al singolo prodotto configurato. Questo aggiornamento non certifica i cataloghi e non ne amplia i contenuti.

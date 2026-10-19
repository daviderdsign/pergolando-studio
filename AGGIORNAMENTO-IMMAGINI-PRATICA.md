# Immagini e disegni persistenti nella pratica

14 ottobre 2026 - aggiornamento cumulativo

## Installazione
Conservare un backup del database del backend. Copiare il contenuto di Aggiornamento nella directory principale del progetto sul NAS, preservando backend.env, .env e il volume dati.

```
docker compose up -d --build backend frontend
docker compose restart gateway
```
La migrazione aggiunge case_media e mediaIds alle righe prodotto. All’avvio il backend del pacchetto NAS deve eseguire prisma migrate deploy. Non usare migrate reset.

## Uso
1. Configurare un prodotto nella Demo 1 e creare il rendering Blender; eventualmente generare l’immagine IA.
2. Premere Salva immagini e disegni nella pratica. Se il prodotto non era ancora salvato, il pulsante lo salva prima. Viene archiviata l’immagine IA quando presente, altrimenti il composito Blender, e le viste tecniche già pronte.
3. Se i disegni arrivano successivamente, premere di nuovo il pulsante per includerli. Il salvataggio è esplicito, non automatico ad ogni rendering.
4. Dall’archivio usare Mostra immagini e disegni salvati: le immagini arrivano dal server anche da un altro dispositivo con lo stesso account.
5. Creare una NUOVA revisione dell’offerta unica dopo aver salvato le immagini. Scaricare il PDF: per ogni prodotto contiene ambientazione e viste disponibili.

## Regole
- Le revisioni precedenti non vengono aggiornate: mantengono i riferimenti alle immagini salvate in quel momento.
- Una modifica alla configurazione del prodotto invalida le immagini correnti della riga. Le copie già utilizzate nelle revisioni precedenti rimangono accessibili al proprietario.
- I file immagine sono deduplicati nella stessa pratica e gli accessi sono autenticati e verificati per proprietario.
- Sono accettati PNG e JPEG, massimo circa 2,2 milioni di caratteri per immagine data URL. Quattro immagini restano sotto il limite del corpo richiesta del backend. L’ambientazione viene ridimensionata a un massimo di 1600 pixel sul lato lungo.
- Questa versione conserva l’immagine finale scelta e le tre viste, non l’intero ambiente di calibrazione (foto originale, punti e camera) né entrambe le alternative Blender/IA. La riapertura del configuratore serve a modificare il prodotto, non a riprendere una sessione di posizionamento fotografico.

## Verifiche
Backend compilato, TypeScript e build di produzione frontend. Test su database temporanei per migrazioni, isolamento, deduplicazione, retry, revisioni con immagini immutabili e invalidazione dopo modifica geometrica; ripetuti i test pratiche/conto economico/offerte.
PDF di prova a 8 pagine verificato visivamente, con ambientazione e tre immagini tecniche dimostrative. Nessuna generazione IA o email inviata durante questi test.

I precedenti file AGGIORNAMENTO descrivono i passaggi storici. Questa nota sostituisce il precedente limite che escludeva immagini e disegni dal PDF unico.

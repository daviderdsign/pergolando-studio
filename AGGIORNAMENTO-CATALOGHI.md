# Cataloghi del rivenditore: originali, versioni e verifiche

## Installazione sul NAS
Prima salvare una copia del database/volume esistente. Copiare il contenuto di Aggiornamento nella cartella del progetto, mantenendo i percorsi. Non sostituire backend.env, .env o i volumi.

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build backend frontend
docker compose restart gateway
```

Il backend esegue prisma migrate deploy all’avvio. La nuova migrazione 20261014210000_dealer_catalogs aggiunge quattro tabelle; le precedenti migrazioni delle pratiche restano incluse. Non usare migrate reset.

## Prova dal telefono
1. Home → Demo 3: caricare un listino, estrarre le tabelle, correggerle e indicare nome e marchio.
2. Premere «Salva bozza sul server». Vengono conservati anche i documenti originali. Aprire «Bozza e verifiche», oppure «Archivio cataloghi» dalla home.
3. Controllare unità, orientamento L/P, celle prezzo, note e confermare ciascuna tabella. Salvare le modifiche.
4. Per ogni tabella eseguire minimo, massimo, un altro prezzo e un caso fuori intervallo. I pulsanti suggeriscono solo le dimensioni: il prezzo atteso va letto e inserito manualmente dall’originale.
5. Per utilizzare la fascia dimensionale superiore, eseguire anche una prova con misure intermedie e quella regola. Verificare manualmente che il produttore la ammetta.
6. Confermare la revisione delle condizioni e approvare la versione. Eventuali test falliti devono essere ripetuti e superati; gli originali devono essere completi.
7. «Preventivo da questa versione» usa prezzi calcolati sul backend. La stessa versione è accessibile da un altro dispositivo con lo stesso account.

## Regole
- Le versioni approvate sono immutabili; «Crea nuova versione» copia dati e originali ma richiede nuove prove. Una sola versione successiva per ogni versione approvata.
- In bozza un originale con lo stesso nome ma contenuto diverso viene sostituito solo nella nuova bozza, azzerando le prove valide per quella revisione; la versione precedente conserva il proprio file.
- Modifiche alle tabelle o agli originali invalidano le prove precedenti, che restano archiviate. Una verifica fallita viene superata ripetendo lo stesso caso correttamente.
- File caricati in blocchi da 1 MB, con controllo SHA-256 finale. Un caricamento interrotto si riprende selezionando nuovamente gli stessi file dalla bozza. Massimo 50 MB per file, 250 MB e 50 originali per catalogo. Dati estratti: massimo 8 milioni di caratteri, 100 tabelle e 100 foto; un catalogo molto grande va suddiviso.
- Accessi limitati al proprietario. La condivisione fra diversi account dello stesso rivenditore attende il modulo ruoli.
- «Verificato dal rivenditore» descrive il controllo umano dei casi provati, non una certificazione automatica di tutte le combinazioni.

## Limiti di questo blocco
L’estrazione rimane nel browser e supporta i formati già previsti: PDF con testo e CSV; OCR e lettura nativa Excel non aggiunti. Supplementi, IVA, vincoli costruttivi e condizioni esterne alla griglia richiedono ancora controllo esplicito. L’anteprima locale del vecchio percorso è indicata come tale e non equivale ad approvazione sul server.

I cataloghi approvati sono utilizzabili nella Demo 3 senza modello 3D. Il successivo blocco AGGIORNAMENTO-PRODOTTI-IMPORTATI.md collega le righe importate alle pratiche multi-prodotto e alla scelta catalogo delle Demo 1/2, mantenendo il percorso senza 3D. La gestione dei ruoli resta successiva.

## Verifiche locali
Compilazione backend, controllo TypeScript e build di produzione frontend. Test su database temporaneo per migrazioni, originali/checksum, proprietà, revisioni, approvazione, regola fascia superiore e parità fra calcolo browser e server. Regressione pratiche, conto economico, offerte e immagini. Nessuna email o richiesta IA inviata. Il collaudo del caricamento sul NAS resta da fare dopo la copia.


## Aggiunta 15 ottobre — Elimina catalogo

Nell’archivio ogni catalogo ha il tasto «Elimina catalogo», con conferma e Annulla. Si elimina solo la versione scelta. Il catalogo sparisce e non può essere usato per nuovi preventivi; dati e originali restano conservati per lo storico, insieme a pratiche e offerte già salvate. Per cambiare un prodotto collegato occorre selezionare un catalogo disponibile. Non è una cancellazione fisica dei documenti. Nessuna nuova migrazione database.

Dopo la copia del pacchetto cumulativo sul NAS:

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build backend frontend
docker compose restart gateway
```

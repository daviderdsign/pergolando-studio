# Cataloghi approvati nelle pratiche multi-prodotto

## Installazione
Salvare prima una copia del database/volume. Copiare il contenuto di Aggiornamento sul NAS mantenendo i percorsi, senza sostituire backend.env, .env o i volumi.

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build backend frontend
docker compose restart gateway
```

Questo blocco non aggiunge migrazioni. Il pacchetto conserva le migrazioni precedenti, compresa quella dei cataloghi; il backend applica quelle mancanti con migrate deploy.

## Percorso di prova
1. Nella Demo 3 importare, verificare e approvare una versione del listino, come descritto in AGGIORNAMENTO-CATALOGHI.md.
2. Dall’archivio pratiche aprire una pratica esistente con Flag o Brera e premere «Aggiungi da un catalogo approvato».
3. Selezionare il preventivo di una versione approvata. I dati cliente arrivano dalla pratica e sono in sola lettura; inserire modello/tabella, dimensioni, colore e supplementi espliciti.
4. Calcolare, quindi «Salva prodotto nella pratica». La pratica contiene ora righe di più marchi e provenienze.
5. «Offerta unica della pratica» conserva tutti i prodotti nella stessa revisione e nel PDF, con posa, trasporto, sconto e IVA del preventivo complessivo.
6. Dall’archivio «Modifica» riapre ciascun prodotto nel proprio percorso: configuratore per Flag/Brera, listino approvato per i prodotti importati. Ricalcolare e aggiornare la riga; le vecchie revisioni restano inalterate.

È possibile iniziare anche dal listino approvato e creare una nuova pratica al salvataggio. Nelle Demo 1/2, dopo i dati cliente, la scelta catalogo comprende il pulsante «Scegli da un catalogo approvato»: conserva la pratica e passa al percorso senza 3D dei listini importati.

## Affidabilità del dato
- Il backend ricalcola la cella prezzo dalla versione approvata del proprietario: non accetta il totale calcolato dal browser come prezzo autorevole.
- Vengono conservati versione/hash del catalogo, tabella, pagina originale, regola dimensionale, misure richieste, colore e supplementi.
- I supplementi sono importi dichiarati esplicitamente dal venditore; non derivano da regole tecniche estratte automaticamente. Vengono distinti nelle voci del prodotto.
- Una versione diversa del catalogo non aggiorna le righe già salvate. La modifica riapre la versione originale; per proporre un altro catalogo si aggiunge una nuova riga ed eventualmente si esclude quella precedente.
- Modifiche protette dalla versione della riga e richieste idempotenti; esclusione e ripristino usano le stesse funzioni delle altre righe.
- I prodotti importati partecipano alle somme e alle revisioni commerciali esistenti. Il prezzo salvato deve essere confermato al netto IVA prima di creare l’offerta unica.

## Limiti
I listini importati seguono il percorso senza 3D: non vengono creati automaticamente modelli Blender, viste tecniche o foto di prodotto nel PDF unico. La fattibilità tecnica e gli accessori restano da verificare. I dati cliente della pratica non vengono modificati da questa pagina. L’invio email della revisione unica, l’accettazione cliente e gli ordini ai produttori restano blocchi successivi.

## Verifiche
Compilazione backend e build frontend; test su database temporanei per righe miste, ricalcolo server, supplementi, accessi, cataloghi in bozza, hash errato, richieste ripetute, modifiche concorrenti, prodotti esclusi, validazione DTO e immutabilità delle offerte. Regressione dei blocchi precedenti. Nessuna email o generazione IA avviata durante i test.

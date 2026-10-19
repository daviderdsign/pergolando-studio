# Pratiche, conto economico e offerte - aggiornamento cumulativo

14 ottobre 2026

## Installazione NAS
Copiare tutto il contenuto di Aggiornamento nella cartella del progetto sul NAS, mantenendo le sottocartelle. Non copiare in una sottocartella Aggiornamento sul NAS. Preservare backend.env, .env e il volume dati.
Prima conservare un backup del database. Le migrazioni sono additive: pratiche, voci del conto, documenti e revisioni. Il backend del pacchetto NAS esegue prisma migrate deploy all’avvio. Non usare migrate reset.

```
docker compose up -d --build backend frontend
docker compose restart gateway
```

## Cosa provare
- Archivio pratiche: salvare Flag e Brera nella stessa pratica.
- Modifica: riaprire una riga, correggere misure/accessori e salvarla. Il prezzo è ricalcolato dal server. Se un vecchio prodotto Flag non ha il dislivello salvato, reinserirlo; i nuovi salvataggi lo conservano.
- Escludi: il prodotto esce dai totali della bozza, ma resta in Prodotti esclusi e può essere ripristinato.
- Offerta unica, revisioni e PDF: confermare prezzi netti IVA, inserire posa e trasporto netti, sconto sui SOLI prodotti, aliquota IVA, acconto sul totale, validità e condizioni. Salvare una revisione e scaricare il PDF.
- Modificare un prodotto e salvare una seconda revisione: il PDF della prima resta identico nei contenuti economici. Una revisione è uno snapshot; non prova accettazione, firma o invio.
- Apri conto economico e documenti: seguire AGGIORNAMENTO-CONTO-ECONOMICO.md. Le offerte non diventano automaticamente ricavi confermati: nessuna duplicazione tra proposta, vendita e incasso.

## Controlli completati
- Backend compilato e frontend con build Next.js di produzione.
- Tre test su database temporanei: pratiche multi-marchio, conto economico e documenti, modifiche/ripristino e revisioni immutabili.
- PDF dimostrativo multi-marchio A4 orizzontale: verificati testi, totale, IVA, acconto e tutte le pagine renderizzate.
- Nessuna migrazione applicata al database operativo locale o del NAS; nessun invio email o pagamento eseguito.

## Limiti espliciti
Il PDF unico contiene riepilogo economico, dettaglio prodotti e condizioni; non archivia ancora immagini, render e disegni tecnici delle singole configurazioni. Il percorso fotografico esistente resta disponibile separatamente.
L’archivio resta riservato al singolo venditore. La gestione dei ruoli del rivenditore è successiva.
L’assistenza è abilitabile alla consegna/collaudo tramite stato: portale, ticket e inviti email sono da realizzare.
Importazione automatica email, abbinamento ordini/documenti, notifiche e report economico PDF, firma/accettazione e pagamenti non sono implementati da questo blocco.
L’aliquota IVA e la natura netta dei prezzi vanno confermate dal rivenditore. Il programma non determina automaticamente il regime fiscale della commessa.

# Punto 3 — Configurazione dei prodotti

Implementato il 15 ottobre 2026. Dopo l'apertura della pratica si entra nei suoi prodotti: cataloghi predisposti e listini approvati dal rivenditore, ricerca, configurazione e riepilogo unico. Ogni riga rappresenta un prodotto; una pratica può avere più prodotti e marchi.

## Percorso operativo

1. Apri o crea la pratica e scegli Prodotti nel percorso inferiore.
2. Scegli il catalogo, poi modello, variante, misure, colore e accessori disponibili.
3. Calcola e salva. «Salva e aggiungi un altro prodotto» riporta al riepilogo; «Continua all’offerta unica» porta alle condizioni commerciali comuni.
4. Dal riepilogo modifica una configurazione, escludi una riga o ripristinala. Il totale qui riguarda i prodotti; IVA, sconti, posa e trasporto si completano nell’offerta.

I prezzi vengono ricalcolati dal server. Il cambio dei parametri invalida il risultato precedente, anche se un calcolo asincrono sta ancora terminando. I retry concorrenti del salvataggio non duplicano righe o revisioni economiche. Le immagini non più coerenti vengono invalidate dalle modifiche della configurazione.

Dopo un’accettazione cliente le modifiche ai prodotti sono bloccate anche dal backend. Per un’accettazione ancora da verificare occorre prima gestire il rifiuto/riapertura nella trattativa. Le varianti dopo conferma definitiva richiedono un modulo successivo. Le revisioni dell’offerta già emesse restano immutate.

I listini importati richiedono ancora verifica manuale delle condizioni e dei supplementi: l’estrazione non certifica automaticamente regole tecniche, compatibilità o fattibilità. Cataloghi non approvati non sono proposti. Un catalogo eliminato conserva lo storico economico delle righe già salvate.

## Installazione NAS

Copia il contenuto cumulativo di Aggiornamento nella cartella del progetto, conservando i file di ambiente. Prima esegui il backup del database. Questo blocco non aggiunge migrazioni; il pacchetto include anche quelle additive dei blocchi precedenti.

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build backend frontend && docker compose restart gateway
docker compose ps
```

## Verifiche eseguite

- Build backend e frontend superate.
- 14 script backend superati, compresa la nuova prova multiprodotto/marchio, prezzi server, concorrenza, esclusione/ripristino e blocco accettazione/conferma.
- Chromium: percorso unico, apertura pratica e prodotti; API simulate, nessuna email reale. Ricerca, cataloghi approvati, recupero caricamenti, navigazione e assenza di scroll orizzontale a 320/390 px.
- Schermata prodotti mobile controllata visivamente.

Resta il collaudo sul NAS con i cataloghi reali. Prossimo blocco: consolidare offerta e trattativa prima dell’ordine, con verifica delle condizioni obbligatorie e delle notifiche. Ordini produttori, posa e assistenza completa restano moduli successivi.

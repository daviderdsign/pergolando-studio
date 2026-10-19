# Offerta unica — 16 ottobre 2026

Il punto successivo alla configurazione prodotti è stato consolidato nella pagina /pratiche/:id/offerta.

- Riepilogo dei prodotti attivi, con marchi, importi e conteggio degli esclusi; ritorno diretto a prodotti e trattativa.
- Anteprima economica aggiornata durante la compilazione: prodotti netti, sconto sui soli prodotti, posa, trasporto, imponibile, IVA, totale, acconto e saldo. Calcolo in centesimi e arrotondamenti coerenti con il server.
- La conferma di verifica del venditore si azzera quando cambiano importi, validità o condizioni e dopo un ricaricamento/salvataggio. I parametri iniziali del rivenditore non sovrascrivono una compilazione già iniziata.
- Le revisioni mostrano i propri importi storici e la propria validità. PDF, invio SMTP esplicito, verifica email cliente e notifiche già presenti vengono mantenuti.
- Dopo accettazione o conferma sono bloccate le nuove revisioni, sia nell’interfaccia sia sul backend. Il rifiuto di una richiesta ancora da confermare riapre la trattativa; varianti dopo conferma definitiva ancora da implementare.
- Retry dello stesso salvataggio riconosciuto anche dentro la transazione: nessuna revisione duplicata o doppio avanzamento economico.
- Conferma/rifiuto e aggiornamento stato cliente ricaricano il contesto della pagina.

Non vengono registrati automaticamente incassi e non vengono inviati ordini ai produttori. Il pagamento resta al rivenditore. Nessuna migrazione aggiuntiva in questo blocco.

## Installazione

Dopo backup del database, copiare il contenuto di Aggiornamento nella directory del progetto sul NAS, senza sovrascrivere i file di ambiente. Quindi:

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build backend frontend && docker compose restart gateway
```

Collaudo richiesto: pratica con più prodotti, sconto/IVA/posa/trasporto, anteprima coerente con la revisione salvata, controllo del PDF, invio volontario a una casella di prova, accettazione, rifiuto/riapertura e conferma. Il pacchetto non è stato installato da questa sessione sul NAS.

## Verifiche eseguite

Build backend e frontend e controllo TypeScript superati. Sei test backend passati (revisioni, configurazione prodotti, accettazione, invii, notifiche, verifica email), con nuova prova concorrente di salvataggio e blocco delle revisioni dopo accettazione/conferma. Tre verifiche Chromium superate: offerta, percorso unico e apertura pratica. Dati API ed email simulati; nessun invio reale. Calcoli confrontati, controlli di modifica/salvataggio e layout senza scroll orizzontale a 320/390 px; screenshot mobile controllato.

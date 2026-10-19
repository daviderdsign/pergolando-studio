# Acconto e verifica incassi — 16 ottobre 2026

Nuova pagina /pratiche/:id/pagamenti, accessibile dall’offerta: registrazione degli incassi e rimborsi nella cassa esistente, senza crearne una parallela, e verifica manuale separata dell’accredito.

## Funzionamento

- Il rivenditore incassa direttamente il cliente. Questa funzione non esegue pagamenti, non si collega alla banca e non modifica l’abbonamento Pergolando.
- Per verificare un movimento serve la conferma tecnica definitiva del rivenditore sulla proposta accettata. L’acconto richiesto è quello della revisione confermata, IVA inclusa.
- I movimenti effettivi registrati in cassa non sono automaticamente verificati. Una ricevuta caricata non costituisce verifica dell’accredito.
- Il rivenditore seleziona il movimento, metodo, riferimento e nota, confermando esplicitamente il controllo. Uscite selezionate in questa pagina devono essere esclusivamente rimborsi al cliente: i pagamenti ai fornitori non vanno verificati come rimborsi.
- Somma incassi verificati meno rimborsi cliente verificati = disponibilità verificata; la pagina mostra la differenza rispetto all’acconto richiesto. Se l’offerta confermata non richiede acconto, il requisito economico è soddisfatto senza registrare movimenti fittizi.
- Verifiche revocabili con nuovo evento storico. Le sostituzioni di movimenti nel conto invalidano il conteggio dei precedenti e richiedono una nuova verifica. Gli importi di cassa non si sommano ai ricavi economici.
- Proprietario, revisione concorrente e idempotenza controllati dal server; eventi con autore, data, metodo, riferimento e nota. Nessuna cancellazione dello storico.
- Il servizio espone il requisito economico per il futuro modulo ordini. Nessun ordine viene ancora inviato o creato da questo blocco. L’autorizzazione operativa degli ordini dovrà controllare di nuovo questo stato sul server, insieme alle verifiche tecniche.

## Installazione NAS

Migrazione additiva **20261016090000_payment_checks**, nuova tabella case_payment_checks. Fare backup del database e copiare Aggiornamento nella directory del progetto senza sostituire gli ambienti. L’avvio backend applica le migrazioni previste dalla configurazione Docker.

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build backend frontend && docker compose restart gateway
docker compose ps
```

Nessun deploy sul NAS eseguito da questa sessione. Collaudare con una commessa di prova: conferma, registrazione acconto parziale, verifica, saldo acconto, rimborso, revoca e correzione del movimento. Il controllo è una dichiarazione del rivenditore, non una certificazione bancaria.

## Verifiche eseguite
Build backend e frontend superate. Cinque script backend passati: acconti, conto economico, revisioni, accettazione e prima configurazione/avvio Nest. Test Chromium acconti e regressione offerta superati con API simulate, senza pagamenti o email reali. Verificati separazione registrazione/verifica, consenso azzerato, accredito/revoca e blocco senza conferma tecnica. Layout 320/390 px senza scroll orizzontale e screenshot controllato.

# Prima configurazione del rivenditore — 15 ottobre 2026

## Percorso disponibile

Dopo accesso e verifica email, gli account non configurati vengono accompagnati in /impostazioni. Gli account già esistenti devono completare questa configurazione una volta. Le pratiche e i cataloghi precedenti non vengono cancellati.

1. Rapporto con Pergolando: testo versionato, rappresentante e azienda, conferma esplicita, copia scaricabile e registrazione sul server.
2. Dati aziendali: ragione sociale, partita IVA/codice fiscale, sede, email, telefono e referente.
3. Carta intestata: editor con logo PNG/JPEG e testi, oppure caricamento di un PDF A4 orizzontale di una pagina fino a 5 MB. Originale conservato nel profilo; immagine ad alta risoluzione utilizzata nel PDF delle offerte. Margini regolabili, anteprima, esportazione della carta e documento di esempio.
4. Parametri commerciali: IVA, acconto, sconto prodotti, posa, trasporto, costo orario squadra, validità, condizioni commerciali e pagamento/IBAN. Proposti nelle nuove offerte; modificabili senza cambiare i listini. Costo orario proposto nel conto economico; importi della manodopera sempre calcolati da ore effettive × costo squadra.
5. Cataloghi: collegamenti a importazione OCR e verifiche; per completare serve almeno un catalogo importato approvato oppure dichiarare il controllo manuale dei cataloghi predisposti. Email: test SMTP e messaggio al solo account autenticato, su pulsante esplicito. Nessuna credenziale nel browser. Rendering: controllo opzionale, non blocca la configurazione commerciale.
6. Riepilogo e completamento, con controllo dei campi obbligatori lato server. Apertura delle pratiche. Impostazioni accessibili dal menu.

La modifica/salvataggio delle impostazioni riapre il controllo finale: completare nuovamente il riepilogo per tornare alle operazioni. Le sezioni cataloghi restano accessibili dopo la conferma del rapporto Pergolando, anche durante la preparazione.

## Documenti e riservatezza

Le nuove revisioni dell’offerta includono una copia della carta intestata e dei soli dati aziendali destinati al cliente. Nessun costo orario interno o parametro economico privato viene incluso nel profilo grafico pubblico. Le revisioni precedenti mantengono la grafica originale. Offerte vecchie senza profilo continuano a funzionare.

Per ora il formato è quello dei documenti già disponibili: A4 orizzontale. Modelli verticali, grafica distinta prima pagina/seguito e futuri documenti di ordine/posa restano da estendere con quei moduli. La nuova pagina è in italiano; traduzione completa EN ancora da completare, selettore lingue mantenuto.

## Contratto e abbonamento

Il testo predefinito è chiaramente una BOZZA DI PROVA: la conferma non attiva pagamenti e non equivale a un contratto commerciale definitivo. Non vengono inventati prezzi o rinnovi. Non esiste ancora un collegamento al pagamento dell’abbonamento.

L’amministratore può predisporre il documento tramite PERGOLANDO_CONTRACT_JSON con campi mode=approved, version, title, text, plan. Non impostarlo come approved finché testo, privacy, eventuali approvazioni specifiche e modalità di sottoscrizione non sono stati validati legalmente. Il semplice flag di configurazione non dà validità legale alle clausole; il flusso di firma/approvazioni specifiche va adeguato ai testi definitivi. Il cambio dell’hash del documento richiede una nuova conferma, mantenendo le precedenti nel database.

## Installazione sul NAS

Fare il backup del database/volume. Copiare il contenuto di Aggiornamento nella cartella del progetto, conservando percorsi. Non sovrascrivere .env, backend.env o volumi.

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build backend frontend && docker compose restart gateway
docker compose ps
```

Inclusa migrazione additiva 20261015210000_dealer_setup: nuove tabelle per profilo e conferme. Il backend applica le migrazioni al suo avvio. Non usare migrate reset. Se appare un errore, leggere docker compose logs --tail=80 backend.

Aprire https://pergolando.rdsign-app.it/impostazioni. L’SMTP deve essere già configurato sul server; il pulsante di prova verifica e invia un messaggio al proprio account. Le condizioni di prova non attivano alcun pagamento.

## Collaudi eseguiti

- Build backend e frontend e controllo TypeScript.
- Dodici test backend con database temporanei: setup, pratiche, finanza, offerte, immagini, cataloghi, importati, collegamenti cliente, invii, notifiche, gestione e OTP. Email simulate.
- Avvio del grafo Nest completo su database temporaneo.
- Chromium mobile: ingresso obbligatorio, conferma, anagrafica, logo, editor/PDF con rifiuto formato verticale, PDF esempio, parametri, verifica email simulata, completamento e riapertura.
- Regressione del percorso unico per account già configurato.
- PDF esempio renderizzato e verificato visivamente, incluse copertina, pagina economica e chiusura.
- Nessun aggiornamento automatico del sito pubblico e nessuna email reale inviata durante i test.

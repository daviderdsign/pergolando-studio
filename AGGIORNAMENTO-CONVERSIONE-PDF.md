# Conversione commerciale PDF e chiarimenti del rivenditore

16 ottobre 2026. Implementato il flusso software di conversione, con un motore eseguibile e controlli bloccanti. **Non è certificata la conversione universale dei PDF e non è ancora completato il collaudo di un catalogo reale approvato.** Il servizio IA ha restituito HTTP 402 (credito prepagato esaurito); le chiamate reali sono state interrotte. Proposte precedenti non eseguibili sono state respinte.

## Percorso nell’app

1. Importare il catalogo e completare il caricamento degli originali nella sua bozza.
2. Aprire il catalogo e scegliere «Analizza e converti tutti gli originali». Il server lavora in background: la pagina controlla lo stato, senza tenere aperta una richiesta lunga attraverso Cloudflare.
3. Esaminare regole proposte, formule, fonte/pagina e copertura del documento. Le matrici possono essere corrette o aggiunte dalla rilettura; restano dati di una bozza.
4. Rispondere alle domande con «Salva risposta e aggiorna le regole». Le risposte sono conservate con autore e data soltanto per quel catalogo. Una risposta cambiata invalida il precedente collegamento alle regole: serve riconversione e nuova validazione.
5. Eseguire i preventivi di prova generati dal sistema: minimo cinque calcolabili, più i casi richiesti per tutte le opzioni e le regole. Il rivenditore controlla ogni risultato sul documento originale, quindi approva esplicitamente la versione.
6. Nel preventivo i campi vengono dalle opzioni estratte. Supplementi e vincoli sono ricalcolati sul server e al salvataggio; nei cataloghi convertiti non si aggiungono importi manuali per compensare regole mancanti.

## Motore e criteri di blocco

- Scelte, quantità, campi sì/no, importi fissi, percentuali, formule su misure/superficie/perimetro, minimi, massimi, arrotondamenti e condizioni di applicazione. Vincoli e incompatibilità rifiutano configurazioni non ammesse.
- Formule dichiarative interpretate: nessun eval o codice dell’IA eseguito. Basi percentuali esplicite e ordine delle voci conservato; test di cumulabilità e arrotondamento in centesimi.
- Base IVA dichiarata per tabella: netto, IVA inclusa con aliquota o dato sconosciuto. Il dato sconosciuto blocca e genera una domanda; nessuna deduzione automatica dal solo termine B2B.
- Originali/checksum e numero delle pagine fisiche collegati alla conversione. Ogni pagina deve risultare coperta, descrittiva o da chiarire. Fonti modificate o pagine mancanti impediscono l’approvazione.
- Valori numerici senza riscontro nella citazione o nelle risposte collegate generano domande. Questo è un controllo aggiuntivo, non una prova semantica infallibile della lettura: il riscontro sul documento e la verifica del rivenditore restano necessari.
- Regole/opzioni senza un caso di prova esercitabile generano chiarimenti. Domande aperte, risposte non tradotte in regole, limiti mancanti, segnalazioni di lettura o prezzi discordanti mantengono il catalogo bloccato.
- I casi di prova sono costruiti dai dati e dai limiti espliciti, senza selezioni casuali o prezzi stimati. Non equivalgono a una dimostrazione di tutte le possibili combinazioni reali.
- Una formula non rappresentabile o una risposta IA non eseguibile viene segnalata: non si dichiara che sia stata implementata. L’IA può sbagliare; il software non deve presentare una proposta come certezza assoluta.

## Configurazione e limiti operativi

Usa la chiave GEMINI_API_KEY già configurata sul backend oppure una CATALOG_CONVERSION_API_KEY dedicata. Modello configurabile con CATALOG_CONVERSION_MODEL; default gemini-3.1-pro-preview. Il modello precedente gemini-2.5-pro è stato rifiutato dall’API per questo account. Non copiare file di ambiente dall’aggiornamento: configurare il vero backend.env sul NAS.

La conversione invia i documenti al servizio IA ed è soggetta a crediti e disponibilità del fornitore. Massimo 18 MB complessivi PDF/CSV e 250 pagine per documento; fino a due conversioni simultanee per processo e sei avvii orari per rivenditore. Nessun retry HTTP automatico; è possibile un tentativo di correzione di una risposta non eseguibile. Gli errori non modificano la bozza. Se il backend si interrompe, lo stato diventa ripetibile dopo il controllo di scadenza; non è ancora un worker distribuito con ripresa automatica.

Limiti del linguaggio: operazioni, campi e condizioni supportati dal motore. Regole che richiedono funzioni non implementate, letture non affidabili o documenti esterni mancanti richiedono chiarimento/estensione. Non promettere conversione completa al 100% su qualunque PDF. Le precedenti versioni approvate rimangono storiche e non vengono riscritte automaticamente.

## Verifiche e installazione

Build backend/frontend superate. Sei script backend passati (conversione/motore, prove cataloghi, cataloghi, prodotti importati, configurazione iniziale, acconti), comprese mancata applicazione su HTTP 402, isolamento risposte, cambio revisione, formule, IVA, vincoli e prezzi. Tre collaudi Chromium con API simulate passati: conversione/configuratore, validazione, percorso unico. Layout 320/390 px e screenshot controllati. Manifest, lockfile e YAML backend coerenti.

Prova reale effettuata sul PDF VISION: ricevute proposte con domande, ma risposte non eseguibili/richieste rifiutate dal servizio; nessun catalogo reale approvato. Ultimo esito HTTP 402: per completare il collaudo occorre ripristinare il credito e riprendere da una bozza con gli originali completi. Scheda BRERA letta e pagine controllate visivamente, non convertita e approvata dal servizio.

Migrazione additiva 20261016150000_catalog_conversion e dipendenza pdf-lib inclusa in manifest/lockfile. Fare backup del database, copiare Aggiornamento senza cambiare gli ambienti, poi:

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build backend frontend && docker compose restart gateway
```

Nessun deploy sul NAS effettuato. Prossimo passaggio: collaudo reale della conversione e dei chiarimenti prima di continuare con gli ordini ai produttori.

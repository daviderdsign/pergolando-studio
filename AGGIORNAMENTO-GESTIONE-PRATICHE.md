# Dati cliente, note e richiami — 15 ottobre 2026

## Installazione
Fare backup del database/volume e copiare il contenuto di Aggiornamento sul NAS mantenendo i percorsi. Non sostituire backend.env, .env o volumi.

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build backend frontend
docker compose restart gateway
```

Migrazione additiva 20261015150000_case_management: storico attività. Applicata dal migrate deploy del backend; non usare migrate reset.

## Uso
Pratiche → Dati cliente, note e richiami. Il collegamento è presente anche nell’offerta unica.

- Correggere nome, cognome, email, telefono o indirizzo e salvare. Lo storico conserva i dati prima/dopo, visibili solo al proprietario della pratica.
- Per usare l’anagrafica corretta nel preventivo, creare una nuova revisione. PDF, collegamenti, email e accettazioni precedenti conservano l’anagrafica originale. Un’offerta già confermata non viene trasformata in una nuova variante.
- Registrare una nota oppure un richiamo con data e ora. I richiami aperti sono ordinati per scadenza; quelli passati sono indicati come scaduti.
- Segnare un richiamo completato oppure riaprirlo. Lo storico conserva anche questi passaggi; le note non vengono sovrascritte.
- Se la pratica è stata modificata altrove, ricaricare prima di salvare: anagrafica e stato richiami hanno controlli di versione.

I richiami sono promemoria consultabili aprendo la pratica, non email programmate o notifiche push. Non sono state aggiunte assegnazioni a collaboratori: gli accessi restano per proprietario. Lo storico non è ancora un audit unico di ogni azione dell’app; invii email e decisioni restano nelle sezioni dedicate.

Una modifica anagrafica non riapre il conto costi e non registra movimenti economici; aggiorna la revisione della pratica per evitare offerte costruite su dati superati. Le schermate già aperte devono ricaricare i dati aggiornati.

## Verifiche
Compilazione backend e build frontend. Test gestione su database temporaneo: anagrafica, storico, immutabilità offerte precedenti, nuove revisioni aggiornate, note, scadenze, completamento/riapertura, richieste ripetute, conflitti e accessi. Ripetuti gli altri nove script di test. Nessuna email reale inviata. Collaudo NAS ancora rinviato come richiesto.

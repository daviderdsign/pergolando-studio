# Repository Pergolando

Il progetto mantiene quattro repository separati. La cartella principale corrisponde a Studio e ai servizi di rendering; le altre tre cartelle sono checkout indipendenti, non sottocartelle versionate da Studio.

| Cartella | Repository |
| --- | --- |
| `.` | https://github.com/daviderdsign/pergolando-studio |
| `pergolando-backend` | https://github.com/daviderdsign/pergolando-backend |
| `pergolando-frontend` | https://github.com/daviderdsign/pergolando-frontend |
| `pergolando-shared` | https://github.com/daviderdsign/pergolando-shared |

## Dati locali

I repository esistenti sono pubblici. Credenziali, file di ambiente operativi, database, cache, dipendenze installate, pacchetti ZIP, `Aggiornamento`, `output` e `work` non vanno pubblicati. Gli esempi di ambiente contengono solo configurazioni di esempio. Le nuove fotografie originali del laboratorio prospettico restano locali. Le fixture e gli asset già versionati continuano a far parte della cronologia: questa sincronizzazione non riscrive la storia Git.

La copia dei file sul NAS e la pubblicazione su GitHub sono operazioni distinte. Un push non distribuisce automaticamente l'applicazione. Prima di migrazioni sul NAS occorre il backup dei dati; non usare `git clean` o `git reset --hard` su installazioni operative.

## Modifiche e versioni

Creare un ramo, verificare le modifiche, eseguire build e test pertinenti, fare commit e pubblicare il ramo; integrare attraverso una pull request. Conservare in una release coordinata gli SHA dei quattro repository. Non cambiare o spostare tag già utilizzati.

Backend e frontend mantengono la dipendenza condivisa fissata al tag `v0.3.0`. Allineare il codice di `pergolando-shared` su GitHub non modifica automaticamente quella dipendenza: un successivo aggiornamento della libreria richiede una nuova versione immutabile e l'aggiornamento coordinato dei lockfile.

## Verifiche del 19 ottobre 2026

Il controllo locale dei file candidati verifica firme note di chiavi API, token, chiavi private e valori sensibili negli esempi di ambiente senza stamparne i valori. È un controllo preventivo, non una certificazione sull'intera cronologia remota.

Build e test locali vengono indicati nel resoconto della sincronizzazione; lo stato dei workflow GitHub va verificato separatamente. Il collaudo funzionale completo sul NAS rimane distinto dai test automatici.

La prima esecuzione CI ha rilevato una doppia dichiarazione della versione pnpm: corretta usando packageManager. Rimossi i vecchi elementi inutilizzati che bloccavano il lint frontend; lint e TypeScript locali superati. Le warning non bloccanti restano visibili nei report. Shared integrato tramite PR #1.

## Esito finale — 19 ottobre 2026
Tutti e quattro i repository sono integrati su main tramite pull request. Backend: CI test e Docker passati (run 39232847639); frontend: lint, TypeScript, build, tre test browser accessibilità/IT-EN e Docker passati (run 39233893547). Shared: build e 35 test locali superati. Le revisioni coordinate sono nel manifest JSON di allineamento.
Corretti conflitto della versione pnpm, configurazione ESLint frontend mancante nel checkout autonomo, diciture obsolete dei test di accesso e contrasto della dicitura iniziale. Nessun controllo disabilitato per forzare un esito verde. Restano warning di lint backend non bloccanti. Credenziali e dati operativi esclusi dai nuovi commit, senza riscrittura della cronologia. Backup locale Blender identico al sorgente originale verificato e mantenuto fuori da Git. Nessun deploy NAS eseguito. Prossimo lavoro: continuare il collaudo funzionale sul NAS; GitHub non sostituisce la verifica della commessa completa.

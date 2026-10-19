# Tre demo Pergolando

Demo 1: percorso completo con ambientazione e Blender.
Demo 2: preventivi e PDF senza 3D.
Demo 3: raccolta di documenti sul dispositivo e percorso dimostrativo senza 3D. L estrazione automatica dei listini non e ancora implementata.

Questo aggiornamento comprende anche la precedente integrazione della prospettiva e del menu di navigazione. Non contiene credenziali o database. Non modifica gli account.

Sul NAS, copiare lo ZIP nella cartella del progetto, poi eseguire:

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker run --rm -v "$PWD":/work -w /work python:3.12-alpine python -m zipfile -e Pergolando-ChatGPT-tre-demo-2026-10-08.zip .
docker compose up -d --build backend frontend
```

La configurazione del backend rimane in backend.env; .env contiene il token del tunnel.
Aprire https://pergolando.rdsign-app.it/demo dopo la compilazione.
I file della Demo 3 sono salvati solo nel browser del dispositivo usato, non sul server.

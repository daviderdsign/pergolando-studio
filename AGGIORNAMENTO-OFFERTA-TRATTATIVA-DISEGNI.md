# Offerta, trattativa e recupero disegni — 20 ottobre 2026

## Percorso venditore
- Punto 3 · Offerta: prodotti, condizioni, revisioni immutabili, PDF e disegni tecnici. Il comando successivo apre il punto 4 sulla revisione selezionata.
- Punto 4 · Trattativa: preparazione e invio email/PDF, stato cliente, accettazione, conferma tecnica, richiami, comunicazioni e collegamento alla verifica degli acconti.
- Punto 5 · Ordini: acquisti ai produttori dopo i controlli tecnici ed economici già previsti.
«Prepara invio al cliente» prepara il collegamento, non spedisce nulla. Servono ancora anteprima email/PDF, conferma del rivenditore e invio esplicito. L’anteprima della pagina cliente e la copia manuale del link sono facoltative, raccolte in una sezione richiudibile.
Lo stato cliente si aggiorna ogni 15 secondi, senza inviare messaggi o salvare decisioni. «Aggiorna stato invii email» riguarda soltanto il trasporto SMTP. Dopo il sì del cliente compare la verifica tecnica; dopo la conferma compare il collegamento agli acconti.

## Accettazione cliente
Per impostazione predefinita bastano il collegamento riservato valido, nome, email coerente con la revisione e conferma della dichiarazione. Si archiviano revisione, testo, data/ora e nominativo/email dichiarati. Non viene registrata una verifica della casella con codice quando non è avvenuta. La conferma tecnica del rivenditore resta separata: nessun ordine, ricavo o incasso automatico.
Notifica al rivenditore e ricevuta al cliente vengono accodate nello stesso salvataggio e non duplicate dai tentativi ripetuti. L’invio usa la coda SMTP esistente; un’accettazione riuscita non garantisce che le email siano state consegnate.
Il codice resta opzionale nella configurazione backend: OFFER_EMAIL_VERIFICATION_REQUIRED=true lo rende obbligatorio. Il valore predefinito è false. Questa impostazione è distinta da EMAIL_VERIFICATION_ENABLED, che continua a gestire la registrazione degli account. I vecchi clienti che inviano un codice continuano a farlo verificare prima del salvataggio. Non è necessario aggiungere la nuova variabile per il percorso semplice.

## Planimetrie e prospetti
La precedente schermata avviava la generazione ma poteva essere lasciata prima del completamento, salvando il prodotto senza viste. Ora Prodotti e Offerta mostrano la sezione dei disegni tecnici. Per i modelli predisposti Arquati/Pratic con misure salvate, se mancano viste parte il recupero da Blender e l’archiviazione delle tre viste quotate.
La richiesta condivisa continua durante la navigazione interna del browser; chiudere completamente il browser non garantisce il completamento. Alla riapertura delle pagine il recupero riparte se necessario. La versione del prodotto impedisce di allegare risultati a una configurazione cambiata nel frattempo.
Se Blender non è disponibile, compare l’errore e «Riprova i disegni tecnici». Non vengono inventate viste per cataloghi importati privi di modello. Il servizio Blender deve essere raggiungibile dal backend.
Salvare solo un rendering o solo i tre disegni conserva ora gli altri allegati già archiviati. Una modifica della geometria continua a invalidare le immagini del prodotto. La perdita della risposta al salvataggio viene riconciliata rileggendo i disegni solo se la configurazione è identica.
Le revisioni e gli invii precedenti non cambiano retroattivamente: dopo il recupero dei disegni creare una nuova revisione, prima dell’accettazione, per includerli nel PDF. Eventuali offerte già accettate richiedono il percorso di verifica/riapertura esistente; nessuno sblocco automatico.

## Distribuzione NAS
Copiare il contenuto cumulativo di Aggiornamento dopo il backup dei dati, senza sostituire .env o backend.env. Nessuna nuova migrazione database richiesta.

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose build backend frontend && docker compose up -d backend frontend && docker compose restart gateway
docker compose logs --since=5m --tail=80 backend
```

Il lavoro locale non modifica la pratica attualmente aperta sul NAS. Dopo la distribuzione ricaricare l’app, aprire Prodotti o Offerta e controllare i disegni; poi proseguire dal punto 4. Nessun invio email o accettazione reale viene eseguito durante i test di questa modifica.

Verifiche locali superate: build backend/frontend, lint e TypeScript; accettazione semplice, OTP, inviti/notifiche e persistenza media su database temporanei. Browser 320/390 px con servizi simulati: recupero/archivio viste, risposta persa, errore Blender e retry, separazione 3/4, accettazione/decisione/acconto. I dati geometrici mancanti non vengono inventati: viene richiesta la conferma della configurazione.

GitHub: verifiche e build Docker superate nelle PR backend #2 e frontend #2. Documentazione in Studio #3. Distribuzione NAS ancora da eseguire copiando Aggiornamento; nessuna pratica reale modificata durante il collaudo.

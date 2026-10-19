# Ordini ricambi assistenza — 16 ottobre 2026

## Percorso

Pratica → Assistenza → ticket → Interventi e ricambi → singolo intervento → «Ordini ricambi al fornitore».

1. Salvare prima codici, descrizioni, quantità necessarie e fornitore di ogni ricambio nell’intervento.
2. Valutare esplicitamente la copertura: garanzia oppure a pagamento. Per l’acquisto legato a un intervento a pagamento serve il preventivo accettato corrispondente ai ricambi previsti.
3. Scegliere un fornitore e indicare le quantità da ordinare, il recapito di consegna e le indicazioni tecniche. Non vengono presunti prezzi, giacenze, garanzie o tempi.
4. Verificare ed emettere il PDF A4 orizzontale. Il documento è archiviato e scaricabile; non contiene prezzi di vendita o note economiche interne.
5. Trasmettere il documento con il proprio canale abituale. Nell’app registrare l’invio realmente effettuato, con data, riferimento e note. Questo blocco non invia automaticamente email o ordini al produttore.
6. Registrare la conferma del fornitore ed eventualmente la data di consegna dichiarata. La data può rimanere non dichiarata: non viene inventata.
7. Registrare gli arrivi cumulativi per ciascun codice, anche parziali. Una successiva registrazione sostituisce il totale precedente, senza sommarlo nuovamente. Le diminuzioni richiedono una verifica esplicita della rettifica.

## Controlli

- Un ordine per fornitore. Selezioni duplicate e fornitori mescolati vengono respinti.
- Somma delle quantità negli ordini attivi non superiore al fabbisogno salvato del singolo ricambio. Le bozze già preparate impegnano il fabbisogno, evitando una seconda richiesta sovrapposta. Annullare una bozza libera le relative quantità.
- Revisioni e chiavi di richiesta proteggono le scritture concorrenti e i retry identici.
- Invio registrabile una sola volta; conferme e arrivi dopo l’invio. Date, riferimenti e note sono obbligatori per gli eventi.
- Annullamento di un ordine trasmesso da registrare soltanto dopo verifica con il fornitore. Gli ordini con materiali ricevuti non sono annullabili senza prima gestire un reso o una rettifica corretta degli arrivi; non è stato inventato un flusso automatico di reso.
- Copertura e ricambi non modificabili mentre esistono ordini attivi. Anche l’annullamento dell’intervento richiede prima la riconciliazione degli ordini. Dati operativi, disponibilità verificata e consuntivi restano modificabili secondo i controlli dell’intervento.
- Storico degli eventi conservato e consultabile. PDF originale immutabile anche dopo annullamento; lo stato attuale si legge nella schermata dell’ordine.

## Disponibilità e conto economico

Gli arrivi dell’ordine non modificano automaticamente il campo «Quantità disponibile» dell’intervento: il rivenditore deve verificare fisicamente l’allocazione del materiale. Questo evita il doppio conteggio con disponibilità già dichiarate manualmente o con ricambi impiegati altrove. Non è ancora un magazzino sincronizzato.

La registrazione di ordine, conferma o arrivo non genera costi, ricavi, fatture o pagamenti. Il costo dei ricambi effettivamente utilizzati continua a essere registrato dal consuntivo dell’intervento. Riconciliazione con fatture produttore e adozione guidata delle voci manuali sono un blocco successivo.

I dati degli ordini sono riservati al rivenditore e non sono aggiunti alle API pubbliche del portale cliente. Nessuna email reale o chiamata IA eseguita nello sviluppo.

## Aggiornamento NAS

Pacchetto cumulativo nella cartella Aggiornamento. Fare prima backup di database e allegati, poi copiare mantenendo i percorsi. Non sostituire .env/backend.env.

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build backend frontend && docker compose restart gateway
```

Migrazione additiva `20261016235940_support_part_orders`. Nessun deploy sul NAS eseguito.

## Collaudo locale e seguito

Build backend/frontend e test su database temporaneo: accessi, fornitore unico, quantità, revisioni e retry, invio esterno, conferme, arrivi parziali/cumulativi, rettifiche, annullamenti e protezione dei ricambi. Regressioni interventi, preventivi, assistenza e notifiche superate. PDF di prova renderizzato e controllato in `output/support/ordine-ricambi.pdf`.

Prossimo: adozione guidata dei costi manuali e riconciliazione economica dell’assistenza. Da estendere: trasmissione SMTP dell’ordine con anteprima, riconciliazione fatture/ricambi, resi, magazzino condiviso, carta intestata del documento ed EN. Collaudo sul NAS con dati reali ancora necessario.

Test browser con API simulate superato a 320/390 px: preparazione, registrazione invio esterno, arrivo parziale. Screenshot controllato in output/support/ordini-ricambi-mobile.png. Chiavi di richiesta mantenute anche dal form durante il retry dello stesso contenuto, per evitare doppie bozze dopo un errore di rete.


Aggiornamento successivo: la trasmissione SMTP con anteprima, conferma esplicita e storico è ora disponibile. Vedere AGGIORNAMENTO-EMAIL-ORDINI-RICAMBI.md. Resta disponibile la registrazione di invii effettuati esternamente.


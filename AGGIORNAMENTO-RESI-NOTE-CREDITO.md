# Resi e note di credito ricambi — 16 ottobre 2026

## Resi fisici
Nell’ordine ricambi è disponibile «Resi cumulativi al fornitore». Indicare, per ogni riga, il totale effettivamente restituito fino a oggi, con data, riferimento e note verificati. Non è una richiesta di autorizzazione al reso e non trasmette documenti al fornitore.
I resi non possono superare gli arrivi registrati. Una diminuzione richiede una rettifica esplicita; gli arrivi non possono scendere sotto i resi. Lo storico rimane conservato, con revisioni e richieste ripetute protette. Dopo il reso completo è possibile registrare l’annullamento concordato dell’ordine. Un reso non riapre automaticamente il fabbisogno per un nuovo ordine: l’eventuale sostituzione richiede la verifica del rivenditore.
Disponibilità, quantità usate, magazzino e costi non sono modificati dal reso: prima verificare cosa è realmente rientrato o restituito.

## Note di credito
In «Documenti e fatture ricambi» è selezionabile «Nota di credito».
1. Archiviare l’originale e indicare numero, data e totale netto positivo.
2. Selezionare la fattura attiva dello stesso ordine.
3. Per il solo archivio lasciare vuoto il costo: nessun effetto economico.
4. Per documentare una riduzione, correggere prima il costo ricambi nel consuntivo dell’intervento e selezionare il costo attivo e il costo precedente da cui deriva.
5. Indicare la quota netta verificata e confermare manualmente originale, fornitore e attribuzione.
La nota documenta una riduzione già presente nel conto, non crea un secondo storno. La somma delle quote non può superare il netto della nota, della fattura o la riduzione verificata dei costi. Per le note dello stesso intervento si mantiene lo stesso costo iniziale: eventuali cambi richiedono la rettifica dei collegamenti. Il collegamento diventa da verificare se il costo viene ulteriormente sostituito.
Le rettifiche conservano lo storico e il tipo documentale. Una fattura con note attive attribuite non può essere rettificata prima di aver rettificato i relativi collegamenti. Una nota per sconto commerciale può esistere anche senza reso fisico: non si presume la causale.
Nessun rimborso o pagamento è dedotto dal documento. Nessuna emissione fiscale viene effettuata. La restituzione di materiali acquistati ma non consumati richiede una gestione di magazzino distinta; non va ridotto il costo dei materiali effettivamente usati senza verificarlo.

## Verifiche e distribuzione
Build backend/frontend superate. Database temporaneo: limiti resi, rettifiche, arrivi inferiori ai resi bloccati, annullamento dopo reso completo, nota limitata alla riduzione, collegamenti/accessi e idempotenza. Regressioni conto economico superate. Browser con API simulate a 320/390 px: registrazione reso e collegamento nota di credito. Nessuna email, chiamata IA, modifica operativa o deploy NAS.
Migrazione aggiuntiva: 20261017002000_support_part_returns. Copiare Aggiornamento dopo backup della pratica/database e degli originali; file .env esclusi.

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build backend frontend && docker compose restart gateway
```

Prossimo: collaudo sul NAS dell’intero flusso già implementato. Acquisizione email, magazzino, ripartizione tra pratiche, carta intestata completa ed EN rimangono aperti.

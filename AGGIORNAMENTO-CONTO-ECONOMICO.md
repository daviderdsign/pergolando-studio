# Conto economico della pratica - 14 ottobre 2026

## Installazione
Copiare il contenuto di Aggiornamento nella cartella principale del progetto sul NAS. Preservare backend.env, .env e il volume dati. Prima conservare un backup del database: questa versione aggiunge tabelle e colonne, senza cancellare le pratiche.

```
docker compose up -d --build backend frontend
docker compose restart gateway
```
Il comando NAS del backend deve continuare a eseguire prisma migrate deploy prima dell’avvio. Non eseguire migrate reset.

## Percorso
Archivio pratiche → Apri conto economico e documenti.

1. Registrare ricavo di vendita previsto e ricavo confermato NETTI IVA. Non si assume che il totale del configuratore sia già una vendita confermata.
2. Registrare costi dei produttori, trasporto, trasferte e altri costi diretti; scegliere Previsto o Effettivo.
3. Per la manodopera usare ORE della squadra × COSTO ORARIO della squadra, non le ore moltiplicate ancora per il numero di persone. Il backend ricalcola l’importo.
4. Quando una fattura sostituisce una conferma d’ordine o si approva una variante, scegliere Sostituisce una voce già registrata. Il totale usa solo la voce più recente; lo storico resta consultabile. La voce sostitutiva è un importo COMPLETO, non la sola differenza. Una rettifica a zero è ammessa.
5. Caricare documenti originali PDF/PNG/JPEG fino a 3 MB e collegarli alle voci. I file identici nella stessa pratica sono deduplicati. L’importazione email non è ancora attiva e nessun allegato viene automaticamente registrato come costo.
6. Registrare eventuali quote di spese generali separatamente. L’abbonamento Pergolando resta esterno alle commesse: non viene allocato automaticamente e non deve essere inserito tra queste quote.
7. Registrare incassi e pagamenti nella cassa, con l’IVA effettivamente movimentata quando presente. Questi movimenti non si sommano ai ricavi/costi economici.
8. Confermare costi completi solo dopo verifica. Il margine resta provvisorio se manca un ricavo confermato, se restano costi previsti attivi o se i costi non sono confermati completi. Un nuovo costo o un prodotto aggiunto riapre la verifica. Il margine percentuale è non calcolabile con ricavo zero.
9. Confermare consegna e collaudo: l’assistenza diventa ABILITABILE indipendentemente dalle fatture mancanti. Questa versione memorizza il requisito; il portale clienti, i ticket e le email di invito non sono ancora implementati.

## Formule
Margine diretto = ricavo netto confermato − costi diretti effettivi netti.
Margine % = margine diretto / ricavo netto confermato × 100.
Margine dopo spese generali = margine diretto − quota di altre spese generali.
Preventivo economico = ricavi previsti − costi diretti previsti. Le previsioni rimangono visibili quando sono sostituite da valori effettivi.
Cassa = incassi − pagamenti; è distinta dal margine.

## Verifiche e limiti
Compilazione backend e TypeScript frontend; test su database temporaneo per migrazioni, formule, sostituzioni, idempotenza, concorrenza e isolamento degli account, documenti e disponibilità assistenza prima della chiusura economica.
Questa è una gestione operativa per commessa, non contabilità fiscale o riconciliazione bancaria. L’esportazione è CSV delle voci con storico. I report PDF e le notifiche ai destinatari autorizzati, l’importazione della casella email, l’abbinamento agli ordini ai produttori e il portale assistenza sono blocchi successivi.
Resta il perimetro del primo blocco: ogni venditore vede le proprie pratiche; ruoli condivisi, PDF commerciale multi-prodotto e versioni del listino sono da completare.

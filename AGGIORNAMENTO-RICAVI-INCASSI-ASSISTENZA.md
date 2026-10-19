# Ricavi, incassi e rimborsi assistenza — 16 ottobre 2026

## Percorso

Pratica → Assistenza → ticket → intervento → «Ricavi, incassi e rimborsi assistenza».

La sezione è riservata al rivenditore. Per registrare serve un intervento completato con copertura «A pagamento» e un preventivo accettato corrispondente alle attività e ai ricambi storici. La semplice accettazione non genera alcun movimento economico.

## Ricavo e cassa separati

- **Ricavo cumulativo netto IVA**: inserire il totale del ricavo confermato fino a quel momento, con data, riferimento al documento/conferma e nota. Una successiva registrazione sostituisce il ricavo precedente, mantenendo lo storico. Può essere inferiore al preventivo; non può superare l’imponibile della versione accettata. Prestazioni aggiuntive richiedono una nuova base commerciale approvata, non una maggiorazione presunta.
- **Incasso effettivo IVA inclusa**: registrare il singolo movimento ricevuto, specificando metodo reale, riferimento univoco della transazione, data e nota. Sono ammessi incassi parziali. Non è un collegamento bancario: la verifica dell’accredito è svolta dal rivenditore.
- **Rimborso effettivo IVA inclusa**: registrare il singolo rimborso già eseguito. Il totale rimborsato non può superare quanto incassato per quell’intervento. Il rimborso non modifica automaticamente il ricavo: eventuali rettifiche economiche vanno documentate e registrate separatamente.

Il riepilogo mostra ricavo netto, saldo incassato al netto dei rimborsi e residuo rispetto al totale IVA inclusa del preventivo. Un importo realmente incassato superiore al preventivo può essere registrato: compare un’eccedenza da verificare con il cliente. Nessun ricavo aggiuntivo o rimborso viene generato per deduzione.

Non vengono emesse fatture, non si eseguono bonifici o pagamenti e non viene inviato alcun messaggio al cliente da questo blocco. L’abbonamento Pergolando rimane separato dalla commessa e non è ripartito sui lavori.

## Collegamenti e correzioni

Una voce manuale già presente può essere selezionata se appartiene interamente allo stesso intervento e allo stesso tipo di registrazione. Viene sostituita dal movimento gestito e resta nello storico con l’eventuale originale collegato. Per il ricavo già gestito, l’adozione di una voce manuale aggiuntiva riconcilia il doppione senza sommare due ricavi.

Per correggere un incasso o rimborso già gestito, selezionare espressamente la sua voce attiva. Altrimenti viene aggiunto un nuovo movimento. Un importo zero è ammesso solo come rettifica documentata di un movimento precedente. Il servizio respinge un secondo movimento attivo dello stesso tipo con identici metodo e riferimento; non cerca corrispondenze probabilistiche.

Se lo stesso incasso è già presente sia fra i movimenti gestiti sia fra le voci manuali, non aggiungerlo nuovamente: riconciliare prima la voce manuale duplicata nel conto con una rettifica documentata. Non è prevista qui la suddivisione di un bonifico che copre più interventi o più commesse.

Le voci gestite sono protette dalle correzioni generiche del conto: si rettificano dal relativo intervento. Dopo aver registrato ricavi o cassa, copertura e ricambi storici dell’intervento non sono modificabili; per nuove prestazioni aprire un nuovo intervento. Le rettifiche dei costi effettivi restano possibili secondo il flusso già presente.

## Acconto originale e conto economico

Gli incassi/rimborsi dell’assistenza sono inclusi nella cassa complessiva della commessa ma esclusi dalla verifica dell’acconto della vendita originale e dai requisiti di incasso degli ordini ai produttori. Non possono essere verificati nuovamente come acconto iniziale. Anche una vecchia voce manuale prima classificata come acconto smette di contribuire a quel conteggio quando viene esplicitamente riclassificata nell’assistenza; le verifiche precedenti restano nello storico.

Il conto economico riporta separatamente ricavi, incassi e rimborsi assistenza nel riepilogo. Sono già inclusi nei totali generali e non vanno aggiunti una seconda volta. Il CSV conserva l’identificativo dell’intervento. Il saldo del preventivo non è una certificazione fiscale del credito o dell’avvenuta fatturazione.

Ogni scrittura richiede revisione economica corrente, verifica del rivenditore e chiave di richiesta idempotente. Il form mantiene la chiave per il retry dello stesso contenuto. Nessun prezzo, aliquota, accredito o data viene inventato.

## Aggiornamento NAS

File cumulativi nella cartella Aggiornamento. Eseguire prima backup di database e allegati; copiare mantenendo i percorsi e senza sostituire .env/backend.env.

```sh
cd /home/davideromeo/Pergolando-chatgpt
docker compose up -d --build backend frontend && docker compose restart gateway
```

Migrazione additiva `20261016235959_support_settlements`: riferimenti all’intervento e alla versione commerciale, dati della verifica economica e indice. Non crea movimenti per interventi preesistenti. Nessun deploy sul NAS eseguito da questa sessione.

## Verifiche e seguito

Build backend/frontend. Test locali su database temporaneo: accessi, preventivo accettato e completamento, ricavo cumulativo distinto dalla cassa, parziali/rimborsi/rettifiche, eccedenze, duplicati, revisioni, adozione manuale e incassi esclusi dall’acconto originale e dalla relativa verifica ordini. Regressioni acconti, conto economico, ordini, interventi e riconciliazione passate. Test browser con API simulate a 320/390 px: verifica esplicita, ricavo senza incasso automatico, metodo/riferimento e residuo. Screenshot in output/support/ricavi-incassi-mobile.png e ricavi-incassi-dettaglio.png.

Nessuna email reale, chiamata IA, operazione bancaria o modifica al database operativo eseguita. Prossimo blocco: trasmissione SMTP degli ordini ricambi con anteprima e storico degli esiti. Restano ripartizioni fra interventi, fatturazione, acquisizione automatica documenti produttori, resi, magazzino, carta intestata, EN e collaudo completo sul NAS.

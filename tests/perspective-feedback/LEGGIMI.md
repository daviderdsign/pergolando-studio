# Prove prospettiche corrette

Le foto originali e le anteprime annotate rimangono locali e sono escluse dal repository pubblico. I test che richiedono questi file vengono esplicitamente saltati quando non sono disponibili. Coordinate e annotazioni geometriche restano versionate.

Cinque casi esportati il 7 ottobre 2026. Le coordinate sono osservazioni dell’utente da verificare, non una calibrazione metrica certificata. Il quinto caso è stato indicato come già accettabile senza correzioni.

Le PNG `verifica-annotata.png` contengono sovrapposizioni: usarle per confronto visivo, mai come ingresso per valutare il rilevatore. Tutti e cinque i casi hanno ora la foto originale: la prima recuperata dal servizio e le altre quattro fornite dall’utente. Le proposte storiche non sono disponibili; il confronto usa una baseline ricalcolata sugli originali, prima delle modifiche derivate dal feedback. I report sono in output/calibration-diagnostics/feedback-baseline.json e feedback-improved.json.

Le metriche verificano soltanto se le tre fughe possono dare una camera a pixel quadrati con centro ottico dentro l’immagine. Un esito negativo può dipendere da riferimenti, ritaglio o ipotesi della camera; non invalida automaticamente il giudizio visivo.

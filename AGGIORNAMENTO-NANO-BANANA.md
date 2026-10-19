# Prova ambientazione Nano Banana

Scompattare lo ZIP nella cartella del progetto sul NAS, preservando backend.env.

Nel backend.env del NAS deve essere presente GEMINI_API_KEY (non comunicarla in chat). L’API Blender non sostituisce la chiave Gemini.

Eseguire:
```
docker compose up -d --build backend frontend
docker compose restart gateway
```

Demo 1: creare il rendering Blender, scegliere il motore, premere Genera immagine finale. Il sistema invia foto composita e maschera bianca della pergola su nero, con il colore richiesto e un prompt per ombre, tavolini e persone. L’immagine IA appare separata; l’originale resta scaricabile. Il PDF usa la versione IA quando presente; Usa l’immagine Blender originale la esclude dal PDF.

La maschera è una guida nel prompt, non un vincolo di inpainting garantito. Controllare sempre geometria e sfondo. Non è attiva la ricomposizione protetta dei pixel Blender. La prova riguarda un’ambientazione da bar; Nano Banana 2.1 richiede qui un’uscita 4:3 2K. Nessuna verifica universale della fedeltà dei prodotti è stata eseguita.

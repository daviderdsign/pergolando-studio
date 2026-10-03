# Note tecniche — modello parametrico Flag (`flag.blend`)

**Nomenclatura (correzione 2026-09-28)**: il pezzo si chiama **Frangitratta**, non
"Frangivento" — rinominato ovunque in questo file, in `generate_flag.py` (variabili,
costanti, nomi oggetto cercati) e negli oggetti/mesh reali dentro `flag.blend` stesso
(6 datablock rinominati via script diretto, file risalvato; backup pre-rename tenuto
come `flag.blend.bak-prerename` finché non si conferma che tutto è a posto).

Log tecnico di dettaglio per il lavoro di parametrizzazione del modello 3D Flag in Blender,
tramite BlenderMCP (sessione interattiva Claude ↔ Blender live, stesso file condiviso).
Il `CHANGELOG.md` in root tiene la cronologia ad alto livello per fase; qui invece le
convenzioni, le costanti di calibrazione e le tecniche usate pezzo per pezzo — necessarie
per continuare il lavoro o rigenerare la logica in uno script headless.

## Convenzioni geometriche condivise

- Ogni mesh è modellata in **centimetri**; ogni oggetto ha `location=(0,0,0)`,
  `rotation_euler=(90°,0,0)`, `scale=(0.01,0.01,0.01)` — la posizione reale è quindi
  **cablata nei vertici**, non nel transform dell'oggetto (eccetto poche eccezioni di
  traslazione pura, es. `Frangitratta_pos_N`, spiegate sotto).
- Mappatura assi locale → mondo (conseguenza della rotazione X di 90°):
  - `world_X = local_x` (larghezza, invariato)
  - `world_Z = local_y` (altezza)
  - `world_Y = -local_z` (profondità/sporgenza — **attenzione al segno**)
- Convenzione fronte/retro: **+Y mondo = retro**, **-Y mondo = fronte**.
- `+Z mondo` = alto.
- **Origine del mondo (dal 2026-09-26 sera): Y=0 è il punto più posteriore di
  `Aggancio_Parete`** (il bracket di fissaggio a parete), non più un punto
  "centrato" arbitrario. Tutta la pergola è stata traslata rigidamente una
  volta per tutte (poi ogni `location` riportata a `(0,0,0)` incorporando lo
  spostamento nei vertici, stessa tecnica di `bake_location` usata più
  sotto) così che **il retro sia fisso nello spazio e SP (profondità)
  misuri sempre da lì** — vedi la sezione "Architettura a perno fisso" qui
  sotto, è il presupposto su cui si basa tutta la riscrittura.

## Architettura a perno fisso (2026-09-27) — sostituisce il sistema a offset

**Cambio di paradigma**, proposto da Davide dopo aver visto che il sistema a offset (tabella
sotto) continuava a rompersi in modo imprevedibile su dimensioni non di riferimento
(Frangitratta troppo vicino alla Guida, Tettuccio che la interseca, ecc.): invece di spostare
ogni pezzo con una formula propria calibrata a mano, **Guida, Telo, Frangitratta (tutti),
Tettuccio e Supporto ruotano insieme, rigidamente, attorno a un unico perno fisico reale** —
il foro delle due "zanche" della Guida (visibile a occhio in Blender, un cerchio). Una
rotazione pura preserva automaticamente e per costruzione ogni relazione geometrica tra i
pezzi (niente più fit di rette/offset per-pezzo, niente più scarti che crescono con le
dimensioni).

### Il perno

Trovato per clustering (nessuna geometria a faccia singola per il foro — un `bmesh.ops.delete`
per faccia non basta, serve cercare un gruppo denso di vertici): seed su un vertice vicino
alla posizione nota, poi mean-shift (`center = media dei vertici entro 5cm`, ripetuto finché
stabile). Stabile a **176 vertici totali entro un raggio di 4-5cm** (due fori/zanche simmetrici
in X, 88 vertici ciascuno). Coordinate locali attuali (dopo lo spostamento origine sopra):

```
PIVOT_LOCAL_Y = 240.3172149658203   # altezza
PIVOT_LOCAL_Z = 13.917588233947754  # profondità dal muro
FRONT_REF_LOCAL_Y = 222.54885838062467  # punto di riferimento "fronte" (anello guida vicino a z max)
FRONT_REF_LOCAL_Z = 310.5169673805073
```

Queste costanti sono state **verificate identiche** sia sul file `flag.blend` originale
(dopo lo spostamento origine) sia sul file di prova `flag5.fbx` che Davide aveva preparato
separatamente con la stessa idea — conferma indipendente che il perno è quello giusto.

### La formula (`compute_rail` in `generate_flag.py`)

Dato **H_cm** (altezza frontale, script), **delta_h_cm** (H1 venditore = retro−fronte) e
**P_cm** (profondità, script = SP venditore):

1. **Altezza target del perno**: `H_cm + delta_h_cm + 5` — i 5cm sono
   `PIVOT_HEIGHT_OFFSET_CM`, deciso da Davide perché non esiste un riferimento fisico preciso
   per "dove il venditore misura H" rispetto al centro del foro: si assume che il perno stia
   5cm sopra quel punto. **Attenzione**: durante i test con Davide, per verificare la sola
   rotazione senza spostare il perno, questa parte va disattivata (rail con `pivot_target_y`
   fisso) — è successo più volte di confondersi tra "voglio vedere solo l'angolo" e "voglio
   il perno vero", vedi sotto.
2. **Punto target fronte**: altezza = `H_cm + (FRONT_REF_LOCAL_Y - REF_H_CM)`, profondità =
   `P_cm + (FRONT_REF_LOCAL_Z - REF_P_NOMINAL_CM)` — sono le stesse formule di offset-da-
   riferimento del sistema vecchio, ma ora applicate a UN SOLO punto (non più per-pezzo).
3. **Angolo e "allungamento"**: `target_angle = atan2(dy, dz)` tra perno e punto-fronte
   target; l'"estensione" è la differenza tra la distanza perno→fronte target e quella di
   riferimento. Una rotazione pura non può cambiare quanto la Guida "arriva lontano" (la
   distanza dal perno resta quella del pezzo rigido) — serve un allungamento aggiuntivo,
   applicato come traslazione lungo la stessa direzione dell'angolo target, **solo ai
   vertici che partivano oltre `FRONT_GROUP_Z_THRESHOLD_CM` (perno+20cm)** — cioè la parte
   del pezzo che "punta verso il fronte", non l'attacco vicino al perno.

Verificato: a `H_cm=REF_H_CM`, `P_cm=REF_P_NOMINAL_CM` e `delta_h_cm` = quello implicito nel
perno (`PIVOT_LOCAL_Y - REF_H_CM - 5 = 35.317...`), rotazione ed estensione tornano
**esattamente zero** e la Guida ricostruita combacia byte-per-byte con l'originale (scarto
misurato: 0.0).

### Chi fa cosa (`rail_transform_verts(obj, rail, delta_x_cm, extend)`)

- **`extend=True`** (ruota E si allunga verso il fronte): Guida, Telo, il Frangitratta
  "Iniziale" (cap), Supporto. Sono i pezzi che devono davvero *raggiungere* il fronte a
  qualunque SP.
- **`extend=False`** (ruota sul posto, nessun allungamento): Tettuccio, Frangitratta_Finale,
  Aggancio_Parete, Montante_Posteriore_Dx/Sx, Trave_Posteriore. Sono pezzi vicini al perno
  che devono solo seguire l'angolo del retro, non "arrivare" da nessuna parte. **Il
  Tettuccio in particolare non deve MAI essere altro che ruotato** — le sue nervature sono
  già generate per L, non c'entrano con SP/Δh (istruzione esplicita di Davide dopo che un
  primo tentativo con `extend=True` gli aveva letteralmente strappato/deformato le
  nervature).
- **Montante/Trave (fronte)**: NON fanno parte del gruppo che ruota — sono pali verticali,
  la loro altezza è `H_cm` diretto e la profondità è un semplice shift
  `P_cm - REF_P_NOMINAL_CM` (stesso principio del vecchio `rear_depth_delta_cm`, ma ora
  applicato al FRONTE che si allontana dal muro, non al retro che si sposta).
- **Frangitratta intermedi**: non hanno una posizione di riferimento propria lungo la guida
  (sono N copie identiche), quindi non possono usare `rail_transform_verts` direttamente —
  si posizionano per **interpolazione lineare tra Cap e Finale già trasformati** (frazione
  `i/(n+1)`), poi si ruotano attorno al **proprio centro** (non al perno globale) per restare
  perpendicolari a Telo/Guida. Tentare di posizionarli con la formula del perno "a monte"
  (prima di trasformarli) dà risultati sbagliati se non si fa attenzione a QUALE stato di
  Cap/Finale si interpola — un tentativo intermedio li ha piazzati "dopo" il Finale invece
  che in mezzo per questo motivo.

### Bug reali trovati costruendo questo sistema (tutti superati, tutti istruttivi)

- **`obj.location` vs vertici**: alcuni pezzi (`Frangitratta_pos_N`, a volte `Finale`) usano
  `object.location` (spazio mondo, metri) invece di codificare la posizione nei vertici
  (spazio locale, cm) — **due sistemi di coordinate diversi**. Ruotare solo i vertici
  ignorando una `location` residua dà risultati completamente sbagliati. Fix sistematico:
  prima di toccare i vertici di QUALSIASI oggetto, **"cuocere" la location nei vertici**
  (leggere le posizioni mondo con la location attuale, azzerare la location, ricalcolare i
  vertici locali dalla nuova matrice) — mai assumere che `location` sia già zero.
- **Mesh condivisa (`data.users > 1`)**: `Frangitratta_Iniziale_Finale` e `Frangitratta_Finale`
  condividevano lo stesso datablock mesh nel file (stesso pezzo fisico installato alle due
  estremità, per design — Davide: "è lo stesso pezzo, lo copi") — modificare i vertici
  dell'uno modificava anche l'altro. Controllare sempre `obj.data.users` e fare
  `obj.data = obj.data.copy()` prima di editare, per qualunque pezzo che potrebbe condividere
  dati con un altro.
- **Contesto Blender dopo un reload**: `bpy.ops.wm.open_mainfile()` seguito nello STESSO
  blocco Python da un operatore che richiede un "active object" (es.
  `bpy.ops.object.mode_set`, usato dentro `build_tettuccio`) fallisce con "Context missing
  active object" — serve impostare `bpy.context.view_layer.objects.active` in una chiamata
  **separata** dopo il reload, prima di richiamare `build_pergola`.
- **Larghezza doppiata**: `stretch_x_symmetric` imposta già la larghezza assoluta finale da
  `L_cm` — passare ANCHE `delta_x_cm` a `rail_transform_verts` per lo stesso pezzo la somma
  di nuovo (bug reale, scoperto perché lo scarto misurato coincideva esattamente con Δh per
  puro caso, cosa che ha inizialmente confuso la diagnosi). Regola: un pezzo usa **o**
  `stretch_x_symmetric` (larghezza assoluta) **o** lo shift `delta_x_cm` dentro
  `rail_transform_verts` (scostamento relativo da una larghezza di riferimento fissa), mai
  entrambi.
- **Tettuccio, buco asimmetrico nelle nervature**: raccontato in dettaglio più sotto
  (sezione "Tettuccio — buco nelle nervature").

### Nomenclatura venditori (per riferimento, da riconciliare col wizard)

Il modulo del venditore (form cartaceo/digitale reale) usa nomi diversi dai nostri:

| Simbolo venditore | Significato | Corrisponde a... |
|---|---|---|
| L | larghezza | `L_cm` (uguale) |
| SP | profondità | `P_cm` |
| P | altezza **frontale** | `H_cm` |
| H | altezza **posteriore** | `H_cm + deltaH_cm` |
| H1 | H − P | `deltaH_cm` |

**Non ancora rinominato nello script** (deliberato, per non toccare il contratto
wizard/backend finché non si aggiornano insieme) — ma da tenere a mente leggendo/scrivendo
config di test: quando Davide dice "P=220" intende l'altezza frontale, non la profondità.

### Tettuccio — buco nelle nervature (bug reale, non dimensionale)

Rigenerando le nervature (`build_tettuccio`), a dimensioni di riferimento (dove tutto
dovrebbe riprodursi esatto) mancava un pezzo consistente di tettuccio **solo sul lato
destro**, mai a sinistra. Diagnosticato passo-passo (rendering top-down, isolando il singolo
step "solo taglio, prima di rigenerare"): non erano le nervature mancanti, era proprio la
**cancellazione a cascata di bmesh**: `bmesh.ops.delete(bm, geom=vertici, context="VERTS")`
cancella anche ogni faccia che tocca uno qualsiasi dei vertici cancellati — con la soglia di
taglio originale (`margin=20`), un vertice che sta appena dentro la zona di taglio SOLO sul
lato destro (mesh non perfettamente specchiata, differenza reale ~2cm, confermato con un test
a tappeto su margini diversi) appartiene a UNA faccia grande e connessa che copre gran parte
del tappo destro — cancellare quel singolo vertice si porta via l'intera faccia (e tutto
ciò che era raggiungibile solo tramite di essa). A sinistra la stessa zona è più suddivisa
(più facce piccole), quindi la cancellazione resta locale. Fix: margine allargato a 22
(sotto quella soglia critica su entrambi i lati, confermato con lo stesso test a tappeto).

Seconda scoperta, da Davide, che semplifica tutto: **le nervature possono benissimo
estendersi sotto le facce di chiusura del tappo** (che esistono apposta per coprirle) — non
serve calcolare con precisione dove le nervature "devono" fermarsi rispetto a quel che
sopravvive al taglio. Il range delle nervature ora si calcola direttamente dal **bordo
esterno vero** (`target_outer`, simmetrico per costruzione) meno un margine fisso di
sicurezza (`rib_reach_margin`), non più misurando cosa resta dopo il taglio (fragile, ha
causato il bug sopra). Margine finale tarato con Davide guardando il render: **8.8cm**
(prima 20cm, troppo conservativo — mancavano visibilmente 1-2 nervature per lato).

**Verificato**: L=300 → 25 nervature, L=500 → 43 nervature (formula simmetrica, confermato a
occhio in Blender da Davide entrambe le volte).

## Pezzi e tecniche di stretch/riposizionamento (sistema VECCHIO — superato per i pezzi
sopra, ancora attuale per quelli non ancora migrati)

| Pezzo | Tecnica | Note |
|---|---|---|
| `Montante` / `.001` (specchiato) | "piede fisso + stiramento": vertici con `local_y > 20cm` (soglia piede/drenaggio) traslati alla nuova altezza; tutti i vertici traslati in X per la nuova larghezza | Altezza pura = `H_frontale`. `.001` è una copia indipendente con X negato. |
| `Trave` / `Trave_Posteriore` | semplice estrusione a 2 anelli (nessun vertice intermedio) → basta traslare simmetricamente `x>0`/`x<0` per allungare | Sbalzo oltre il bordo esterno del montante: **Trave 2.41cm/lato**, **Trave_Posteriore 1.2cm/lato** (costanti fisiche del pezzo, indipendenti da L) |
| `Montante_Posteriore_Dx/Sx` | rigenerati **da zero** ogni volta dal `Montante` (mesh copy + stiramento fino a `H_frontale+Δh` + shift di profondità pari a quello di `Trave_Posteriore`) | Non esistono come pezzo di riferimento proprio: sono sempre derivati |
| `Supporto` / `.001` | trasla solo in X (segue il montante) + in altezza (segue l'aumento di `H_frontale`) | Nessuna dipendenza da P/Δh |
| `Guida` / `.001` | 2 soli anelli (fronte ~233 vert, retro ~575 vert) → trattati come **gruppi rigidi**: anello fronte trasla in X e in altezza (`H_frontale`); anello retro trasla in X, altezza (`H_frontale+Δh`) e profondità | Calibrazione P: la campata reale guida fronte-retro è **P_nominale − 2.9cm** (misurato una volta sul file di riferimento, non ri-derivato ogni volta). Pendenza reale della guida **non coincide con Δh/P teorico** — va sempre ricalcolata dal centroide fronte/retro della mesh (vedi sotto), mai assunta. Il piccolo disallineamento angolare dell'innesto nella trave posteriore (rotazione del dettaglio di taglio) è stato finora **ignorato** come approssimazione accettabile. |
| `Frangitratta_Iniziale_Finale` (+ `Frangitratta_Finale` linkata) | stessa tecnica 2-anelli di Trave; posizione fronte = offset fisso da Trave (~4.2cm verso il centro); posizione/quota retro ricalcolata a parte per non intersecare i pilastri posteriori (margine 2cm) | `Frangitratta_Finale` condivide la stessa mesh-data (linked, non copiata) |
| `Frangitratta_Intermedio` → `Frangitratta_pos_N` | copie **linked** (stessa mesh-data condivisa) traslate via `object.location`; conteggio ricalcolato ogni volta con la regola ~50cm: `n = round(span/0.50) - 1` | **Attenzione**: quando si sostituisce la mesh sorgente (`tgt.data = ref.data`), bisogna ri-collegare `.data` anche su OGNI copia `pos_N`/`Finale`, altrimenti restano agganciate alla mesh vecchia (bug reale già capitato, oggetti "a pavimento") |
| Quota Z dei Frangitratta | formula `target_local_y = slope*target_local_y_guida... ` più precisamente: `target_z_world = slope*target_y_world + intercept`, con `slope` = pendenza reale della guida (vedi sotto) e `intercept` calibrato dal pezzo di riferimento originale (offset costante sotto la guida, verificato quasi identico tra pezzo iniziale e intermedio) | Bug reale: dimenticare la componente Z (quota) e spostare solo lungo Y stacca il frangitratta dalla guida |
| `Tettuccio` | pannello con 2 tappi laterali fissi (dettaglio ~20cm a ogni estremo) + un'unica nervatura centrale da moltiplicare; periodo di ripetizione misurato con precisione sub-mm: **11.1994875 cm** | Tecnica: estrarre la nervatura centrale (bmesh, finestra `-6.5<x<6.5`), cancellare la vecchia zona nervata, allargare i tappi, ri-generare N copie (`k_min..k_max` = quante ne entrano nello spazio utile tra i tappi) |
| `Tettuccio_Lato_Dx/Sx` | pezzo separato (`tettuccio_lato.fbx`), copre il "buco" laterale del tettuccio; stessa logica di offset/pendenza del tettuccio | Segue anch'esso la pendenza reale della guida (slope ricalcolato, non quello teorico) |
| `Telo` | rimappaggio proporzionale: fit lineare `local_y = a*local_z+b` sui dati originali, poi per ogni vertice si preserva il **residuo** rispetto alla retta e si ricalcola sulla nuova retta/nuova estensione — per non perdere le pieghe/dettagli del telo originale | Deve restare **sotto la guida**, nello spazio tra guida e frangitratta (offset negativo rispetto alla retta guida, non sopra) |
| `Aggancio_Parete` / `.002` | bracket per variante a parete; stessa logica di shift di `Trave_Posteriore` (X, altezza, profondità) | Sostituita almeno una volta con mesh più dettagliata da `aggancio_parete.fbx` — solo riposizionamento, nessuna logica nuova |
| `Timpano` + `Trave_Laterale` | pannello di chiusura laterale opzionale (solo se la pergola è "chiusa"); il bordo superiore deve restare parallelo alla guida | **Tecnica corretta** (validata da Davide): NON forzare ogni vertice sulla retta della guida (appiattisce lo spessore/profilo alluminio) — invece **traslare rigidamente l'intero gruppo di vertici superiori di un'estremità** (es. l'angolo fronte) lungo l'asse Z, mantenendo fissa l'altra estremità, fino a far coincidere la distanza dal bordo guida **nei due vertici più esterni** (fronte e retro), non nella media del gruppo |
| `Pilastrino_intermedio`, `Skipper` | introdotti in `flag4.fbx`; **chiarito 2026-10-03**: entrambi allo stesso spigolo di `Montante`/`Guida` (non al centro) — quasi certamente geometria del prodotto "Skipper" (non incluso in questo bundle) rimasta mescolata nell'FBX | Tenuti nascosti in scena |

## Pendenza reale della guida (da ricalcolare sempre, mai assumere)

```python
pts = [(v.co.y, v.co.z) for v in guida.data.vertices]
front = [(y,z) for (y,z) in pts if z > 0]
rear  = [(y,z) for (y,z) in pts if z < 0]
centroid = lambda pts: tuple(sum(p[i] for p in pts)/len(pts) for i in range(2))
fc, rc = centroid(front), centroid(rear)
a_guide = (rc[0]-fc[0]) / (rc[1]-fc[1])   # local_y = a*local_z + b
b_guide = fc[0] - a_guide*fc[1]
```

Il campionamento **per centroide fronte/retro** (non per singoli vertici estremi) è
importante: la guida ha dettagli complessi alle due estremità (flare frontale, taglio
d'innesto posteriore) che distorcono una stima "punto per punto".

## Bug reali già incontrati (per non ripeterli)

- Confondere `local_y` (altezza) con `local_z` (profondità) quando si scrive codice di
  shift — capitato più volte, sempre risolto verificando il bounding box mondiale subito
  dopo ogni edit, mai fidandosi del solo calcolo simbolico.
- Editare la mesh di un pezzo "master" senza ripropagare `.data` alle copie
  linked/derivate (Frangitratta_pos_N, Montante_Posteriore).
- Ordinare/stampare i vertici per debug (es. `sorted(..., key=...)`) e poi provare a
  "ripristinare" scrivendo `zip(mesh.vertices, lista_ordinata)` — **corrompe la topologia**
  perché l'ordine dei vertici nella mesh non è quello con cui sono stati stampati. Per
  ripristinare in sicurezza: o si rilegge il `.blend` salvato, o si fa un lookup per
  `(x,z)` (coordinate non toccate dall'edit) invece di affidarsi all'ordine.
- Forzare più vertici di un dettaglio (profilo/spessore reale del pezzo) sulla stessa
  retta matematica — appiattisce dettagli 3D reali (visto sul Timpano). Va mosso il
  gruppo **rigidamente**, mai i singoli vertici indipendentemente, quando il dettaglio ha
  un proprio spessore/profilo da preservare.

## Varianti di fissaggio (collection Blender)

Due collection alternative, mutuamente esclusive (una sola attiva per volta via
`layer_collection.exclude`):
- **`Config_Autoportante`**: `Trave_Posteriore` + `Montante_Posteriore_Dx/Sx`.
- **`Config_Parete`**: `Aggancio_Parete` + `.002`, nessuna trave/pilastro posteriore.

Tutti gli altri pezzi (fronte, guide, frangitratta, tettuccio, telo) sono condivisi tra le
due varianti e stanno fuori da entrambe le collection.

## Stato / test eseguiti

- Pergola 3x3 (P nominale 300, H 200, Δh 40) — assemblaggio originale, validato pezzo per
  pezzo da Davide dal vivo.
- Pergola 560×450 (H 220, Δh 60) — primo vero test parametrico end-to-end, generalizzando
  tutte le tecniche sopra. Validato visivamente da Davide, poi **riportato manualmente allo
  stato 3x3** per allineare l'importazione di `flag4.fbx` (fatto sui riferimenti originali).

## `3d/generate_flag.py` — script headless (Fase G, passo 4)

Trascrive tutte le tecniche sopra in funzioni riutilizzabili (`build_montante`,
`build_trave`, `build_guida`, `build_frangitratta`, `build_tettuccio`, `build_telo`, ecc.),
guidate da un'unica `build_pergola(L_cm, P_cm, H_cm, delta_h_cm, fissaggio)`. Va eseguito con
Blender in `--background`, aprendo **`3d/flag.blend` stesso** come file (il suo stato su
disco — 3x3, H=200, Δh=40 — è la calibrazione di riferimento): non scrive mai su
`flag.blend`, produce solo un render (e opzionalmente un `.blend` separato per ispezione).

Scoperta algebrica utile: le costanti di "offset" per-pezzo (13.8cm per la trave, 2.9cm per
la guida) usate finora per calcolare lo spostamento in profondità si **semplificano
sempre** a un unico valore universale `P_cm - 300` (l'offset e la campata di riferimento si
elidono a vicenda) — niente più bisogno di ricalcolare uno span per ogni pezzo.

Bug reale trovato e corretto durante la stesura (non ancora vissuto durante il lavoro
interattivo, perché lì il Telo era sempre stato sistemato per un singolo cambio di
dimensione alla volta): la logica del **Telo** riusava la pendenza VECCHIA della guida per
ricostruire la nuova posizione — nella sessione interattiva questo aveva funzionato solo
perché la guida era già stata aggiornata all'iterazione precedente. Nello script generale va
catturata la pendenza di riferimento (`ref_slope_a/b`) **prima** di toccare la guida, e la
nuova pendenza **dopo**, applicando l'offset fisso del Telo (misurato una volta) sulla retta
nuova, non su quella vecchia.

**Secondo bug reale, trovato il 2026-09-26** rivedendo un render con Davide (il Frangitratta
appariva sollevato sopra il Telo invece di esserci annegato dentro, come nel file
originale): `build_telo` sommava l'offset **due volte** — `new_front_y`/`new_rear_y` lo
includevano già, poi il ciclo aggiungeva di nuovo l'intero `residual` (che per i vertici
estremi coincide esattamente con l'offset), raddoppiandolo (~7cm di troppo, confermato
confrontando con il file `.blend` reale via BlenderMCP: `Telo` a Z=2,1729m nel file originale
contro Z=2,1016m prodotto dallo script). C'era anche uno scambio fronte/retro nella stessa
formula (l'altezza del fronte finiva sul vertice posteriore e viceversa). Riscritta con lo
stesso pattern, più semplice, già usato in `build_tettuccio_lato`: residuo rispetto alla
retta VECCHIA preservato e sommato **una sola volta** alla retta NUOVA valutata alla nuova
z del vertice — niente più `offset_front`/`offset_rear`/endpoint da scambiare. Verificato: a
dimensioni di riferimento riproduce ora esattamente il file `.blend` originale (confronto
diretto via BlenderMCP, scarto zero); a Δh=20 il Telo risulta correttamente **dentro**
l'inviluppo verticale del Frangitratta su tutta la profondità, con la Guida appena sopra —
l'ordine fisico corretto confermato da Davide (Frangitratta sotto, Telo in mezzo, Guida sopra).

Verificato con render headless (fotocamera di debug + luce, nessun materiale reale):
- Dimensione di riferimento (300×300, H200, Δh40): riproduce la struttura originale.
- Dimensione diversa (450×350, H230, Δh50): si generalizza correttamente — pilastri
  posteriori visibilmente più alti, proporzioni coerenti, nervature tettuccio ricalcolate.
- Variante a parete (350×280, H220, Δh35, `fissaggio: "parete"`): niente pilastri
  posteriori, corretto.

### Fotocamera dalla posa OpenCV (`setup_camera_from_pnp`)

Converte l'output di `solvePnP` (stessa convenzione PnP-world del backend: X destra, Y
verso il basso, Z profondità, tutto in cm) in un transform camera di Blender. **Verificato
numericamente**: passando una posa reale calcolata dal backend per 4 punti noti (es. piede
anteriore sinistro a coordinate normalizzate (0.15, 0.75) su un'immagine 1200×900), i piedi
del modello renderizzato proiettano esattamente in quelle stesse coordinate (scarto di 1-2px
su 1200) — conferma che l'intera pipeline punti-tap → solvePnP → camera Blender è coerente.
**Questa verifica risale a prima della riscrittura "architettura a perno fisso" e del cambio
di origine del 2026-09-26** — vedi sotto per la riverifica reale del 2026-09-28.

#### Architettura di calibrazione ATTUALE — diversa da quanto sopra (scoperta 2026-09-28)

**Il passo 2/3 descritto altrove in questo file e in CHANGELOG.md ("4 punti tappati sui
piedi, solvePnP in browser via opencv-js WASM") è STORICO/SUPERATO.** Trovato durante la
sessione del 2026-09-28 (non documentato da nessuna parte finché non è stato scritto qui):
esiste ora un intero servizio nuovo, `pergolando-geocalib-service/` (Python, non ancora in
CHANGELOG.md, creato 2026-09-27 — verificare con Davide se è farina di questa stessa serie
di sessioni o di una sessione parallela), che sostituisce l'approccio a 4 punti con:

1. **GeoCalib** (`cvg/GeoCalib`, rete neurale PyTorch): calibrazione camera da una singola
   immagine, senza alcuna linea di riferimento manuale — stima focale (fx,fy) e direzione di
   gravità (roll, pitch) direttamente dai contenuti dell'immagine.
2. **Resection a 2 punti** (`resection.py`, `resect_points`): il venditore traccia UNA riga
   sulla foto reale — la giunzione parete-pavimento, esattamente dove si aggancerà la
   pergola (non più i 4 piedi di una pergola non ancora installata: per il fissaggio a
   parete quei piedi posteriori non esistono nemmeno) — e conferma la sua lunghezza reale.
   Risolve i 4 gradi di libertà rimanenti (yaw, tx,ty,tz) via least-squares non lineare
   dati roll/pitch/focale di GeoCalib. Supporta anche una riga di controllo opzionale
   (secondo punto, es. il bordo del terrazzo perpendicolare alla parete) che sovra-determina
   il sistema — **~4.5x meno errore di yaw sotto rumore di tap simulato**, verificato
   sinteticamente prima di collegarlo.
   Storia documentata nel docstring di `server.py`: due schemi precedenti (solvePnP su 4
   piedi tappati, poi 2 piedi con la larghezza L della pergola come riferimento di scala)
   sono stati provati e abbandonati per imprecisione/nonsenso geometrico (piedi posteriori
   inesistenti per il fissaggio a parete).
3. Convenzione mondo: **identica** a `generate_flag.py`/`PerspectiveService` — X larghezza,
   Y altezza (giù+), Z profondità (fronte=0, retro=P). La riga tracciata (parete) è trattata
   come il **retro** (Z=P), non il fronte — bug reale già trovato e corretto prima di questa
   sessione (spingeva la pergola dentro il muro invece che verso lo spazio aperto).

Isolato in un proprio servizio HTTP (stesso motivo di `pergolando-blender-service`: torch/
opencv/scipy non hanno senso nell'immagine Node del backend). Il backend lo chiama da
`PerspectiveService` (`POST {GEOCALIB_SERVICE_URL}/calibrate-placement`).

**Ambiente locale verificato pronto** (2026-09-28): `pergolando-geocalib-service/.venv` ha
torch/opencv/geocalib già installati e funzionanti (CPU, no CUDA disponibile in questo
ambiente — un run reale ha impiegato pochi secondi, accettabile per un test manuale ma da
valutare per l'uso interattivo nel wizard).

#### Riverifica end-to-end con foto reale (2026-09-28)

Primo test reale mai fatto di **tutta** la catena punti-tap → GeoCalib → Blender su una foto
vera (non sintetica) di un terrazzo di Davide. Riga tracciata: giunzione parete-pavimento tra
un lampione e l'inizio di un tettuccio esistente, 650cm reali (misurati da Davide), punti
campionati per colore pixel (non tap manuale — script standalone, non nel wizard).

**Bug reale trovato e corretto**: in `setup_camera_from_pnp`, dopo aver impostato
`cam_obj.location`/`cam_obj.rotation_euler` su un oggetto camera appena creato, mancava un
`bpy.context.view_layer.update()` — senza quello, `cam_obj.matrix_world` (e qualunque cosa
lo legga, es. `bpy_extras.object_utils.world_to_camera_view`, usata per verificare la
proiezione) restituiva ancora la matrice "stale" pre-creazione: ogni punto del mondo
proiettava sullo stesso identico pixel (centro immagine). **Non influenzava il render vero**
(`bpy.ops.render.render()` valuta sempre il proprio depsgraph fresco, indipendentemente) —
scoperto solo perché la verifica numerica via `world_to_camera_view` dava risultati assurdi
mentre il render stesso, riguardato con più attenzione, era in realtà già corretto. Fix
comunque necessario per qualunque futuro script di verifica/overlay basato su quell'utility.

**Falso allarme iniziale**: il primissimo render/composito sembrava "collassato" (una sottile
barra diagonale invece di una pergola credibile) — sembrava un bug, ma proiettando
numericamente i punti strutturali noti (piedi, angoli tetto) con `world_to_camera_view` i
valori combaciavano bene con la riga tappata sulla foto. Spiegazione reale: con le dimensioni
inventate per il test (L=600, SP=350, P=250 — mai confermate da Davide) e la camera calcolata
a **~9.4m dalla parete**, il tetto (largo 6m ma profondo solo 3.5m) è visto quasi di taglio
dalla distanza/altezza di quella camera — la profondità del tetto proietta su un'estensione
verticale minima rispetto alla sua larghezza, quindi appare come una barra sottile invece che
un rettangolo ampio. Effetto prospettico reale di quella specifica combinazione
angolo/distanza/dimensioni, non un bug — confermato controllando lo stesso render su sfondo
verde pieno (non composito) invece che sopra la foto: si vede chiaramente la sagoma di una
pergola con due gambe fino a terra, non rumore.

**Verificato**: le coordinate proiettate dei due estremi della riga tappata (retro, a
parete) coincidono con i pixel tappati originali entro ~13px su 640 — buon accordo per un
primo test con punti campionati a occhio/per-colore, non con un vero tap interattivo.
Composito visivo mandato a Davide per giudizio umano su posizione/altezza reali (le
dimensioni L/SP/P usate erano invenzioni di questa sessione, non i valori veri del suo
progetto).

**Non ancora fatto**: nessun test con la riga di controllo opzionale (secondo punto);
nessuna verifica con L/SP/H reali del progetto di Davide (servono da lui); il test ha usato
punti campionati via script, non il vero componente `FotoRiferimentoPunti` del wizard
(`pergolando-frontend`) — la UI di tap reale non è stata esercitata in questa sessione.

### Modalità depth map (`render_depth_map`, per il vero passo 5)

Il render "di debug" (`render_isolated`, materiale grigio + luce) serve **solo** a
verificare visivamente la geometria — non è quello che serve a ControlNet. Per la vera
mappa strutturale (passo 5) c'è `render_depth_map`: nessuna luce/materiale, solo il canale
di profondità (Z-pass) di Blender, normalizzato in scala di grigi (vicino = chiaro) con
sfondo trasparente. Selezionabile via `"outputMode": "depth"` nel config (default:
`"silhouette"`, il render di debug attuale).

Nota tecnica: Blender 5.x sta a metà di un'unificazione tra i nodi del compositor e quelli
shader — `CompositorNodeMath`/`CompositorNodeMapRange`/`CompositorNodeComposite` **non
esistono più** in questa versione. Gli equivalenti `ShaderNodeMath`/`ShaderNodeMapRange`
funzionano se aggiunti a un `CompositorNodeTree`; il compositor della scena è ora un vero e
proprio node **group** (`scene.compositing_node_group`), quindi serve un socket di
interfaccia (`tree.interface.new_socket(..., in_out="OUTPUT")`) + un nodo `NodeGroupOutput`
al posto del vecchio nodo "Composite" dedicato.

### Modalità Freestyle line art (`render_freestyle`, passo 6b sperimentale)

Proposta di Davide (2026-09-28): invece/in aggiunta al conditioning "morbido" via
immagini di riferimento usato oggi per Gemini (passo 6), generare dei **contorni puliti
via Freestyle** di Blender da dare in pasto a un vero ControlNet (Stable Diffusion/Flux
via API, non ancora scelta) — un vincolo geometrico rigido, non un suggerimento visivo.
Diversa da Canny (edge detection su un render raster): Freestyle calcola le linee
direttamente dalla topologia (silhouette/crease/border), quindi il risultato è più
vicino a un input per ControlNet-**lineart**/scribble che per ControlNet-canny classico
— da tenere a mente scegliendo il modello ControlNet lato API.

Selezionabile via `"outputMode": "freestyle"` nel config (come `"depth"` per
`render_depth_map`).

**Scoperta tecnica (verificata empiricamente, non assumere il contrario)**: in Blender
5.x **non esiste** un pass "Freestyle" separato da estrarre nel compositor — confermato
per introspezione RNA (nessun `ViewLayer.use_pass_freestyle`, nessun socket "Freestyle"
sul nodo Render Layers, a differenza dello Z-pass usato da `render_depth_map`). Il primo
tentativo (stesso pattern del depth pass: nodo Render Layers → output group) falliva con
`KeyError` sull'output inesistente. Le strokes di Freestyle vengono disegnate **sempre**
sopra il Combined (superfici shadate + linee), mai come pass isolato.

**Tecnica che funziona invece** (verificata prima su un cubo di test isolato, poi sul
vero `flag.blend` a due misure): dare a **ogni mesh un materiale Holdout**
(`ShaderNodeHoldout` → `ShaderNodeOutputMaterial`). Freestyle legge i bordi dalla
geometria, non dallo shading — quindi le strokes restano visibili anche quando l'Holdout
"buca" la superficie (trasparente, con `film_transparent=True`), dando linee pulite su
sfondo trasparente senza bisogno di alcun pass separato. Lo scambio di materiali non
viene mai salvato (il processo Blender headless renderizza ed esce, non scrive mai su
`flag.blend`).

Tentativo intermedio scartato: `layer_collection.holdout` (la flag "holdout" visibile
nell'Outliner) — esiste in RNA ma **non fa nulla in un singolo view layer**: serve solo
quando si combinano più view layer nel compositor (alpha-over tra layer), non taglia
l'alpha del proprio Combined da solo. Confermato per render identici con/senza.

Motore: Freestyle richiede Cycles o EEVEE — **Workbench (usato altrove in questo script
per le viste "debug" di riferimento) non lo supporta affatto**. `render_freestyle`
prova `CYCLES` → `BLENDER_EEVEE_NEXT` → `BLENDER_EEVEE` in ordine (stesso pattern
difensivo try/except suggerito dalle istruzioni BlenderMCP, mai un identificatore
hardcoded).

**Verificato** (Blender 5.2.2, locale, non tramite BlenderMCP — la sessione BlenderMCP
non era raggiungibile in questo momento, handshake fallito): render a dimensioni di
riferimento (300×300, H200, Δh40, autoportante) e a dimensione diversa (450×350, H230,
Δh50, **parete**) — contorni puliti, nervature del tettuccio correttamente visibili come
dettaglio geometrico reale (coerente con la nota sull'allucinazione "tetto a lamelle" più
sotto — qui non c'è il problema perché non c'è nessuna luce/ombra, solo linee).

**Primo test reale su Replicate (2026-09-28)**: account Replicate di Davide, modello
`jagilley/controlnet-scribble` (SD1.5, 38M run, il più maturo/documentato per input
lineart — vedi `3d/replicate_scribble_test.py`, script standalone non ancora collegato al
backend, token in `3d/.env` gitignored). Input: il render Freestyle di riferimento
(300×300), appiattito su sfondo bianco e ridotto a 768px di larghezza per stare sotto il
limite di 256KB dei data URL dell'API Replicate (vedi `to_data_url` nello script). Nota
operativa: questo modello restituisce **due immagini** nell'array di output — la prima
(`output_0`) è solo la mappa di controllo preprocessata da ControlNet (praticamente
identica all'input), la vera immagine generata è la **seconda** (`output_1`) — capito
solo dopo aver controllato entrambe, non documentato nello schema.

**Risultato**: aderenza geometrica nettamente migliore di Gemini sugli stessi problemi
noti — 4 pilastri nella posizione corretta, tetto continuo piatto (**nessuna lamella**,
nessun rullo/tamburo frontale inventato, nessuna lucina) — coerente con l'aspettativa
che un vincolo ControlNet vero sia più rigido di un semplice suggerimento via immagini di
riferimento. Il contesto (ambientazione tropicale, piscina, arredi) è totalmente
inventato dal prompt testuale libero, come atteso: questo primo test genera un'immagine
da zero, non compone sulla foto reale del cliente.

**Non ancora fatto**: comporre il risultato sulla foto reale del cliente — serve un
secondo step (inpainting mascherato solo sull'area della pergola, o img2img a bassa
denoising strength sulla foto stessa) non ancora prototipato. Non ancora provato Z-Image
(`prunaai/z-image-turbo-controlnet` su Replicate, confermato esistere ma senza supporto
lineart esplicito nello schema — da verificare) né una variante SDXL (qualità/risoluzione
superiore a SD1.5, es. `adirik/t2i-adapter-sdxl-lineart`). Materiali/colori reali della
struttura non ancora guidati nel prompt (oggi generico "aluminum pergola").

### Viste tecniche 2D ortografiche (`setup_ortho_camera`, documentazione preventivo)

Richiesto da Davide (2026-09-28): tre viste 2D in scala reale (pianta dall'alto, prospetto
frontale, prospetto laterale) con quote, stile disegno tecnico — per allegarle al
preventivo, non per il compositing fotorealistico. Riusa la stessa tecnica Freestyle +
materiale Holdout di `render_freestyle`, ma con una **camera ortografica** (nessuna
prospettiva, proiezione parallela in scala) invece di quella prospettica. Selezionabile via
`"outputMode": "ortho_top" | "ortho_front" | "ortho_side"`.

Ogni vista è definita da una coppia `(forward, up)` in coordinate mondo Blender (X=larghezza,
Y=profondità con -Y=fronte/+Y=retro-parete, Z=altezza). Il terzo asse (`right`) si ricava
come **`forward.cross(up)`** — attenzione, **non** `up.cross(forward)` (segno invertito,
bug reale del primo tentativo: la vista dall'alto usciva comunque giusta per caso/simmetria,
ma front/side uscivano completamente vuote, camera che guardava nella direzione sbagliata).

Oltre al PNG, `ortho_*` scrive anche un **JSON sidecar** (`<output>.json`) con gli assi
`right`/`up` usati, il centro mondo, `ortho_scale` e la risoluzione — necessario per
disegnare poi le linee di quota in un post-processing separato (proiezione ortografica pura,
niente divisione prospettica, quindi è una semplice trasformazione affine calcolabile senza
richiamare Blender).

**Bug reale trovato e corretto, specifico di Freestyle**: `mirror_x_copy` (usata per
`Montante.001`, `Supporto.001`, `Guida.001` — i pezzi speculari sul lato destro) nega la
coordinata X dei vertici ma non inverte il verso di avvolgimento delle facce — questo
**capovolge le normali** del pezzo copiato. Invisibile in ogni render "a materiale" usato
finora (silhouette, depth, i render isolati per Gemini) perché quelli non dipendono
dall'orientamento delle facce. Freestyle invece sì: nella vista frontale ortografica
esattamente frontale, il montante speculare (`Montante.001`) spariva quasi del tutto (solo
un piccolo dettaglio del piede, non mirrorato allo stesso modo, restava visibile) mentre
quello non speculare rendeva correttamente. Fix: flip esplicito delle normali via `bmesh`
(`f.normal_flip()` su ogni faccia) subito dopo la copia/mirroring, dentro `mirror_x_copy`
stessa — beneficia automaticamente tutti e tre i pezzi che la usano.

### Render colorato (`render_colored`, quarta vista documentazione preventivo)

`"outputMode": "colored"` — prospettiva "come sarebbe davvero" invece di linee tecniche.
Accetta un `camera` (stesso blocco rvec/tvec/fovDeg/imageWidthPx/imageHeightPx di
`setup_camera_from_pnp`) per condividere l'identica inquadratura degli altri tre output
dello stesso scatto (freestyle/depth/mask) — se omesso, usa la propria camera orbitale di
default ("un po' dall'alto"). Motore Cycles (128 sample, denoising).

**Materiali (rivisti 2026-09-30 su feedback Davide — il primo giro era piatto/senza
riflessi)**: struttura in alluminio (`colorRgb`, tutti i pezzi tranne `Telo`) —
verniciato a polvere, non metallo grezzo, ma comunque riflettente: `Metallic=0.9`,
`Roughness=0.3` (satinato, non specchio). `Telo` (`fabricRgb`, se dato) resta
non-metallico, `Roughness=0.75` (tessuto opaco). **Non ancora fatto**: differenziare le
parti in **plastica** (bianche ma non metalliche, es. i "carrelli"/staffe menzionati in
`pergolando-backend/src/render/prompt.ts`) dal resto della struttura in alluminio — serve
sapere quali oggetti Blender specifici sono plastica, non ancora mappato.

**Illuminazione**: niente sole/lampade dirette — solo un World come sorgente. Prima un
colore piatto uniforme; **ora una vera mappa HDRI** (Poly Haven, CC0,
`studio_small_08_1k.hdr`, scaricata in `3d/hdri/`, caricata via
`ShaderNodeTexEnvironment`) — un materiale metallico con un colore piatto attorno resta
comunque uniforme/senza riflessi (un metallo riflette quello che ha intorno: niente
varietà nell'ambiente, niente riflesso visibile), l'HDRI risolve questo mantenendo comunque
ombre morbide (nessuna sorgente diretta aggiunta). Il render diventa più lento (~3m30s a
1280×960 su CPU in questo ambiente, contro i ~60-80s della versione a colore piatto) per il
GI più complesso.

**Shadow catcher**: pavimento e (se `fissaggio: "parete"`) un piano verticale dietro
esistono solo per dare all'illuminazione qualcosa su cui proiettare un'ombra di contatto —
mai visibili loro stessi nel render finale (Davide, 2026-09-30). Sono
`obj.is_shadow_catcher = True` (proprietà Cycles, confermata esistere per introspezione
diretta prima di usarla), output `color_mode="RGBA"` + `film_transparent=True` — il
risultato finale è "solo la pergola + la sua ombra" su sfondo trasparente, componibile su
qualunque sfondo dopo.

Verificato su entrambe le varianti (parete e autoportante) a L=600/SP=350/H=250/Δh=40; nota
di Davide dopo aver visto un primo giro con la camera PnP calibrata sulla foto reale: quella
camera guarda il tetto troppo di taglio per giudicare bene la pergola — resta comunque
valida per allineare i 4 output allo stesso frame, ma per valutare l'estetica serve un
angolo più aperto (es. "isometrico").

### `add_dimensions.py` — quote sulle viste ortografiche

Script standalone (no Blender — la proiezione ortografica è una trasformazione affine
pura, calcolabile da `ortho_scale`/`right_axis`/`up_axis`/`center_world` nel JSON sidecar
di `ortho_*`). Disegna linee di quota in stile tecnico (linee di estensione, frecce,
etichetta in cm) agganciate al **bbox reale renderizzato** (`bbox_min`/`bbox_max` nel
sidecar), non ai valori nominali L/P/H da soli — così restano precise anche se un pezzo
sporge di qualche cm oltre la misura nominale. Aggiunge un margine bianco di 140px al
canvas prima di disegnare (altrimenti le etichette sul lato destro/basso escono dai
bordi — scoperto al primo tentativo). Uso: `python 3d/add_dimensions.py <output ortho>.png`
→ salva `<output>_quotato.png`.

### Workflow ComfyUI Z-Image + ControlNet Canny (`3d/comfyui/z_image_controlnet_canny.json`)

Richiesto da Davide (2026-09-28), stessa esplorazione ControlNet ma via ComfyUI locale
invece di Replicate. **Non inventato**: scaricato verbatim dal template ufficiale
Comfy-Org (`Comfy-Org/workflow_templates`, file
`templates/image_z_image_turbo_fun_union_controlnet.json`, linkato dalla card "Z-Image-Turbo
Fun Union ControlNet" sia su comfy.org/workflows sia dalla README di
`huggingface.co/Comfy-Org/z_image_turbo`) — poi personalizzati solo due `widgets_values`
(il prompt testuale e il nome placeholder dell'immagine da caricare), nessuna modifica
strutturale al grafo/subgraph.

Usa `alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union` (supporta anche HED/Depth/Pose/MLSD,
questo workflow dimostra solo Canny — per le altre basta cambiare il nodo di
preprocessing). Genera un'immagine **da zero** condizionata sui contorni Canny + prompt
testuale — non compone su una foto reale esistente (stessa categoria del primo test
Replicate `jagilley/controlnet-scribble`, non del tentativo di inpainting).

Percorso modelli richiesti (elencati anche nel nodo "Guide" dentro il workflow stesso,
ComfyUI mostra i link di download in automatico se mancanti):
```
ComfyUI/models/text_encoders/qwen_3_4b.safetensors        (7.49 GB)
ComfyUI/models/diffusion_models/z_image_turbo_bf16.safetensors  (11.46 GB)
ComfyUI/models/vae/ae.safetensors                          (319.8 MB)
ComfyUI/models/model_patches/Z-Image-Turbo-Fun-Controlnet-Union.safetensors  (2.89 GB)
```

Come immagine di riferimento da cui il nodo `Canny` estrae i contorni: usare uno dei
render già prodotti in questa sessione (es. `colored_parete.png` o un render isolato),
non una foto vuota del sito — serve un'immagine che contenga già la pergola.

### Maschera di inpainting (`render_mask`, terzo output ComfyUI)

Richiesto da Davide (2026-09-29): un terzo output oltre a Canny (`render_freestyle`) e
foto di sfondo, per il workflow ComfyUI SDXL/Z-Image ControlNet. Selezionabile via
`"outputMode": "mask"`, stessa `camera`/risoluzione del Canny (deve combaciare pixel per
pixel — verificato via overlay diretto).

**Risposta alla domanda originale su Object Index**: non serve. Nella scena Blender
esistono SOLO i pezzi della pergola (nessun oggetto di sfondo concorrente — lo sfondo è
la foto reale, esterna, composta dopo), quindi il canale **Alpha** di un render con
`film_transparent=True` è già una maschera oggetto/non-oggetto esatta senza configurare
`pass_index` su nessun pezzo.

**Versione corretta (2026-09-30)**: il primo tentativo aveva margine di dilatazione
(`CompositorNodeDilateErode`) e bordi sfumati (`CompositorNodeBlur`) per l'inpainting, più
output RGB con il valore maschera replicato nei 3 canali invece di un vero alfa — Davide
ha chiesto di eliminare entrambe le cose: **niente margine, niente sfumatura, solo la
sagoma esatta della pergola**, e soprattutto un **vero canale alfa PNG** (RGBA). Ora
`render_mask` è tornata minimale: `film_transparent=True` + `color_mode="RGBA"` +
render diretto, nessun grafo compositor custom — esattamente l'Alpha pass della camera,
niente altro. Verificato: alpha extrema (0,255), sagoma pixel-esatta confrontata su sfondo
magenta di prova.

### Crash di `pergolando-geocalib-service` su foto reale ad alta risoluzione (2026-10-03)

Primo vero test con una foto scattata da telefono (4096×3072, 12,6MP — `3d/test_photos/
test_02/sfondo.jpg`), tramite il wizard reale (non più uno script one-shot): il servizio
**crashava con un'access violation nativa** (`exit code 3221225477` = `0xC0000005`),
nessun traceback Python, il processo moriva e basta — tutti i test precedenti avevano
usato foto piccole (640×480), mai una vera foto da fotocamera.

**Causa reale, riprodotta fuori dal server** (`test_crash_repro.py`, poi cancellato):
il preprocessing interno di GeoCalib (kornia, `gaussian_blur2d` prima del resize — un
anti-aliasing filter) alloca un buffer proporzionale alla risoluzione di **input**, non a
quella target — su un'immagine da 12,6MP, ~384MB per un singolo tensore intermedio.
Fuori dal server questo dà un pulito `RuntimeError: not enough memory`; **dentro il
server HTTP persistente la stessa condizione di memoria esaurita si manifesta come
access violation nativa** (probabilmente per via della memoria già impegnata dal modello
caricato una volta sola all'avvio + più thread, più frammentazione — non indagato oltre,
non necessario avendo trovato la causa a monte).

**Fix**: `calibrate_placement` ora ridimensiona l'immagine (PIL, lato massimo 1600px,
preservando l'aspect ratio) **prima** di passarla a GeoCalib — la calibrazione camera non
ha bisogno di dettaglio fine. Bonus nello stesso punto di codice: `ImageOps.exif_transpose`
per correggere l'orientamento di foto scattate in verticale da telefono (l'orientamento
Exif non applicato ai pixel grezzi avrebbe rotto la stima di gravità in modo silenzioso —
non ancora capitato con una foto reale, ma un rischio concreto ora che il flusso riceve
foto vere da telefono, quindi corretto preventivamente). `punti` restano normalizzati
(xNorm/yNorm) quindi tutto il resto (resection, `tettoNormalizzato`) resta coerente
qualunque sia la risoluzione effettivamente caricata — verificato: lo stesso script di
riproduzione, identico payload, ora restituisce una posa valida invece di crashare.

### Crash di Blender su chiamate ripetute reali — addon di terze parti + processo zombie (2026-10-03)

Stesso test dal vivo: dopo il fix del crash GeoCalib, il passo successivo (render 3D)
falliva con "bad allocation" durante il caricamento della config OpenColorIO, oppure
restava bloccato. Causa reale, in due parti:
1. Un vecchio processo Blender rimasto **zombie** da un crash precedente (verificato via
   PowerShell, poi terminato con `Stop-Process`) — occupava memoria/lock inutilmente.
2. **Ogni singola invocazione** headless caricava comunque gli addon utente installati
   su questa macchina: `bonsai` (incompatibile con la versione Python di questo Blender,
   errore ad ogni avvio) e `BlenderKit` (lancia un proprio processo client in background
   ad ogni avvio) — overhead reale e non necessario per un rendering headless scriptato.

**Fix**: aggiunto `--factory-startup` agli argomenti CLI in
`pergolando-blender-service/server.js` (subito dopo `--background`) — salta il
caricamento di userpref/addon di terze parti, lasciando solo gli addon core. Verificato:
chiamate ripetute ora stabili, nessun processo Blender residuo dopo la risposta HTTP.

### deltaH (H1) mai realmente inviato al render (2026-10-03)

Davide ha selezionato Δh=80 nel wizard reale, ma il render mostrava visivamente qualcosa
più vicino a 60 e basta — non un errore di percezione: `wizard/page.tsx` calcolava un
`deltaHCmStimato` (una stima segnaposto, 12% della sporgenza, già documentata come tale
in un commento preesistente nel codice) e lo usava al posto del vero campo H1 raccolto
dal form (`altezzaInclinazione`), sia per `/catalog/render3d` che per `/catalog/
render-finale`. **Fix**: entrambe le chiamate ora inviano `deltaHCm: Number(altezzaInclinazione)`
— il valore reale scelto dal venditore, non più una stima.

### Colore selezionato dal venditore non applicato al render 3D (2026-10-03)

Davide aveva selezionato bianco, il render mostrava un grigio scuro uniforme: il modello
3D non riceveva **nessuna** informazione di colore — ogni chiamata a `/catalog/render3d`
girava sempre nella modalità "silhouette" grigia di debug, indipendentemente da cosa
l'utente avesse scelto nel catalogo.

**Fix** (frontend → DTO → service → Blender):
- `wizard/page.tsx`: aggiunte `coloreStruttura`/`colorePlastica` al body POST di
  `/catalog/render3d` (le stringhe catalogo già disponibili, es. "RAL 9016 Bianco").
- `render-scene3d.dto.ts`: due nuovi campi opzionali `@IsString()`, con nota che restano
  `undefined` per le viste isolate di riferimento di `render-finale` (che devono restare
  grigie neutre — Gemini riceve il colore via prompt testuale, non via immagine).
- `scene3d.service.ts`: nuova `RAL_COLORS` (tabella RGB approssimata, solo i codici che
  compaiono davvero nel catalogo bundle `Flag`, letto da `catalog/database.json`) +
  `colorStringToRgb()` (regex sul codice RAL a 4 cifre, poi match per nome "antracite",
  poi grigio neutro di fallback) — passati a `generate_flag.py` come `outputMode:
  'colored'`, `colorRgb`, `frangitrattaRgb` (quest'ultimo per le parti in plastica/
  Frangitratta — confermato dal campo `prodotto.colori.parti_plastiche.tag` = "Colore
  frangitratta" nel catalogo reale, non un'ipotesi).
- Bug collaterale trovato e corretto nello stesso punto: un commento JSDoc conteneva
  `Flag/*/catalog/` — il `*/` letterale chiudeva il blocco di commento in anticipo,
  causando una cascata di ~12 errori TypeScript nei file successivi. Risolto riformulando
  il commento per evitare quella sottostringa.

### Payload di `render-finale` troppo grande, nessuna traccia nei log backend (2026-10-03)

Ultimo passo del test dal vivo: "Si è verificato un errore nella generazione dell'immagine
finale. Riprova." — ma `preview_logs` sul backend non mostrava **nessuna** richiesta
arrivata a `/catalog/render-finale` (solo la precedente `/catalog/render3d`, riuscita).
Puntava a un fallimento lato client, prima che la richiesta partisse davvero.

**Riprodotto isolatamente** (harness HTML servito via `python -m http.server`, foto reale
`sfondo.jpg` 4096×3072 + overlay colorato): la vecchia `compositeImages` disegnava il
composito alla risoluzione PIENA della foto originale e lo codificava **PNG** — risultato,
un data URL da **~27MB**. Causa a monte confermata leggendo `pergolando-backend/src/
main.ts`: `app.useBodyParser('json', { limit: '15mb' })` — il body totale (composito
~27MB + `fotoAmbienteBase64` a piena risoluzione, altri ~4MB) superava il limite e veniva
rifiutato silenziosamente prima di arrivare a qualunque punto che lo loggasse.

**Fix** (`pergolando-frontend/src/lib/image-compose.ts`): stessa strategia già usata per
GeoCalib — ridimensionare prima di codificare. Aggiunto `MAX_DIMENSION_PX = 1600` e una
nuova `downscaleDataUrl()` esportata; `compositeImages` ora disegna a risoluzione limitata
e codifica **JPEG qualità 0.9** invece di PNG a piena risoluzione (è sempre una foto
appiattita, senza trasparenza da preservare). `wizard/page.tsx` → `handleGeneraFinale` usa
`downscaleDataUrl(fotoAmbiente)` per `fotoAmbienteBase64`, in parallelo al composito.

**Verificato**: stesso harness isolato, stessa foto reale — il payload totale scende da
~27MB a **1.26MB**, ben sotto il limite di 15MB. `npm run typecheck` e `npm run lint` sul
frontend entrambi puliti dopo il fix.

### Multi-guida (2/3/4 guide) + export del set di immagini ComfyUI con nomenclatura fissa (2026-10-03)

Due richieste dirette di Davide dopo il test dal vivo, affrontate insieme:

**1) Nomenclatura fissa per il set di riferimento ComfyUI**, concordata il 2026-09-30 ma
mai davvero collegata al codice: `01_original.jpg`, `02_lineart.png`, `03_depth.png`,
`04_mask.png`, `05_beauty.png` (+ `06_material_id.png`, aggiunto dopo). Fino ad oggi
`generate_flag.py` scriveva sempre su un path temporaneo casuale
(`pergolando-blender-service/server.js`, `${randomUUID()}.png`) — nessun punto del sistema
salvava mai questi file con un nome "parlante". **Nuovo script standalone**
`3d/export_reference_set.py` (Python puro, gira FUORI da Blender — orchestratore via
`subprocess`, stesso pattern di invocazione CLI di `pergolando-blender-service/server.js`:
`--background --factory-startup flag.blend --python generate_flag.py -- --config-json ...
--output ...`): dato un config JSON (stesso shape del generatore) + opzionalmente una foto
reale e una camera (stesso shape PnP del wizard), produce l'intero set numerato in una
cartella di output, con la stessa camera condivisa fra tutte le modalità così il set resta
allineato pixel-per-pixel. Deliberatamente non collegato al flusso live del wizard/backend
— è uno strumento offline per preparare i riferimenti ComfyUI, eseguibile da terminale.
Verificato end-to-end con la foto reale `sfondo.jpg` e L=800 (3 guide): 6 file prodotti,
nessun errore.

**2) Multi-guida reale (2/3/4 guide)**: Davide aveva selezionato "Flag 3 guide" nel wizard
(L=550, che però è già al limite della fascia 2 guide — vedi sotto) e il render ignorava
comunque la scelta, generando sempre la variante a 2 guide — bug di wiring **and** gap di
modellazione, risolti insieme:

- **Dato reale di catalogo** (`apps/studio/storage/bundles/Flag/*/catalog/database.json`,
  `sotto_modelli.flag.varianti_montaggio`): "2guide" copre L 200-550cm, "3guide" L
  600-1100cm, "4guide" L 1150-1400cm (1400 è anche l'`L_max_modulo_cm` assoluto del
  prodotto — **non esiste una variante "5 guide"** nel listino reale). I due intervalli
  551-599 e 1101-1149 sono vuoti per davvero: il listino stesso non vende quelle larghezze
  (`note_estrazione`).
- **Nessun pezzo del modello rappresenta davvero una guida/pilastro centrale** — ipotesi
  iniziale che `Pilastrino_intermedio` fosse quel pezzo, smentita (vedi sopra, sezione
  "Rimasto in sospeso"): non esiste nell'FBX reverse-engineered un asset dedicato per
  l'hardware delle guide intermedie. **Approccio adottato, esplicitamente un'approssimazione
  non verificata contro l'hardware reale**: `Guida`/`Supporto` (i due pezzi che già
  rappresentano una guida sui bordi) vengono duplicati per traslazione pura (non mirror —
  nessuna ragione nota per assumere che una guida centrale sia "specchiata" come quella di
  bordo) alle posizioni intermedie, evenly-spaced sull'intera larghezza: `n_guide=3` aggiunge
  una guida al centro, `n_guide=4` aggiunge due guide ai punti a 1/4 e 3/4. Nessuna gamba
  (`Montante`) o pilastro aggiuntivo per le guide centrali: `Trave`/`Telo` sono già pezzi
  continui su tutta la L, e il listino prezza "Guida aggiuntiva" come accessorio a sé
  (indicizzato solo per sporgenza), non come un set gamba+guida — coerente con l'assenza di
  supporto verticale dedicato.
- Nuove funzioni in `generate_flag.py`: `derive_n_guide_from_l(L_cm)` (soglie sopra,
  arrotonda per eccesso nei due gap vuoti — più struttura, mai meno), `guide_x_targets(L_cm,
  n_guide)`, `_translate_x_copy`/`_remove_stale_copies` (stesso pattern difensivo di
  pulizia-e-ricostruzione già usato per i Frangitratta intermedi), `nGuide` opzionale nel
  config (`cfg["nGuide"]`, altrimenti derivato da `L_cm`). **Verificato**: soglie corrette su
  9 punti di L (200→1400), posizioni calcolate corrette, render reale a L=1300/n_guide=4
  (4 guide visibili, telo diviso in 3 pannelli) e regressione a L=300/n_guide=2 di default
  (identico all'architettura originale, nessuna guida intermedia spuria).
- **Wiring reale** (il bug che Davide aveva effettivamente segnalato): il wizard raccoglie
  già la scelta del venditore in `varianteKey` (`"2guide"`/`"3guide"`/`"4guide"`, le stesse
  chiavi del catalogo) ma non la mandava mai a `/catalog/render3d`. Aggiunto
  `varianteMontaggio` (stesso valore grezzo di catalogo, stesso pattern di
  `coloreStruttura`/`colorePlastica`) a `RenderScene3dDto`, risolto in `Scene3dService` via
  `varianteMontaggioToNGuide()` (regex `^(\d+)guide$` sulla chiave — il numero È già nella
  chiave, nessuna tabella di lookup separata), passato come `nGuide` a
  `pergolando-blender-service`. Propagato anche a `RenderFinaleService`'s tre viste isolate
  per Gemini (prima sempre a 2 guide indipendentemente da cosa stesse configurando il
  venditore).

## `pergolando-blender-service` — container isolato (Fase G)

Blender **non** viene eseguito dentro `pergolando-backend`. È isolato in un proprio
servizio/container (`pergolando-blender-service/`, HTTP puro con `node:http`, nessun
framework) — così il peso di Blender (~300MB, binario precompilato, nessuna compilazione da
gestire in Docker) non tocca mai l'immagine del backend principale. Il backend chiama
`POST {BLENDER_SERVICE_URL}/render3d` invece di eseguire Blender direttamente
(`Scene3dService`).

Non esiste una build "ridotta" ufficiale di Blender — l'archivio Linux ufficiale è
autonomo (si scompatta e si lancia, nessuna installazione in senso tradizionale, nessuna
compilazione C++ come per `better-sqlite3`/`argon2`), ma è comunque un unico binario
monolitico. Dato che il RAID del NAS ha ~270GB liberi, i ~300MB extra sono trascurabili.

**Verificato end-to-end**: catena completa frontend → backend → `pergolando-blender-service`
→ Blender → immagine trasparente, per entrambe le varianti di fissaggio.

**Il `Dockerfile` è stato buildato per davvero sul NAS** (2026-09-26) — build riuscita dopo
un fix reale: mancava `ca-certificates` nell'immagine base `node:24-slim`, senza il quale
`curl` non ha certificati root e fallisce (`error setting certificate file`) scaricando il
tarball Blender. Aggiunto all'`apt-get install` insieme agli altri pacchetti.

**Scoperta più importante: il NAS non può eseguire Blender, punto.** La CPU del NAS (AMD
Athlon II Neo N36L, architettura K10 del 2010) è sotto i requisiti minimi ufficiali di
Blender 5.x su **due fronti**: non supporta SSE4.2 (introdotto da AMD solo con Bulldozer,
2011) ed è dual-core contro i 4 core richiesti. Il container si builda correttamente ma
Blender si rifiuta di partire (`Unsupported CPU ... Blender requires a CPU with SSE42
support`). Non è un problema risolvibile con una versione Blender diversa: risalire a una
build precedente rimetterebbe in discussione il lavoro fatto sul compositor (specifico per
le breaking change dell'API di Blender 5.x, vedi sopra) per compatibilità con un hardware
comunque troppo debole (dual-core) per renderizzare in tempi ragionevoli.

**Soluzione adottata**: dato che il servizio parla solo HTTP (`BLENDER_SERVICE_URL`), non
deve necessariamente girare sullo stesso host del backend — esattamente il motivo per cui è
stato isolato. Per ora gira sul PC di sviluppo di Davide, raggiunto dal NAS via **Tailscale**
(stessa tailnet, nessuna porta esposta pubblicamente, nessuna modifica al firewall) —
verificato con successo (`GET /health` e `POST /render3d` raggiungibili dal NAS,
render reale generato e scaricato). Il PC resta acceso solo durante i test; per l'uso in
produzione serve un host dedicato sempre acceso (da reperire), puntando
`BLENDER_SERVICE_URL` al suo indirizzo Tailscale — nessun'altra modifica architetturale
necessaria quando cambierà host.

## Rimasto in sospeso

**Stato al 2026-09-27 sera**: `generate_flag.py` è stato riscritto per usare
l'architettura a perno fisso (sezione sopra) per Guida, Telo, Frangitratta (Iniziale/
Finale/intermedi), Tettuccio, Supporto, Montante, Trave, Montante_Posteriore_Dx/Sx,
Trave_Posteriore, Aggancio_Parete. **Verificato**:
- Riproduzione esatta (scarto zero) a dimensioni di riferimento.
- Render coerente end-to-end su L=400/SP=400/H(front)=200/Δh=50 (headless) e dal vivo con
  Davide su L=550/SP=480/H(front)=220/Δh=50 (nomenclatura venditore: P=220, H=270) —
  confermato "mi sembra tutto a posto".
- Tettuccio isolato, testato a L=300 (25 nervature) e L=500 (43 nervature), simmetrico,
  nessun buco.

**Da fare, prossima sessione**:
- `compute_guide_slope` e `build_tettuccio_lato` sono state **rimosse** dallo script (la
  vecchia convenzione fronte=z>0/retro=z<0 su cui si basavano non è più valida dopo lo
  spostamento dell'origine — ora è tutto z>0). ~~Davide sta cancellando `Tettuccio_Lato_Dx/Sx`
  dalla scena~~ **confermato 2026-09-27**: `Tettuccio_Lato_Dx/Sx` non esiste più in
  `flag.blend` (verificato via query diretta degli oggetti). Resta da confermare che la
  riorganizzazione di `Frangitratta*`/`Pilastrino_intermedio`/`Skipper`/`Timpano`/
  `Trave_Laterale` nella collection principale sia coerente.
- `setup_camera_from_pnp` (pipeline foto reale, passi 3-4) **non è stata riverificata** dopo
  lo spostamento dell'origine — `front_offset` al suo interno presumeva la vecchia
  convenzione "fronte circa centrato sull'origine mondo", non più vera. Probabile che serva
  un aggiornamento prima di rifare il test end-to-end con una foto reale.
- Nomenclatura: lo script usa ancora i propri nomi interni (`L_cm`, `P_cm`, `H_cm`,
  `deltaH_cm`) mentre il venditore usa L/SP/P/H/H1 (mappatura documentata sopra) — da
  riconciliare quando si tocca il wizard/backend, non prima.
- **2026-09-27, allucinazione tetto a lamelle — RISOLTA (3 fix cumulativi)**:
  1. Le viste isolate di riferimento per il passo 6 (Gemini, `render-finale`) mostravano,
     nella striscia di Tettuccio più vicina alla guida, un'ombra netta a ogni nervatura —
     indistinguibile da fessure reali tra lamelle. NON era un artefatto di angolazione
     camera né il pezzo `Tettuccio_Lato_Dx/Sx` (confermato assente dalla scena). Causa
     reale: il singolo sole direzionale hard-shadow usato per queste viste "debug". Fix:
     passate a **Workbench FLAT shading** (nessuna luce, nessuna ombra — vedi
     `generate_flag.py`, branch "no camera" di `main()`) — le nervature ora non proiettano
     più ombre false.
  2. Anche con riferimenti puliti, un primo retest end-to-end è risultato PEGGIORE (tetto a
     lamelle su tutta la superficie + un rullo/tamburo frontale inventato + lucine tornate)
     — prova che il problema non era solo visivo: il prompt testuale (`prompt.ts`,
     `structuralChecklist`) da solo non basta a vincolare Gemini, che ha un prior fortissimo
     verso "pergola bioclimatica".
  3. **Causa architetturale di fondo** (emersa riguardando il piano originale di
     CHANGELOG.md, Fase G): il piano dei 6 passi prevedeva un vero **ControlNet** (mappa
     Canny/depth → vincolo geometrico rigido). `render_depth_map` in `generate_flag.py` fu
     costruita apposta ma non è mai stata collegata a nulla — il passo 6 usa Gemini
     (`generateContent`, multi-image prompting), che **non ha alcun meccanismo ControlNet**:
     ogni immagine passata è solo un suggerimento, mai un vincolo. Valutata l'alternativa
     (Flux/SDXL ControlNet+inpaint via Replicate, modello `batouresearch/flux-controlnet-
     inpaint` verificato con schema reale) ma scartata per ora: tempi/costi molto più alti e
     qualità estetica inferiore a Nano Banana per la parte lifestyle.
  4. Fix finale che ha davvero funzionato: **`temperature: 0.2, topP: 0.8`** nel
     `generationConfig` della chiamata Gemini (`render-finale.service.ts`) — prima non era
     impostato affatto (default SDK). Risultato: sparito il rullo frontale, sparite le
     lucine, tetto principale continuo; restano piccole tacche regolari sul bordo anteriore
     che però combaciano esattamente con i "carrelli" reali (confrontato pixel-per-pixel con
     la vista isolata `laterale`) — non è più un'allucinazione, è il dettaglio corretto.
  **Da fare**: ripetere il test un paio di volte per verificare che il miglioramento sia
  stabile (Gemini è non-deterministico anche a temperatura bassa) prima di considerarlo
  definitivamente chiuso; il fixture di test usato (`abs_position_render.png` + `1.jpg`
  nello scratchpad) ha la sagoma isolata in mezzo al prato, non contro un muro reale — va
  rifatto con una foto/sagoma coerenti per un giudizio pulito anche sul resto della scena.
- ~~`Pilastrino_intermedio` e `Skipper` (da `flag4.fbx`) — ancora da spiegare/lavorare.~~
  **chiarito 2026-10-03**: nessuno dei due è legato al numero di guide (vedi sezione
  "Multi-guida" sotto) — entrambi hanno il proprio bounding box X nello stesso angolo di
  `Montante`/`Guida`/`Supporto` (x≈139-150, lo spigolo di riferimento), non al centro.
  Quasi certamente geometria del prodotto "Skipper" (pag. 18-29 del listino originale,
  esplicitamente NON incluso in questo bundle — vedi `note_estrazione` in
  `catalog/database.json`) rimasta mescolata nell'FBX comune. Restano nascosti in scena
  come prima; non più considerati un mistero aperto.
- `Timpano`/`Trave_Laterale` non sono ancora parametrizzati per L/P/H arbitrari — esclusi da
  ogni render finché non vengono generalizzati (probabile candidato per la stessa
  architettura a perno, non ancora provato).
- ~~Materiali/colori reali (colore struttura, colore plastica) non sono ancora applicati nel
  render — oggi è tutto un unico materiale grigio di debug (modalità "silhouette").~~
  **risolto 2026-10-03**, vedi sezione dedicata sopra.
- ~~**Modello 3D non supporta configurazioni a 3 guide/3 pilastri**~~ **risolto 2026-10-03**,
  vedi sezione "Multi-guida (2/3/4 guide)" sotto.
- Verificare davvero il build Docker di `pergolando-blender-service` (mai testato in questo
  ambiente — però verificato con successo direttamente sul NAS, vedi sezione dedicata sopra).
- Pipeline downstream (compositing ControlNet vero, passo 6b) — solo l'immagine di
  conditioning esiste (`render_freestyle`, sezione sopra), nessuna chiamata API ancora
  scritta. Sia la mappa depth (`render_depth_map`) che la line art Freestyle esistono come
  funzioni ma **nessuna delle due è collegata a un endpoint/UI**, e vanno ricontrollate alla
  luce del cambio di convenzione degli assi (vedi punto `setup_camera_from_pnp` sopra).
- Prossimo passo esplicito di Davide: "domani continuiamo con i primi rendering" — quindi
  probabilmente si parte da qui a inizio sessione, non da zero.

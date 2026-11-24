# Immagini del sito Rosáda

Ogni gioiello è una **tavola 4:5** (720x900 px) con il pezzo **intero**, centrato, su **nero puro**.
Il nome del file è l'`id` del prodotto nell'elenco `PRODUCTS` di `index.html`
(per esempio `etna.jpg` per il prodotto con id `etna`).

Le foto sono incorporate dentro `index.html`, così il sito funziona anche come file unico.

## Importante: le foto attuali sono segnaposto

Vengono da screenshot di Instagram: i pezzi originali sono larghi 250-400 px e sono stati
ingranditi 2-3 volte. Sono ritagliati sul nero e puliti, ma restano morbidi. Il sito le mostra
a dimensioni contenute per non peggiorarle. **Per il sito finale servono le foto originali.**

## Come sostituire una foto con quella reale (alta risoluzione)

**Metodo semplice**
1. Prepara una tavola 4:5 con fondo nero, pezzo intero e margine attorno, di almeno **1440x1800 px**.
2. Salvala qui con lo stesso nome (es. `images/etna.jpg`).
3. Dal progetto lancia `python3 tools/embed-images.py`.

**Metodo con lo script** (ritaglia il fondo bianco e centra il pezzo da solo)
1. Metti l'originale in `images/source/` e aggiungi o cambia la riga in `tools/prepare-images.py`
   (`PIECES`): nome file, riquadro (`None` = tutta la foto) e tipo di fondo (`white` o `black`).
2. `python3 tools/prepare-images.py etna` e poi `python3 tools/embed-images.py`.
   Con foto grandi il pezzo non viene più ingrandito: resta nitido.

## Elenco

| File | Pezzo | Nota |
|---|---|---|
| `portorotondo.jpg` | Bracciale a maglie, argento palladiato | foto originale ricevuta, fondo nero |
| `portorotondorosa.jpg` | Stesso bracciale, versione rosa | da screenshot |
| `fortedeimarmi.jpg` | Bracciale a catena in oro giallo | da screenshot |
| `capri.jpg` | Anello oro rosa con diamanti | da "All our rings" |
| `circeo.jpg` | Anello argento con gemma gialla | da "All our rings" |
| `iglesias.jpg` | Anello argento brunito | da "All our rings" |
| `gransasso.jpg` | Anello brunito con gemma viola | da "New release" |
| `granparadiso.jpg` `stelvio.jpg` `gargano.jpg` `pantelleria.jpg` | Ciondoli | da screenshot |
| `etna.jpg` `taormina.jpg` `eolie.jpg` | Orecchini | da screenshot |

Il prodotto `nebida` (croce) non ha ancora foto: il sito mostra un riquadro con le indicazioni di scatto.

## Foto ricevute e non usate

- **Panarea** (cerchi in argento), **Portofino** (rigido), **Sanremo** (cordino nero): su fondo bianco con
  riflessi che si confondono con l'argento, il ritaglio automatico non è pulito. Servono gli originali.
- **Anelli in collaborazione con Portosette**: fondo grigio e un pezzo di un altro marchio.

`images/source/` contiene gli originali da cui sono state ricavate le tavole.

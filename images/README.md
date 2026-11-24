# Immagini del sito

Le foto sono incorporate dentro `index.html`, così il sito funziona anche come file unico.
Questa cartella contiene gli originali da cui vengono incorporate.

## Cambiare o aggiungere foto

1. Sostituisci il file qui con la nuova foto, **stesso nome** (JPG, fondo nero puro, lato lungo ≥ 1600 px).
2. Dalla cartella del progetto lancia `python3 tools/embed-images.py`.

Fondo nero puro (#000) consigliato: il sito fonde il nero della foto con quello della pagina,
così il gioiello sembra sospeso senza cornice.

| File | Chiave nel codice | Dove appare |
|---|---|---|
| `bracciale.jpg` | `bracciale` | Atelier (best seller), Collezioni, Lookbook |
| `anello-oro-rosa.jpg` | `anelloOroRosa` | Collezioni (Capri), Lookbook |
| `anello-argento-gemma.jpg` | `anelloArgento` | Atelier, Collezioni (Circeo), Lookbook |
| `anello-brunito.jpg` | `anelloBrunito` | Collezioni (Pantelleria), Lookbook |
| `dettaglio-maglie.jpg` | `dettaglioMaglie` | Processo, Lookbook |
| `dettaglio-granuli.jpg` | `dettaglioGranuli` | Processo, Lookbook |

Le foto degli anelli sono ritagliate dal post Instagram "All our rings" e sono piccole:
vanno sostituite con gli scatti originali in alta risoluzione.

## Prodotti senza foto

Ciondolo Pantelleria, Croce Iglesias, Orecchini Circeo e Anello Scultura mostrano un riquadro
con le indicazioni per lo scatto. Per aggiungere la foto: mettila in questa cartella, aggiungi
la riga corrispondente in `tools/embed-images.py` e scrivi la chiave nel campo `img` del prodotto
(array `PRODUCTS` in `index.html`).

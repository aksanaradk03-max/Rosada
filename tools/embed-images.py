#!/usr/bin/env python3
"""Incorpora le foto di /images dentro index.html, così il sito resta un file unico.

Uso: python3 tools/embed-images.py
Per cambiare una foto basta sostituire il file in /images (stesso nome) e rilanciare.
"""
import base64, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
# chiave usata nell'HTML (data-img / PRODUCTS.img) -> file in /images
IMAGES = {
    "bracciale": "bracciale.jpg",
    "anelloOroRosa": "anello-oro-rosa.jpg",
    "anelloArgento": "anello-argento-gemma.jpg",
    "anelloBrunito": "anello-brunito.jpg",
    "dettaglioGranuli": "dettaglio-granuli.jpg",
    "dettaglioMaglie": "dettaglio-maglie.jpg",
}
MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}

data = {}
for key, name in IMAGES.items():
    f = ROOT / "images" / name
    if f.exists():
        data[key] = f"data:{MIME[f.suffix.lower()]};base64," + base64.b64encode(f.read_bytes()).decode()

html = (ROOT / "index.html").read_text(encoding="utf-8")
block = "/*IMAGES-START*/" + json.dumps(data, indent=0) + "/*IMAGES-END*/"
html, n = re.subn(r"/\*IMAGES-START\*/.*?/\*IMAGES-END\*/", lambda _: block, html, flags=re.S)
if n != 1:
    raise SystemExit("Marcatori IMAGES-START/END non trovati in index.html")
(ROOT / "index.html").write_text(html, encoding="utf-8")
print(f"Incorporate {len(data)} immagini in index.html")

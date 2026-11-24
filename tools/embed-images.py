#!/usr/bin/env python3
"""Incorpora le foto di /images dentro index.html, così il sito resta un file unico.

Uso: python3 tools/embed-images.py

Ogni file images/NOME.jpg (o .png/.webp) diventa window.ROSADA_IMAGES["NOME"]. Il sito usa
il nome del file come chiave: per un prodotto è il suo "id" nell'elenco PRODUCTS in index.html
(es. images/etna.jpg per il prodotto con id "etna").
Per cambiare una foto: sostituisci il file (stesso nome) e rilancia questo script.
Le foto originali e i ritagli sono in images/source/ (non vengono incorporati).
"""
import base64, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}

data = {}
for f in sorted((ROOT / "images").iterdir()):
    if f.is_file() and f.suffix.lower() in MIME:
        data[f.stem] = f"data:{MIME[f.suffix.lower()]};base64," + base64.b64encode(f.read_bytes()).decode()

html = (ROOT / "index.html").read_text(encoding="utf-8")
block = "/*IMAGES-START*/" + json.dumps(data, indent=0) + "/*IMAGES-END*/"
html, n = re.subn(r"/\*IMAGES-START\*/.*?/\*IMAGES-END\*/", lambda _: block, html, flags=re.S)
if n != 1:
    raise SystemExit("Marcatori IMAGES-START/END non trovati in index.html")
(ROOT / "index.html").write_text(html, encoding="utf-8")
print(f"Incorporate {len(data)} immagini in index.html: {', '.join(data)}")

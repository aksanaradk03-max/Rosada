#!/usr/bin/env python3
"""Prepara le foto dei gioielli per il sito Rosáda.

Ogni gioiello diventa una "tavola" 4:5 (720x900, JPG) con fondo nero puro e il pezzo
intero, centrato, con margine attorno. Le foto con fondo bianco vengono ritagliate sul
nero (ombre e riflessi tolti); quelle già su nero vengono solo ripulite.

Uso:
    pip install opencv-python-headless numpy pillow
    python3 tools/prepare-images.py             # rifà tutte le tavole in images/
    python3 tools/prepare-images.py etna eolie  # solo alcune
    python3 tools/embed-images.py               # poi incorpora le foto in index.html

PER USARE LE FOTO REALI AD ALTA RISOLUZIONE
  1. Metti il file in images/source/ (es. etna.jpg) e aggiungi/cambia la riga in PIECES:
     nome file, riquadro None (= tutta la foto), tipo di fondo ("white" o "black").
  2. Lancia questo script. Con foto grandi il pezzo non viene più ingrandito: resta nitido.
  Oppure salta lo script: crea tu una tavola 4:5 con fondo nero (min. 1440x1800 px) e salvala
  in images/ con lo stesso nome (es. images/etna.jpg), poi lancia embed-images.py.
"""
import sys, pathlib
import cv2
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "images" / "source"
OUT = ROOT / "images"
PLATE_W, PLATE_H = 720, 900          # tavola 4:5
FILL_W, FILL_H = 0.80, 0.80          # quanto della tavola può occupare il pezzo
MAX_UPSCALE = 3.0                    # mai ingrandire più di così (oltre, la foto si impasta)

# chiave: (file sorgente, riquadro in pixel del file originale o None, fondo, parametri)
# Per gli screenshot iPad (2360x1640) i riquadri sono presi dal post visualizzato a 2000 px
# di larghezza e riportati sul file reale con scale=1.18.
S = 1.18
PIECES = {
    # --- orecchini -------------------------------------------------------------------------------
    "etna":          ("earrings.png",  (600, 380, 830, 630),   "white", {"scale": S, "hole_max": 120, "min_area": 250}),
    "taormina":      ("earrings.png",  (680, 740, 880, 1000),  "white", {"scale": S, "hole_max": 160, "min_area": 250}),
    "eolie":         ("earrings.png",  (1120, 690, 1340, 950), "white", {"scale": S, "hole_max": 300, "min_area": 250}),
    # --- ciondoli (la catena sfuma in alto invece di essere tagliata) ----------------------------
    "granparadiso":  ("pendants.png",  (640, 478, 840, 800),   "white", {"scale": S, "hole_max": 400, "fade_top": 0.12, "g_thr": 13, "wall_r": 3}),
    "stelvio":       ("pendants.png",  (912, 372, 1070, 700),  "white", {"scale": S, "hole_max": 400, "fade_top": 0.12, "g_thr": 13, "wall_r": 3}),
    "gargano":       ("pendants.png",  (1200, 300, 1370, 600), "white", {"scale": S, "fade_top": 0.12, "g_thr": 13, "wall_r": 3}),
    "pantelleria":   ("pendants.png",  (1200, 735, 1360, 940), "white", {"scale": S, "fade_top": 0.12, "g_thr": 13, "wall_r": 3}),
    # --- bracciali -------------------------------------------------------------------------------
    "portorotondo":  ("bracciale.jpg", None,                   "black", {"fill_w": 0.94}),
    "portorotondorosa": ("bracelets.png", (570, 385, 940, 625), "color", {"scale": S, "sat": 0.16, "close": 9, "hole_max": 40, "fill_w": 0.94}),
    "fortedeimarmi": ("bracelets.png", (1020, 605, 1395, 830), "color", {"scale": S, "sat": 0.22, "close": 11, "hole_max": 80, "fill_w": 0.94}),
    # --- anelli ----------------------------------------------------------------------------------
    "capri":         ("anelli.jpg",    (40, 15, 300, 335),     "black", {}),
    "circeo":        ("anelli.jpg",    (495, 15, 775, 345),    "black", {}),
    "iglesias":      ("anelli.jpg",    (25, 625, 325, 830),    "black", {}),
    "gransasso":     ("gransasso.png", (700, 500, 950, 790),   "stars", {"scale": S}),
}

# ------------------------------------------------------------------------------------------------
def ell(n):
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (n, n))

def drop_small(m, min_area):
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, 8)
    keep = np.zeros_like(m)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= min_area:
            keep[lab == i] = 1
    return keep

def fill_holes(m, hole_max):
    h, w = m.shape
    n, lab, stats, _ = cv2.connectedComponentsWithStats(1 - m, 4)
    out = m.copy()
    for i in range(1, n):
        x, y, ww, hh, a = stats[i]
        if not (x == 0 or y == 0 or x + ww == w or y + hh == h) and a <= hole_max:
            out[lab == i] = 1
    return out

def bg_color(f):
    border = np.concatenate([f[:5].reshape(-1, 3), f[-5:].reshape(-1, 3), f[:, :5].reshape(-1, 3), f[:, -5:].reshape(-1, 3)])
    return np.percentile(border, 75, axis=0)

def compose(f, a, bg):
    """Toglie il fondo chiaro in proporzione alla trasparenza: nessun bordo bianco residuo."""
    return np.clip(f - (1 - a)[..., None] * bg[None, None, :], 0, 255).astype(np.uint8)

def cut_white(img, g_thr=26, wall_r=5, strong=85, hole_max=900, bg_tol=10, min_area=60, shrink=2, den=2, keep_ratio=0.03, **_):
    """Fondo chiaro -> nero, ombre morbide comprese.
    I contorni del gioiello sono 'muri' (bordi netti). Le zone morbide che comunicano con
    l'esterno senza attraversare un muro sono fondo o ombra; quelle chiuse dai muri sono gioiello."""
    f = cv2.fastNlMeansDenoisingColored(img, None, den, den, 5, 15).astype(np.float32)
    h, w = f.shape[:2]
    bg = bg_color(f)
    d = np.max(bg[None, None, :] - f, axis=2).clip(0, 255)
    gray = cv2.GaussianBlur(cv2.cvtColor(np.clip(f, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 0.7)
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    walls = cv2.dilate(((np.hypot(gx, gy) > g_thr) | (d > strong)).astype(np.uint8), ell(wall_r))
    n, lab, stats, _ = cv2.connectedComponentsWithStats((1 - walls).astype(np.uint8), 4)
    outside = np.zeros((h, w), np.uint8)
    for i in range(1, n):
        x, y, ww, hh, a = stats[i]
        if x == 0 or y == 0 or x + ww == w or y + hh == h:
            outside[lab == i] = 1
    obj = drop_small((1 - outside).astype(np.uint8), min_area)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(obj, 8)      # via i riflessi sotto il pezzo: componenti molto più piccole della principale
    if n > 1:
        big = stats[1:, cv2.CC_STAT_AREA].max()
        for i in range(1, n):
            if stats[i, cv2.CC_STAT_AREA] < keep_ratio * big:
                obj[lab == i] = 0
    pure = ((d < bg_tol) & (obj > 0)).astype(np.uint8)       # aperture grandi: trasparenti; riflessi piccoli: restano
    n, lab, stats, _ = cv2.connectedComponentsWithStats(pure, 4)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] > hole_max:
            obj[lab == i] = 0
    obj = cv2.erode(obj, ell(shrink * 2 + 1))
    return compose(f, cv2.GaussianBlur(obj.astype(np.float32), (0, 0), 0.9), bg)

def cut_color(img, sat=0.20, close=9, hole_max=500, shrink=1, min_area=200, **_):
    """Metalli colorati (oro, rosa): il gioiello è saturo, l'ombra è grigia."""
    f8 = cv2.fastNlMeansDenoisingColored(img, None, 2, 2, 5, 15)
    s = cv2.cvtColor(f8, cv2.COLOR_BGR2HSV)[..., 1] / 255.0
    m = cv2.morphologyEx((s > sat).astype(np.uint8), cv2.MORPH_CLOSE, ell(close))
    m = fill_holes(drop_small(m, min_area), hole_max)
    m = cv2.erode(m, ell(shrink * 2 + 1))
    f = f8.astype(np.float32)
    return compose(f, cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.9), bg_color(f))

def clean_black(img, black_point=14, **_):
    """Foto già su nero: nero puro nel fondo, un filo di pulizia dal rumore JPEG."""
    f = cv2.fastNlMeansDenoisingColored(img, None, 3, 3, 5, 15).astype(np.float32)
    f = (f - black_point) * (255.0 / (255.0 - black_point))
    return np.clip(f, 0, 255).astype(np.uint8)

def clean_stars(img, **_):
    """Foto su cielo stellato: le stelle fuori dal gioiello vengono tolte, il fondo diventa nero."""
    f = cv2.fastNlMeansDenoisingColored(img, None, 3, 3, 5, 15)
    lum = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    m = cv2.morphologyEx((lum > 62).astype(np.uint8), cv2.MORPH_OPEN, ell(3))
    m = cv2.morphologyEx(drop_small(m, 40), cv2.MORPH_CLOSE, ell(25))
    m = fill_holes(m, 10 ** 6)
    m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 3)
    return clean_black(np.clip(f.astype(np.float32) * m[..., None], 0, 255).astype(np.uint8), black_point=10)

def fade_top(img, frac):
    h = img.shape[0]; n = int(h * frac)
    ramp = np.ones(h, np.float32); ramp[:n] = np.linspace(0, 1, n) ** 1.6
    return (img.astype(np.float32) * ramp[:, None, None]).astype(np.uint8)

def to_plate(img, fill_w=FILL_W, fill_h=FILL_H):
    """Centra il pezzo (riquadro dei pixel non neri) in una tavola 4:5, con margine."""
    lum = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ys, xs = np.where(lum > 28)
    if len(xs) == 0:
        raise SystemExit("nessun gioiello trovato nel ritaglio")
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    piece = img[y0:y1, x0:x1]
    ph, pw = piece.shape[:2]
    sc = min(PLATE_W * fill_w / pw, PLATE_H * fill_h / ph, MAX_UPSCALE)
    nw, nh = max(1, round(pw * sc)), max(1, round(ph * sc))
    interp = cv2.INTER_LANCZOS4 if sc > 1 else cv2.INTER_AREA
    piece = cv2.resize(piece, (nw, nh), interpolation=interp)
    if sc > 1:   # nitidezza leggera dopo l'ingrandimento
        blur = cv2.GaussianBlur(piece, (0, 0), 1.3)
        piece = cv2.addWeighted(piece, 1.55, blur, -0.55, 0)
    plate = np.zeros((PLATE_H, PLATE_W, 3), np.uint8)
    ox, oy = (PLATE_W - nw) // 2, (PLATE_H - nh) // 2
    plate[oy:oy + nh, ox:ox + nw] = piece
    return plate, sc

def process(key):
    fname, box, kind, kw = PIECES[key]
    im = Image.open(SRC / fname).convert("RGB")
    if box:
        k = kw.get("scale", 1.0)
        im = im.crop(tuple(int(v * k) for v in box))
    img = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    out = {"white": cut_white, "color": cut_color, "black": clean_black, "stars": clean_stars}[kind](img, **kw)
    if kw.get("fade_top"):
        out = fade_top(out, kw["fade_top"])
    plate, sc = to_plate(out, kw.get("fill_w", FILL_W), kw.get("fill_h", FILL_H))
    Image.fromarray(cv2.cvtColor(plate, cv2.COLOR_BGR2RGB)).save(OUT / f"{key}.jpg", quality=92, subsampling=0, optimize=True)
    return sc

if __name__ == "__main__":
    keys = sys.argv[1:] or list(PIECES)
    for k in keys:
        print(f"{k:18s} ingrandimento x{process(k):.2f}")

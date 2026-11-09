"""Imágenes de ejemplo de Rédito: escenas dibujadas por código (no son fotografías).

Todas comparten dirección de arte: se dibujan en luminancia y se pasan a un duotono
tinta → latón → marfil (los tres colores del diario), con grano fino. Así la portada
tiene imágenes coherentes sin usar fotos de terceros.
  python3 datos/imagenes.py   → img/<nombre>-<ancho>.webp
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parent.parent / "img"
OUT.mkdir(exist_ok=True)
W, H = 1600, 1066  # 3:2
RNG = np.random.default_rng(7)

# duotono: tinta oklch(0.17) → latón → marfil, en sRGB
PARADAS = [(0.0, (22, 23, 27)), (0.42, (92, 78, 58)), (0.72, (176, 142, 84)), (1.0, (246, 241, 230))]


def duotono(lum):
    lum = np.clip(lum, 0, 1)
    out = np.zeros(lum.shape + (3,))
    for (a, ca), (b, cb) in zip(PARADAS, PARADAS[1:]):
        m = (lum >= a) & (lum <= b)
        t = ((lum - a) / (b - a))[m][:, None]
        out[m] = np.array(ca) * (1 - t) + np.array(cb) * t
    return out


def acabar(lum, nombre, grano=0.035):
    lum = lum + RNG.normal(0, grano, lum.shape)
    img = Image.fromarray(duotono(lum).astype(np.uint8), "RGB")
    for w in (480, 800, 1200):
        img.resize((w, round(w * img.height / img.width)), Image.LANCZOS).save(OUT / f"{nombre}-{w}.webp", quality=78, method=6)
    print("ok", nombre)


def desenfocar(im, r):
    """Desenfoque gaussiano separable en numpy (PIL no lo hace en modo F)."""
    a = a_np(im)
    k = np.arange(-int(3 * r), int(3 * r) + 1)
    g = np.exp(-(k / r) ** 2 / 2); g /= g.sum()
    a = np.apply_along_axis(lambda v: np.convolve(np.pad(v, len(k) // 2, mode="edge"), g, "valid"), 1, a)
    a = np.apply_along_axis(lambda v: np.convolve(np.pad(v, len(k) // 2, mode="edge"), g, "valid"), 0, a)
    return Image.fromarray(a.astype(np.float32), "F")


def capa():
    return Image.new("F", (W, H), 0.0)


def a_np(im):
    return np.asarray(im, dtype=np.float64)


def cielo(top, bottom, sol=None, r=500, fuerza=0.35):
    y = np.linspace(0, 1, H)[:, None] * np.ones((1, W))
    lum = top * (1 - y) + bottom * y
    if sol:
        xx, yy = np.meshgrid(np.arange(W), np.arange(H))
        d = np.hypot(xx - sol[0], yy - sol[1])
        lum += fuerza * np.exp(-(d / r) ** 2)
    return lum


def columnas():
    lum = cielo(0.62, 0.38, sol=(1250, 250), r=600, fuerza=0.35)
    im = Image.fromarray(lum.astype(np.float32), "F")
    d = ImageDraw.Draw(im)
    x0, x1 = 120, 1480
    base, cap = 960, 330
    d.polygon([(x0 - 40, cap - 40), ((x0 + x1) / 2, 90), (x1 + 40, cap - 40)], fill=0.30)   # frontón
    d.polygon([(x0 + 60, cap - 60), ((x0 + x1) / 2, 130), (x1 - 60, cap - 60)], fill=0.22)
    d.rectangle([x0 - 40, cap - 40, x1 + 40, cap + 60], fill=0.42)                          # entablamento
    d.rectangle([x0 - 40, cap + 60, x1 + 40, cap + 80], fill=0.18)
    for i, y in enumerate(range(base, H, 36)):                                               # escalinata
        d.rectangle([x0 - 120 - i * 30, y, x1 + 120 + i * 30, y + 36], fill=0.55 - 0.05 * (i % 2))
    arr = a_np(im)
    n, ancho = 8, 110
    paso = (x1 - x0 - ancho) / (n - 1)
    for k in range(n):
        cx = x0 + ancho / 2 + k * paso
        xs = np.arange(int(cx - ancho / 2), int(cx + ancho / 2))
        u = (xs - cx) / (ancho / 2)
        sombra = 0.18 + 0.62 * np.clip(np.cos((u - 0.35) * math.pi / 2), 0, 1) ** 1.4   # luz desde la derecha
        estrias = 0.04 * np.cos(u * math.pi * 10)
        arr[cap + 80:base, xs] = (sombra + estrias)[None, :]
        arr[cap + 60:cap + 92, int(cx - ancho * 0.62):int(cx + ancho * 0.62)] = 0.62           # capitel
    arr[cap + 80:base] *= np.linspace(1.0, 0.8, base - cap - 80)[:, None]
    acabar(arr, "tesoro")


def pantallas():
    lum = np.full((H, W), 0.06)
    im = Image.fromarray(lum.astype(np.float32), "F")
    d = ImageDraw.Draw(im)
    for fila in range(3):
        for col in range(5):
            x, y = 60 + col * 310, 90 + fila * 300
            d.rectangle([x, y, x + 280, y + 250], fill=0.16)
            pts, v = [], y + 160
            for i in range(14):
                v += RNG.normal(-3, 14)
                pts.append((x + 15 + i * 19, min(max(v, y + 30), y + 230)))
            d.line(pts, fill=0.85, width=5)
    im = desenfocar(im, 6)
    arr = a_np(im)
    xx, yy = np.meshgrid(np.arange(W), np.arange(H))
    for _ in range(26):                                                                       # bokeh
        cx, cy, r = RNG.uniform(0, W), RNG.uniform(H * 0.45, H), RNG.uniform(30, 110)
        arr += 0.22 * np.clip(1 - np.hypot(xx - cx, yy - cy) / r, 0, 1) ** 0.5
    arr *= 0.75 + 0.35 * np.exp(-((xx - 900) / 900) ** 2)
    acabar(arr, "bolsa")


def contenedores():
    lum = cielo(0.70, 0.52, sol=(300, 220), r=500, fuerza=0.2)
    im = Image.fromarray(lum.astype(np.float32), "F")
    d = ImageDraw.Draw(im)
    for gx in (980, 1300):                                                                    # grúas
        d.rectangle([gx, 120, gx + 22, 720], fill=0.12)
        d.rectangle([gx - 300, 150, gx + 160, 178], fill=0.12)
        d.line([(gx + 11, 120), (gx - 280, 160)], fill=0.12, width=6)
        d.line([(gx - 120, 178), (gx - 120, 420)], fill=0.15, width=4)
    tonos = [0.30, 0.45, 0.58, 0.38, 0.66, 0.26]
    x = -40
    while x < W:                       # pilas por columna: ningún contenedor flota
        w = 260 if RNG.random() > 0.3 else 130
        alto = int(RNG.integers(1, 7))
        for fila in range(alto):
            y = 1000 - (fila + 1) * 92
            t = tonos[RNG.integers(len(tonos))]
            d.rectangle([x, y, x + w - 6, y + 86], fill=t)
            for cx in range(int(x) + 10, int(x + w - 10), 14):  # ondulado
                d.line([(cx, y + 8), (cx, y + 78)], fill=t - 0.07, width=4)
        x += w
    d.rectangle([0, 1000, W, H], fill=0.20)
    acabar(a_np(im), "puerto")


def fabrica():
    lum = cielo(0.42, 0.78, sol=(820, 760), r=520, fuerza=0.25)
    im = Image.fromarray(lum.astype(np.float32), "F")
    vapor = Image.new("F", (W, H), 0.0)
    dv = ImageDraw.Draw(vapor)
    for cx in (520, 690, 1120):
        for i in range(9):
            r = 60 + i * 26
            dv.ellipse([cx + i * 34 - r, 420 - i * 46 - r, cx + i * 34 + r, 420 - i * 46 + r], fill=0.35 - i * 0.03)
    vapor = desenfocar(vapor, 40)
    d = ImageDraw.Draw(im)
    for cx, h in ((520, 380), (690, 300), (1120, 430)):
        d.polygon([(cx - 34, 820), (cx - 22, 820 - h), (cx + 22, 820 - h), (cx + 34, 820)], fill=0.08)
    d.rectangle([200, 700, 1400, 860], fill=0.10)
    for x in range(240, 1380, 90):
        d.polygon([(x, 700), (x + 45, 650), (x + 90, 700)], fill=0.10)
    d.rectangle([0, 860, W, H], fill=0.06)
    arr = a_np(im) + a_np(vapor)
    acabar(arr, "industria")


def viviendas():
    lum = np.full((H, W), 0.28)
    im = Image.fromarray(lum.astype(np.float32), "F")
    d = ImageDraw.Draw(im)
    for fila in range(9):
        for col in range(11):
            x, y = 30 + col * 146, 20 + fila * 118
            d.rectangle([x, y, x + 140, y + 112], fill=0.36)
            luz = RNG.random()
            d.rectangle([x + 28, y + 18, x + 112, y + 92], fill=0.90 if luz > 0.72 else 0.14)
            d.rectangle([x + 20, y + 90, x + 120, y + 98], fill=0.50)                         # balcón
    arr = a_np(im)
    xx, yy = np.meshgrid(np.arange(W), np.arange(H))
    arr *= 0.6 + 0.5 * (xx / W)
    acabar(arr, "vivienda")


def eolicos():
    lum = cielo(0.48, 0.86, sol=(1150, 640), r=380, fuerza=0.15)
    xx = np.arange(W)
    arr = lum.copy()
    for k, (base, amp, tono) in enumerate(((760, 60, 0.30), (850, 40, 0.18), (930, 30, 0.08))):
        perfil = base + amp * np.sin(xx / (260 + 90 * k) + k)
        yy = np.arange(H)[:, None]
        arr = np.where(yy > perfil[None, :], tono, arr)
    im = Image.fromarray(arr.astype(np.float32), "F")
    d = ImageDraw.Draw(im)
    for cx, cy, s in ((300, 420, 1.0), (760, 520, 0.7), (1080, 470, 0.85), (1380, 560, 0.55)):
        d.polygon([(cx - 7 * s, cy), (cx + 7 * s, cy), (cx + 11 * s, cy + 420 * s), (cx - 11 * s, cy + 420 * s)], fill=0.10)
        for a in (90, 210, 330):
            t = math.radians(a + 15 * s)
            d.polygon([(cx, cy), (cx + 230 * s * math.cos(t) - 8 * s * math.sin(t), cy - 230 * s * math.sin(t) - 8 * s * math.cos(t)),
                       (cx + 230 * s * math.cos(t), cy - 230 * s * math.sin(t))], fill=0.10)
        d.ellipse([cx - 12 * s, cy - 12 * s, cx + 12 * s, cy + 12 * s], fill=0.10)
    acabar(a_np(im), "energia")


def datos():
    arr = np.full((H, W), 0.05)
    im = Image.fromarray(arr.astype(np.float32), "F")
    d = ImageDraw.Draw(im)
    vx, vy = W / 2, H * 0.46
    for lado in (-1, 1):
        for i in range(14):
            t0, t1 = i / 14, (i + 1) / 14
            xa = vx + lado * (60 + 740 * t0 ** 1.6)
            xb = vx + lado * (60 + 740 * t1 ** 1.6)
            ya0, ya1 = vy - 40 - 520 * t0 ** 1.6, vy + 40 + 520 * t0 ** 1.6
            yb0, yb1 = vy - 40 - 520 * t1 ** 1.6, vy + 40 + 520 * t1 ** 1.6
            d.polygon([(xa, ya0), (xb, yb0), (xb, yb1), (xa, ya1)], fill=0.12 + 0.02 * (i % 2))
            for j in range(10):
                f = 0.15 + j * 0.07
                xl = xa + (xb - xa) * 0.5
                yl = (ya0 + (ya1 - ya0) * f + yb0 + (yb1 - yb0) * f) / 2
                if RNG.random() > 0.35:
                    r = 2 + 6 * t1
                    d.ellipse([xl - r, yl - r, xl + r, yl + r], fill=0.95 if RNG.random() > 0.5 else 0.7)
    im = desenfocar(im, 1.2)
    arr = a_np(im)
    xx, yy = np.meshgrid(np.arange(W), np.arange(H))
    arr += 0.30 * np.exp(-(((xx - vx) / 160) ** 2 + ((yy - vy) / 120) ** 2))
    acabar(arr, "tecnologia")


if __name__ == "__main__":
    for f in (columnas, pantallas, contenedores, fabrica, viviendas, eolicos, datos):
        f()

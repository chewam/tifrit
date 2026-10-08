#!/usr/bin/env python3
"""Génère static/images/carte.jpg : carte fixe (tuiles OpenStreetMap) avec un repère rouge sur la maison.
Usage : python3 tools/carte.py   (coordonnées lues dans data/site.json)"""
import json, math, io, os, time, urllib.request
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.join(os.path.dirname(__file__), "..")
site = json.load(open(os.path.join(ROOT, "data/site.json")))
LAT, LNG = site["geo"]["lat"], site["geo"]["lng"]
Z = 12
# cadre : Agadir au sud, Imouzzer au nord, Taghazout à l'ouest
LON0, LON1, LAT0, LAT1 = -9.80, -9.30, 30.40, 30.71

def xy(lat, lon, z=Z):
    n = 2 ** z
    x = (lon + 180) / 360 * n
    y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n
    return x, y
x0, y0 = xy(LAT1, LON0); x1, y1 = xy(LAT0, LON1)
tx0, ty0, tx1, ty1 = int(x0), int(y0), int(x1), int(y1)
W, H = (tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256
canvas = Image.new("RGB", (W, H), "#e8e4d8")
for tx in range(tx0, tx1 + 1):
    for ty in range(ty0, ty1 + 1):
        url = f"https://tile.openstreetmap.org/{Z}/{tx}/{ty}.png"
        req = urllib.request.Request(url, headers={"User-Agent": "MaisonTifritSite/1.0 (carte statique, une fois)"})
        try:
            tile = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=30).read())).convert("RGB")
            canvas.paste(tile, ((tx - tx0) * 256, (ty - ty0) * 256))
        except Exception as e:
            print("tuile manquante", tx, ty, e)
        time.sleep(0.15)
# recadrage exact
crop = (int((x0 - tx0) * 256), int((y0 - ty0) * 256), int((x1 - tx0) * 256), int((y1 - ty0) * 256))
img = canvas.crop(crop)
# léger voile pour que le repère ressorte
img = Image.blend(img, Image.new("RGB", img.size, "#f7f4ee"), 0.12)
d = ImageDraw.Draw(img)
px, py = xy(LAT, LNG); px = (px - x0) * 256; py = (py - y0) * 256
# repère rouge : goutte + point
r = 22
d.polygon([(px, py), (px - r * 0.75, py - r * 1.35), (px + r * 0.75, py - r * 1.35)], fill="#c62828")
d.ellipse([px - r, py - r * 2.3, px + r, py - r * 0.3], fill="#c62828", outline="#ffffff", width=4)
d.ellipse([px - 8, py - r * 1.3 - 8, px + 8, py - r * 1.3 + 8], fill="#ffffff")
# étiquette
try:
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 30)
except Exception:
    font = ImageFont.load_default()
label = site["nom"]
tw = d.textlength(label, font=font); th = 34
bx, by = px + r + 10, py - r * 1.3 - th / 2 - 8
d.rounded_rectangle([bx, by, bx + tw + 24, by + th + 16], radius=10, fill="#c62828")
d.text((bx + 12, by + 7), label, font=font, fill="#ffffff")
# attribution
att = "© OpenStreetMap contributors"
try: f2 = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 18)
except Exception: f2 = font
aw = d.textlength(att, font=f2)
d.rectangle([img.width - aw - 20, img.height - 30, img.width, img.height], fill=(255, 255, 255))
d.text((img.width - aw - 10, img.height - 26), att, font=f2, fill="#333333")
out = os.path.join(ROOT, "static/images")
img.save(os.path.join(out, "carte.jpg"), quality=82, optimize=True, progressive=True)
img.save(os.path.join(out, "carte.webp"), quality=78, method=6)
small = img.resize((600, int(img.height * 600 / img.width)), Image.LANCZOS)
small.save(os.path.join(out, "carte-600.webp"), quality=74, method=6)
print("carte", img.size, "repère en", int(px), int(py))

#!/usr/bin/env python3
"""Fabrique les versions WebP (1200 px et 600 px) de chaque JPG de static/images. Nécessite Pillow : pip3 install pillow"""
import os, sys
from PIL import Image, ImageOps
D = os.path.join(os.path.dirname(__file__), "..", "static", "images")
for f in sorted(os.listdir(D)):
    if not f.lower().endswith((".jpg", ".jpeg")): continue
    base = f.rsplit(".", 1)[0]; p = os.path.join(D, f)
    im = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
    if im.width > 1600:
        im = im.resize((1600, int(im.height * 1600 / im.width)), Image.LANCZOS); im.save(p, quality=80, optimize=True, progressive=True)
    im.save(os.path.join(D, base + ".webp"), quality=74, method=6)
    w = min(600, im.width)
    im.resize((w, int(im.height * w / im.width)), Image.LANCZOS).save(os.path.join(D, base + "-600.webp"), quality=72, method=6)
    print(f, im.size)

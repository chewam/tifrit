#!/usr/bin/env python3
"""Générateur statique de la Maison d'hôtes Tifrit.
Aucune dépendance : python3 build.py  ->  public/
Contenus : content/<lang>/*.md (texte), data/*.json (prix, contacts, avis, disponibilités)."""
import json, os, re, shutil, html, datetime
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "public"
LANGS = ["fr", "en", "de"]
SITE = json.loads((ROOT / "data/site.json").read_text(encoding="utf-8"))
SEJOURS = json.loads((ROOT / "data/sejours.json").read_text(encoding="utf-8"))
AVIS = json.loads((ROOT / "data/avis.json").read_text(encoding="utf-8"))
DISPO = json.loads((ROOT / "data/disponibilites.json").read_text(encoding="utf-8"))
UI = json.loads((ROOT / "data/ui.json").read_text(encoding="utf-8"))
_mq = ROOT / "data/maquette.json"
MAQUETTE = json.loads(_mq.read_text(encoding="utf-8")) if _mq.exists() else {"actif": False}
BASE = (ROOT / "templates/base.html").read_text(encoding="utf-8")

try:
    from PIL import Image
except ImportError:
    Image = None
_dimfile = ROOT / "data/dimensions.json"
_dims = json.loads(_dimfile.read_text()) if _dimfile.exists() else {}
def dims(name):
    if name in _dims: return tuple(_dims[name])
    p = ROOT / "static/images" / name
    d = None
    if Image and p.exists():
        with Image.open(p) as im: d = im.size
    _dims[name] = d
    return d

# ---------- front matter ----------
def parse_md(text):
    meta = {}
    if text.startswith("---"):
        _, fm, body = text.split("---", 2)
        for line in fm.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1); meta[k.strip()] = v.strip().strip('"')
    else:
        body = text
    return meta, body.strip()

# ---------- inline markdown ----------
def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', s)
    return s

# ---------- shortcodes ----------
def picture(name, alt, cls="", sizes="(max-width: 700px) 100vw, 50vw", lazy=True):
    base = name.rsplit(".", 1)[0]
    d = dims(name); wh = f' width="{d[0]}" height="{d[1]}"' if d else ""
    small = (ROOT / "static/images" / f"{base}-600.webp").exists()
    srcset = f"/images/{base}-600.webp 600w, /images/{base}.webp 1200w" if small else f"/images/{base}.webp"
    lz = ' loading="lazy"' if lazy else ""
    return (f'<picture class="{cls}"><source type="image/webp" srcset="{srcset}" sizes="{sizes}">'
            f'<img src="/images/{name}" alt="{html.escape(alt)}"{wh}{lz}></picture>')

def mock_for(label, lang):
    """Photo d'illustration temporaire (data/maquette.json) correspondant à un emplacement."""
    if not MAQUETTE.get("actif"): return None
    for fn, m in MAQUETTE.get("images", {}).items():
        key = m.get(lang) or m.get("fr")
        if key and key.lower() in label.lower() and (ROOT / "static/images" / fn).exists():
            return fn
    return None

def placeholder(label, lang, cls=""):
    fn = mock_for(label, lang)
    if fn:
        return f'<div class="mock {cls}" data-badge="{UI[lang]["mock_badge"]}">{picture(fn, label)}</div>'
    return f'<div class="ph {cls}"><span>{UI[lang]["photo_soon"]}</span><em>{inline(label)}</em></div>'

def render_sejours(lang):
    ui = UI[lang]; out = ['<div class="sejours">']
    for s in SEJOURS["formules"]:
        t = s[lang]
        prix = s["prix"]
        badge = "" if s.get("prix_confirme") else f'<span class="todo">{ui["prix_indicatif"]}</span>'
        days = "".join(f"<li><strong>{inline(d['titre'])}</strong> {inline(d['texte'])}</li>" for d in t["jours"])
        inc = "".join(f"<li>{inline(x)}</li>" for x in t["inclus"])
        pas = "".join(f"<li>{inline(x)}</li>" for x in t["pas_pour"])
        out.append(f'''<article class="sejour{' phare' if s.get('phare') else ''}" id="{s['id']}">
  <div class="sejour-head"><div><div class="eyebrow">{inline(t['sous_titre'])}</div><h2>{inline(t['titre'])}</h2></div>
  <div class="prix"><strong>{prix['montant']} {prix['devise']}</strong><span>{inline(t['prix_detail'])}</span>{badge}</div></div>
  <p class="lead">{inline(t['intro'])}</p>
  <div class="sejour-cols">
    <div><h3>{ui['chaque_jour']}</h3><ol class="jours">{days}</ol></div>
    <div><h3>{ui['inclus']}</h3><ul class="check">{inc}</ul><h3>{ui['pas_pour']}</h3><ul class="non">{pas}</ul></div>
  </div>
  <a class="btn btn-primary" href="{page_url(lang,'reserver')}?sejour={s['id']}">{ui['reserver_ce_sejour']}</a>
</article>''')
    out.append("</div>")
    return "\n".join(out)

def render_avis(lang):
    ui = UI[lang]; out = ['<div class="notes">']
    for src in AVIS["sources"]:
        if not src.get("note") and not src.get("nb"): continue
        score = f'<strong>{src["note"]}</strong><span>{src["sur"]}</span>' if src.get("note") else f'<strong>{src["nb"]}</strong><span> {ui["nb_avis"]}</span>'
        label = f'{src["nom"]} · {src["nb"]} {ui["avis"]}' if src.get("note") else src["nom"]
        out.append(f'<a class="note" href="{src.get("url","#")}" target="_blank" rel="noopener">{score}<em>{label}</em></a>')
    out.append('</div><div class="quotes">')
    for a in AVIS["extraits"]:
        out.append(f'<blockquote class="quote" lang="{a["lang"]}"><p>« {inline(a["texte"])} »</p><footer>{inline(a["auteur"])} · {a["source"]} · {a["date"]}</footer></blockquote>')
    out.append("</div>")
    return "\n".join(out)

def render_reserver(lang):
    ui = UI[lang]; c = SITE["contact"]
    wa = re.sub(r"\D", "", c["whatsapp"])
    opts = "".join(f'<option value="{s["id"]}">{inline(s[lang]["titre"])}</option>' for s in SEJOURS["formules"])
    pay = "".join(f"<li>{inline(p[lang])}</li>" for p in SITE["paiement"])
    return f'''<div class="reserver">
<div class="reserver-side">
  <a class="btn wa" href="https://wa.me/{wa}?text={html.escape(ui['wa_message'])}" target="_blank" rel="noopener">{ui['wa_btn']}</a>
  <p class="small">{ui['wa_note']}</p>
  <p><a href="tel:{c['telephone'].replace(' ','')}">{c['telephone']}</a><br><a href="mailto:{c['email']}">{c['email']}</a></p>
  <h3>{ui['paiement']}</h3><ul class="check">{pay}</ul>
  <h3>{ui['disponibilites']}</h3>
  <div id="cal" data-dispo='{json.dumps(DISPO, ensure_ascii=False)}' data-lang="{lang}"></div>
  <p class="small">{ui['cal_note']}</p>
</div>
<form class="form" action="{SITE['form_action']}" method="POST" name="reservation" data-netlify="true" data-wa="{wa}" data-mail="{c['email']}" data-intro="{html.escape(ui['wa_message'])}" data-subject="{html.escape(ui['f_subject'])}">
  <input type="hidden" name="lang" value="{lang}">
  <div class="row"><label>{ui['f_arrivee']}<input type="date" name="arrivee" required></label><label>{ui['f_depart']}<input type="date" name="depart" required></label></div>
  <div class="row"><label>{ui['f_personnes']}<select name="personnes"><option>1</option><option selected>2</option><option>3</option><option>4</option><option>5+</option></select></label>
  <label>{ui['f_sejour']}<select name="sejour" id="sejour"><option value="">{ui['f_sejour_libre']}</option>{opts}</select></label></div>
  <label>{ui['f_nom']}<input type="text" name="nom" required></label>
  <label>{ui['f_email']}<input type="email" name="email" required></label>
  <label>{ui['f_message']}<textarea name="message" rows="4"></textarea></label>
  <button class="btn btn-primary" type="submit">{ui['f_envoyer']}</button>
  <p class="small">{ui['f_note']}</p>
</form></div>'''

def render_nuit(lang):
    ui = UI[lang]; n = SEJOURS["nuit_seule"]; t = n[lang]
    badge = "" if n.get("prix_confirme") else f'<span class="todo">{ui["prix_indicatif"]}</span>'
    return (f'<div class="nuit"><div><h3>{inline(t["titre"])}</h3><p>{inline(t["texte"])}</p></div>'
            f'<div class="prix"><strong>{n["prix"]["montant"]} {n["prix"]["devise"]}</strong><span>{inline(t["prix_detail"])}</span>{badge}</div>'
            f'<a class="btn btn-outline" href="{page_url(lang,"reserver")}">{ui["f_sejour_libre_btn"]}</a></div>')

def render_map(lang):
    ui = UI[lang]; g = SITE.get("geo", {}); lat, lng = g.get("lat"), g.get("lng")
    if not lat: return f'<div class="ph"><span>{ui["photo_soon"]}</span><em>{ui["map_missing"]}</em></div>'
    gmaps = f"https://www.google.com/maps/dir/?api=1&destination={lat:.5f},{lng:.5f}"
    big = f"https://www.openstreetmap.org/?mlat={lat:.5f}&mlon={lng:.5f}#map=13/{lat:.4f}/{lng:.4f}"
    if (ROOT / "static/images/carte.jpg").exists():
        media = f'<a href="{gmaps}" target="_blank" rel="noopener" class="map-img">{picture("carte.jpg", ui["map_title"], sizes="(max-width: 700px) 100vw, 1100px")}</a>'
    else:
        d = 0.045
        bbox = f"{lng-d*1.6:.4f}%2C{lat-d:.4f}%2C{lng+d*1.6:.4f}%2C{lat+d:.4f}"
        media = f'<iframe title="{ui["map_title"]}" loading="lazy" src="https://www.openstreetmap.org/export/embed.html?bbox={bbox}&layer=mapnik&marker={lat:.5f}%2C{lng:.5f}"></iframe>'
    return (f'<div class="map">{media}'
            f'<div class="map-links"><a class="btn btn-primary" href="{gmaps}" target="_blank" rel="noopener">{ui["map_gmaps"]}</a>'
            f'<a class="btn btn-outline" href="{big}" target="_blank" rel="noopener">{ui["map_osm"]}</a>'
            f'<span class="small">GPS {lat:.5f}, {lng:.5f}</span></div></div>')

def render_journal(lang, pages):
    arts = sorted([p for p in pages if p["lang"] == lang and p["section"] == "journal"], key=lambda p: p["meta"].get("date",""), reverse=True)
    out = ['<div class="cards">']
    for a in arts:
        out.append(f'<a class="card" href="{a["url"]}"><div class="body"><div class="meta">{a["meta"].get("date","")}</div><h3>{inline(a["meta"]["title"])}</h3><p>{inline(a["meta"].get("description",""))}</p></div></a>')
    out.append("</div>")
    return "\n".join(out)

# ---------- block markdown ----------
def md_to_html(body, lang, pages):
    lines = body.split("\n"); out = []; i = 0; para = []; mode = None; block = []; gallery_cols = ""
    def flush():
        if para: out.append(f"<p>{inline(' '.join(para))}</p>"); para.clear()
    def close_block():
        nonlocal mode, block
        if mode in ("cards", "facts"):
            items = []; cur = None
            for l in block:
                if l.startswith("### "):
                    cur = {"t": l[4:], "b": []}; items.append(cur)
                elif cur is not None and l.strip():
                    cur["b"].append(l.strip())
            cls = "cards cards-text" if mode == "cards" else "facts"
            out.append(f'<div class="{cls}">' + "".join(
                (f'<div class="card"><div class="body">' if mode=="cards" else f'<div class="fact"><div class="num">{n:02d}</div>') +
                f"<h3>{inline(it['t'])}</h3>" + "".join(f"<p>{inline(x)}</p>" for x in it["b"]) +
                ("</div></div>" if mode=="cards" else "</div>") for n, it in enumerate(items, 1)) + "</div>")
        elif mode == "gallery":
            cls = f" g{gallery_cols}" if gallery_cols else ""
            out.append(f'<div class="gallery{cls}">' + "".join(block) + "</div>")
        mode = None; block = []
    while i < len(lines):
        l = lines[i]; s = l.strip()
        m = re.match(r"\{\{(\w+)(?::\s*(.*?))?\}\}$", s)
        if m and m.group(1) in ("cards", "facts", "gallery"):
            flush(); mode = m.group(1); block = []; gallery_cols = (m.group(2) or "").strip(); i += 1; continue
        if re.match(r"\{\{/(cards|facts|gallery)\}\}$", s):
            flush(); close_block(); i += 1; continue
        if mode in ("cards", "facts"):
            block.append(l); i += 1; continue
        if m:
            flush(); kind, arg = m.group(1), (m.group(2) or "")
            parts = [a.strip() for a in arg.split("|")]
            if kind == "photo": h = placeholder(parts[0], lang)
            elif kind == "img": h = picture(parts[0], parts[1] if len(parts) > 1 else "")
            elif kind == "cta": h = f'<p><a class="btn btn-primary" href="{parts[0]}">{inline(parts[1])}</a></p>'
            elif kind == "sejours": h = render_sejours(lang)
            elif kind == "avis": h = render_avis(lang)
            elif kind == "reserver": h = render_reserver(lang)
            elif kind == "id": h = f'<div id="{parts[0]}" class="anchor"></div>'
            elif kind == "nuit": h = render_nuit(lang)
            elif kind == "map": h = render_map(lang)
            else: h = ""
            (block if mode == "gallery" else out).append(h); i += 1; continue
        if mode == "gallery":
            i += 1; continue
        if not s: flush(); i += 1; continue
        if s.startswith("### "): flush(); out.append(f"<h3>{inline(s[4:])}</h3>")
        elif s.startswith("## "): flush(); out.append(f"<h2>{inline(s[3:])}</h2>")
        elif s.startswith("# "): flush(); out.append(f"<h1>{inline(s[2:])}</h1>")
        elif s.startswith("> "): flush(); out.append(f"<blockquote><p>{inline(s[2:])}</p></blockquote>")
        elif s.startswith("- "):
            flush(); items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(f"<li>{inline(lines[i].strip()[2:])}</li>"); i += 1
            out.append("<ul>" + "".join(items) + "</ul>"); continue
        else: para.append(s)
        i += 1
    flush(); close_block()
    return "\n".join(out)

# ---------- pages ----------
def page_url(lang, key, slug=None):
    for p in PAGES:
        if p["lang"] == lang and p["key"] == key and (slug is None or p["meta"].get("slug") == slug):
            return p["url"]
    return f"/{lang}/"

PAGES = []
def load_pages():
    for lang in LANGS:
        for f in sorted((ROOT / "content" / lang).glob("*.md")):
            meta, body = parse_md(f.read_text(encoding="utf-8"))
            key = f.stem; slug = meta.get("slug", key)
            url = f"/{lang}/" if key == "index" else f"/{lang}/{slug}/"
            PAGES.append(dict(lang=lang, key=key, section="page", meta=meta, body=body, url=url))
        jdir = ROOT / "content" / lang / "journal"
        for f in (sorted(jdir.glob("*.md")) if jdir.exists() else []):
            meta, body = parse_md(f.read_text(encoding="utf-8"))
            url = f"/{lang}/journal/{meta.get('slug', f.stem)}/"
            PAGES.append(dict(lang=lang, key=f"journal/{f.stem}", section="journal", meta=meta, body=body, url=url))

def nav_html(lang, current):
    ui = UI[lang]; items = []
    for key in ["maison", "sejours", "vallee", "acces", "avis"]:
        cur = ' aria-current="page"' if key == current else ""
        items.append(f'<li><a href="{page_url(lang,key)}"{cur}>{ui["nav"][key]}</a></li>')
    items.append(f'<li><a class="btn btn-primary" href="{page_url(lang,"reserver")}">{ui["nav"]["reserver"]}</a></li>')
    return "".join(items)

def lang_switch(page):
    out = []
    for lang in LANGS:
        alt = next((p for p in PAGES if p["lang"] == lang and p["key"] == page["key"]), None)
        url = alt["url"] if alt else f"/{lang}/"
        cur = ' aria-current="true"' if lang == page["lang"] else ""
        out.append(f'<a href="{url}" hreflang="{lang}" lang="{lang}"{cur}>{lang.upper()}</a>')
    return "".join(out)

def hreflangs(page):
    out = []
    for lang in LANGS:
        alt = next((p for p in PAGES if p["lang"] == lang and p["key"] == page["key"]), None)
        if alt: out.append(f'<link rel="alternate" hreflang="{lang}" href="{SITE["url"]}{alt["url"]}">')
    fr = next((p for p in PAGES if p["lang"] == "fr" and p["key"] == page["key"]), None)
    if fr: out.append(f'<link rel="alternate" hreflang="x-default" href="{SITE["url"]}{fr["url"]}">')
    return "\n".join(out)

def jsonld(lang):
    c = SITE["contact"]; a = SITE["adresse"]
    d = {"@context": "https://schema.org", "@type": "LodgingBusiness", "name": SITE["nom"], "url": SITE["url"] + f"/{lang}/",
         "telephone": c["telephone"].replace(" ", ""), "email": c["email"], "image": SITE["url"] + "/images/hero-piscine.jpg",
         "address": {"@type": "PostalAddress", "streetAddress": a["rue"], "addressLocality": a["ville"], "addressRegion": a["region"], "postalCode": a["cp"], "addressCountry": "MA"},
         "priceRange": SITE.get("price_range", "€€"), "petsAllowed": False,
         "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": n, "value": True} for n in ["Swimming pool", "Free parking", "Restaurant", "Terrace", "Hiking"]]}
    if SITE.get("geo", {}).get("lat"): d["geo"] = {"@type": "GeoCoordinates", "latitude": SITE["geo"]["lat"], "longitude": SITE["geo"]["lng"]}
    g = next((s for s in AVIS["sources"] if s.get("note") and s["nom"].lower().startswith("google")), None)
    if g: d["aggregateRating"] = {"@type": "AggregateRating", "ratingValue": g["note"], "bestRating": g["sur"], "reviewCount": g["nb"]}
    if SITE.get("google_business_url"): d["sameAs"] = [SITE["google_business_url"]]
    return f'<script type="application/ld+json">{json.dumps(d, ensure_ascii=False)}</script>'

def render_page(page):
    lang, meta = page["lang"], page["meta"]; ui = UI[lang]
    body_html = md_to_html(page["body"], lang, PAGES)
    tag = f"<p>{inline(meta['tagline'])}</p>" if meta.get("tagline") else ""
    tag_lead = f'<p class="lead">{inline(meta["tagline"])}</p>' if meta.get("tagline") else ""
    cta = (f'<div class="hero-cta"><a class="btn btn-primary" href="{page_url(lang,"sejours")}">{ui["voir_sejours"]}</a>'
           f'<a class="btn btn-ghost" href="{page_url(lang,"reserver")}">{ui["nav"]["reserver_long"]}</a></div>') if page["key"] == "index" else ""
    if MAQUETTE.get("actif") and MAQUETTE.get("hero", {}).get(page["key"]):
        meta = dict(meta, hero_img=MAQUETTE["hero"][page["key"]], hero_mock=True)
    if meta.get("hero_img"):
        strip = "".join(f"<span>{inline(x)}</span>" for x in ui.get("strip", [])) if page["key"] == "index" else ""
        strip_html = f'<div class="strip">{strip}</div>' if strip else ""
        hero = f'<header class="hero"><div class="hero-media{" mock" if meta.get("hero_mock") else ""}" data-badge="{ui["mock_badge"]}">{picture(meta["hero_img"], meta.get("hero_alt",""), sizes="100vw", lazy=False)}</div><div class="wrap"><h1>{inline(meta["title"])}</h1><div class="hero-side">{tag}{cta}</div></div>{strip_html}</header>'
    elif meta.get("hero_photo"):
        hero = f'<header class="hero hero-ph"><div class="hero-media">{placeholder(meta["hero_photo"], lang)}</div><div class="wrap"><h1>{inline(meta["title"])}</h1>{tag}</div></header>'
    else:
        hero = f'<header class="page-head"><div class="wrap"><h1>{inline(meta["title"])}</h1>{tag_lead}</div></header>'
    if page["section"] == "journal":
        hero = f'<header class="page-head"><div class="wrap"><div class="eyebrow">{meta.get("date","")}</div><h1>{inline(meta["title"])}</h1><p class="lead">{inline(meta.get("description",""))}</p></div></header>'
    c = SITE["contact"]; wa = re.sub(r"\D", "", c["whatsapp"])
    return (BASE.replace("{{lang}}", lang).replace("{{title}}", html.escape(meta["title"]) + " · " + SITE["nom"])
            .replace("{{description}}", html.escape(meta.get("description", "")))
            .replace("{{canonical}}", SITE["url"] + page["url"]).replace("{{hreflangs}}", hreflangs(page))
            .replace("{{jsonld}}", jsonld(lang) if page["key"] == "index" else "")
            .replace("{{nav}}", nav_html(lang, page["key"].split("/")[0])).replace("{{langs}}", lang_switch(page))
            .replace("{{home}}", f"/{lang}/").replace("{{site_name}}", SITE["nom"]).replace("{{hero}}", hero)
            .replace("{{content}}", body_html).replace("{{narrow}}", "narrow" if page["section"] == "journal" or meta.get("narrow") else "")
            .replace("{{footer_adresse}}", f"{SITE['adresse']['rue']}, {SITE['adresse']['ville']} {SITE['adresse']['cp']}, {SITE['adresse']['pays'][lang]}")
            .replace("{{footer_contact}}", f'<a href="https://wa.me/{wa}">WhatsApp</a> · <a href="tel:{c["telephone"].replace(" ","")}">{c["telephone"]}</a> · <a href="mailto:{c["email"]}">{c["email"]}</a>')
            .replace("{{footer_links}}", " · ".join(f'<a href="{s["url"]}" rel="noopener" target="_blank">{s["nom"]}</a>' for s in SITE["reseaux"]))
            .replace("{{menu_label}}", ui["menu"]).replace("{{year}}", str(datetime.date.today().year))
            .replace("{{footer_note}}", ui["footer_note"]).replace("{{skip}}", ui["skip"])
            .replace("{{body_class}}", "has-hero" if meta.get("hero_img") else "")
            .replace("{{wa_url}}", f"https://wa.me/{wa}?text={html.escape(ui['wa_message'])}").replace("{{wa_btn}}", ui["wa_btn"]))

def build():
    if OUT.exists(): shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT)
    load_pages()
    for p in PAGES:
        d = OUT / p["url"].strip("/"); d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(render_page(p), encoding="utf-8")
    # racine : détection de langue puis /fr/
    (OUT / "index.html").write_text(f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>{SITE["nom"]}</title>
<meta name="robots" content="noindex"><link rel="canonical" href="{SITE["url"]}/fr/">
<script>var l=(navigator.language||"fr").slice(0,2);location.replace("/"+(["fr","en","de"].indexOf(l)>-1?l:"fr")+"/")</script>
<meta http-equiv="refresh" content="0;url=/fr/"></head><body><a href="/fr/">Français</a> · <a href="/en/">English</a> · <a href="/de/">Deutsch</a></body></html>''', encoding="utf-8")
    today = datetime.date.today().isoformat()
    urls = []
    for p in PAGES:
        alts = "".join(f'<xhtml:link rel="alternate" hreflang="{q["lang"]}" href="{SITE["url"]}{q["url"]}"/>' for q in PAGES if q["key"] == p["key"])
        urls.append(f'<url><loc>{SITE["url"]}{p["url"]}</loc><lastmod>{today}</lastmod>{alts}</url>')
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemap.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">' + "".join(urls) + "</urlset>", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}/sitemap.xml\n", encoding="utf-8")
    print(f"{len(PAGES)} pages générées dans {OUT}")

if __name__ == "__main__":
    build()

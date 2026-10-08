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

ICONS = {
 "eau": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 12c2 0 2-2 4-2s2 2 4 2 2-2 4-2 2 2 4 2 2-2 4-2"/><path d="M2 17c2 0 2-2 4-2s2 2 4 2 2-2 4-2 2 2 4 2 2-2 4-2"/><path d="M2 7c2 0 2-2 4-2s2 2 4 2 2-2 4-2 2 2 4 2 2-2 4-2"/></svg>',
 "soleil": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
 "table": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 11h18l-2 7H5z"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
 "navette": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 17h14l2-6-4-1-3-4H9L6 10l-4 1z"/><circle cx="7.5" cy="17.5" r="1.5"/><circle cx="16.5" cy="17.5" r="1.5"/></svg>',
 "star": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="m12 2 3 7 7 .6-5.3 4.6L18.5 22 12 18l-6.5 4 1.8-7.8L2 9.6 9 9z"/></svg>',
 "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg>',
}

def phare():
    return next((s for s in SEJOURS["formules"] if s.get("phare")), SEJOURS["formules"][0])

NBSP = "\u00a0"

def prix_html(s, lang, cls="prix", note=True):
    ui = UI[lang]; t = s[lang]; prix = s["prix"]
    badge = "" if s.get("prix_confirme") or not note else f' <span class="todo">{ui["prix_indicatif"]}</span>'
    montant = prix["montant"].replace(" ", NBSP) + NBSP + prix["devise"]
    return f'<div class="{cls}"><strong>{montant}</strong><span>{inline(t["prix_detail"])}</span>{badge}</div>'

def render_confort(lang):
    ui = UI[lang]
    items = "".join(f'<div>{ICONS.get(c.get("icone",""), "")}<p><b>{inline(c["titre"])}</b><small>{inline(c["texte"])}</small></p></div>' for c in ui.get("confort", []))
    return f'<section class="confort" aria-label="{ui["confort_label"]}"><div class="wrap">{items}</div></section>' if items else ""

def render_phare(lang):
    ui = UI[lang]; s = phare(); t = s[lang]
    nights = re.search(r"\d+", t.get("sous_titre", "")); n = nights.group(0) if nights else ""
    days = "".join(f'<li><b>J{i}</b><span>{inline(d["texte"])}</span></li>' for i, d in enumerate(t["jours"], 1))
    media = placeholder(ui["phare_photo"], lang) if ui.get("phare_photo") else picture("bassins.jpg", t["titre"])
    return f'''<section class="phare-panel" id="phare">
  <div class="text">
    <div class="tags"><span class="eyebrow">{ui["phare_label"]}</span><span class="pill">{ui["phare_pill"].replace("{n}", n)}</span></div>
    <h2>{inline(t["titre"])}</h2>
    <p>{inline(t["intro"])}</p>
    <ol>{days}</ol>
    <div class="foot">{prix_html(s, lang)}<a class="btn btn-light" href="{page_url(lang,"sejours")}#{s["id"]}">{ui["phare_btn"]}</a></div>
  </div>
  <div class="media">{media}</div>
</section>'''

def render_sejours(lang):
    ui = UI[lang]; out = ['<div class="compare">']
    for s in SEJOURS["formules"]:
        t = s[lang]; ph = s.get("phare")
        tag = f'<span class="tag">{ui["compare_tag"]}</span>' if ph else ""
        cls = ' class="phare"' if ph else ""
        out.append(f'<a href="#{s["id"]}"{cls}><span class="tag-row">{tag}</span><small>{inline(t["sous_titre"])}</small><h3>{inline(t["titre"])}</h3>{prix_html(s, lang, note=False)}<p>{inline(t["intro"].split(". ")[0])}.</p></a>')
    n = SEJOURS["nuit_seule"]; tn = n[lang]
    out.append(f'<a href="#nuit" class="nuit-c"><span class="tag-row"></span><small>{ui["nuit_eyebrow"]}</small><h3>{inline(tn["titre"])}</h3>{prix_html(n, lang, note=False)}<p>{inline(tn["texte"].split(". ")[0])}.</p></a>')
    out.append(f'</div><p class="compare-note">{ui["compare_note"]}</p><div class="sejours">')
    for s in SEJOURS["formules"]:
        t = s[lang]
        days = "".join(f"<li><strong>{inline(d['titre'])}</strong><span>{inline(d['texte'])}</span></li>" for d in t["jours"])
        inc = "".join(f"<li>{inline(x)}</li>" for x in t["inclus"])
        pas = "".join(f"<li>{inline(x)}</li>" for x in t["pas_pour"])
        out.append(f'''<article class="sejour{' phare' if s.get('phare') else ''}" id="{s['id']}">
  <div>
    <div class="sejour-head"><div class="eyebrow">{inline(t['sous_titre'])}</div><h2>{inline(t['titre'])}</h2></div>
    <p class="lead">{inline(t['intro'])}</p>
    <h3>{ui['chaque_jour']}</h3><ol class="jours">{days}</ol>
  </div>
  <aside class="sejour-aside">
    {prix_html(s, lang)}
    <div class="block"><h3>{ui['inclus']}</h3><ul class="check">{inc}</ul></div>
    <div class="block"><h3>{ui['pas_pour']}</h3><ul class="non">{pas}</ul></div>
    <a class="btn btn-primary" href="{page_url(lang,'reserver')}?sejour={s['id']}">{ui['reserver_ce_sejour']}</a>
  </aside>
</article>''')
    out.append("</div>")
    return "\n".join(out)

def render_avis(lang):
    ui = UI[lang]; out = ['<div class="notes">']
    for src in AVIS["sources"]:
        if not src.get("note"): continue
        out.append(f'<a class="note" href="{src.get("url","#")}" target="_blank" rel="noopener"><em>{src["nom"]} ·</em><strong>{src["note"]}</strong><span>{src["sur"]}</span></a>')
    out.append('</div><div class="quotes">')
    for a in AVIS["extraits"]:
        out.append(f'<blockquote class="quote" lang="{a["lang"]}"><p>« {inline(a["texte"])} »</p><footer><b>{inline(a["auteur"])}</b> · {a["source"]}, {a["date"]}</footer></blockquote>')
    out.append("</div>")
    return "\n".join(out)

def render_reserver(lang):
    ui = UI[lang]; c = SITE["contact"]
    wa = re.sub(r"\D", "", c["whatsapp"])
    picks = []
    for s in SEJOURS["formules"] + [dict(SEJOURS["nuit_seule"], id="nuit")]:
        t = s[lang]; prix = s["prix"]
        picks.append(f'<label class="pick"><input type="radio" name="sejour" value="{s["id"]}" data-titre="{html.escape(t["titre"])}" data-prix="{prix["montant"]} {prix["devise"]}" data-detail="{html.escape(t["prix_detail"])}"{" checked" if s.get("phare") else ""}><small>{inline(t.get("sous_titre", ui["nuit_eyebrow"]))}</small><b>{inline(t["titre"])}</b><i>{prix["montant"]} {prix["devise"]}</i></label>')
    pay = "".join(f"<li>{inline(p[lang])}</li>" for p in SITE["paiement"])
    strings = {k: ui[k] for k in ["recap_a_preciser", "recap_du", "recap_oui", "recap_non", "preview_text", "preview_nom", "adulte", "adultes", "enfant", "enfants", "f_navette", "f_adultes", "f_enfants"]}
    ph = phare()
    return f'''<div class="reserver">
<form class="form" action="{SITE['form_action']}" method="POST" name="reservation" data-netlify="true" data-wa="{wa}" data-mail="{c['email']}" data-subject="{html.escape(ui['f_subject'])}" data-lang="{lang}" data-ui='{html.escape(json.dumps(strings, ensure_ascii=False), quote=True)}'>
  <input type="hidden" name="lang" value="{lang}">
  <fieldset><legend>{ui['f_sejour_legend']}</legend><div class="picks">{"".join(picks)}</div></fieldset>
  <fieldset><legend>{ui['f_dates_legend']}</legend>
    <div class="row r4">
      <label>{ui['f_arrivee']}<input type="date" name="arrivee" required></label>
      <label>{ui['f_depart']}<input type="date" name="depart" required></label>
      <label>{ui['f_adultes']}<span class="stepper"><button type="button" data-step="-1" aria-label="{ui['f_moins']}">−</button><output name="adultes_out">2</output><button type="button" data-step="1" aria-label="{ui['f_plus']}">+</button><input type="hidden" name="adultes" value="2" data-min="1" data-max="12"></span></label>
      <label>{ui['f_enfants']}<span class="stepper"><button type="button" data-step="-1" aria-label="{ui['f_moins']}">−</button><output name="enfants_out">0</output><button type="button" data-step="1" aria-label="{ui['f_plus']}">+</button><input type="hidden" name="enfants" value="0" data-min="0" data-max="10"></span></label>
    </div>
    <label class="chk"><input type="checkbox" name="navette" value="1" checked>{ui['f_navette']}</label>
  </fieldset>
  <fieldset><legend>{ui['f_vous_legend']}</legend>
    <div class="row"><label>{ui['f_nom']}<input type="text" name="nom" required autocomplete="name"></label><label>{ui['f_tel']}<input type="tel" name="tel" autocomplete="tel"></label></div>
    <label>{ui['f_email']}<input type="email" name="email" required autocomplete="email"></label>
    <label>{ui['f_message']}<textarea name="message" rows="3"></textarea></label>
  </fieldset>
  <div class="actions"><button class="btn btn-accent" type="submit">{ICONS["arrow"]}{ui['f_envoyer']}</button><button class="btn btn-ghost" type="button" data-mail>{ui['f_mail_btn']}</button></div>
  <p class="small">{ui['f_note']}</p>
</form>
<div class="reserver-side">
  <div class="recap"><div class="media">{picture("piscine-soir.jpg", "")}</div><div class="text">
    <span class="eyebrow">{ui['recap_title']}</span>
    <dl><div><dt>{ui['recap_sejour']}</dt><dd data-recap="sejour">{inline(ph[lang]['titre'])}</dd></div><div><dt>{ui['recap_dates']}</dt><dd data-recap="dates">{ui['recap_a_preciser']}</dd></div><div><dt>{ui['recap_personnes']}</dt><dd data-recap="personnes">2 {ui['adultes']}</dd></div><div><dt>{ui['recap_navette']}</dt><dd data-recap="navette">{ui['recap_oui']}</dd></div></dl>
    <div class="prix"><strong data-recap="prix">{ph['prix']['montant']} {ph['prix']['devise']}</strong><span data-recap="detail">{inline(ph[lang]['prix_detail'])}</span><span> · {ui['recap_prix_note']}</span></div>
  </div></div>
  <div class="preview"><span class="eyebrow">{ui['preview_title']}</span><p data-preview></p></div>
  <p class="small">{ui['direct']} <a href="https://wa.me/{wa}?text={html.escape(ui['wa_message'])}" target="_blank" rel="noopener">WhatsApp</a> · <a href="tel:{c['telephone'].replace(' ','')}">{c['telephone']}</a> · <a href="mailto:{c['email']}">{c['email']}</a></p>
  <h3>{ui['paiement']}</h3><ul class="check">{pay}</ul>
  <h3>{ui['disponibilites']}</h3>
  <div id="cal" data-dispo='{json.dumps(DISPO, ensure_ascii=False)}' data-lang="{lang}"></div>
  <p class="small">{ui['cal_note']}</p>
</div></div>'''

def render_nuit(lang):
    ui = UI[lang]; n = SEJOURS["nuit_seule"]; t = n[lang]
    return (f'<div class="nuit" id="nuit"><div class="media">{picture("chambre-2.jpg", t["titre"])}</div><div class="text"><div class="eyebrow">{ui["nuit_eyebrow"]}</div><h3>{inline(t["titre"])}</h3><p>{inline(t["texte"])}</p>'
            f'{prix_html(n, lang)}<a class="btn btn-primary" href="{page_url(lang,"reserver")}?sejour=nuit">{ui["f_sejour_libre_btn"]}</a></div></div>')

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
    lines = body.split("\n"); out = []; i = 0; para = []; mode = None; block = []; gallery_cols = ""; last_cards = None
    def flush():
        if para: out.append(f"<p>{inline(' '.join(para))}</p>"); para.clear()
    def close_block():
        nonlocal mode, block, last_cards
        if mode in ("cards", "facts"):
            items = []; cur = None
            for l in block:
                if l.startswith("### "):
                    cur = {"t": l[4:], "b": []}; items.append(cur)
                elif cur is not None and l.strip():
                    cur["b"].append(l.strip())
            cls = "cards cards-text" if mode == "cards" else "facts"
            if mode == "cards": last_cards = (len(out), items)
            out.append(f'<div class="{cls}">' + "".join(
                (f'<div class="card"><div class="body">' if mode=="cards" else f'<div class="fact"><div class="num">{n:02d}</div>') +
                f"<h3>{inline(it['t'])}</h3>" + "".join(f"<p>{inline(x)}</p>" for x in it["b"]) +
                ("</div></div>" if mode=="cards" else "</div>") for n, it in enumerate(items, 1)) + "</div>")
        elif mode == "gallery":
            cls = f" g{gallery_cols}" if gallery_cols else ""
            if last_cards and last_cards[0] == len(out) - 1 and len(last_cards[1]) == len(block):
                # tuiles texte suivies d'autant de photos : on fusionne en tuiles photo
                out[-1] = '<div class="cards-photo">' + "".join(
                    f'<div class="card"><div class="media">{img}</div><div class="body"><h3>{inline(it["t"])}</h3>' + "".join(f"<p>{inline(x)}</p>" for x in it["b"]) + "</div></div>"
                    for it, img in zip(last_cards[1], block)) + "</div>"
            else:
                out.append(f'<div class="gallery{cls}">' + "".join(block) + "</div>")
            last_cards = None
        mode = None; block = []
    while i < len(lines):
        l = lines[i]; s = l.strip()
        m = re.match(r"\{\{(\w+)(?::\s*(.*?))?\}\}$", s)
        if m and m.group(1) in ("cards", "facts", "gallery"):
            flush(); mode = m.group(1); block = []; gallery_cols = (m.group(2) or "").strip(); i += 1; continue
        if re.match(r"\{\{/(cards|facts|gallery)\}\}$", s):
            flush(); close_block(); i += 1; continue
        if s == "{{split}}":
            flush(); j = i + 1; inner = []
            while j < len(lines) and lines[j].strip() != "{{/split}}": inner.append(lines[j]); j += 1
            parts = md_to_html("\n".join(inner), lang, pages).split("\n")
            media = [x for x in parts if x.startswith(('<div class="gallery', '<picture', '<div class="mock', '<div class="ph'))]
            text = [x for x in parts if x not in media]
            out.append(f'<section class="split"><div class="text">{"".join(text)}</div><div class="media">{"".join(media)}</div></section>')
            i = j + 1; continue
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
            elif kind == "phare": h = render_phare(lang)
            elif kind == "dates":
                h = '<div class="eau-dates">' + "".join(f"<div><b>{inline(x.split('~')[0])}</b><small>{inline(x.split('~')[1] if '~' in x else '')}</small></div>" for x in parts) + "</div>"
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
    cta = (f'<div class="hero-cta"><a class="btn btn-primary" href="{page_url(lang,"sejours")}">{ui["voir_sejours"]}{ICONS["arrow"]}</a>'
           f'<a class="btn btn-ghost" href="{page_url(lang,"reserver")}">{ui["nav"]["reserver_long"]}</a></div>') if page["key"] == "index" else ""
    if MAQUETTE.get("actif") and MAQUETTE.get("hero", {}).get(page["key"]):
        meta = dict(meta, hero_img=MAQUETTE["hero"][page["key"]], hero_mock=True)
    if meta.get("hero_img"):
        strip = "".join(f"<span>{inline(x)}</span>" for x in ui.get("strip", [])) if page["key"] == "index" else ""
        strip_html = f'<div class="strip">{strip}</div>' if strip else ""
        badge = f'<span class="badge">{inline(ui["hero_badge"])}</span>' if page["key"] == "index" and ui.get("hero_badge") else ""
        g = next((x for x in AVIS["sources"] if x.get("note") and x["nom"].lower().startswith("google")), None)
        rating = f'<div class="rating"><i>{ICONS["star"]*5}</i><span><strong>{g["note"]} {g["sur"]}</strong> {ui["rating_on"]}</span></div>' if g and page["key"] == "index" else ""
        hero = f'<header class="hero"><div class="hero-media{" mock" if meta.get("hero_mock") else ""}" data-badge="{ui["mock_badge"]}">{picture(meta["hero_img"], meta.get("hero_alt",""), sizes="100vw", lazy=False)}</div><div class="wrap">{badge}<h1>{inline(meta["title"])}</h1><div class="hero-side">{tag}{cta}{rating}</div></div>{strip_html}</header>'
    elif meta.get("hero_photo"):
        hero = f'<header class="hero hero-ph"><div class="hero-media">{placeholder(meta["hero_photo"], lang)}</div><div class="wrap"><h1>{inline(meta["title"])}</h1>{tag}</div></header>'
    else:
        hero = f'<header class="page-head"><div class="wrap"><h1>{inline(meta["title"])}</h1>{tag_lead}</div></header>'
    if page["section"] == "journal":
        hero = f'<header class="page-head"><div class="wrap"><div class="eyebrow">{meta.get("date","")}</div><h1>{inline(meta["title"])}</h1><p class="lead">{inline(meta.get("description",""))}</p></div></header>'
    c = SITE["contact"]; wa = re.sub(r"\D", "", c["whatsapp"])
    ph = phare(); pt = ph[lang]
    footer_nav = "".join(f'<a href="{page_url(lang,k)}">{ui["nav"][k]}</a>' for k in ["maison", "sejours", "vallee", "acces", "avis"])
    return (BASE.replace("{{lang}}", lang).replace("{{title}}", html.escape(meta["title"].replace("*", "")) + " · " + SITE["nom"])
            .replace("{{brand_tag}}", ui["brand_tag"]).replace("{{confort}}", render_confort(lang) if page["key"] == "index" else "")
            .replace("{{band_title}}", ui["band_title"]).replace("{{band_text}}", ui["band_text"]).replace("{{band_btn}}", ui["band_btn"])
            .replace("{{reserver_url}}", page_url(lang, "reserver")).replace("{{footer_site}}", ui["footer_site"]).replace("{{footer_nav}}", footer_nav)
            .replace("{{footer_contact_title}}", ui["footer_contact_title"]).replace("{{footer_follow}}", ui["footer_follow"])
            .replace("{{sticky_label}}", ui["sticky_label"].replace("{titre}", pt["titre"])).replace("{{sticky_price}}", ui["sticky_price"].replace("{prix}", f'{ph["prix"]["montant"]} {ph["prix"]["devise"]}')).replace("{{sticky_btn}}", ui["sticky_btn"])
            .replace("{{description}}", html.escape(meta.get("description", "")))
            .replace("{{canonical}}", SITE["url"] + page["url"]).replace("{{hreflangs}}", hreflangs(page))
            .replace("{{jsonld}}", jsonld(lang) if page["key"] == "index" else "")
            .replace("{{nav}}", nav_html(lang, page["key"].split("/")[0])).replace("{{langs}}", lang_switch(page))
            .replace("{{home}}", f"/{lang}/").replace("{{site_name}}", SITE["nom"]).replace("{{hero}}", hero)
            .replace("{{content}}", body_html).replace("{{narrow}}", "narrow" if page["section"] == "journal" or meta.get("narrow") else "")
            .replace("{{footer_adresse}}", f"{SITE['adresse']['rue']}, {SITE['adresse']['ville']} {SITE['adresse']['cp']}, {SITE['adresse']['pays'][lang]}")
            .replace("{{footer_contact}}", f'<a href="tel:{c["telephone"].replace(" ","")}">{c["telephone"]}</a><a href="https://wa.me/{wa}">WhatsApp</a><a href="mailto:{c["email"]}">{c["email"]}</a>')
            .replace("{{footer_links}}", "".join(f'<a href="{s["url"]}" rel="noopener" target="_blank">{s["nom"]}</a>' for s in SITE["reseaux"]))
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

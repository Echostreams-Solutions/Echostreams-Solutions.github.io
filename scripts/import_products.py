"""Generate _products/*.md from the spec CSV, enriched with the Shopify metafield export.

Usage (from site/):  python scripts/import_products.py
Re-running overwrites the generated files in _products/ (example-product.md is left alone).
"""
import csv, html, json, re, urllib.parse
from collections import Counter
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
DATA = SITE / "_source-data"
OUT = SITE / "_products"
SPEC = DATA / "Product-Specification - server.csv"
EXPORT = next(DATA.glob("*export_products*.csv"))

LABELS = {"Driver Bays": "Drive Bays"}
SECTIONS = {"1": "System", "2": "System", "3": "I/O", "5": "Power", "7": "Environment", "8": "Physical"}

def norm(s): return re.sub(r"[^a-z0-9]", "", s.lower())
def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

# model -> full Shopify title (export has one row per metafield); handle -> model
full_titles, handle_model, export_meta = {}, {}, {}
with open(EXPORT, encoding="utf-8-sig", newline="") as f:
    for r in csv.DictReader(f):
        export_meta.setdefault(r["Product handle"], {})[r["Metafield key"]] = r["Metafield value"]
        if r["Metafield key"] == "title":
            full_titles[norm(r["Metafield value"])] = r["Product title"].strip()
            handle_model[r["Product handle"]] = norm(r["Metafield value"])

# Product images live in assets/img/<shopify-handle>/*.png. A folder belongs to a model if the export
# maps its handle to that model, or (fallback) the handle starts with the model's slug.
# Product descriptions (Shopify "Body (HTML)") come from the products export, keyed by handle.
body_by_handle, export_handles = {}, set()
for pe in SITE.glob("_source-data/products_export*.csv"):
    with open(pe, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            export_handles.add(r["Handle"])
            if r["Body (HTML)"].strip():
                body_by_handle[r["Handle"]] = r["Body (HTML)"].strip()

def clean_body(html):
    html = re.sub(r'\s(?:id|class|style)="[^"]*"', "", html)  # drop theme animation classes (mk-animate-element hides text)
    assert "{{" not in html and "{%" not in html
    return html

# Download links: metafield key (a resource name such as "DS_FlacheSAN1L-U5_E") -> URL, or a comma-separated
# list of URLs and/or other keys. Resolution is case/punctuation-insensitive; a trailing "_E" (English) variant
# is tried too. Names that cannot be resolved stay plain text on the product page.
downloads = {}
for dm in SITE.glob("_source-data/download-metafields*.csv"):
    with open(dm, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            downloads[r["Metafield key"].strip()] = r["Metafield value"].strip()
dl_norm = {}
for k in downloads: dl_norm.setdefault(norm(k), k)

def dl_key(name):
    name = name.strip()
    if name in downloads: return name
    return dl_norm.get(norm(name)) or dl_norm.get(norm(name + "_E"))

def resolve_links(name, seen=()):
    k = dl_key(name)
    if not k or k in seen: return []
    out = []
    for part in (x.strip() for x in downloads[k].split(",")):
        if part.startswith("http"): out.append({"label": k, "url": part})
        elif part: out += resolve_links(part, seen + (k,))
    return out

def resource_links(name):
    links = []
    for token in name.split(","):
        for l in resolve_links(token):
            if l not in links: links.append(l)
    return links

ECHO = "https://echostreams.blob.core.windows.net/"

def echostreams_datasheet(model):
    """Preferred data sheet for a model: the copy hosted on echostreams.blob.core.windows.net (container 'datasheet').
    Priority: DS_<model>_E (current English sheet), then DS_<model>, then <model>."""
    for cand in ("DS" + model + "E", "DS" + model, model):
        k = dl_norm.get(norm(cand))
        if k and downloads[k].startswith(ECHO + "datasheet/"):
            return {"label": k, "url": downloads[k]}
    return None

_ov = SITE / "_source-data" / "resource_overrides.json"
OVERRIDES = {k.lower(): v for k, v in json.loads(_ov.read_text(encoding="utf-8")).items() if not k.startswith("_")} if _ov.exists() else {}

IMG_ROOT = SITE / "assets" / "img"
img_dirs = sorted(d.name for d in IMG_ROOT.iterdir() if d.is_dir())
known_handles = sorted(export_handles)  # only products listed in products_export_*.csv are published

def image_key(name):
    n = name.lower()
    return (re.sub(r"^new_", "", n), )

def images_for(model):
    ms, mn = slug(model), norm(model)
    dirs = [d for d in known_handles if handle_model.get(d) == mn]
    dirs += [d for d in known_handles if d not in dirs and handle_model.get(d) not in all_models and (d == ms or d.startswith(ms + "-"))]
    out = []
    for d in dirs:
        if not (IMG_ROOT / d).is_dir(): continue
        files = sorted((p.name for p in (IMG_ROOT / d).iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")), key=image_key)
        out += [f"/assets/img/{d}/{f}" for f in files]
    return dirs, out

used_dirs = set()

def export_value(handles, col):
    """Spec value for a numbered column from the Shopify export (entities decoded), '' if none."""
    for h in handles:
        v = export_meta.get(h, {}).get(col, "").strip()
        if v: return html.unescape(v)
    return ""
with open(SPEC, encoding="utf-8-sig", newline="") as f:
    all_models = {norm(r["title"]) for r in csv.DictReader(f)}

for old in OUT.glob("*.md"):
    if old.name != "example-product.md":
        old.unlink()

counts, no_export, no_images, no_body, unresolved, skipped, replaced, filled = Counter(), [], [], [], [], [], [], []
with open(SPEC, encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))

for i, r in enumerate(rows, 1):
    model = r["title"].strip()
    series = r["product series"].strip()
    family = series.split("-")[0].lower()
    cpu = r["processor"].strip().lower()
    sections, order = {}, []
    resources = []
    handles = images_for(model)[0]
    for col, val in r.items():
        val = (val or "").strip()
        m = re.match(r"(\d{3})_(.+)$", col)
        if m and not m.group(1).endswith("00"):
            ev = export_value(handles, col)
            if ev and (not val or (len(ev) > len(val) and ev.startswith(val))):  # blank or cut off in the spec sheet
                filled.append((model, col, val, ev))
                val = ev
        if m and val:
            num, label = m.groups()
            if num.endswith("00"):
                continue  # section header column, not a spec row
            title = SECTIONS.get(num[0])
            if title is None:
                continue
            if title not in sections:
                sections[title] = []
                order.append(title)
            sections[title].append([LABELS.get(label, label), val])
        elif col.startswith("resource_") and val:
            links = resource_links(val)
            res = {"label": col[len("resource_"):], "name": val}
            if res["label"] == "Data Sheet" and links and all(not l["url"].startswith(ECHO) for l in links):
                better = echostreams_datasheet(model)  # replace an old premio.blob copy with the echostreams.blob one
                if better:
                    links, res["name"] = [better], better["label"]
                    replaced.append((model, val, better["label"]))
            if not links:
                unresolved.append((model, col[len("resource_"):], val))  # no URL known: not published
                continue
            res["links"] = links
            resources.append(res)
    for label, url in OVERRIDES.get(model.lower(), {}).items():
        name = urllib.parse.unquote(url.rsplit("/", 1)[-1]).rsplit(".", 1)[0]
        resources = [r for r in resources if r["label"] != label]
        entry = {"label": label, "name": name, "links": [{"label": name, "url": url}]}
        resources.insert(0, entry) if label == "Data Sheet" else resources.append(entry)
    fm = {
        "title": model,
        "family": family,
        "cpu": cpu,
        "series": series,
        "order": i,
    }
    dirs, imgs = images_for(model)
    if not dirs:
        skipped.append(model)
        continue
    body = next((clean_body(body_by_handle[d]) for d in dirs if d in body_by_handle), "")
    used_dirs.update(dirs)
    fm["image"] = imgs[0] if imgs else "/assets/img/no-image.svg"
    if len(imgs) > 1: fm["images"] = imgs
    if not imgs: no_images.append(model)
    if not body: no_body.append(model)
    ft = full_titles.get(norm(model))
    if ft: fm["full_title"] = ft
    else: no_export.append(model)
    fm["spec_sections"] = [{"title": t, "rows": sections[t]} for t in sorted(order, key=lambda t: list(SECTIONS.values()).index(t))]
    fm["resources"] = resources
    lines = ["---"] + [f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in fm.items()] + ["---", "", body, ""]
    (OUT / f"{slug(model)}.md").write_text("\n".join(lines), encoding="utf-8")
    counts[(family, cpu)] += 1

print(f"wrote {len(rows) - len(skipped)} products; skipped (not in products export): {skipped}")
for k, n in sorted(counts.items()): print(" ", k, n)
print("no Shopify export match:", no_export)
print("no images:", no_images)
print("no body:", [m for m in no_body])
print("handles matching no product:", [d for d in known_handles if d not in used_dirs])
print(f"spec cells filled from the Shopify export (blank/truncated in the spec sheet): {len(filled)}")
for m_, c_, o_, n_ in filled: print(f"   {m_} {c_}: {o_!r} -> {n_[:70]!r}")
print(f"data sheets moved to echostreams.blob: {len(replaced)}")
print(f"downloads dropped (no link): {len(unresolved)}")
for k, n in Counter((l, v) for _, l, v in unresolved).most_common(): print("  ", k, n)

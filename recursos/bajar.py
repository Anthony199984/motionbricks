"""Baja recursos GRATIS con licencia CC0 para los videos de Antonydfilms (lo corre GitHub Actions, que sí tiene internet).

Lee recursos/pedido.json:
{
  "catalogo": true,                                   # guarda la lista de Poly Haven (modelos, HDRI, texturas) para elegir
  "polyhaven": [{"id": "brick_wall_001", "res": "1k"}, ...],   # el tipo (modelo/hdri/textura) se averigua solo
  "urls": [{"url": "https://...", "destino": "carpeta/archivo.ext"}]       # descargas directas (CC0 verificadas)
}
Todo queda en recursos/out/ y se sube a la rama `recursos`. Poly Haven: CC0, sin créditos obligatorios.
"""
import json, os, re, sys, time, urllib.request, urllib.parse

UA = {"User-Agent": "Antonydfilms-recursos/1.0 (GitHub Actions)"}
OUT = "recursos/out"
MAX_MB = 90                                           # GitHub rechaza archivos de más de 100 MB
informe = {"bajados": [], "errores": [], "saltados": []}


def leer(url, intentos=3):
    for k in range(intentos):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                return r.read()
        except Exception as e:                        # noqa: BLE001
            if k == intentos - 1: raise
            time.sleep(3 * (k + 1))


def guardar(url, destino):
    ruta = os.path.join(OUT, destino)
    if os.path.exists(ruta): return ruta
    datos = leer(url)
    if len(datos) > MAX_MB * 2**20:
        informe["saltados"].append({"url": url, "mb": round(len(datos) / 2**20, 1)}); return None
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    open(ruta, "wb").write(datos)
    informe["bajados"].append({"destino": destino, "mb": round(len(datos) / 2**20, 2)})
    return ruta


def catalogo():
    d = json.loads(leer("https://api.polyhaven.com/assets"))
    tipos = {0: "hdri", 1: "textura", 2: "modelo"}
    cat = {k: {"nombre": v.get("name"), "tipo": tipos.get(v.get("type"), v.get("type")), "categorias": v.get("categories"),
               "tags": v.get("tags"), "dimensiones_mm": v.get("dimensions"), "polys": v.get("polycount")} for k, v in d.items()}
    os.makedirs(OUT, exist_ok=True)
    json.dump(cat, open(f"{OUT}/catalogo_polyhaven.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print("catálogo Poly Haven:", len(cat), "recursos")


def _incluir(archivo, carpeta):
    """Baja un archivo de Poly Haven y sus 'include' (texturas y .bin de un glTF) con sus rutas relativas."""
    guardar(archivo["url"], f"{carpeta}/{os.path.basename(urllib.parse.urlparse(archivo['url']).path)}")
    for rel, sub in (archivo.get("include") or {}).items():
        guardar(sub["url"], f"{carpeta}/{rel}")


def polyhaven(item):
    i, res = item["id"], item.get("res", "1k")
    info = json.loads(leer(f"https://api.polyhaven.com/info/{i}"))
    f = json.loads(leer(f"https://api.polyhaven.com/files/{i}"))
    t = info.get("type")
    if t == 0:                                        # HDRI
        h = f["hdri"].get(res) or f["hdri"][sorted(f["hdri"])[0]]
        guardar(h["hdr"]["url"], f"hdri/{i}_{res}.hdr")
    elif t == 1:                                      # textura PBR: mapas sueltos en jpg
        for mapa in ("Diffuse", "nor_gl", "Rough", "AO", "Displacement", "arm"):
            if mapa in f and res in f[mapa]:
                fmt = f[mapa][res].get("jpg") or f[mapa][res].get("png")
                if fmt: guardar(fmt["url"], f"texturas/{i}/{i}_{mapa}_{res}.{ 'jpg' if 'jpg' in f[mapa][res] else 'png'}")
    else:                                             # modelo: glTF con sus texturas
        g = f.get("gltf", {}); r = g.get(res) or g.get("1k") or g[sorted(g)[0]]
        _incluir(r["gltf"], f"modelos/{i}")
    informe.setdefault("info", {})[i] = {"nombre": info.get("name"), "autores": info.get("authors"), "licencia": "CC0 (Poly Haven)"}


# ------------------------------------------------------------------ Sketchfab (búsqueda pública) + Objaverse (descarga sin cuenta)
def sketchfab_buscar(b):
    """Busca en Sketchfab (API pública, sin cuenta) y guarda candidatos + miniaturas para elegir."""
    q = b["q"]; params = {"type": "models", "q": q, "downloadable": "true", "count": 24, "sort_by": b.get("orden", "-likeCount")}
    if b.get("animado"): params["animated"] = "true"
    url = "https://api.sketchfab.com/v3/search?" + urllib.parse.urlencode(params)
    res = []
    for _ in range(b.get("paginas", 1)):                 # varias páginas (la API da 24 por página)
        d = json.loads(leer(url)); res += d.get("results", []); url = d.get("next")
        if not url: break
    if b.get("solo_objaverse"):                         # solo los que se pueden bajar sin cuenta (están en Objaverse)
        rutas = objaverse_rutas(); res = [m for m in res if m["uid"] in rutas]
    out = []
    for m in res[:b.get("max", 40)]:
        lic = (m.get("license") or {}).get("label") or (m.get("license") or {}).get("slug")
        th = sorted((m.get("thumbnails") or {}).get("images", []), key=lambda i: abs(i.get("width", 0) - 256))
        c = dict(uid=m["uid"], nombre=m.get("name"), autor=(m.get("user") or {}).get("username"), licencia=lic,
                 animaciones=m.get("animationCount"), caras=m.get("faceCount"), url=m.get("viewerUrl"))
        if th:
            try:
                guardar(th[0]["url"], f"miniaturas/{b['clave']}/{m['uid']}.jpg"); c["miniatura"] = f"miniaturas/{b['clave']}/{m['uid']}.jpg"
            except Exception as e:                    # noqa: BLE001
                c["miniatura_error"] = repr(e)[:100]
        out.append(c)
    informe.setdefault("sketchfab", {})[b["clave"]] = out
    print("sketchfab", q, len(out))


_RUTAS = {}
def objaverse_rutas():
    if not _RUTAS:
        import gzip
        d = leer("https://huggingface.co/datasets/allenai/objaverse/resolve/main/object-paths.json.gz")
        _RUTAS.update(json.loads(gzip.decompress(d)))
    return _RUTAS


def objaverse_bajar(it):
    """Baja el .glb de un modelo de Sketchfab desde Objaverse (Hugging Face, sin cuenta) por su uid."""
    r = objaverse_rutas().get(it["uid"])
    if not r:
        informe["errores"].append({"uid": it["uid"], "error": "no está en Objaverse"}); return
    guardar(f"https://huggingface.co/datasets/allenai/objaverse/resolve/main/{r}", f"objaverse/{it['nombre']}.glb")
    informe.setdefault("objaverse", {})[it["nombre"]] = it


# ------------------------------------------------------------------ sonidos de Wikimedia Commons (sin cuenta)
def commons_buscar(b):
    """Busca audios en Wikimedia Commons y baja los cortos (licencias libres: CC0, CC BY, CC BY-SA, dominio público)."""
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search", "gsrnamespace": 6, "gsrlimit": b.get("n", 15),
        "gsrsearch": b["q"] + " filetype:audio", "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata"})
    d = json.loads(leer(api)); out = []
    for pg in (d.get("query", {}).get("pages", {}) or {}).values():
        ii = (pg.get("imageinfo") or [{}])[0]; em = ii.get("extmetadata", {})
        c = dict(titulo=pg.get("title"), url=ii.get("url"), mb=round(ii.get("size", 0)/2**20, 2), mime=ii.get("mime"),
                 licencia=(em.get("LicenseShortName") or {}).get("value"), autor=re.sub("<[^>]+>", "", (em.get("Artist") or {}).get("value", ""))[:80],
                 pagina=ii.get("descriptionurl"))
        if c["url"] and c["mb"] <= b.get("max_mb", 4):
            ext = os.path.splitext(urllib.parse.urlparse(c["url"]).path)[1]
            nombre = re.sub(r"[^A-Za-z0-9_.-]+", "_", pg.get("title", "x").replace("File:", ""))[:70]
            try:
                guardar(c["url"], f"sonidos/{b['clave']}/{nombre}" + ("" if nombre.endswith(ext) else ext)); c["archivo"] = f"sonidos/{b['clave']}/{nombre}"
            except Exception as e:                    # noqa: BLE001
                c["error"] = repr(e)[:100]
        out.append(c)
    informe.setdefault("commons", {})[b["clave"]] = out
    print("commons", b["q"], len(out))


# ------------------------------------------------------------------ sonidos de Mixkit (licencia gratis de Mixkit, sin créditos obligatorios)
def mixkit(b):
    """Lee una página de categoría o búsqueda de mixkit.co y baja los efectos (mp3 de vista previa, que es el sonido entero)."""
    html = leer(b["pagina"]).decode("utf-8", "ignore")
    urls = list(dict.fromkeys(re.findall(r"https://assets\.mixkit\.co/[^\"'\s]+?\.mp3", html)))[:b.get("max", 12)]
    titulos = re.findall(r'<h2[^>]*class="[^"]*item-grid-card__title[^"]*"[^>]*>\s*([^<]+)', html)
    out = []
    for n, u in enumerate(urls):
        tit = titulos[n].strip() if n < len(titulos) else os.path.basename(u)
        nombre = re.sub(r"[^A-Za-z0-9_.-]+", "_", tit)[:50] + "_" + os.path.basename(u)
        c = dict(titulo=tit, url=u, licencia="Mixkit Sound Effects Free License")
        try:
            guardar(u, f"sonidos/{b['clave']}/{nombre}"); c["archivo"] = f"sonidos/{b['clave']}/{nombre}"
        except Exception as e:                         # noqa: BLE001
            c["error"] = repr(e)[:100]
        out.append(c); time.sleep(.5)
    informe.setdefault("mixkit", {})[b["clave"]] = out
    print("mixkit", b["pagina"], len(out))


# ------------------------------------------------------------------ sonidos de Freesound (vistas previas públicas, sin cuenta)
def freesound_buscar(b):
    """Busca en freesound.org (página pública) y baja las vistas previas mp3 (128 kbps) de los primeros resultados,
    con el autor y la licencia de la página de cada sonido."""
    q = urllib.parse.urlencode({"q": b["q"], "f": b.get("filtro", "duration:[0.3 TO 20]"), "s": b.get("orden", "Rating highest first")})
    html = leer("https://freesound.org/search/?" + q).decode("utf-8", "ignore")
    ids = list(dict.fromkeys(re.findall(r'/people/([^/"]+)/sounds/(\d+)/', html)))[:b.get("max", 8)]
    mp3s = re.findall(r'https://cdn\.freesound\.org/previews/\d+/(\d+)_\d+-(?:hq|lq)\.mp3', html)
    urls = dict()
    for m in re.finditer(r'(https://cdn\.freesound\.org/previews/\d+/(\d+)_\d+-hq\.mp3)', html): urls.setdefault(m.group(2), m.group(1))
    out = []
    for usuario, sid in ids:
        c = dict(id=sid, autor=usuario, pagina=f"https://freesound.org/people/{usuario}/sounds/{sid}/")
        try:
            pg = leer(c["pagina"]).decode("utf-8", "ignore")
            t = re.search(r'<meta property="og:title" content="([^"]+)"', pg); c["titulo"] = t.group(1) if t else sid
            lic = re.search(r'creativecommons\.org/(publicdomain/zero|licenses/[a-z-]+)/', pg); c["licencia"] = lic.group(1) if lic else "?"
            u = urls.get(sid) or (re.search(r'(https://cdn\.freesound\.org/previews/\d+/' + sid + r'_\d+-hq\.mp3)', pg) or [None, None])[1]
            if u:
                nombre = re.sub(r"[^A-Za-z0-9_.-]+", "_", c["titulo"])[:50] + f"_{sid}.mp3"
                guardar(u, f"sonidos/{b['clave']}/{nombre}"); c["archivo"] = f"sonidos/{b['clave']}/{nombre}"
        except Exception as e:                         # noqa: BLE001
            c["error"] = repr(e)[:120]
        out.append(c); time.sleep(.6)
    informe.setdefault("freesound", {})[b["clave"]] = out
    print("freesound", b["q"], len(out), "mp3 en búsqueda", len(mp3s))


def transcribir(b):
    """Transcribe un audio del repo (recursos/entrada/...) con faster-whisper, con tiempos por palabra."""
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "faster-whisper"], check=True)
    from faster_whisper import WhisperModel
    m = WhisperModel(b.get("modelo", "small"), device="cpu", compute_type="int8")
    segs, info = m.transcribe(b["archivo"], language=b.get("idioma", "es"), word_timestamps=True)
    out = [dict(ini=round(s.start, 2), fin=round(s.end, 2), texto=s.text.strip()) for s in segs]
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(f"{OUT}/{b['salida']}", "w"), ensure_ascii=False, indent=1)
    print("transcrito", b["archivo"], len(out))


def main():
    p = json.load(open("recursos/pedido.json"))
    for b in p.get("transcribir", []):
        try: transcribir(b)
        except Exception as e:                        # noqa: BLE001
            informe["errores"].append({"transcribir": b, "error": repr(e)[:300]}); print("ERROR", b, e)
    for b in p.get("freesound_buscar", []):
        try: freesound_buscar(b)
        except Exception as e:                        # noqa: BLE001
            informe["errores"].append({"freesound": b, "error": repr(e)[:300]}); print("ERROR", b, e)
    for b in p.get("sketchfab_buscar", []):
        try: sketchfab_buscar(b)
        except Exception as e:                        # noqa: BLE001
            informe["errores"].append({"buscar": b, "error": repr(e)[:300]}); print("ERROR", b, e)
    for b in p.get("mixkit", []):
        try: mixkit(b)
        except Exception as e:                        # noqa: BLE001
            informe["errores"].append({"mixkit": b, "error": repr(e)[:300]}); print("ERROR", b, e)
    for b in p.get("commons_buscar", []):
        try: commons_buscar(b)
        except Exception as e:                        # noqa: BLE001
            informe["errores"].append({"commons": b, "error": repr(e)[:300]}); print("ERROR", b, e)
    for it in p.get("objaverse", []):
        try: objaverse_bajar(it); print("ok objaverse", it["nombre"])
        except Exception as e:                        # noqa: BLE001
            informe["errores"].append({"objaverse": it, "error": repr(e)[:300]}); print("ERROR", it, e)
    if p.get("catalogo"): catalogo()
    for it in p.get("polyhaven", []):
        try: polyhaven(it); print("ok", it["id"])
        except Exception as e:                        # noqa: BLE001
            informe["errores"].append({"id": it.get("id"), "error": repr(e)[:300]}); print("ERROR", it, e)
    for u in p.get("urls", []):
        try: guardar(u["url"], u["destino"]); print("ok", u["destino"])
        except Exception as e:                        # noqa: BLE001
            informe["errores"].append({"url": u["url"], "error": repr(e)[:300]}); print("ERROR", u, e)
    os.makedirs(OUT, exist_ok=True)
    nombre = p.get("informe", "informe.json")
    json.dump(informe, open(f"{OUT}/{nombre}", "w"), ensure_ascii=False, indent=1)
    print("bajados", len(informe["bajados"]), "errores", len(informe["errores"]))


if __name__ == "__main__":
    main()

"""Baja recursos GRATIS con licencia CC0 para los videos de Antonydfilms (lo corre GitHub Actions, que sí tiene internet).

Lee recursos/pedido.json:
{
  "catalogo": true,                                   # guarda la lista de Poly Haven (modelos, HDRI, texturas) para elegir
  "polyhaven": [{"id": "brick_wall_001", "res": "1k"}, ...],   # el tipo (modelo/hdri/textura) se averigua solo
  "urls": [{"url": "https://...", "destino": "carpeta/archivo.ext"}]       # descargas directas (CC0 verificadas)
}
Todo queda en recursos/out/ y se sube a la rama `recursos`. Poly Haven: CC0, sin créditos obligatorios.
"""
import json, os, sys, time, urllib.request, urllib.parse

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
    res = json.loads(leer(url)).get("results", [])
    out = []
    for m in res:
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


def main():
    p = json.load(open("recursos/pedido.json"))
    for b in p.get("sketchfab_buscar", []):
        try: sketchfab_buscar(b)
        except Exception as e:                        # noqa: BLE001
            informe["errores"].append({"buscar": b, "error": repr(e)[:300]}); print("ERROR", b, e)
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

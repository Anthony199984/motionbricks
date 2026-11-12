"""Prendas: carga un .glb de candidatos, lo orienta (Z arriba, frente hacia -Y), lo escala a un hombre de 1,87 m,
le pone tela de Poly Haven si hace falta, lo dibuja con el render del motor y lo exporta a .glb limpio (metros, Y arriba,
frente hacia +Z, como pide glTF)."""
import sys, os, io, json, struct, numpy as np
sys.path.insert(0, '/home/claude/fbxtool'); sys.path.insert(0, '/home/claude/endo_proyecto'); sys.path.insert(0, '/home/claude')
import gltf
from PIL import Image

CAND = '/home/claude/ropa_nueva/candidatos'
TEX = '/home/claude/ropa_nueva/repo/recursos/out/texturas'
C3 = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0.]])                 # glTF (Y arriba) -> Z arriba
ALTO = 1.87


def rot(rx=0, ry=0, rz=0):
    a, b, c = np.radians([rx, ry, rz])
    X = np.array([[1, 0, 0], [0, np.cos(a), -np.sin(a)], [0, np.sin(a), np.cos(a)]])
    Y = np.array([[np.cos(b), 0, np.sin(b)], [0, 1, 0], [-np.sin(b), 0, np.cos(b)]])
    Z = np.array([[np.cos(c), -np.sin(c), 0], [np.sin(c), np.cos(c), 0], [0, 0, 1]])
    return Z @ Y @ X


def _imagenes(path):
    """Imágenes de los materiales (incluye specular-glossiness viejo de Sketchfab) y normal maps."""
    d = open(path, 'rb').read(); o = 12; J = B = None
    while o < len(d):
        ln, ty = struct.unpack('<II', d[o:o+8]); ch = d[o+8:o+8+ln]; o += 8 + ln
        if ty == 0x4E4F534A: J = json.loads(ch)
        elif ty == 0x004E4942: B = ch
    cache = {}
    def img(ti):
        if ti in cache: return cache[ti]
        si = J['textures'][ti].get('source')
        if si is None: cache[ti] = None; return None
        im = J['images'][si]
        if 'bufferView' not in im: cache[ti] = None; return None
        v = J['bufferViews'][im['bufferView']]; s = v.get('byteOffset', 0)
        cache[ti] = Image.open(io.BytesIO(B[s:s+v['byteLength']])).convert('RGBA'); return cache[ti]
    return J, img


def soldar(V, tol=1e-6):
    esc = max(np.ptp(V, 0).max(), 1e-9)
    q = np.round(V / (esc*tol)).astype(np.int64)
    _, idx, inv = np.unique(q, axis=0, return_index=True, return_inverse=True)
    return idx, inv.ravel()


def orientar(Fw):
    """Orienta los triángulos (índices soldados) de forma pareja recorriendo las aristas compartidas. Devuelve máscara de los que se dan vuelta."""
    from collections import deque
    nf = len(Fw); flip = np.zeros(nf, bool); visto = np.zeros(nf, bool)
    aristas = {}
    for f in range(nf):
        a, b, c = Fw[f]
        for u, v in ((a, b), (b, c), (c, a)):
            aristas.setdefault((min(u, v), max(u, v)), []).append(f)
    def dirigidas(f):
        a, b, c = Fw[f]; e = [(a, b), (b, c), (c, a)]
        return [(v, u) for u, v in e] if flip[f] else e
    comp = np.full(nf, -1); k = 0
    for s0 in range(nf):
        if visto[s0]: continue
        visto[s0] = True; comp[s0] = k; dq = deque([s0])
        while dq:
            f = dq.popleft()
            for u, v in dirigidas(f):
                for g in aristas[(min(u, v), max(u, v))]:
                    if visto[g] or g == f: continue
                    eg = dirigidas(g)
                    if (u, v) in eg: flip[g] = not flip[g]          # misma dirección = orientación opuesta
                    visto[g] = True; comp[g] = k; dq.append(g)
        k += 1
    return flip, comp


def arreglar_normales(V, F, N):
    """Deja el orden de los triángulos y las normales de acuerdo entre sí (el shader del motor da vuelta la normal
    en las caras de atrás según ese orden). Si las normales del artista ya concuerdan, no se toca nada."""
    t = V[F]; fn = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    if N is not None:
        acuerdo = (np.sum(fn * N[F].sum(1), 1) > 0).mean()
        if acuerdo > .97: return F, N
        if acuerdo < .03: return F[:, ::-1].copy(), N
    idx, inv = soldar(V); Fw = inv[F]
    ok = (Fw[:, 0] != Fw[:, 1]) & (Fw[:, 1] != Fw[:, 2]) & (Fw[:, 0] != Fw[:, 2])
    flip = np.zeros(len(F), bool); comp = np.full(len(F), -1)
    fl, cp = orientar(Fw[ok]); flip[ok] = fl; comp[ok] = cp
    F2 = F.copy(); F2[flip] = F2[flip][:, ::-1]
    # cada pieza conectada: hacia el lado que diga la mayoría de las normales del artista (o hacia afuera)
    t = V[F2]; fn = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    ref = N[F2].sum(1) if N is not None else (t.mean(1) - V.mean(0))
    for c in np.unique(comp[comp >= 0]):
        m = comp == c
        if np.sum(np.sum(fn[m] * ref[m], 1)) < 0: F2[m] = F2[m][:, ::-1]
    # normales suaves sobre los vértices soldados (sin rayas en las costuras de UV)
    Fw2 = inv[F2]; Vw = V[idx]; Nw = normales(Vw, Fw2)
    return F2, Nw[inv]


def cargar(nombre, partes=None):
    """Lista de piezas indexadas en Z arriba (sin escalar). Cada pieza: V, N, UV, F, color, imagen, normal, rough, metal, alpha."""
    p = f'{CAND}/{nombre}.glb'
    parts, J = gltf.load(p); _, img = _imagenes(p)
    # para saber el material de cada primitiva se recorre igual que gltf.load
    mats_prim = []
    def walk(ni):
        n = J['nodes'][ni]
        if 'mesh' in n:
            for pr in J['meshes'][n['mesh']]['primitives']:
                if pr.get('mode', 4) == 4: mats_prim.append(J['materials'][pr['material']] if 'material' in pr else {})
        for c in n.get('children', []): walk(c)
    for ni in J['scenes'][J.get('scene', 0)]['nodes']: walk(ni)
    out = []
    for i, (q, m) in enumerate(zip(parts, mats_prim)):
        if partes is not None and i not in partes: continue
        V = q['pos'] @ C3.T; F = q['idx'].reshape(-1, 3)
        N = (q['nor'] @ C3.T) if q['nor'] is not None else None
        im = q['image']; sg = m.get('extensions', {}).get('KHR_materials_pbrSpecularGlossiness')
        col = list(q['color'][:3])
        if im is None and sg and 'diffuseTexture' in sg: im = img(sg['diffuseTexture']['index'])
        if sg and 'diffuseFactor' in sg and im is None: col = sg['diffuseFactor'][:3]
        nm = img(m['normalTexture']['index']) if 'normalTexture' in m else None
        pb = m.get('pbrMetallicRoughness', {})
        F, N = arreglar_normales(V, F, N)
        out.append(dict(V=V.astype(np.float64), N=N, UV=np.asarray(q['uv'], np.float64), F=F, color=tuple(col), imagen=im, normal=nm,
                        rough=float(pb.get('roughnessFactor', .85) if pb.get('roughnessFactor') is not None else .85),
                        metal=float(pb.get('metallicFactor', 0) or 0), alpha=q['alpha'], mat=m.get('name', f'm{i}')))
    return out


def normales(V, F):
    t = V[F]; n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]); N = np.zeros_like(V)
    for k in range(3): np.add.at(N, F[:, k], n)
    return N / np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)


def colocar(piezas, R=np.eye(3), alto=None, largo=None, escala=None, pos=(0, 0, 0), base='piso', espejo=False):
    """Gira, escala y pone la prenda. base='piso': apoyada en z=pos[2]; 'arriba': su punto más alto en z=pos[2].
    alto = medida vertical deseada (m); largo = medida mayor en planta (zapatos)."""
    allV = np.concatenate([p['V'] for p in piezas]) @ R.T
    lo, hi = allV.min(0), allV.max(0); t = hi - lo
    if escala is None:
        escala = alto / t[2] if alto is not None else largo / max(t[0], t[1])
    S = np.diag([-1., 1, 1]) if espejo else np.eye(3)
    c = np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2] if base == 'piso' else hi[2]])
    out = []
    for p in piezas:
        V = ((p['V'] @ R.T - c) * escala) @ S.T + np.asarray(pos, float)
        F = p['F'][:, ::-1] if espejo else p['F']
        N = normales(V, F) if p['N'] is None else (p['N'] @ R.T) @ S.T
        N = N / np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)
        out.append(dict(p, V=V, N=N, F=F))
    return out, escala


def tamano(piezas):
    V = np.concatenate([p['V'] for p in piezas]); return V.min(0), V.max(0)


# ------------------------------------------------------------------ telas de Poly Haven
_TENIDAS = {}
_TELAS = {}
def tela(tid, res='2k'):
    if (tid, res) in _TELAS: return _TELAS[(tid, res)]
    _TELAS[(tid, res)] = _tela(tid, res); return _TELAS[(tid, res)]


def _tela(tid, res='2k'):
    d = f'{TEX}/{tid}'
    col = Image.open(f'{d}/{tid}_Diffuse_{res}.jpg').convert('RGBA')
    nor = Image.open(f'{d}/{tid}_nor_gl_{res}.jpg').convert('RGBA') if os.path.exists(f'{d}/{tid}_nor_gl_{res}.jpg') else None
    return col, nor


def tela_uv(V, N, rep):
    """UV nuevas por proyección triplanar simple (cada vértice se proyecta en el plano de su normal dominante).
    rep = metros que mide un cuadro de tela. Sirve cuando la prenda no trae UV o sus UV no sirven para tela."""
    a = np.abs(N); k = a.argmax(1); UV = np.zeros((len(V), 2))
    m = k == 0; UV[m] = V[m][:, [1, 2]]
    m = k == 1; UV[m] = V[m][:, [0, 2]]
    m = k == 2; UV[m] = V[m][:, [0, 1]]
    return UV / rep


def vestir_tela(piezas, tid, tinte=(1, 1, 1), rep=.25, rough=.9, cuales=None, uv='propias', uv_esc=None, solo_relieve=False):
    """Pone la tela `tid` (color teñido + normal map) en las piezas (todas o `cuales`).
    uv='propias' usa las UV de la prenda (Marvelous las trae en tamaño real) escaladas para que un cuadro mida `rep` m."""
    col, nor = tela(tid)
    c = np.asarray(col).astype(np.float32); c[..., :3] *= np.asarray(tinte, np.float32)
    col = Image.fromarray(np.clip(c, 0, 255).astype(np.uint8))
    out = []
    if cuales == 'grandes':                           # solo la tela grande (no hilos, botones ni etiquetas)
        tot = sum(len(p['F']) for p in piezas); cuales = [i for i, p in enumerate(piezas) if len(p['F']) > .03*tot]
    for i, p in enumerate(piezas):
        if cuales is not None and i not in cuales: out.append(p); continue
        if uv == 'propias':
            UV = p['UV']
            if uv_esc is None:          # cuántos metros mide 1 unidad de UV: comparar áreas en 3D y en UV
                t3 = p['V'][p['F']]; tu = UV[p['F']]
                a3 = np.linalg.norm(np.cross(t3[:, 1] - t3[:, 0], t3[:, 2] - t3[:, 0]), axis=1).sum()
                a_, b_ = tu[:, 1] - tu[:, 0], tu[:, 2] - tu[:, 0]; au = np.abs(a_[:, 0]*b_[:, 1] - a_[:, 1]*b_[:, 0]).sum()
                m_por_uv = np.sqrt(a3 / max(au, 1e-12))
            else:
                m_por_uv = uv_esc
            UV = UV * m_por_uv / rep
        else:
            UV = tela_uv(p['V'], p['N'], rep)
        if solo_relieve and p['imagen'] is not None:      # ya tiene su propia textura de color: no se toca
            out.append(p); continue
        if solo_relieve:                                  # conserva el color de la prenda; la tela da el tejido (relieve y un poco de tono)
            kc = (tid, tuple(np.round(p['color'][:3], 3)))
            if kc not in _TENIDAS:
                g = np.asarray(col.convert('L'), np.float32); g = g / max(g.mean(), 1)
                _TENIDAS[kc] = Image.fromarray(np.clip(np.stack([g*255*cc for cc in p['color'][:3]] + [np.full_like(g, 255)], -1), 0, 255).astype(np.uint8))
            out.append(dict(p, UV=UV, imagen=_TENIDAS[kc], normal=nor, color=(1, 1, 1), rough=rough, metal=0.0, alpha='OPAQUE'))
            continue
        out.append(dict(p, UV=UV, imagen=col, normal=nor, color=(1, 1, 1), rough=rough, metal=0.0, alpha='OPAQUE'))
    return out


# ------------------------------------------------------------------ al render del motor
def a_objs(r, piezas, clave, maxtex=2048):
    import skin
    objs = []
    for i, p in enumerate(piezas):
        nm = f'{clave}_{i}'
        if nm not in r.meshes:
            P = p['V'][p['F']].reshape(-1, 3); N = p['N'][p['F']].reshape(-1, 3); UV = p['UV'][p['F']].reshape(-1, 2)
            UV = np.stack([UV[:, 0], 1 - UV[:, 1]], 1)
            r.add_mesh(nm, skin.interleave(P.astype(np.float32), N.astype(np.float32), UV.astype(np.float32)))
        tex, nmap = 'white', None
        if p['imagen'] is not None:
            tex = f'{nm}_t'
            if tex not in getattr(r, 'textures', {}):
                im = p['imagen']; im = im.resize((maxtex, maxtex)) if max(im.size) > maxtex else im
                if p['alpha'] == 'MASK' or (p['alpha'] == 'BLEND' and np.asarray(im)[..., 3].min() < 128):
                    a = np.array(im); a[..., 3] = np.where(a[..., 3] >= 128, 255, 0); im = Image.fromarray(a)
                r.add_texture(tex, im); r.set_texture_filter(tex, 'linear')
        if p['normal'] is not None:
            nmap = f'{nm}_n'
            if nmap not in getattr(r, 'textures', {}):
                im = p['normal']; im = im.resize((maxtex, maxtex)) if max(im.size) > maxtex else im
                r.add_texture(nmap, im)
        objs.append(dict(mesh=nm, texture=tex, normalmap=nmap, nstrength=.9, color=tuple(p['color']), roughness=p['rough'],
                         metal=p['metal'], transparent=False, model=np.eye(4, dtype=np.float32)))
    return objs


# ------------------------------------------------------------------ exportar .glb limpio
def exportar(piezas, ruta, nombre='prenda', jpg=92):
    """GLB en metros, Y arriba, frente hacia +Z (convención glTF). Texturas embebidas (JPG; PNG si tienen transparencia)."""
    Cinv = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0.]])          # Z arriba -> Y arriba (frente -Y -> +Z)
    blob = bytearray(); bvs, accs, meshes_p, mats, texs, imgs = [], [], [], [], [], []
    def pad():
        while len(blob) % 4: blob.append(0)
    def add(arr, tipo, target=None, minmax=False):
        a = np.ascontiguousarray(arr); pad(); off = len(blob); blob.extend(a.tobytes())
        bv = dict(buffer=0, byteOffset=off, byteLength=a.nbytes)
        if target: bv['target'] = target
        bvs.append(bv)
        ct = 5126 if a.dtype == np.float32 else 5125
        acc = dict(bufferView=len(bvs) - 1, componentType=ct, count=len(a), type=tipo)
        if minmax: acc['min'] = a.min(0).tolist(); acc['max'] = a.max(0).tolist()
        accs.append(acc); return len(accs) - 1
    cache_img = {}
    def add_img(im):
        if id(im) in cache_img: return cache_img[id(im)]
        b = io.BytesIO(); alfa = np.asarray(im)[..., 3].min() < 255 if im.mode == 'RGBA' else False
        (im.save(b, 'PNG') if alfa else im.convert('RGB').save(b, 'JPEG', quality=jpg))
        d = b.getvalue(); pad(); off = len(blob); blob.extend(d); bvs.append(dict(buffer=0, byteOffset=off, byteLength=len(d)))
        imgs.append(dict(bufferView=len(bvs) - 1, mimeType='image/png' if alfa else 'image/jpeg'))
        texs.append(dict(source=len(imgs) - 1, sampler=0)); cache_img[id(im)] = len(texs) - 1; return len(texs) - 1
    for i, p in enumerate(piezas):
        V = (p['V'] @ Cinv.T).astype(np.float32); N = (p['N'] @ Cinv.T).astype(np.float32); UV = p['UV'].astype(np.float32)
        F = p['F'].astype(np.uint32).ravel()
        a_p = add(V, 'VEC3', 34962, True); a_n = add(N, 'VEC3', 34962); a_t = add(UV, 'VEC2', 34962); a_i = add(F, 'SCALAR', 34963)
        mat = dict(name=p['mat'], pbrMetallicRoughness=dict(baseColorFactor=list(map(float, p['color'])) + [1.0],
                   metallicFactor=float(p['metal']), roughnessFactor=float(p['rough'])), doubleSided=True)
        if p['imagen'] is not None: mat['pbrMetallicRoughness']['baseColorTexture'] = dict(index=add_img(p['imagen']))
        if p['normal'] is not None: mat['normalTexture'] = dict(index=add_img(p['normal']))
        if p['alpha'] == 'MASK': mat['alphaMode'] = 'MASK'
        mats.append(mat)
        meshes_p.append(dict(attributes=dict(POSITION=a_p, NORMAL=a_n, TEXCOORD_0=a_t), indices=a_i, material=i))
    pad()
    J = dict(asset=dict(version='2.0', generator='Antonydfilms ropa_nueva'), scene=0, scenes=[dict(nodes=[0])],
             nodes=[dict(mesh=0, name=nombre)], meshes=[dict(name=nombre, primitives=meshes_p)], materials=mats,
             accessors=accs, bufferViews=bvs, buffers=[dict(byteLength=len(blob))])
    if texs: J.update(textures=texs, images=imgs, samplers=[dict(magFilter=9729, minFilter=9987, wrapS=10497, wrapT=10497)])
    js = bytearray(json.dumps(J, separators=(',', ':')).encode())
    while len(js) % 4: js += b' '
    with open(ruta, 'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(blob)))
        f.write(struct.pack('<II', len(js), 0x4E4F534A)); f.write(js)
        f.write(struct.pack('<II', len(blob), 0x004E4942)); f.write(blob)
    return ruta

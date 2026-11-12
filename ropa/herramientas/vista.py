"""Vistas de prendas sobre el maniquí neutro (render del motor, luz de estudio neutra)."""
import sys, numpy as np
sys.path.insert(0, '/home/claude/ropa_nueva/herramientas'); sys.path.insert(0, '/home/claude/velocidad_proyecto')
import prendas as PR
from PIL import Image

_E = {}

def motor(w, h):
    """Renderer HQ2 del motor sin cargar a Max."""
    if (w, h) in _E: return _E[(w, h)]
    sys.path.insert(0, '/home/claude/mosquito_proyecto')
    import base_vel as BV
    r = BV.HQ2M.HQ2(w, h)
    for n, m in (('box', BV.G.box()),):
        if n not in r.meshes: r.add_mesh(n, m)
    _E[(w, h)] = r; return r


def luz_estudio(foco, azim=-60, elev=48):
    import base_vel as BV, math
    L = BV.luces(foco, 0.0)
    e, a = math.radians(elev), math.radians(azim)
    d = (math.cos(e)*math.cos(a), math.cos(e)*math.sin(a), math.sin(e))
    L.update(cielo=False, sun=d, sun_col=(1.25, 1.23, 1.20), shadow_target=tuple(foco), shadow_extent=2.6,
             shadow_eye=tuple(np.asarray(foco) + np.asarray(d)*8),
             env_top=(.62, .62, .64), env_hor=(.52, .52, .53), env_bot=(.30, .30, .30), env_k=.62,
             bg_top=(.80, .80, .81), bg_hor=(.86, .86, .86), bg_bot=(.80, .80, .80), ao=1.0, ao_rad=.025, near=.02, far=60)
    L['lights'] = [dict(pos=tuple(np.asarray(foco) + (2.2, -2.0, .6)), col=(.42, .42, .44)),
                   dict(pos=tuple(np.asarray(foco) + (-.6, 2.4, 1.4)), col=(.55, .55, .58))]
    return L


def piso(r, color=(.83, .83, .83)):
    import real_scene as RS
    M = np.eye(4, dtype=np.float32); M[:3, :3] = np.diag([30, 30, .1]); M[:3, 3] = (0, 0, -.05)
    return [RS.box_obj(r, M, color=color, roughness=.95)]


# ------------------------------------------------------------------ maniquí
_BASE = []
def _base():
    """Maniquí soldado (vértices únicos, normales suaves) y con la cabeza lisa, sin rasgos, como uno de tienda."""
    if _BASE: return _BASE[0]
    m, _ = PR.colocar(PR.cargar('m_male_body'), alto=PR.ALTO)
    p = m[0]; V0 = p['V'][p['F'].ravel()] if False else p['V']
    q = np.round(V0 / 1e-5).astype(np.int64)
    _, inv, uni = np.unique(q, axis=0, return_inverse=True, return_index=False), None, None
    claves, idx_u, inv = np.unique(q, axis=0, return_index=True, return_inverse=True)
    V = V0[idx_u].copy(); F = inv.ravel()[p['F']]
    F = F[(F[:, 0] != F[:, 1]) & (F[:, 1] != F[:, 2]) & (F[:, 0] != F[:, 2])]
    # cabeza de maniquí: se quita la cabeza real (rasgos, boca por dentro) y va una cabeza ovalada lisa
    quitar = V[F][:, :, 2].min(1) > 1.615
    F = F[~quitar]
    ang_u, ang_v = np.meshgrid(np.linspace(0, 2*np.pi, 64, endpoint=False), np.linspace(0, np.pi, 33))
    cx, cy, cz, rx, ry, rz = 0.0, -.005, 1.742, .083, .102, .128
    Ve = np.stack([cx + rx*np.sin(ang_v)*np.cos(ang_u), cy + ry*np.sin(ang_v)*np.sin(ang_u), cz + rz*np.cos(ang_v)], -1).reshape(-1, 3)
    Ve[:, 1] -= .012*np.clip((Ve[:, 2] - 1.70)/.08, 0, 1)        # mentón apenas hacia adelante
    nu, nv = 64, 33; Fe = []
    for a in range(nv - 1):
        for b in range(nu):
            i0 = a*nu + b; i1 = a*nu + (b + 1) % nu; i2 = (a + 1)*nu + b; i3 = (a + 1)*nu + (b + 1) % nu
            Fe += [(i0, i2, i1), (i1, i2, i3)]
    Fe = np.array(Fe) + len(V); V = np.concatenate([V, Ve]); F = np.concatenate([F, Fe])
    p = dict(p, V=V, F=F, UV=np.zeros((len(V), 2)), N=PR.normales(V, F))
    _BASE.append(p); return p


_MAN = {}
def maniqui(brazo=0.0, achicar=None, mover=(0.0, 0.0)):
    """Maniquí de 1,87 m (frente -Y). brazo = grados que SUBE cada brazo (gira en el hombro). achicar = dict zona->factor
    (torso, piernas, pies, brazos) para que la ropa lo tape (el maniquí se adelgaza hacia su eje dentro de la ropa)."""
    k = (brazo, tuple(sorted((achicar or {}).items())), tuple(mover))
    if k in _MAN: return _MAN[k]
    p = _base()
    V = p['V'].copy()
    x, y, z = V.T
    # zonas
    torso_hw = np.interp(z, [.8, 1.1, 1.3, 1.45, 1.55], [.17, .17, .19, .19, .19])
    es_brazo = (np.abs(x) > np.interp(z, [.55, 1.25, 1.32, 1.56], [.26, .25, .20, .20])) & (z > .55) & (z < 1.56)
    manga = es_brazo & (z > 1.12)
    es_pierna = (z < .86) & (np.abs(x) < .3)
    es_pie = z < .13
    a = achicar or {}
    def hacia(mask, c, f):                       # adelgaza hacia el eje vertical c=(cx, cy) por el factor f
        V[mask, 0] = c[0] + (V[mask, 0] - c[0]) * f; V[mask, 1] = c[1] + (V[mask, 1] - c[1]) * f
    if 'torso' in a:
        t = (~es_brazo) & (z >= .80) & (z < 1.58) & (np.abs(x) < .3); hacia(t, (0, .03), a['torso'])
    if 'piernas' in a:
        for sg in (-1, 1):
            t = es_pierna & (np.sign(x) == sg) & ~es_pie
            idx = np.where(t)[0]; zz = V[idx, 2]; bins = np.arange(.10, .90, .04); cx, cy = [], []
            for b in bins:                               # centro real de la pierna a cada altura (curva suave)
                m = np.abs(zz - b) < .03; c = V[idx[m], :2].mean(0) if m.any() else np.array([sg*.15, .03])
                cx.append(c[0]); cy.append(c[1])
            ker = np.ones(3)/3; cx = np.convolve(np.pad(cx, 1, 'edge'), ker, 'valid'); cy = np.convolve(np.pad(cy, 1, 'edge'), ker, 'valid')
            Cx = np.interp(zz, bins, cx); Cy = np.interp(zz, bins, cy)
            V[idx, 0] = Cx + (V[idx, 0] - Cx) * a['piernas']; V[idx, 1] = Cy + (V[idx, 1] - Cy) * a['piernas']
    if 'pies' in a:
        for sg in (-1, 1):
            t = es_pie & (np.sign(x) == sg); V[t, 0] = sg*.185 + (V[t, 0] - sg*.185)*a['pies']; V[t, 2] *= a['pies']; V[t, 1] = .03 + (V[t, 1] - .03)*a['pies']
    if 'brazos' in a:
        zona = es_brazo & (z > a.get('brazo_hasta', 1.12))
        for sg in (-1, 1):
            t = zona & (np.sign(x) == sg)
            # eje del brazo: hombro -> muñeca
            P0 = np.array([sg*.20, .02, 1.46]); P1 = np.array([sg*.52, .0, .93]); d = (P1 - P0)/np.linalg.norm(P1 - P0)
            q = V[t] - P0; s = q @ d; perp = q - np.outer(s, d); V[t] = P0 + np.outer(s, d) + perp*a['brazos']
    if brazo:
        for sg in (-1, 1):
            t = es_brazo & (np.sign(x) == sg)
            piv = np.array([sg*.185, .02, 1.45]); q = V[t] - piv
            dist = np.linalg.norm(q[:, [0, 2]], axis=1); w = np.clip((dist - .02)/.10, 0, 1); w = w*w*(3 - 2*w)
            ang = np.radians(brazo)*sg*w                 # sube el brazo: gira en XZ alrededor del hombro
            c, s_ = np.cos(ang), np.sin(ang)
            qx = q[:, 0]*c - q[:, 2]*s_; qz = q[:, 0]*s_ + q[:, 2]*c
            V[t, 0] = piv[0] + qx; V[t, 2] = piv[2] + qz
    if any(mover):
        for sg in (-1, 1):
            t = es_brazo & (np.sign(x) == sg)
            piv = np.array([sg*.185, .02, 1.45]); dist = np.linalg.norm((V[t] - piv)[:, [0, 2]], axis=1)
            w = np.clip((dist - .02)/.12, 0, 1); w = w*w*(3 - 2*w)
            V[t, 0] += sg*mover[0]*w; V[t, 1] += mover[1]*w
    out = [dict(p, V=V, N=PR.normales(V, p['F']), imagen=None, normal=None, color=(.86, .86, .85), rough=.55, metal=0.0)]
    _MAN[k] = out; return out


def foto(r, objs, ojo, mira, fov, L):
    import base_vel as BV
    cam = (tuple(map(float, ojo)), tuple(map(float, mira)), float(fov))
    h = r.draw(objs, cam, L); img = BV.revelar(r, h, 0, near=L['near'])
    return Image.fromarray(np.asarray(img)[..., :3].astype(np.uint8))

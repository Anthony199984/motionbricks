"""Arma cada prenda en su lugar sobre el maniquí de 1,87 m (Z arriba, frente -Y)."""
import sys, numpy as np
sys.path.insert(0, '/home/claude/ropa_nueva/herramientas')
import prendas as PR, defs as D

PIE_X, PIE_Y = .185, .015          # centro de cada pie del maniquí


def _orientar_zapato(piezas):
    """Gira un zapato suelto para que el largo vaya en Y y la punta mire a -Y (el talón es la punta más alta)."""
    V = np.concatenate([p['V'] for p in piezas]); lo, hi = V.min(0), V.max(0)
    R = np.eye(3)
    if hi[0] - lo[0] > hi[1] - lo[1]: R = PR.rot(rz=90)
    V2 = V @ R.T; y = V2[:, 1]; y0, y1 = y.min(), y.max(); L = y1 - y0
    zf = V2[y < y0 + .2*L, 2].max(); zb = V2[y > y1 - .2*L, 2].max()
    if zf > zb: R = PR.rot(rz=180) @ R          # el lado alto (talón) tiene que quedar atrás (+Y)
    return R


def prenda(nombre, extra_R=None):
    d = D.PRENDAS[nombre]
    p = PR.cargar(d['src'], d.get('partes'))
    R = PR.rot(*d.get('R', (0, 0, 0)))
    if extra_R is not None: R = extra_R @ R
    if d['tipo'] in ('arriba', 'abajo'):
        p, _ = PR.colocar(p, R, alto=d['alto'], base='arriba', pos=(d.get('dx', 0), d.get('dy', .02), d['z_top']))
        # ancho al cuerpo: se mide la prenda a una altura de referencia y se escala en planta (alrededor del eje del cuerpo)
        z_ref, ancho = (1.22, d.get('ancho', .44)) if d['tipo'] == 'arriba' else (.96, d.get('ancho', .43))
        V = np.concatenate([q['V'] for q in p]); sl = V[np.abs(V[:, 2] - z_ref) < .02]
        if d['tipo'] == 'arriba':                         # solo el cuerpo de la prenda, no las mangas
            sl = sl[np.abs(sl[:, 0] - d.get('dx', 0)) < .30]
        f = ancho / max(sl[:, 0].max() - sl[:, 0].min(), 1e-6) if len(sl) else 1.0
        f = d.get('esc_xy', f); cx, cy = d.get('dx', 0), d.get('dy', .02)
        for q in p:
            q['V'][:, 0] = cx + (q['V'][:, 0] - cx) * f; q['V'][:, 1] = cy + (q['V'][:, 1] - cy) * f
        d['_f'] = f
    else:
        if d.get('par'):
            p, _ = PR.colocar(p, R, largo=d['largo'], pos=(0, PIE_Y, 0))
        else:
            if 'R' not in d: R = _orientar_zapato([dict(q, V=q['V'] @ R.T) for q in p]) @ R
            der, _ = PR.colocar(p, R, largo=d['largo'], pos=(PIE_X, PIE_Y + d.get('dy', 0), 0))          # pie derecho del maniquí (x>0)
            izq, _ = PR.colocar(p, R, largo=d['largo'], pos=(-PIE_X, PIE_Y + d.get('dy', 0), 0), espejo=True)
            p = der + izq
    for viejo, nuevo in d.get('colores', []):           # recolorear piezas por su color (p. ej. pespuntes)
        p = [dict(q, color=tuple(nuevo)) if np.abs(np.asarray(q['color'][:3]) - viejo).max() < .06 else q for q in p]
    if d.get('blanco'):                                  # camisa de vestir blanca: la tela principal pasa a blanco
        p = [dict(q, color=(.93, .93, .92)) if 'FABRIC' in q['mat'].upper() else q for q in p]
    if 'tela' in d:
        t = d['tela']; p = PR.vestir_tela(p, t['id'], t.get('tinte', (1, 1, 1)), t.get('rep', .25), t.get('rough', .9),
                                          t.get('cuales'), t.get('uv', 'propias'), t.get('uv_esc'), t.get('solo_relieve', False))
    return p

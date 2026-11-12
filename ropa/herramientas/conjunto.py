"""Render de un conjunto completo sobre el maniquí: frente y lado."""
import sys, numpy as np
sys.path.insert(0, '/home/claude/ropa_nueva/herramientas')
import vista as VI, armar as A, prendas as PR, defs as D

def vistas(r, noms, clave, alto_img):
    brazo = 0; ach = {}
    for n in noms:
        d = D.PRENDAS[n]
        if d['tipo'] == 'arriba':
            ach.update(torso=.9, brazos=.72); brazo = d.get('brazo', 0)
            if d.get('manga_larga'): ach.update(brazos=.6, brazo_hasta=.97)
        if d['tipo'] == 'abajo': ach.update(piernas=.3, torso=.9)
        if d['tipo'] == 'zapato': ach.update(pies=.35)
    arriba_ = [n for n in noms if D.PRENDAS[n]['tipo'] == 'arriba']; mover = (0.0, 0.0)
    if arriba_ and D.PRENDAS[arriba_[0]].get('brazo') == 'auto':
        top = A.prenda(arriba_[0]); brazo = brazo_auto(top)
        V = np.concatenate([q['V'] for q in top]); M = VI.maniqui(brazo, ach)[0]['V']
        s = V[(V[:, 0] > .25) & (np.abs(V[:, 2] - 1.15) < .02)]; m = M[(M[:, 0] > .25) & (np.abs(M[:, 2] - 1.15) < .02)]
        mover = (round(float((s[:, 0].min() + s[:, 0].max())/2 - (m[:, 0].min() + m[:, 0].max())/2), 3),
                 round(float(s[:, 1].mean() - m[:, 1].mean()), 3))
    man = VI.maniqui(brazo, ach, mover)
    objs = VI.piso(r) + PR.a_objs(r, man, f'man_{clave}')
    piezas = {n: A.prenda(n) for n in noms}
    arriba = [n for n in noms if D.PRENDAS[n]['tipo'] == 'arriba']
    for n in noms:
        if D.PRENDAS[n]['tipo'] == 'abajo' and arriba:
            piezas[n] = meter_bajo(piezas[n], piezas[arriba[0]])
    for n in noms: objs += PR.a_objs(r, piezas[n], f'{n}_{clave}')
    tg = np.array([0, 0, .94]); L = VI.luz_estudio(tg)
    fr = VI.foto(r, objs, tg + [0, -5.6, .2], tg, 22.5, L)
    la = VI.foto(r, objs, tg + [3.96, -3.96, .2], tg, 22.5, L)       # tres cuartos: se ve el lado y el frente
    lado = VI.foto(r, objs, tg + [5.6, 0, .2], tg, 22.5, L)
    return fr, la, lado


def meter_bajo(pant, top):
    """La parte del pantalón que queda bajo la prenda de arriba se mete un poco hacia el cuerpo (no se ve y así no la atraviesa)."""
    V = np.concatenate([q['V'] for q in top]); cuerpo = V[np.abs(V[:, 0]) < .2]
    hem = np.percentile(cuerpo[:, 2], 2)                      # borde de abajo de la prenda de arriba
    out = []
    for q in pant:
        V = q['V'].copy(); w = np.clip((V[:, 2] - (hem - .08)) / .06, 0, 1); f = 1 - .22*w
        V[:, 0] *= f; V[:, 1] = .02 + (V[:, 1] - .02)*f
        out.append(dict(q, V=V))
    return out


def brazo_auto(top):
    """Grados que hay que subir el brazo del maniquí para que vaya por el centro de la manga (se mide la manga derecha)."""
    V = np.concatenate([q['V'] for q in top]); s = V[(V[:, 0] > .30) & (V[:, 2] > .8)]
    if len(s) < 50: return 0
    c = s.mean(0); u = np.linalg.svd(s - c)[2][0]
    if u[2] > 0: u = -u                                       # hacia abajo
    ang_manga = np.degrees(np.arctan2(u[0], -u[2]))          # grados desde la vertical
    ang_brazo = np.degrees(np.arctan2(.335, .52))
    return round(float(ang_manga - ang_brazo), 1)

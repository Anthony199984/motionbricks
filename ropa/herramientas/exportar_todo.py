import sys, os, numpy as np
sys.path.insert(0, '/home/claude/ropa_nueva/herramientas')
import armar as A, prendas as PR, defs as D, vista as VI
OUT = '/home/claude/ropa_nueva/entrega/prendas'
for n in D.PRENDAS:
    p = A.prenda(n); f = PR.exportar(p, f'{OUT}/{n}.glb', n)
    V = np.concatenate([q['V'] for q in p]); print(n.ljust(20), f'{os.path.getsize(f)/2**20:6.1f} MB', 'tris', sum(len(q['F']) for q in p), 'z', V[:, 2].min().round(3), V[:, 2].max().round(3))
m = VI.maniqui(0, {}); PR.exportar(m, f'{OUT}/maniqui_neutro_1_87m.glb', 'maniqui'); print('maniqui ok')

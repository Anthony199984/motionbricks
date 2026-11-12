import sys, numpy as np
sys.path.insert(0, '/home/claude/ropa_nueva/herramientas')
import prendas as PR, vista as VI, defs as D
from PIL import Image, ImageDraw
PR.CAND = '/home/claude/ropa_nueva/entrega/prendas'
r = VI.motor(300, 540); celdas = []
grupos = [noms for _, noms in D.CONJUNTOS] + [['camiseta_gris', 'jeans_azul', 'zapato_cuero_viejo'], ['camiseta_rayas', 'pantalon_vestir', 'zapato_casual'], ['polo_blanco', 'jeans_clasico', 'tenis_blancos'], ['camisa_cuadros', 'pantalon_deportivo', 'tenis_correr']]
man = PR.cargar('maniqui_neutro_1_87m')
for i, g in enumerate(grupos):
    objs = VI.piso(r) + PR.a_objs(r, man, 'mv')
    for n in g: objs += PR.a_objs(r, PR.cargar(n), f'v_{n}')
    tg = np.array([0, 0, .94]); L = VI.luz_estudio(tg)
    c = VI.foto(r, objs, tg + [2.8, -4.8, .2], tg, 23, L); ImageDraw.Draw(c).text((4, 4), ' + '.join(g), fill='black'); celdas.append(c)
o = Image.new('RGB', (1200, 1080))
for i, c in enumerate(celdas): o.paste(c, ((i % 4)*300, (i//4)*540))
o.save('/home/claude/ropa_nueva/revision/verificacion_glb.jpg', quality=85); print('ok')

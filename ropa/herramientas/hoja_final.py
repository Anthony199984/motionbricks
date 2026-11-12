"""Hoja PNG con los conjuntos numerados (frente, tres cuartos y lado) sobre el maniquí neutro."""
import sys, json, numpy as np
sys.path.insert(0, '/home/claude/ropa_nueva/herramientas')
import vista as VI, conjunto as CJ, defs as D
from PIL import Image, ImageDraw, ImageFont
W, H = 520, 936
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans'
def fuente(t, b=False):
    try: return ImageFont.truetype(F + ('-Bold' if b else '') + '.ttf', t)
    except Exception: return ImageFont.load_default()
CRED = json.load(open('/home/claude/ropa_nueva/herramientas/creditos.json'))
r = VI.motor(W, H)
bloques = []
for i, (nom, noms) in enumerate(D.CONJUNTOS):
    a, b, c = CJ.vistas(r, noms, f'h{i}', H)
    blk = Image.new('RGB', (3*W + 40, H + 300), (245, 245, 243)); dr = ImageDraw.Draw(blk)
    dr.text((24, 14), f"{i+1}. {nom.upper()}", fill=(25, 25, 25), font=fuente(52, True))
    for k, (im, et) in enumerate(((a, 'Frente'), (b, 'Tres cuartos'), (c, 'Lado'))):
        blk.paste(im, (20 + k*W, 90)); dr.text((30 + k*W, 100), et, fill=(70, 70, 70), font=fuente(26))
    y = H + 104
    for n in noms:
        cr = CRED[n]
        dr.text((28, y), f"• {n}.glb", fill=(20, 20, 20), font=fuente(30, True))
        dr.text((470, y + 3), f"\"{cr['titulo'][:38]}\" · {cr['autor']} · {cr['licencia_corta']}", fill=(60, 60, 60), font=fuente(26))
        y += 52
    bloques.append(blk)
bw, bh = bloques[0].size
hoja = Image.new('RGB', (2*bw + 60, 2*bh + 200), (255, 255, 255)); dr = ImageDraw.Draw(hoja)
dr.text((30, 30), "Ropa 3D para personaje masculino de 1,87 m · 4 conjuntos", fill=(15, 15, 15), font=fuente(64, True))
dr.text((32, 112), "Maniquí neutro (no es Max). Mallas de ropa sueltas, tela real con arrugas y costuras; telas extra de Poly Haven (CC0).", fill=(80, 80, 80), font=fuente(32))
for i, blk in enumerate(bloques): hoja.paste(blk, (20 + (i % 2)*(bw + 20), 180 + (i // 2)*(bh + 20)))
hoja.save(sys.argv[1], optimize=True); print('ok', hoja.size)

import json, sys, os
from PIL import Image, ImageDraw, ImageFont
OUT = '/home/claude/ropa_nueva/repo/recursos/out'
d = json.load(open(f'{OUT}/{sys.argv[1]}'))['sketchfab']
fnt = ImageFont.load_default()
for k, v in d.items():
    if not v: continue
    c = 8; w, h = 200, 150; filas = (len(v) + c - 1)//c
    o = Image.new('RGB', (c*w, filas*(h+24)), 'white'); dr = ImageDraw.Draw(o)
    for i, m in enumerate(v):
        x, y = (i % c)*w, (i//c)*(h+24)
        if m.get('miniatura') and os.path.exists(f"{OUT}/{m['miniatura']}"):
            im = Image.open(f"{OUT}/{m['miniatura']}").convert('RGB'); im.thumbnail((w-4, h)); o.paste(im, (x+2, y))
        lic = (m['licencia'] or '?').replace('CC Attribution', 'BY').replace('-NonCommercial', '-NC').replace('-ShareAlike','-SA').replace('-NoDerivs','-ND')
        dr.text((x+2, y+h+1), f"{i} {lic} {m['caras'] or 0}c", fill='black', font=fnt)
        dr.text((x+2, y+h+12), (m['nombre'] or '')[:30], fill='blue', font=fnt)
    o.save(f'/home/claude/ropa_nueva/revision/mini_{k}.jpg', quality=80)
    print(k, o.size)

"""Baja .glb de Objaverse (Hugging Face) por clave/índice de un informe de búsqueda. Uso: bajar_hf.py informe.json clave:idx:nombre ..."""
import json, sys, os, gzip, subprocess
OUT = '/home/claude/ropa_nueva/repo/recursos/out'; DEST = '/home/claude/ropa_nueva/candidatos'; os.makedirs(DEST, exist_ok=True)
rutas = json.loads(gzip.open('/home/claude/ropa_nueva/datos/object-paths.json.gz').read())
inf = json.load(open(f'{OUT}/{sys.argv[1]}'))['sketchfab']
reg = f'{DEST}/registro.json'; R = json.load(open(reg)) if os.path.exists(reg) else {}
for a in sys.argv[2:]:
    k, i, nom = a.split(':'); m = inf[k][int(i)]
    dst = f'{DEST}/{nom}.glb'
    if not os.path.exists(dst):
        r = subprocess.run(['curl', '-sSL', '-m', '600', '-o', dst, f"https://huggingface.co/datasets/allenai/objaverse/resolve/main/{rutas[m['uid']]}"])
    R[nom] = dict(m, archivo=dst, mb=round(os.path.getsize(dst)/2**20, 1))
    print(nom, R[nom]['mb'], 'MB', m['licencia'], m['autor'], m['nombre'])
json.dump(R, open(reg, 'w'), ensure_ascii=False, indent=1)

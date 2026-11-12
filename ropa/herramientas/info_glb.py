import sys, json, struct, numpy as np, glob, os
sys.path.insert(0, '/home/claude/fbxtool'); import gltf
C3 = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0.]])
def info(p):
    d = open(p, 'rb').read(); ln = struct.unpack('<I', d[12:16])[0]; J = json.loads(d[20:20+ln])
    ext = J.get('extensionsUsed', [])
    try: parts, _ = gltf.load(p)
    except Exception as e: return dict(error=repr(e)[:80], ext=ext)
    P = np.concatenate([q['pos'] @ C3.T for q in parts]); lo, hi = P.min(0), P.max(0)
    tris = sum(len(q['idx'])//3 for q in parts)
    mats = J.get('materials', []); nmaps = sum('normalTexture' in m for m in mats)
    texs = [max(q['image'].size) if q['image'] is not None else 0 for q in parts]
    return dict(tam=np.round(hi-lo, 3).tolist(), partes=len(parts), tris=tris, mats=len(mats), normalmaps=nmaps, tex_max=max(texs), skin='skins' in J, anim=len(J.get('animations', [])), ext=ext)
for p in sorted(glob.glob(sys.argv[1])):
    print(os.path.basename(p)[:-4].ljust(22), info(p))

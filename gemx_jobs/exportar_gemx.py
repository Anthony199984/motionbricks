"""Saca de motion.pt (GEM-X) lo que el motor de Max necesita: rotaciones y posiciones de los 77 huesos SOMA por cuadro
(y las de la pose cero), en un .npz sin torch."""
import sys
import numpy as np
import torch
from gem.common.soma import SomaFixedGs1BodyAdapter, SomaRuntimeConfig

entrada, salida, assets = sys.argv[1:4]
r = torch.load(entrada, map_location="cpu", weights_only=False)
print("claves:", list(r.keys()))
out = {}
body = SomaFixedGs1BodyAdapter(SomaRuntimeConfig(data_root=assets, device="cpu", apply_correctives=False))
for vista in ("global", "incam"):
    k = f"pred_soma_params_{vista}"
    if k not in r:
        continue
    p = {n: torch.as_tensor(v).float() for n, v in r[k].items() if torch.is_tensor(v) or isinstance(v, np.ndarray)}
    print(vista, {n: tuple(v.shape) for n, v in p.items()})
    for n, v in p.items():
        out[f"{vista}_{n}"] = v.numpy()
    args = dict(global_orient=p["global_orient"], body_pose=p["body_pose"], identity_coeffs=p["identity_coeffs"],
                scale_params=p["scale_params"], transl=p.get("transl"))
    with torch.no_grad():
        o = body(**args, return_joints_only=True)
        out[f"{vista}_joints"] = o["joints"].numpy()
        if o.get("transforms") is not None:
            out[f"{vista}_transforms"] = o["transforms"].numpy()
        z = dict(args); z["global_orient"] = torch.zeros_like(p["global_orient"][:, :1]); z["body_pose"] = torch.zeros_like(p["body_pose"][:, :1])
        z["identity_coeffs"] = p["identity_coeffs"][:, :1] if p["identity_coeffs"].dim() == 3 else p["identity_coeffs"]
        z["scale_params"] = p["scale_params"][:, :1] if p["scale_params"].dim() == 3 else p["scale_params"]
        z["transl"] = None
        o0 = body(**z, return_joints_only=True)
        out[f"{vista}_cero_joints"] = o0["joints"].numpy()
        if o0.get("transforms") is not None:
            out[f"{vista}_cero_transforms"] = o0["transforms"].numpy()
rt = body.runtime
for nombre in ("public_joint_names",):
    if hasattr(rt, nombre):
        out[nombre] = np.array([str(x) for x in getattr(rt, nombre)])
try:
    out["rig_parents"] = np.asarray(rt.rig_data.get("joint_parents", rt.rig_data.get("parents")))
    out["rig_names"] = np.array([str(x) for x in rt.rig_data["joint_names"]])
except Exception as e:
    print("sin rig_data:", e)
for k in ("static_contact_logits", "contact_logits", "fps"):
    if k in r and (torch.is_tensor(r[k]) or isinstance(r[k], np.ndarray)):
        out[k] = torch.as_tensor(r[k]).numpy()
np.savez_compressed(salida, **out)
print("guardado", salida, {k: v.shape for k, v in out.items()})

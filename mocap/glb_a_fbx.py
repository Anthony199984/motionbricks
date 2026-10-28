"""Blender (fondo): MonoRhesus.glb -> MonoRhesus.fbx (base) y MonoRhesus-Idle.fbx, los dos con su acción activa
(Mocap-Anything mide el movimiento de cada FBX). Uso: blender -b -P glb_a_fbx.py -- entrada.glb carpeta_salida"""
import bpy, sys, os
args = sys.argv[sys.argv.index('--') + 1:]
glb, out = args[0], args[1]
os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
arm.name = 'MonoRhesus'
acts = list(bpy.data.actions)
print('acciones:', [a.name for a in acts])
if not arm.animation_data: arm.animation_data_create()
for tr in list(arm.animation_data.nla_tracks): arm.animation_data.nla_tracks.remove(tr)
arm.animation_data.action = acts[0]
fr = acts[0].frame_range; sc = bpy.context.scene
sc.frame_start, sc.frame_end = int(fr[0]), int(fr[1]); sc.render.fps = 30
print('acción activa:', arm.animation_data.action.name, fr[:])
for nombre in ('MonoRhesus.fbx', 'MonoRhesus-Idle.fbx'):
    bpy.ops.export_scene.fbx(filepath=os.path.join(out, nombre), use_selection=False, add_leaf_bones=False, bake_anim=True,
                             bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False, object_types={'ARMATURE', 'MESH'},
                             path_mode='COPY', embed_textures=True)
print('FBX listos con movimiento')

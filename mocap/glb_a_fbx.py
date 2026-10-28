"""Blender (fondo): MonoRhesus.glb -> MonoRhesus.fbx (malla + esqueleto, base) y MonoRhesus-Idle.fbx (con movimiento).
Uso: blender -b -P glb_a_fbx.py -- entrada.glb carpeta_salida"""
import bpy, sys, os
args = sys.argv[sys.argv.index('--') + 1:]
glb, out = args[0], args[1]
os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
arm.name = 'MonoRhesus'
base = os.path.join(out, 'MonoRhesus.fbx'); mov = os.path.join(out, 'MonoRhesus-Idle.fbx')
bpy.ops.export_scene.fbx(filepath=mov, use_selection=False, add_leaf_bones=False, bake_anim=True, bake_anim_use_all_actions=False,
                         object_types={'ARMATURE', 'MESH'}, path_mode='COPY', embed_textures=True)
if arm.animation_data: arm.animation_data.action = None
bpy.context.scene.frame_set(0)
bpy.ops.export_scene.fbx(filepath=base, use_selection=False, add_leaf_bones=False, bake_anim=False,
                         object_types={'ARMATURE', 'MESH'}, path_mode='COPY', embed_textures=True)
print('FBX listos:', base, mov)

"""blender -b -P convertir.py -- <carpeta_avatar> <salida.glb>
Importa el FBX con caras (_facial.fbx) de Rocketbox, vuelve a enlazar las texturas TGA y exporta GLB."""
import bpy, sys, os, glob
a = sys.argv[sys.argv.index('--') + 1:]; carpeta, salida = a[0], a[1]
nombre = os.path.basename(carpeta.rstrip('/'))
bpy.ops.wm.read_factory_settings(use_empty=True)
fbx = os.path.join(carpeta, 'Export', nombre + '_facial.fbx')
if not os.path.exists(fbx): fbx = os.path.join(carpeta, 'Export', nombre + '.fbx')
bpy.ops.import_scene.fbx(filepath=fbx, use_anim=False, automatic_bone_orientation=False, ignore_leaf_bones=False)
tex = {os.path.basename(p).lower(): p for p in glob.glob(os.path.join(carpeta, 'Textures', '*'))}
for im in bpy.data.images:
    b = os.path.basename(bpy.path.abspath(im.filepath)).lower()
    if b in tex:
        im.filepath = tex[b]; im.reload()
    print('imagen', im.name, im.filepath, tuple(im.size))
for o in bpy.data.objects: print('objeto', o.type, o.name, [k.name for k in (o.data.shape_keys.key_blocks if o.type == 'MESH' and o.data.shape_keys else [])][:3])
bpy.ops.export_scene.gltf(filepath=salida, export_format='GLB', export_skins=True, export_morph=True, export_morph_normal=False,
                          export_animations=False, export_yup=True, export_image_format='JPEG', export_jpeg_quality=88, export_apply=False)
print('ok', salida, os.path.getsize(salida))

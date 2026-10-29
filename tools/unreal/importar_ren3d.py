"""Importa en Kennedy360 lo que exporta exportar_edificios.py (carpeta Importar): texturas PBR de fachada, materiales
(ladrillo, pintado, techo, follaje), la malla de edificios y el árbol tipo maqueta; deja las mallas en /Game/Kennedy/Ren3D
y anota en Saved/importar_ren3d.txt las medidas de cada malla (para ubicarlas sobre la malla de Google)."""
import os, unreal

PROY = r'C:\Users\ACER\Documents\Unreal Projects\Kennedy360'
SRC = os.path.join(PROY, 'Importar')
DST = '/Game/Kennedy/Ren3D'
EAL, MEL = unreal.EditorAssetLibrary, unreal.MaterialEditingLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
info = []
def log(s): info.append(str(s)); unreal.log('[Kennedy360] ' + str(s))

def importar(archivo, destino=DST):
    t = unreal.AssetImportTask()
    t.set_editor_property('filename', os.path.join(SRC, archivo)); t.set_editor_property('destination_path', destino)
    t.set_editor_property('automated', True); t.set_editor_property('replace_existing', True); t.set_editor_property('save', True)
    tools.import_asset_tasks([t])
    return [unreal.load_asset(p) for p in t.get_editor_property('imported_object_paths')]

# ---------- texturas ----------
tex = {}
for tipo in ('ladrillo', 'pintado'):
    for k in ('color', 'normal', 'rugosidad'):
        a = importar('fachada_%s_%s.png' % (tipo, k))[0]
        if k == 'normal':
            a.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_NORMALMAP); a.set_editor_property('srgb', False)
        elif k == 'rugosidad':
            a.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_MASKS); a.set_editor_property('srgb', False)
        EAL.save_loaded_asset(a); tex[(tipo, k)] = a
log('texturas: %d' % len(tex))

# ---------- materiales ----------
def material(nombre):
    ruta = DST + '/' + nombre
    if EAL.does_asset_exist(ruta): EAL.delete_asset(ruta)
    return tools.create_asset(nombre, DST, unreal.Material, unreal.MaterialFactoryNew())
def muestra(m, t, x, y, tipo=None):
    n = MEL.create_material_expression(m, unreal.MaterialExpressionTextureSample, x, y)
    n.set_editor_property('texture', t)
    if tipo: n.set_editor_property('sampler_type', tipo)
    return n
mats = {}
for tipo in ('ladrillo', 'pintado'):
    m = material('M_Fachada_' + tipo)
    c = muestra(m, tex[(tipo, 'color')], -600, -200)
    nr = muestra(m, tex[(tipo, 'normal')], -600, 100, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    r = muestra(m, tex[(tipo, 'rugosidad')], -600, 400, unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
    if tipo == 'ladrillo':  # de lejos el ladrillo se mezcla con vidrios y marcos y se veía gris: tinte cálido de ladrillo bogotano
        ti = MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -600, -400); ti.set_editor_property('constant', unreal.LinearColor(1.35, 0.95, 0.78, 1))
        mu = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -300, -250)
        MEL.connect_material_expressions(c, 'RGB', mu, 'A'); MEL.connect_material_expressions(ti, '', mu, 'B')
        MEL.connect_material_property(mu, '', unreal.MaterialProperty.MP_BASE_COLOR)
    else:
        MEL.connect_material_property(c, 'RGB', unreal.MaterialProperty.MP_BASE_COLOR)
    MEL.connect_material_property(nr, 'RGB', unreal.MaterialProperty.MP_NORMAL)
    MEL.connect_material_property(r, 'R', unreal.MaterialProperty.MP_ROUGHNESS)
    m.set_editor_property('two_sided', True)  # el OBJ pasa por un cambio de ejes al importar: a dos caras se ve bien sea cual sea el orden de los vértices
    MEL.recompile_material(m); EAL.save_loaded_asset(m); mats[tipo] = m
m = material('M_Techo')  # cubierta: losa gris cálida, mate
k = MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -400, 0); k.set_editor_property('constant', unreal.LinearColor(0.20, 0.18, 0.16, 1))
MEL.connect_material_property(k, '', unreal.MaterialProperty.MP_BASE_COLOR)
kr = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -400, 200); kr.set_editor_property('r', 0.9)
MEL.connect_material_property(kr, '', unreal.MaterialProperty.MP_ROUGHNESS)
m.set_editor_property('two_sided', True)
MEL.recompile_material(m); EAL.save_loaded_asset(m); mats['techo'] = m
m = material('M_Follaje')  # verde vivo con variación por árbol (PerInstanceRandom) y claro arriba / oscuro abajo
a1 = MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -900, -200); a1.set_editor_property('constant', unreal.LinearColor(0.07, 0.20, 0.03, 1))
a2 = MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -900, 0); a2.set_editor_property('constant', unreal.LinearColor(0.16, 0.30, 0.05, 1))
pr = MEL.create_material_expression(m, unreal.MaterialExpressionPerInstanceRandom, -900, 200)
lp = MEL.create_material_expression(m, unreal.MaterialExpressionLinearInterpolate, -600, 0)
MEL.connect_material_expressions(a1, '', lp, 'A'); MEL.connect_material_expressions(a2, '', lp, 'B'); MEL.connect_material_expressions(pr, '', lp, 'Alpha')
MEL.connect_material_property(lp, '', unreal.MaterialProperty.MP_BASE_COLOR)
kr = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -400, 300); kr.set_editor_property('r', 0.75)
MEL.connect_material_property(kr, '', unreal.MaterialProperty.MP_ROUGHNESS)
m.set_editor_property('used_with_instanced_static_meshes', True)
MEL.recompile_material(m); EAL.save_loaded_asset(m); mats['follaje'] = m
log('materiales listos')

# ---------- mallas (se borran antes: la reimportación dejaba la versión vieja) ----------
for viejo in ('ladrillo', 'pintado', 'techo', 'arbol'):
    if EAL.does_asset_exist(DST + '/' + viejo): EAL.delete_asset(DST + '/' + viejo)
for archivo in ('edificios.obj', 'arbol.obj'):
    objs = importar(archivo)
    for o in objs:
        if isinstance(o, unreal.StaticMesh):
            b = o.get_bounding_box()
            log('%s: %s min %s max %s, %d materiales' % (archivo, o.get_name(), b.min, b.max, len(o.static_materials)))
            for i, sm in enumerate(o.static_materials):
                nombre = str(sm.material_slot_name).lower()
                for k2, mm in mats.items():
                    if k2 in nombre: o.set_material(i, mm)
                log('   slot %d %s' % (i, sm.material_slot_name))
            EAL.save_loaded_asset(o)
        else:
            log('%s: importado %s' % (archivo, type(o).__name__))
with open(os.path.join(PROY, 'Saved', 'importar_ren3d.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(info))

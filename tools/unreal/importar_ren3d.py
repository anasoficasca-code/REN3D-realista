"""Importa en Kennedy360 lo que exporta exportar_edificios.py (carpeta Importar): texturas PBR de fachada, materiales
(ladrillo, pañete salmón / crema / blanco, techo, lámina, balcón), la malla de edificios y los árboles reales de Poly Haven
(jacaranda e island tree, con Nanite); deja todo en /Game/Kennedy/Ren3D y anota en Saved/importar_ren3d.txt lo importado."""
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
def constante3(m, c, x, y):
    k = MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, x, y); k.set_editor_property('constant', unreal.LinearColor(c[0], c[1], c[2], 1)); return k
def constante(m, v, x, y):
    k = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, x, y); k.set_editor_property('r', v); return k
mats = {}
# fachadas: textura de ladrillo o de pañete (blanco) por un tinte; los colores salen de los videos de dron del humedal
FACHADAS = {'ladrillo': ('ladrillo', (1.35, 0.95, 0.78)), 'salmon': ('pintado', (1.0, 0.62, 0.47)), 'crema': ('pintado', (1.0, 0.86, 0.66)), 'blanco': ('pintado', (0.95, 0.94, 0.92))}
for nombre, (tipo, tinte) in FACHADAS.items():
    m = material('M_Fachada_' + nombre)
    c = muestra(m, tex[(tipo, 'color')], -700, -200)
    nr = muestra(m, tex[(tipo, 'normal')], -700, 100, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    r = muestra(m, tex[(tipo, 'rugosidad')], -700, 400, unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
    mu = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -350, -250)
    MEL.connect_material_expressions(c, 'RGB', mu, 'A'); MEL.connect_material_expressions(constante3(m, tinte, -700, -400), '', mu, 'B')
    MEL.connect_material_property(mu, '', unreal.MaterialProperty.MP_BASE_COLOR)
    MEL.connect_material_property(nr, 'RGB', unreal.MaterialProperty.MP_NORMAL)
    MEL.connect_material_property(r, 'R', unreal.MaterialProperty.MP_ROUGHNESS)
    m.set_editor_property('two_sided', True)
    MEL.recompile_material(m); EAL.save_loaded_asset(m); mats[nombre] = m
for nombre, color, rug, met in (('techo', (0.2, 0.18, 0.16), 0.9, 0.0), ('lamina', (0.16, 0.19, 0.19), 0.45, 0.6), ('balcon', (0.62, 0.6, 0.56), 0.8, 0.0)):
    m = material('M_' + nombre.capitalize())
    MEL.connect_material_property(constante3(m, color, -400, 0), '', unreal.MaterialProperty.MP_BASE_COLOR)
    MEL.connect_material_property(constante(m, rug, -400, 200), '', unreal.MaterialProperty.MP_ROUGHNESS)
    MEL.connect_material_property(constante(m, met, -400, 300), '', unreal.MaterialProperty.MP_METALLIC)
    m.set_editor_property('two_sided', True)
    MEL.recompile_material(m); EAL.save_loaded_asset(m); mats[nombre] = m
log('materiales listos: %s' % ', '.join(mats))

# ---------- edificios (se borran antes: la reimportación dejaba la versión vieja) ----------
for viejo in list(mats) + ['pintado', 'arbol']:
    if EAL.does_asset_exist(DST + '/' + viejo): EAL.delete_asset(DST + '/' + viejo)
for o in importar('edificios.obj'):
    if isinstance(o, unreal.StaticMesh):
        nombre = o.get_name()
        if nombre in mats: o.set_material(0, mats[nombre])
        # sin Nanite: el importador lo activa solo y, con una malla de 1,8 km escalada x100, simplificaba los muros y faltaban triángulos
        ns = o.get_editor_property('nanite_settings'); ns.set_editor_property('enabled', False); o.set_editor_property('nanite_settings', ns)
        log('edificios: %s (%d materiales)' % (nombre, len(o.static_materials)))
        EAL.save_loaded_asset(o)

# ---------- árboles reales (glTF de Poly Haven), con Nanite para miles de copias ----------
for nombre in ('jacaranda_L0_hojas', 'jacaranda_L0_madera', 'island_tree_01_L0_hojas', 'island_tree_01_L0_madera'):
    carpeta = DST + '/Arboles/' + nombre
    if EAL.does_directory_exist(carpeta): EAL.delete_directory(carpeta)
    objs = importar(nombre + '.glb', carpeta)
    sm = [o for o in objs if isinstance(o, unreal.StaticMesh)]
    if not sm:  # el importador de glTF a veces devuelve solo la escena: se buscan las mallas en la carpeta
        sm = [unreal.load_asset(p) for p in EAL.list_assets(carpeta, recursive=True) if isinstance(unreal.load_asset(p), unreal.StaticMesh)]
    for o in sm:
        try:
            ns = o.get_editor_property('nanite_settings'); ns.set_editor_property('enabled', True); o.set_editor_property('nanite_settings', ns)
        except Exception as e: log('nanite %s: %s' % (nombre, e))
        EAL.save_loaded_asset(o)
        b = o.get_bounding_box()
        log('arbol %s -> %s  min %s max %s' % (nombre, o.get_path_name(), b.min, b.max))
with open(os.path.join(PROY, 'Saved', 'importar_ren3d.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(info))

"""Agua realista para el humedal El Burro: color de agua de humedal (verde oscuro con algo de café), oleaje fino con dos capas
del mapa de normales de agua (escalas y velocidades distintas), superficie muy lisa que refleja el cielo y las orillas (Lumen),
y más claridad del cielo en los ángulos rasantes (Fresnel). Reemplaza el material de la malla de agua del suelo."""
import unreal
EAL, MEL = unreal.EditorAssetLibrary, unreal.MaterialEditingLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
D = '/Game/Kennedy/Suelo'
t = unreal.AssetImportTask(); t.set_editor_property('filename', r'C:\Users\ACER\REN3D-realista\data3d\waternormals.jpg')
t.set_editor_property('destination_path', D + '/Tex'); t.set_editor_property('automated', True); t.set_editor_property('replace_existing', True); t.set_editor_property('save', True)
tools.import_asset_tasks([t]); nrm = unreal.load_asset(t.get_editor_property('imported_object_paths')[0])
nrm.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_NORMALMAP); nrm.set_editor_property('srgb', False); EAL.save_loaded_asset(nrm)

if EAL.does_asset_exist(D + '/M_AguaReal'): EAL.delete_asset(D + '/M_AguaReal')
m = tools.create_asset('M_AguaReal', D, unreal.Material, unreal.MaterialFactoryNew()); m.set_editor_property('two_sided', True)
def ex(cls, x, y): return MEL.create_material_expression(m, cls, x, y)
def capa(escala, vel, y):  # coordenadas (las UV del OBJ van en metros / 8) escaladas y desplazándose
    tc = ex(unreal.MaterialExpressionTextureCoordinate, -1400, y); tc.set_editor_property('u_tiling', escala); tc.set_editor_property('v_tiling', escala)
    pn = ex(unreal.MaterialExpressionPanner, -1150, y); pn.set_editor_property('speed_x', vel[0]); pn.set_editor_property('speed_y', vel[1])
    MEL.connect_material_expressions(tc, '', pn, 'Coordinate')
    s = ex(unreal.MaterialExpressionTextureSample, -900, y); s.set_editor_property('texture', nrm); s.set_editor_property('sampler_type', unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    MEL.connect_material_expressions(pn, '', s, 'UVs'); return s
a, b = capa(2.2, (0.012, 0.007), -200), capa(0.7, (-0.006, 0.01), 150)
mezcla = ex(unreal.MaterialExpressionLinearInterpolate, -600, 0)
MEL.connect_material_expressions(a, 'RGB', mezcla, 'A'); MEL.connect_material_expressions(b, 'RGB', mezcla, 'B')
k = ex(unreal.MaterialExpressionConstant, -800, 400); k.set_editor_property('r', 0.5); MEL.connect_material_expressions(k, '', mezcla, 'Alpha')
plano = ex(unreal.MaterialExpressionConstant3Vector, -600, 300); plano.set_editor_property('constant', unreal.LinearColor(0, 0, 1, 1))
suave = ex(unreal.MaterialExpressionLinearInterpolate, -350, 100)  # oleaje suave: 45 % del relieve del mapa
MEL.connect_material_expressions(plano, '', suave, 'A'); MEL.connect_material_expressions(mezcla, '', suave, 'B')
k2 = ex(unreal.MaterialExpressionConstant, -600, 450); k2.set_editor_property('r', 0.45); MEL.connect_material_expressions(k2, '', suave, 'Alpha')
MEL.connect_material_property(suave, '', unreal.MaterialProperty.MP_NORMAL)
# color: agua de humedal en el centro, algo más clara y del color del cielo en ángulo rasante (Fresnel)
hondo = ex(unreal.MaterialExpressionConstant3Vector, -600, -600); hondo.set_editor_property('constant', unreal.LinearColor(0.012, 0.03, 0.025, 1))
rasante = ex(unreal.MaterialExpressionConstant3Vector, -600, -450); rasante.set_editor_property('constant', unreal.LinearColor(0.05, 0.08, 0.085, 1))
fr = ex(unreal.MaterialExpressionFresnel, -600, -300); fr.set_editor_property('exponent', 4.0)
col = ex(unreal.MaterialExpressionLinearInterpolate, -300, -500)
MEL.connect_material_expressions(hondo, '', col, 'A'); MEL.connect_material_expressions(rasante, '', col, 'B'); MEL.connect_material_expressions(fr, '', col, 'Alpha')
MEL.connect_material_property(col, '', unreal.MaterialProperty.MP_BASE_COLOR)
for prop, v, y in ((unreal.MaterialProperty.MP_ROUGHNESS, 0.03, 600), (unreal.MaterialProperty.MP_SPECULAR, 0.7, 700), (unreal.MaterialProperty.MP_METALLIC, 0.0, 800)):
    c = ex(unreal.MaterialExpressionConstant, -300, y); c.set_editor_property('r', v); MEL.connect_material_property(c, '', prop)
MEL.recompile_material(m); EAL.save_loaded_asset(m)
agua = unreal.load_asset(D + '/agua.agua')
agua.set_material(0, m); EAL.save_loaded_asset(agua)
unreal.log('[Kennedy360] agua realista lista')

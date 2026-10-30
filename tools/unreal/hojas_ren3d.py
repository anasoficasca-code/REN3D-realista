"""Material de follaje para las hojas de los árboles de Poly Haven: el material que trae el glTF las dejaba gris azuladas.
Color de la textura con un tinte verde, recorte por el alfa de la hoja, modelo de sombreado de follaje de dos caras (la luz
atraviesa la hoja) y su mapa de normales."""
import unreal
EAL, MEL = unreal.EditorAssetLibrary, unreal.MaterialEditingLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
B = '/Game/Kennedy/Ren3D/Arboles'
for n, hoja, tinte in (('jacaranda_L0_hojas', 'jacaranda_tree_leaves', (0.85, 1.05, 0.6)), ('island_tree_01_L0_hojas', 'island_tree_01_leaves', (0.85, 1.05, 0.65))):
    base = '%s/%s/%s' % (B, n, n)
    dif = unreal.load_asset('%s/Textures/%s_diff-%s_alpha' % (base, hoja, hoja)); nor = unreal.load_asset('%s/Textures/%s_nor_gl' % (base, hoja))
    ruta = B + '/M_Follaje_' + n
    if EAL.does_asset_exist(ruta): EAL.delete_asset(ruta)
    m = tools.create_asset('M_Follaje_' + n, B, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property('blend_mode', unreal.BlendMode.BLEND_MASKED); m.set_editor_property('two_sided', True)
    m.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_TWO_SIDED_FOLIAGE)
    m.set_editor_property('used_with_instanced_static_meshes', True); m.set_editor_property('used_with_nanite', True)
    t = MEL.create_material_expression(m, unreal.MaterialExpressionTextureSample, -800, -200); t.set_editor_property('texture', dif)
    k = MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -800, -400); k.set_editor_property('constant', unreal.LinearColor(tinte[0], tinte[1], tinte[2], 1))
    mu = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -450, -250)
    MEL.connect_material_expressions(t, 'RGB', mu, 'A'); MEL.connect_material_expressions(k, '', mu, 'B')
    MEL.connect_material_property(mu, '', unreal.MaterialProperty.MP_BASE_COLOR)
    MEL.connect_material_property(t, 'A', unreal.MaterialProperty.MP_OPACITY_MASK)
    ss = MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -800, 300); ss.set_editor_property('constant', unreal.LinearColor(0.25, 0.4, 0.08, 1))
    MEL.connect_material_property(ss, '', unreal.MaterialProperty.MP_SUBSURFACE_COLOR)
    nn = MEL.create_material_expression(m, unreal.MaterialExpressionTextureSample, -800, 50); nn.set_editor_property('texture', nor)
    nn.set_editor_property('sampler_type', unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL); MEL.connect_material_property(nn, 'RGB', unreal.MaterialProperty.MP_NORMAL)
    r = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -800, 500); r.set_editor_property('r', 0.75)
    MEL.connect_material_property(r, '', unreal.MaterialProperty.MP_ROUGHNESS)
    MEL.recompile_material(m); EAL.save_loaded_asset(m)
    sm = unreal.load_asset('%s/StaticMeshes/%s' % (base, n))
    for i in range(len(sm.static_materials)): sm.set_material(i, m)
    EAL.save_loaded_asset(sm)
    unreal.log('[Kennedy360] follaje %s listo' % n)

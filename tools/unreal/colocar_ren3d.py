"""Pone en el nivel Kennedy los edificios REN3D (tres mallas: ladrillo, pintado, techo) y siembra los árboles como instancias
(HISM). El OBJ entra a Unreal en centímetros y con los ejes (este, -alto, -norte): se escala x100 y queda en (este, sur, alto) sin girar, en
quedar en (este, sur, alto) de la georreferencia Cesium."""
import json, os, unreal

PROY = r'C:\Users\ACER\Documents\Unreal Projects\Kennedy360'
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.load_level('/Game/Kennedy/Kennedy')
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
info = []
for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith('REN3D_'): eas.destroy_actor(a)
GIRO = unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0)  # el OBJ ya viene en (este, norte, alto): el importador lo deja en (este, sur, alto)
for parte in ('ladrillo', 'pintado', 'techo'):
    m = unreal.load_asset('/Game/Kennedy/Ren3D/%s.%s' % (parte, parte))
    act = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, 0), GIRO)
    act.static_mesh_component.set_static_mesh(m)
    act.set_actor_label('REN3D_edificios_' + parte); act.set_actor_scale3d(unreal.Vector(100, 100, 100))
    info.append('edificios %s: %s' % (parte, act.get_actor_bounds(False)))
# árboles: una malla instanciada (HISM) colgada de un actor
D = json.load(open(os.path.join(PROY, 'Importar', 'arboles.json'), encoding='utf-8'))
arbol = unreal.load_asset('/Game/Kennedy/Ren3D/arbol.arbol')
host = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, 0))
host.set_actor_label('REN3D_arboles')
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
raiz = sds.k2_gather_subobject_data_for_instance(host)[0]
h, motivo = sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=raiz, new_class=unreal.HierarchicalInstancedStaticMeshComponent, blueprint_context=None))
comp = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h))
comp.set_static_mesh(arbol)
comp.set_editor_property('cast_shadow', True)
suelo = D['suelo']
tr = []
for x, y, alto, rot, wf, _ in D['arboles']:
    w = alto * wf
    tr.append(unreal.Transform(unreal.Vector(x * 100, -y * 100, (suelo - 0.3) * 100), unreal.Rotator(roll=90.0, pitch=0.0, yaw=rot), unreal.Vector(w * 100, alto * 100, w * 100)))
comp.add_instances(tr, False)
info.append('arboles: %d instancias' % comp.get_instance_count())
les.save_current_level()
with open(os.path.join(PROY, 'Saved', 'colocar_ren3d.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(str(s) for s in info))

"""Deja UNA sola georreferencia (Kennedy) como la predeterminada y enlaza a ella la malla de Google y el sol."""
import unreal
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.load_level('/Game/Kennedy/Kennedy')
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actores = eas.get_all_level_actors()
mia = [a for a in actores if a.get_actor_label() == 'Georreferencia_Kennedy'][0]
for a in actores:
    if isinstance(a, unreal.CesiumGeoreference) and a != mia:
        unreal.log('[Kennedy360] borrando georreferencia sobrante %s %s' % (a.get_actor_label(), a.get_origin_longitude_latitude_height()))
        eas.destroy_actor(a)
mia.tags = [unreal.Name('DEFAULT_GEOREFERENCE')]
for a in eas.get_all_level_actors():
    if isinstance(a, (unreal.Cesium3DTileset, unreal.CesiumSunSky)):
        try:
            a.set_editor_property('georeference', mia)
            unreal.log('[Kennedy360] %s -> georreferencia Kennedy' % a.get_actor_label())
        except Exception as e:
            unreal.log_warning('[Kennedy360] %s: %s' % (a.get_actor_label(), e))
les.save_current_level()
with open(r'C:\Users\ACER\Documents\Unreal Projects\Kennedy360\Saved\fijar_geo.txt', 'w', encoding='utf-8') as f:
    for a in eas.get_all_level_actors():
        if isinstance(a, (unreal.CesiumGeoreference, unreal.Cesium3DTileset, unreal.CesiumSunSky)):
            g = None
            try: g = a.get_editor_property('georeference')
            except Exception: pass
            f.write('%s %s tags=%s geo=%s\n' % (a.get_actor_label(), a.get_class().get_name(), [str(t) for t in a.tags], g.get_actor_label() if g else g))

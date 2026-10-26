"""Ajustes para el giro de 360°: teselas en TODAS las direcciones (no solo lo que ve la cámara), sin descartar lo lejano
por bruma, y sin nubes volumétricas (salían como manchas blancas sobre la ciudad)."""
import unreal
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.load_level('/Game/Kennedy/Kennedy')
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
info = []
for a in eas.get_all_level_actors():
    if isinstance(a, unreal.Cesium3DTileset):
        a.set_editor_property('enable_frustum_culling', False)          # baja también lo que queda detrás de la cámara
        a.set_editor_property('enforce_culled_screen_space_error', True)
        a.set_editor_property('culled_screen_space_error', 8.0)         # lo que está fuera de cuadro, con buen detalle igual
        a.set_editor_property('enable_fog_culling', False)              # el horizonte lejano no se descarta
        a.set_editor_property('maximum_cached_bytes', 4 * 1024 * 1024 * 1024)
        info.append('tileset ajustado')
    for comp in a.get_components_by_class(unreal.VolumetricCloudComponent):
        comp.set_visibility(False)
        comp.set_editor_property('hidden_in_game', True)
        info.append('nubes volumetricas ocultas en ' + a.get_actor_label())
les.save_current_level()
with open(r'C:\Users\ACER\Documents\Unreal Projects\Kennedy360\Saved\ajustes_giro.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(info))

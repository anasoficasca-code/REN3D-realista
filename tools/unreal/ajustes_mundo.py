import unreal
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.load_level('/Game/Kennedy/Kennedy')
mundo = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
ws = mundo.get_world_settings()
ws.set_editor_property('enable_world_bounds_checks', False)  # recomendado por Cesium (coordenadas planetarias)
les.save_current_level()
unreal.log('[Kennedy360] world bounds checks desactivado')

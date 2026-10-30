"""Secuencia 'Arriba': cámara cenital a ALTO m sobre el centro del humedal El Burro (centro de la zona del proyecto), lente de 24 mm.
Se renderiza con ConfigPrueba: -LevelSequence=/Game/Kennedy/Arriba -MoviePipelineConfig=/Game/Kennedy/ConfigPrueba"""
import unreal
ALTO, SUELO = 900.0, 15.8
EAL = unreal.EditorAssetLibrary; tools = unreal.AssetToolsHelpers.get_asset_tools()
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les.load_level('/Game/Kennedy/Kennedy')
cam = eas.spawn_actor_from_class(unreal.CineCameraActor, unreal.Vector(0, 0, (SUELO + ALTO) * 100), unreal.Rotator(roll=0.0, pitch=-90.0, yaw=0.0))
cc = cam.get_cine_camera_component(); cc.set_editor_property('current_focal_length', 24.0)
fs = cc.get_editor_property('focus_settings'); fs.set_editor_property('focus_method', unreal.CameraFocusMethod.DISABLE); cc.set_editor_property('focus_settings', fs)
fb = cc.get_editor_property('filmback'); fb.set_editor_property('sensor_width', 36.0); fb.set_editor_property('sensor_height', 20.25); cc.set_editor_property('filmback', fb)
if EAL.does_asset_exist('/Game/Kennedy/Arriba'): EAL.delete_asset('/Game/Kennedy/Arriba')
seq = tools.create_asset('Arriba', '/Game/Kennedy', unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
seq.set_display_rate(unreal.FrameRate(24, 1)); seq.set_playback_start(0); seq.set_playback_end(2)
b = unreal.MovieSceneSequenceExtensions.add_spawnable_from_instance(seq, cam)
eas.destroy_actor(cam)
cut = seq.add_track(unreal.MovieSceneCameraCutTrack); cs = cut.add_section(); cs.set_range(0, 3)
cs.set_camera_binding_id(seq.get_binding_id(b) if hasattr(seq, 'get_binding_id') else unreal.MovieSceneSequenceExtensions.get_binding_id(seq, b))
EAL.save_loaded_asset(seq)
cfg = unreal.load_asset('/Game/Kennedy/ConfigPrueba')
out = cfg.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
out.set_editor_property('custom_start_frame', 0); out.set_editor_property('custom_end_frame', 1)
EAL.save_loaded_asset(cfg)
unreal.log('[Kennedy360] secuencia Arriba lista')

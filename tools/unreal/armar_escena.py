"""Arma la escena Kennedy360: malla fotorrealista de Google (Cesium ion), sol y cielo de Bogotá, postproceso
tipo render de maqueta, cámara que gira alrededor del humedal El Burro y configuraciones de render (Movie Render Queue)."""
import math, os, unreal

PROY = r'C:\Users\ACER\Documents\Unreal Projects\Kennedy360'
LOG = os.path.join(PROY, 'Saved', 'armar_escena.txt')
lineas = []
def log(s):
    lineas.append(str(s)); unreal.log('[Kennedy360] ' + str(s))

TOKEN = open(os.path.join(PROY, 'Config', 'cesium_ion_token.txt'), encoding='utf-8').read().strip()  # token local (no va a GitHub)
LAT, LON, H = 4.640683, -74.149778, 2548.0  # centro del humedal El Burro (georreferencia del modelo) y altura elipsoidal del suelo
FRAMES, RADIO_M, ALTO_M, FOCAL = 72, 900.0, 380.0, 24.0

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary

# ---------- nivel ----------
if EAL.does_asset_exist('/Game/Kennedy/Kennedy'):
    EAL.delete_asset('/Game/Kennedy/Kennedy')
les.new_level('/Game/Kennedy/Kennedy')
log('nivel creado')

# ---------- georreferencia ----------
geo = eas.spawn_actor_from_class(unreal.CesiumGeoreference, unreal.Vector(0, 0, 0))
geo.set_origin_longitude_latitude_height(unreal.Vector(LON, LAT, H))
geo.set_actor_label('Georreferencia_Kennedy')
log('georreferencia: ' + str(geo.get_origin_longitude_latitude_height()))

# ---------- malla fotorrealista de Google ----------
ts = eas.spawn_actor_from_class(unreal.Cesium3DTileset, unreal.Vector(0, 0, 0))
ts.set_actor_label('Google_Fotorrealista')
ts.set_editor_property('tileset_source', unreal.TilesetSource.FROM_CESIUM_ION)
ts.set_editor_property('ion_asset_id', 2275207)  # Google Photorealistic 3D Tiles
ts.set_editor_property('ion_access_token', TOKEN)
ts.set_editor_property('maximum_screen_space_error', 4.0)  # más detalle que el valor por defecto (16)
ts.set_editor_property('maximum_cached_bytes', 2 * 1024 * 1024 * 1024)
ts.set_editor_property('maximum_simultaneous_tile_loads', 40)
ts.set_editor_property('enable_occlusion_culling', False)
log('tileset: asset %s, sse %s' % (ts.get_editor_property('ion_asset_id'), ts.get_editor_property('maximum_screen_space_error')))

# ---------- sol y cielo (Bogotá, tarde) ----------
sky = eas.spawn_actor_from_class(unreal.CesiumSunSky, unreal.Vector(0, 0, 0))
sky.set_actor_label('Sol_y_cielo')
for k, v in (('time_zone', -5.0), ('solar_time', 16.4), ('day', 15), ('month', 1), ('year', 2026), ('use_daylight_saving_time', False)):
    try:
        sky.set_editor_property(k, v)
    except Exception as e:
        log('sol: no se pudo poner %s: %s' % (k, e))
try:
    sky.update_sun()
except Exception as e:
    log('update_sun: %s' % e)
log('sol: hora solar %s' % sky.get_editor_property('solar_time'))

# bruma de altura suave (profundidad, como en las maquetas renderizadas)
fog = eas.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0))
fog.set_actor_label('Bruma')
fc = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
fc.set_editor_property('fog_density', 0.0035)
fc.set_editor_property('fog_height_falloff', 0.04)
fc.set_editor_property('fog_inscattering_luminance', unreal.LinearColor(0.55, 0.65, 0.8, 1.0))

# ---------- postproceso tipo render de maqueta ----------
ppv = eas.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 0))
ppv.set_actor_label('Postproceso_render')
ppv.set_editor_property('unbound', True)
ps = ppv.get_editor_property('settings')
def pp(nombre, valor):
    try:
        ps.set_editor_property('override_' + nombre, True)
    except Exception:
        pass
    try:
        ps.set_editor_property(nombre, valor)
    except Exception as e:
        log('postproceso: %s: %s' % (nombre, e))
pp('auto_exposure_method', unreal.AutoExposureMethod.AEM_HISTOGRAM)
pp('auto_exposure_min_brightness', 12.5)
pp('auto_exposure_max_brightness', 14.5)
pp('auto_exposure_bias', 0.3)
pp('bloom_intensity', 0.35)
pp('vignette_intensity', 0.28)
pp('color_saturation', unreal.Vector4(1.08, 1.08, 1.08, 1.0))
pp('color_contrast', unreal.Vector4(1.06, 1.06, 1.06, 1.0))
pp('white_temp', 6200.0)
pp('lens_flare_intensity', 0.0)
pp('motion_blur_amount', 0.0)
ppv.set_editor_property('settings', ps)
log('postproceso listo')

# ---------- cámara de cine ----------
cam = eas.spawn_actor_from_class(unreal.CineCameraActor, unreal.Vector(0, -RADIO_M * 100, ALTO_M * 100))
cam.set_actor_label('Camara_giro')
cc = cam.get_cine_camera_component()
cc.set_editor_property('current_focal_length', FOCAL)
fs = cc.get_editor_property('focus_settings')
fs.set_editor_property('focus_method', unreal.CameraFocusMethod.DISABLE)  # todo nítido, como en las maquetas
cc.set_editor_property('focus_settings', fs)
fb = cc.get_editor_property('filmback')
fb.set_editor_property('sensor_width', 36.0); fb.set_editor_property('sensor_height', 20.25)  # 16:9
cc.set_editor_property('filmback', fb)

# ---------- secuencia: vuelta completa alrededor del humedal ----------
if EAL.does_asset_exist('/Game/Kennedy/Giro'):
    EAL.delete_asset('/Game/Kennedy/Giro')
seq = tools.create_asset('Giro', '/Game/Kennedy', unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
seq.set_display_rate(unreal.FrameRate(24, 1))
seq.set_playback_start(0)
seq.set_playback_end(FRAMES)
b = seq.add_possessable(cam)
tr = b.add_track(unreal.MovieScene3DTransformTrack)
sec = tr.add_section()
sec.set_range(0, FRAMES + 1)
canales = sec.get_all_channels()  # x, y, z, roll, pitch, yaw, sx, sy, sz
objetivo = unreal.Vector(0, 0, 25 * 100)  # mira un poco por encima del suelo
for f in range(FRAMES + 1):
    a = 2 * math.pi * f / FRAMES
    x, y, z = math.sin(a) * RADIO_M * 100, -math.cos(a) * RADIO_M * 100, ALTO_M * 100
    dx, dy, dz = objetivo.x - x, objetivo.y - y, objetivo.z - z
    yaw = math.degrees(math.atan2(dy, dx))
    pitch = math.degrees(math.atan2(dz, math.hypot(dx, dy)))
    t = unreal.FrameNumber(f)
    for ch, val in zip(canales[:6], (x, y, z, 0.0, pitch, yaw)):
        k = ch.add_key(t, val)
        try:
            k.set_interpolation_mode(unreal.RichCurveInterpMode.RCIM_LINEAR)
        except Exception:
            pass
# los ángulos no deben "volver" de 180 a -180 entre fotogramas: se desenrolla el yaw
yaw_ch = canales[5]
prev = None
for k in yaw_ch.get_keys():
    v = k.get_value()
    if prev is not None:
        while v - prev > 180: v -= 360
        while v - prev < -180: v += 360
        k.set_value(v)
    prev = v
cut = seq.add_track(unreal.MovieSceneCameraCutTrack)
cs = cut.add_section()
cs.set_range(0, FRAMES + 1)
cs.set_camera_binding_id(seq.get_binding_id(b) if hasattr(seq, 'get_binding_id') else unreal.MovieSceneSequenceExtensions.get_binding_id(seq, b))
EAL.save_loaded_asset(seq)
log('secuencia: %d fotogramas' % FRAMES)

# ---------- configuraciones de render ----------
def config(nombre, desde, hasta, ancho, alto, muestras, calentamiento):
    ruta = '/Game/Kennedy/' + nombre
    if EAL.does_asset_exist(ruta):
        EAL.delete_asset(ruta)
    cfg = tools.create_asset(nombre, '/Game/Kennedy', unreal.MoviePipelinePrimaryConfig, None)
    out = cfg.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
    out.set_editor_property('output_directory', unreal.DirectoryPath(os.path.join(PROY, 'Saved', 'Giro').replace('\\', '/')))
    out.set_editor_property('file_name_format', 'giro_{frame_number}')
    out.set_editor_property('output_resolution', unreal.IntPoint(ancho, alto))
    out.set_editor_property('use_custom_playback_range', True)
    out.set_editor_property('custom_start_frame', desde)
    out.set_editor_property('custom_end_frame', hasta)
    out.set_editor_property('zero_pad_frame_numbers', 3)
    cfg.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
    cfg.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_JPG)
    aa = cfg.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)
    aa.set_editor_property('override_anti_aliasing', True)
    aa.set_editor_property('anti_aliasing_method', unreal.AntiAliasingMethod.AAM_NONE)
    aa.set_editor_property('spatial_sample_count', 1)
    aa.set_editor_property('temporal_sample_count', muestras)
    aa.set_editor_property('engine_warm_up_count', calentamiento)  # tiempo para que bajen las teselas de Google antes del primer fotograma
    aa.set_editor_property('render_warm_up_count', 64)
    aa.set_editor_property('use_camera_cut_for_warm_up', False)
    go = cfg.find_or_add_setting_by_class(unreal.MoviePipelineGameOverrideSetting)
    go.set_editor_property('cinematic_quality_settings', True)
    go.set_editor_property('flush_streaming_managers', True)
    EAL.save_loaded_asset(cfg)
    log('config %s: fotogramas %d-%d, %dx%d, %d muestras' % (nombre, desde, hasta, ancho, alto, muestras))

config('ConfigPrueba', 0, 1, 1920, 1080, 8, 400)
config('ConfigGiro', 0, FRAMES, 1920, 1080, 8, 400)

les.save_current_level()
log('nivel guardado')
with open(LOG, 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(lineas))

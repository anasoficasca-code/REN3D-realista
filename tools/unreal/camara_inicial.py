"""La cámara del giro queda activa desde que arranca el juego y mirando como el fotograma 0,
para que durante la espera inicial Cesium baje justo las teselas que se van a ver."""
import math, unreal
RADIO_M, ALTO_M = 900.0, 380.0
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.load_level('/Game/Kennedy/Kennedy')
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
cam = [a for a in eas.get_all_level_actors() if a.get_actor_label() == 'Camara_giro'][0]
x, y, z = 0.0, -RADIO_M * 100, ALTO_M * 100
dx, dy, dz = -x, -y, 25 * 100 - z
yaw = math.degrees(math.atan2(dy, dx)); pitch = math.degrees(math.atan2(dz, math.hypot(dx, dy)))
cam.set_actor_location_and_rotation(unreal.Vector(x, y, z), unreal.Rotator(roll=0.0, pitch=pitch, yaw=yaw), False, False)
cam.set_editor_property('auto_activate_for_player', unreal.AutoReceiveInput.PLAYER0)
les.save_current_level()
unreal.log('[Kennedy360] camara inicial: pitch %.1f yaw %.1f' % (pitch, yaw))

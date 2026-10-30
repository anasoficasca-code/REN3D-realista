"""Script de inicio del proyecto: si existe Saved/vista_arriba.pedido, al cargar el visor pone la cámara a 1.500 m sobre el
humedal El Burro mirando hacia abajo y borra el pedido (se hace una sola vez)."""
import os, unreal
PEDIDO = os.path.join(unreal.Paths.project_saved_dir(), 'vista_arriba.pedido')
if os.path.exists(PEDIDO):
    estado = {'n': 0, 'h': None}
    def tick(dt):
        estado['n'] += 1
        if estado['n'] < 300: return  # que termine de cargar el nivel y el visor
        try:
            unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(
                unreal.Vector(0, 0, 150000), unreal.Rotator(roll=0.0, pitch=-89.9, yaw=0.0))
            unreal.log('[Kennedy360] vista desde arriba lista')
            os.remove(PEDIDO)
        finally:
            unreal.unregister_slate_post_tick_callback(estado['h'])
    estado['h'] = unreal.register_slate_post_tick_callback(tick)

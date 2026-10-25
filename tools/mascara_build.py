"""Máscara de huellas de edificios (blanco = libre, negro = edificio) para recortar la geometría de Google
donde la Maqueta dibuja su propio edificio. Se calcula aquí una sola vez (antes se dibujaba en el navegador
y se subía a la tarjeta gráfica 51 veces, una por celda: 44 MB cada vez).
Mismo encuadre que el shader: 2,5 m por píxel, coordenadas del modelo, norte arriba."""
import json, os
from PIL import Image, ImageDraw

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data3d')
XM, YM, R = 10800, 6400, 2.5
W, H = int(XM // R + (XM % R > 0)), int(YM // R + (YM % R > 0))

def mascara(B, salida):
    im = Image.new('L', (W, H), 255)
    dr = ImageDraw.Draw(im)
    n = 0
    for b in B:
        p = b['pts']
        if len(p) > 1 and p[0] == p[-1]: p = p[:-1]
        if len(p) < 3: continue
        xs = [q[0] for q in p]; ys = [q[1] for q in p]
        if (max(xs) - min(xs)) < 2 and (max(ys) - min(ys)) < 2 and b['h'] <= 3: continue  # la misma basura que descarta buildChunks
        poly = [(x / R, (YM - y) / R) for x, y in p]
        dr.polygon(poly, fill=0, outline=0, width=2)  # el borde agranda cada huella ~2,5 m, como antes
        n += 1
    im.save(salida, optimize=True)
    print(os.path.basename(salida), n, 'huellas', '%.2f MB' % (os.path.getsize(salida) / 1e6))

os.makedirs(os.path.join(D, 'edif'), exist_ok=True)
mascara(json.load(open(os.path.join(D, 'buildings.json'))), os.path.join(D, 'edif', 'mascara.png'))
mascara(json.load(open(os.path.join(D, 'buildings_humedal.json'))), os.path.join(D, 'edif', 'mascara_humedal.png'))

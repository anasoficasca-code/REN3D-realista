"""Suelo propio de la zona del proyecto para Unreal (dentro de la zona se recorta la malla de Google):
- suelo.obj: base de pasto (disco de la zona), parques, agua, vías de asfalto (ancho según la clase) y andenes, con UV en metros.
- carro.obj: sedán (perfil extruido, cabina de vidrio, llantas) de 1 m = 1 unidad; carros.json: posición y rumbo de cada carro
  sobre los carriles de las vías (densidad según la clase de vía).
Mismas coordenadas que exportar_edificios.py: metros al este y al norte del origen de la georreferencia de Unreal.
Uso: python tools/unreal/exportar_suelo.py [carpeta_salida]"""
import json, math, os, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
OUT = sys.argv[1] if len(sys.argv) > 1 else r'C:\Users\ACER\Documents\Unreal Projects\Kennedy360\Importar'
MXg = 111320 * math.cos(math.radians(4.63)); MYg = 110540.0
DX = -5193.24 - (-74.149778 + 74.17) * MXg; DY = -2090.06 - (4.640683 - 4.63) * MYg
def en(x, y): return x + DX, y + DY
ZC = en(7437, 3271); RADIO = 900.0; SUELO = 15.8
def enZona(x, y, m=0): return (x - ZC[0]) ** 2 + (y - ZC[1]) ** 2 < (RADIO + m) ** 2
rnd = random.Random(5)

V, VT, F = [], [], {m: [] for m in ('pasto', 'parque', 'agua', 'via', 'anden', 'linea')}
def v(x, y, z): V.append((x, y, z)); return len(V)
def vt(u, w): VT.append((u, w)); return len(VT)
def tri(m, a, b, c): F[m].append((a, b, c))
def triangular(poly):  # recorte de orejas (antihorario); el abanico desde el centro hacía picos en el agua y los parques cóncavos
    idx = list(range(len(poly))); tris = []
    cruz = lambda a, b, c: (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    dentro = lambda p, a, b, c: cruz(a, b, p) >= -1e-9 and cruz(b, c, p) >= -1e-9 and cruz(c, a, p) >= -1e-9
    while len(idx) > 3:
        hecho = False
        for k in range(len(idx)):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % len(idx)]; a, b, c = poly[i0], poly[i1], poly[i2]
            if cruz(a, b, c) <= 1e-9: continue
            if any(dentro(poly[j], a, b, c) for j in idx if j not in (i0, i1, i2)): continue
            tris.append((i0, i1, i2)); idx.pop(k); hecho = True; break
        if not hecho:
            k = max(range(len(idx)), key=lambda k: cruz(poly[idx[k - 1]], poly[idx[k]], poly[idx[(k + 1) % len(idx)]]))
            tris.append((idx[k - 1], idx[k], idx[(k + 1) % len(idx)])); idx.pop(k)
    if len(idx) == 3: tris.append(tuple(idx))
    return tris
def poligono(m, pts, z, esc=4.0):
    pts = [p for i, p in enumerate(pts) if i == 0 or math.dist(p, pts[i - 1]) > 0.05]
    if len(pts) < 3: return
    if sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts))) < 0: pts = pts[::-1]
    ids = [(v(p[0], p[1], z), vt(p[0] / esc, p[1] / esc)) for p in pts]
    for a, b, c in triangular(pts): tri(m, ids[a], ids[b], ids[c])
def cinta(m, pts, ancho, z, desp=0.0, esc_u=4.0, esc_v=None):  # franja a lo largo de una polilínea (UV: u a lo largo, v a lo ancho)
    acum = 0.0; prev = None
    for i, p in enumerate(pts):
        a = pts[max(0, i - 1)]; b = pts[min(len(pts) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; l = math.hypot(dx, dy) or 1; nx, ny = -dy / l, dx / l
        if i: acum += math.hypot(p[0] - pts[i - 1][0], p[1] - pts[i - 1][1])
        o1, o2 = desp - ancho / 2, desp + ancho / 2
        L_ = (v(p[0] + nx * o1, p[1] + ny * o1, z), vt(acum / esc_u, 0)); R_ = (v(p[0] + nx * o2, p[1] + ny * o2, z), vt(acum / esc_u, 1 if esc_v is None else ancho / esc_v))
        if prev: tri(m, prev[0], prev[1], R_); tri(m, prev[0], R_, L_)
        prev = (L_, R_)

# base: disco de pasto en toda la zona
pts = [(ZC[0] + math.cos(a / 96 * 2 * math.pi) * (RADIO + 30), ZC[1] + math.sin(a / 96 * 2 * math.pi) * (RADIO + 30)) for a in range(96)]
poligono('pasto', pts, SUELO - 0.05, 6.0)
for p in json.load(open(os.path.join(RAIZ, 'data3d', 'parques.json'), encoding='utf-8')):
    q = [en(*a) for a in p['pts']]
    if any(enZona(*a) for a in q): poligono('parque', q[:-1] if q[0] == q[-1] else q, SUELO + 0.02, 5.0)
for w in json.load(open(os.path.join(RAIZ, 'data3d', 'water_bodies.json'), encoding='utf-8')):
    q = [en(*a) for a in w['pts']]
    if not any(enZona(*a) for a in q): continue
    cerrado = len(q) > 3 and math.dist(q[0], q[-1]) < 1
    if cerrado: poligono('agua', q[:-1], SUELO + 0.04, 8.0)
    else: cinta('agua', q, 6 if 'uebrada' in w.get('tipo', '') else 8, SUELO + 0.04, esc_u=8.0, esc_v=8.0)
ANCHO = {'major': 15.0, 'mid': 10.0, 'local': 6.5}
CARROS_POR_M = {'major': 0.0, 'mid': 0.0, 'local': 1 / 60.0}  # quietos solo en las calles locales (estacionados); en las avenidas andan (trafico.json)
N = json.load(open(os.path.join(RAIZ, 'data3d', 'net.json'), encoding='utf-8'))
carros = []
for cls, e in N['edges']:
    q = [en(*a) for a in e]
    if len(q) < 2 or not any(enZona(*a, -40) for a in q): continue
    w = ANCHO.get(cls, 6.5)
    cinta('anden', q, w + 4.0, SUELO + 0.07, esc_u=2.0, esc_v=2.0)   # andén de 2 m a cada lado (debajo de la vía)
    cinta('via', q, w, SUELO + 0.10, esc_u=6.0, esc_v=6.0)
    if cls != 'local':
        cinta('linea', q, 0.15, SUELO + 0.12, esc_u=1.0)          # línea central
    # carros sobre los carriles, con rumbo de la vía
    for i in range(len(q) - 1):
        a, b = q[i], q[i + 1]; L = math.dist(a, b)
        if L < 1: continue
        dx, dy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        k = L * CARROS_POR_M.get(cls, 0.02); n = int(k) + (1 if rnd.random() < k - int(k) else 0)
        for _ in range(n):
            s = rnd.random() * L; sentido = 1 if rnd.random() < 0.5 else -1
            carril = sentido * (w / 4 if cls != 'local' else 1.5)
            x, y = a[0] + dx * s - dy * carril, a[1] + dy * s + dx * carril
            if enZona(x, y): carros.append([round(x, 2), round(y, 2), round(math.degrees(math.atan2(dy * sentido, dx * sentido)), 1), rnd.randrange(8)])
with open(os.path.join(OUT, 'suelo.obj'), 'w') as f:
    f.write('# REN3D - suelo de la zona del humedal El Burro\n')
    for p in V: f.write('v %.2f %.2f %.2f\n' % p)
    for t in VT: f.write('vt %.4f %.4f\n' % t)
    for m, fs in F.items():
        if not fs: continue
        f.write('g %s\nusemtl %s\n' % (m, m))
        for t in fs: f.write('f %s\n' % ' '.join('%d/%d' % c for c in t))
json.dump({'suelo': SUELO, 'carros': carros}, open(os.path.join(OUT, 'carros.json'), 'w'))
print('suelo: %d triangulos; carros: %d' % (sum(len(x) for x in F.values()), len(carros)))

# ---------- tráfico en movimiento: rutas largas encadenando avenidas, trayectoria de cada carro ----------
# Las aristas de la red se encadenan por sus extremos (misma clase, la continuación más recta) hasta rutas de 600+ m. Cada carro
# va por su carril derecho a velocidad constante (8 a 14 m/s) durante la secuencia de 30 s (720 cuadros a 24 por segundo);
# se guarda una clave cada 12 cuadros: [cuadro, x, y, rumbo en grados (este = 0, antihorario)].
FPS, DUR, PASO = 24, 30.0, 12
ext = {}
lineas = []
for cls, e in N['edges']:
    if cls == 'local': continue
    q = [en(*a) for a in e]
    if len(q) < 2 or not any(enZona(*a, 300) for a in q): continue
    k = len(lineas); lineas.append((cls, q))
    for extremo in (q[0], q[-1]): ext.setdefault((round(extremo[0]), round(extremo[1])), []).append(k)
usada = [False] * len(lineas)
def seguir(ruta, cls):
    while True:
        a, b = ruta[-2], ruta[-1]; dx, dy = b[0] - a[0], b[1] - a[1]; l = math.hypot(dx, dy) or 1
        mejor, mc = None, 0.7
        for k in ext.get((round(b[0]), round(b[1])), []):
            if usada[k] or lineas[k][0] != cls: continue
            q = lineas[k][1]; q = q if math.dist(q[0], b) < 2 else q[::-1]
            if len(q) < 2: continue
            ex, ey = q[1][0] - q[0][0], q[1][1] - q[0][1]; c = (dx * ex + dy * ey) / (l * (math.hypot(ex, ey) or 1))
            if c > mc: mejor, mc = (k, q), c
        if not mejor: return ruta
        usada[mejor[0]] = True; ruta += mejor[1][1:]
rutas = []
for k, (cls, q) in enumerate(lineas):
    if usada[k]: continue
    usada[k] = True; r = seguir(list(q), cls); r = seguir(r[::-1], cls)[::-1] if len(r) > 1 else r
    L = sum(math.dist(r[i], r[i + 1]) for i in range(len(r) - 1))
    if L > 300: rutas.append((cls, r, L))
def punto(r, s):  # posición y dirección a distancia s a lo largo de la ruta
    for i in range(len(r) - 1):
        l = math.dist(r[i], r[i + 1])
        if s <= l or i == len(r) - 2:
            f = min(1.0, s / l) if l else 0; dx, dy = (r[i + 1][0] - r[i][0]) / (l or 1), (r[i + 1][1] - r[i][1]) / (l or 1)
            return r[i][0] + dx * l * f, r[i][1] + dy * l * f, dx, dy
        s -= l
trafico = []
for cls, r, L in rutas:
    w = ANCHO[cls]; sep = 24.0 if cls == 'major' else 40.0
    for sentido in (1, -1):
        rr = r if sentido == 1 else r[::-1]
        for s0 in [x * sep + rnd.random() * sep * 0.6 for x in range(int(L / sep))]:
            v = rnd.uniform(8.0, 14.0)
            if s0 + v * DUR > L: continue  # que no se salga de la ruta durante la secuencia
            claves = []
            for fr in range(0, int(DUR * FPS) + 1, PASO):
                x, y, dx, dy = punto(rr, s0 + v * fr / FPS)
                carril = w / 4  # carril derecho
                claves.append([fr, round(x + dy * carril, 2), round(y - dx * carril, 2), round(math.degrees(math.atan2(dy, dx)), 1)])
            if any(enZona(c[1], c[2], 150) for c in claves): trafico.append({'tipo': rnd.random() < 0.28, 'color': rnd.randrange(8), 'claves': claves})
json.dump({'suelo': SUELO, 'fps': FPS, 'cuadros': int(DUR * FPS), 'carros': trafico}, open(os.path.join(OUT, 'trafico.json'), 'w'))
print('trafico: %d rutas, %d carros en movimiento' % (len(rutas), len(trafico)))

# ---------- carros: sedán y camioneta (SUV), frente hacia +X, una sola malla con cuatro materiales ----------
def carro(nombre, cuerpo, cabina, ancho, ruedas, radio):
    CV, CF = [], {'pintura': [], 'vidrio': [], 'llanta': [], 'luces': []}
    def cv(x, y, z): CV.append((x, y, z)); return len(CV)
    def extruir(m, perfil, an, dy=0.0):
        n = len(perfil); iz = [cv(p[0], dy - an / 2, p[1]) for p in perfil]; de = [cv(p[0], dy + an / 2, p[1]) for p in perfil]
        for i in range(1, n - 1): CF[m].append((iz[0], iz[i + 1], iz[i])); CF[m].append((de[0], de[i], de[i + 1]))
        for i in range(n): j = (i + 1) % n; CF[m].append((iz[i], iz[j], de[j])); CF[m].append((iz[i], de[j], de[i]))
    extruir('pintura', cuerpo, ancho)
    extruir('vidrio', cabina, ancho - 0.22)
    xs = [p[0] for p in cuerpo]; fr, tr = max(xs), min(xs)
    for dy in (-ancho * 0.33, ancho * 0.33):  # faros adelante y luces traseras
        extruir('luces', [(fr - 0.02, 0.62), (fr + 0.03, 0.62), (fr + 0.03, 0.74), (fr - 0.02, 0.74)], 0.36, dy)
        extruir('luces', [(tr - 0.03, 0.72), (tr + 0.02, 0.72), (tr + 0.02, 0.84), (tr - 0.03, 0.84)], 0.36, dy)
    for sx in ruedas:
        for sy in (-ancho / 2 + 0.11, ancho / 2 - 0.11):
            extruir('llanta', [(sx + math.cos(a / 16 * 2 * math.pi) * radio, radio + math.sin(a / 16 * 2 * math.pi) * radio) for a in range(16)], 0.24, sy)
    with open(os.path.join(OUT, nombre + '.obj'), 'w') as f:
        f.write('# REN3D - %s\n' % nombre)
        for p in CV: f.write('v %.3f %.3f %.3f\n' % p)
        for p in CV: f.write('vt %.3f %.3f\n' % (p[0] / 4.5 + 0.5, p[2] / 1.8))
        f.write('g %s\n' % nombre)  # un solo grupo: una sola malla con varias ranuras de material
        for m, fs in CF.items():
            f.write('usemtl %s\n' % m)
            for t in fs: f.write('f %s\n' % ' '.join('%d/%d' % (c, c) for c in t))
carro('sedan', [(-2.18, 0.30), (2.20, 0.30), (2.26, 0.48), (2.20, 0.70), (1.60, 0.84), (0.80, 0.92), (-1.40, 0.96), (-2.10, 0.92), (-2.26, 0.66)],
      [(-1.36, 0.92), (-0.90, 1.38), (0.32, 1.40), (0.98, 0.92)], 1.78, (-1.40, 1.45), 0.32)
carro('camioneta', [(-2.30, 0.40), (2.30, 0.40), (2.36, 0.62), (2.28, 0.94), (1.70, 1.06), (1.00, 1.10), (-2.20, 1.14), (-2.34, 0.80)],
      [(-2.10, 1.12), (-1.95, 1.72), (0.62, 1.74), (1.12, 1.10)], 1.88, (-1.48, 1.52), 0.37)
print('carros listos')

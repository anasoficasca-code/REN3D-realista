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
CARROS_POR_M = {'major': 1 / 14.0, 'mid': 1 / 22.0, 'local': 1 / 60.0}
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

# ---------- carro: sedán de 4,3 m, frente hacia +X (perfil lateral extruido) ----------
CV, CF = [], {'pintura': [], 'vidrio': [], 'llanta': []}
def cv(x, y, z): CV.append((x, y, z)); return len(CV)
def extruir(m, perfil, ancho, z0=0.0):  # perfil (x, alto) extruido a lo ancho (eje y)
    n = len(perfil); iz = [cv(p[0], -ancho / 2, p[1] + z0) for p in perfil]; de = [cv(p[0], ancho / 2, p[1] + z0) for p in perfil]
    for i in range(1, n - 1): CF[m].append((iz[0], iz[i + 1], iz[i])); CF[m].append((de[0], de[i], de[i + 1]))
    for i in range(n): j = (i + 1) % n; CF[m].append((iz[i], iz[j], de[j])); CF[m].append((iz[i], de[j], de[i]))
extruir('pintura', [(-2.12, 0.34), (2.12, 0.34), (2.18, 0.54), (2.10, 0.74), (1.52, 0.86), (0.78, 0.93), (-1.50, 0.95), (-2.06, 0.89), (-2.18, 0.62)], 1.78)
extruir('vidrio', [(-1.28, 0.93), (-0.84, 1.36), (0.28, 1.36), (0.96, 0.93)], 1.52)
extruir('pintura', [(-0.86, 1.34), (0.30, 1.34), (0.30, 1.40), (-0.86, 1.40)], 1.40)
for sx in (-1.36, 1.42):
    for sy in (-0.80, 0.80):
        rueda = [(sx + math.cos(a / 14 * 2 * math.pi) * 0.33, 0.33 + math.sin(a / 14 * 2 * math.pi) * 0.33) for a in range(14)]
        n0 = len(CV); extruir('llanta', rueda, 0.24)
        for k in range(n0, len(CV)): x, y, z = CV[k]; CV[k] = (x, y + sy, z)
with open(os.path.join(OUT, 'carro.obj'), 'w') as f:
    f.write('# REN3D - sedan\n')
    for p in CV: f.write('v %.3f %.3f %.3f\n' % p)
    for p in CV: f.write('vt %.3f %.3f\n' % (p[0] / 4.3 + 0.5, p[2] / 1.4))
    for m, fs in CF.items():
        f.write('g %s\nusemtl %s\n' % (m, m))
        for t in fs: f.write('f %s\n' % ' '.join('%d/%d' % (c, c) for c in t))
print('carro listo')

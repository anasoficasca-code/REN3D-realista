/* ============ TORRES DE LADRILLO CON BALCONES-HUERTA (Kennedy, 4.64416, -74.15350) ============
   Conjunto de torres de 12 pisos como el de la foto de referencia: costados en ladrillo a la vista con ventanas de marco blanco,
   columnas de paneles gris oscuro y, en cada torre, columnas de balcones de losa curva con baranda metálica de barrotes.
   En cada balcón hay una huerta: jardineras a lo largo de la baranda con hortalizas, aromáticas, tomates y flores, una
   jardinera colgada por fuera y una matera grande en la esquina.
   Uso: const T = crearTorres(THREE, T3, { liviano }); T.agregar([{ W: [[x, z], ...], h, y0 }]); T.actualizar(camara) en cada cuadro. */
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

export function crearTorres(THREE, T3, opt = {}) {
  const LIV = !!opt.liviano, PISO = 3, PX = 64; // 3 m por piso; 64 px por metro en las texturas
  let sem = 11; const rnd = () => (sem = (sem * 16807) % 2147483647) / 2147483647;
  const lienzo = (w, h, f, alfa) => { const c = document.createElement('canvas'); c.width = w; c.height = h; f(c.getContext('2d'), w, h); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; if (alfa) { t.wrapS = THREE.RepeatWrapping; } return t; };

  /* ---------- atlas de fachada: 4 variantes x 3 tipos (ladrillo, panel gris, fondo de balcón); cada celda = 3 m x 1 piso ---------- */
  const CW = 3 * PX, CH = PISO * PX;
  const atlas = lienzo(CW * 4, CH * 3, (g) => {
    const ladrillo = (x0, y0) => {
      g.fillStyle = '#7d4430'; g.fillRect(x0, y0, CW, CH); // mortero oscuro
      const hb = 0.075 * PX, lb = 0.24 * PX;
      for (let f = 0, y = y0; y < y0 + CH; f++, y += hb) for (let x = x0 - (f % 2) * lb / 2; x < x0 + CW; x += lb) {
        const r = 146 + rnd() * 34, gg = 80 + rnd() * 22, b = 58 + rnd() * 18; // ladrillo terracota apagado g.fillStyle = `rgb(${r},${gg},${b})`;
        g.fillRect(Math.max(x0, x + 1), y + 1, Math.min(lb - 2, x0 + CW - x - 1), hb - 1.5); }
      g.fillStyle = 'rgba(0,0,0,0.10)'; g.fillRect(x0, y0 + CH - 0.22 * PX, CW, 0.22 * PX); // línea de placa
    };
    const panel = (x0, y0) => { g.fillStyle = '#4a4e54'; g.fillRect(x0, y0, CW, CH);
      for (let k = 0; k < 300; k++) { g.fillStyle = `rgba(${rnd() < 0.5 ? '0,0,0' : '255,255,255'},0.04)`; g.fillRect(x0 + rnd() * CW, y0 + rnd() * CH, 6, 6); }
      g.fillStyle = '#3a3d42'; for (const fx of [0, 1.5, 3]) g.fillRect(x0 + fx * PX - 1, y0, 2, CH); g.fillRect(x0, y0 + CH - 2, CW, 2); g.fillRect(x0, y0 + CH * 0.5, CW, 1.5); };
    // ventana: marco blanco, vidrio con reflejo de cielo, divisiones y cortina según la variante
    const ventana = (x0, y0, x, y, w, h, v) => {
      const X = x0 + x * PX, Y = y0 + CH - (y + h) * PX, W = w * PX, H = h * PX;
      g.fillStyle = '#f1efe9'; g.fillRect(X - 4, Y - 4, W + 8, H + 8);
      const gr = g.createLinearGradient(X, Y, X + W * 0.3, Y + H); gr.addColorStop(0, '#9fb8cc'); gr.addColorStop(0.45, '#2c3b48'); gr.addColorStop(1, '#1a232b'); g.fillStyle = gr; g.fillRect(X, Y, W, H);
      if (v === 0) { g.fillStyle = 'rgba(236,232,222,0.88)'; g.fillRect(X, Y, W * 0.42, H); g.fillRect(X + W * 0.58, Y, W * 0.42, H); } // cortinas blancas
      if (v === 1) { g.fillStyle = 'rgba(205,70,120,0.9)'; g.fillRect(X, Y, W * 0.5, H); g.fillStyle = 'rgba(236,232,222,0.85)'; g.fillRect(X + W * 0.5, Y, W * 0.5, H * 0.9); } // cortina fucsia (como en la foto)
      if (v === 2) { g.fillStyle = 'rgba(220,214,200,0.5)'; g.fillRect(X, Y, W, H * 0.18); }
      g.fillStyle = '#f1efe9'; g.fillRect(X + W / 2 - 2, Y, 4, H); g.fillRect(X, Y + H * 0.28, W, 3); // divisiones
      g.fillStyle = 'rgba(0,0,0,0.25)'; g.fillRect(X - 4, Y + H + 4, W + 8, 5); // alfeizar
    };
    for (let v = 0; v < 4; v++) {
      ladrillo(v * CW, 0); if (v < 3) ventana(v * CW, 0, 0.7, 0.95, 1.6, 1.45, v);
      panel(v * CW, CH); if (v < 3) ventana(v * CW, CH, 0.75, 0.95, 1.5, 1.4, v);
      // fondo de balcón: panel gris con puerta-ventana corrediza de piso a techo
      panel(v * CW, CH * 2); ventana(v * CW, CH * 2, 0.35, 0.05, 2.3, 2.45, v === 3 ? 2 : v);
    }
  });
  // baranda de barrotes (transparente entre barrotes)
  const barrotes = lienzo(64, 128, (g) => { g.clearRect(0, 0, 64, 128); g.fillStyle = '#2a2d31';
    for (let x = 2; x < 64; x += 8) g.fillRect(x, 0, 2.5, 128); g.fillRect(0, 0, 64, 7); g.fillRect(0, 60, 64, 3); g.fillRect(0, 122, 64, 6); }, true);

  const env = T3.env || null;
  const M = {
    fachada: new THREE.MeshStandardMaterial({ map: atlas, roughness: 0.82, envMap: env, envMapIntensity: 0.4, side: THREE.DoubleSide }),
    concreto: new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.88, side: THREE.DoubleSide }),
    baranda: new THREE.MeshStandardMaterial({ map: barrotes, alphaTest: 0.5, side: THREE.DoubleSide, metalness: 0.6, roughness: 0.45, envMap: env }),
    partes: new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.8 }),
    plantas: new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.85 })
  };

  /* ---------- utilidades ---------- */
  const prep = (g, col) => { if (g.index) g = g.toNonIndexed(); if (!g.attributes.normal) g.computeVertexNormals(); const n = g.attributes.position.count;
    if (!g.attributes.uv) g.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(n * 2), 2));
    const c = new Float32Array(n * 3); for (let i = 0; i < n; i++) { const v = col || [1, 1, 1]; c[i * 3] = v[0]; c[i * 3 + 1] = v[1]; c[i * 3 + 2] = v[2]; }
    const o = new THREE.BufferGeometry(); o.setAttribute('position', g.attributes.position); o.setAttribute('normal', g.attributes.normal); o.setAttribute('uv', g.attributes.uv); o.setAttribute('color', new THREE.BufferAttribute(c, 3)); return o; };
  const MATA = (() => { const g = new THREE.IcosahedronGeometry(1, 1); const p = g.attributes.position, nn = new Float32Array(p.count * 3);
    for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i), z = p.getZ(i), l = Math.hypot(x, y, z) || 1, k = 0.82 + 0.18 * Math.sin(x * 9.1 + z * 7.3) * Math.cos(y * 5.7); p.setXYZ(i, x * k, y * k, z * k); nn[i * 3] = x / l; nn[i * 3 + 1] = y / l; nn[i * 3 + 2] = z / l; }
    g.setAttribute('normal', new THREE.BufferAttribute(nn, 3)); return g; })();
  // cuadrilátero vertical de fachada con la celda (col, fila) del atlas
  const quad = (Pa, a, b, y0, y1, col, fila, u0 = 0, u1 = 1) => {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute([a[0], y0, a[1], b[0], y0, b[1], b[0], y1, b[1], a[0], y0, a[1], b[0], y1, b[1], a[0], y1, a[1]], 3));
    const U0 = (col + 0.004 + u0 * 0.992) / 4, U1 = (col + 0.004 + u1 * 0.992) / 4, V0 = 1 - (fila + 1) / 3 + 0.002, V1 = 1 - fila / 3 - 0.002, vv = V0 + (V1 - V0) * Math.min(1, (y1 - y0) / PISO);
    g.setAttribute('uv', new THREE.Float32BufferAttribute([U0, V0, U1, V0, U1, vv, U0, V0, U1, vv, U0, vv], 2)); g.computeVertexNormals(); Pa.push(prep(g)); };

  const grupo = new THREE.Group(); grupo.name = 'torresBalcones'; T3.scene.add(grupo);
  const cercanas = [], CERCA = 360;
  const api = { grupo, torres: 0, balcones: 0 };
  api.actualizar = (cam) => { for (const c of cercanas) { const v = Math.hypot(c.x - cam.position.x, c.z - cam.position.z, c.y - cam.position.y) < CERCA; if (c.m.visible !== v) c.m.visible = v; } };

  api.agregar = (lista) => {
    const B = { fachada: [], concreto: [], baranda: [], partes: [] };
    for (const T of lista) {
      const W = T.W, n = W.length, y0 = T.y0, h = T.h, pisos = Math.max(1, Math.round((h - y0) / PISO)), hp = (h - y0) / pisos;
      let area = 0; for (let i = 0; i < n; i++) { const a = W[i], b = W[(i + 1) % n]; area += a[0] * b[1] - b[0] * a[1]; }
      const sgn = area > 0 ? 1 : -1; api.torres++;
      sem = 1 + (Math.abs(Math.round(W[0][0] * 31 + W[0][1] * 17)) % 2147483646);
      let Lm = 0, ax = 1, az = 0; for (let i = 0; i < n; i++) { const a = W[i], b = W[(i + 1) % n], l = Math.hypot(b[0] - a[0], b[1] - a[1]); if (l > Lm) { Lm = l; ax = (b[0] - a[0]) / l; az = (b[1] - a[1]) / l; } }
      const PL = []; // plantas de esta torre (malla propia: solo se dibujan de cerca)
      let cx = 0, cz = 0; W.forEach(p => { cx += p[0]; cz += p[1]; }); cx /= n; cz /= n;
      for (let i = 0; i < n; i++) {
        const a = W[i], b = W[(i + 1) % n], L = Math.hypot(b[0] - a[0], b[1] - a[1]); if (L < 0.05) continue;
        const ux = (b[0] - a[0]) / L, uz = (b[1] - a[1]) / L, nx = uz * sgn, nz = -ux * sgn; // normal hacia afuera
        const par = Math.abs(ux * ax + uz * az) > 0.7;
        // tramos del muro: [desde, hasta, fila del atlas, ¿balcón?]
        let tramos;
        if (!par && L >= 6) { const bw = Math.min(5.2, L - 3), m0 = (L - bw) / 2; tramos = [[0, m0, 0, false], [m0, m0 + bw, 2, true], [m0 + bw, L, 0, false]]; } // frente: ladrillo + columna central de balcones
        else if (par && L >= 8) tramos = [[0, L, 0, false]]; // costado de ladrillo
        else if (par && L >= 3.8) tramos = [[0, L, 2, true]]; // retroceso con balcones
        else tramos = [[0, L, 1, false]]; // panel gris
        for (const [t0, t1, fila, balcon] of tramos) {
          const lt = t1 - t0, bays = Math.max(1, Math.round(lt / 3)), bw = lt / bays;
          for (let k = 0; k < bays; k++) {
            const s0 = t0 + k * bw, s1 = s0 + bw, A = [a[0] + ux * s0, a[1] + uz * s0], Bq = [a[0] + ux * s1, a[1] + uz * s1];
            for (let f = 0; f < pisos; f++) {
              const r0 = rnd(), v = bw < 1.8 ? 3 : r0 < 0.5 ? 0 : r0 < 0.58 ? 1 : 2; // tramos angostos: sin ventana; pocas cortinas fucsia, como en la foto
              quad(B.fachada, A, Bq, y0 + f * hp, y0 + (f + 1) * hp, bw < 1.8 && fila !== 2 ? 3 : (fila === 2 ? Math.min(v, 2) : v), fila, Math.max(0, 0.5 - bw / 6), Math.min(1, 0.5 + bw / 6));
            }
          }
          if (!balcon) continue;
          // columna de balcones curvos (del piso 2 al último) con su huerta
          const w = lt - 0.3, mid = (t0 + t1) / 2, ox = a[0] + ux * mid, oz = a[1] + uz * mid, D = 1.15, C = 0.38;
          const P2W = (t, d) => [ox + ux * t + nx * d, oz + uz * t + nz * d]; // (a lo largo, hacia afuera) -> mundo
          const borde = []; const NP = 14; // borde exterior de la losa: lados rectos + frente curvo
          borde.push([-w / 2, 0.02]); for (let k = 0; k <= NP; k++) { const t = -w / 2 + w * k / NP, s = 1 - (2 * t / w) ** 2; borde.push([t, D + C * s]); } borde.push([w / 2, 0.02]);
          for (let f = 1; f < pisos; f++) {
            const yb = y0 + f * hp; api.balcones++;
            // losa curva (con canto)
            const sh = new THREE.Shape(borde.map(([t, d]) => new THREE.Vector2(t, d)));
            const gl = new THREE.ExtrudeGeometry(sh, { depth: 0.18, bevelEnabled: false, curveSegments: 1 }); gl.rotateX(Math.PI / 2); // (t, d) -> (x = t, z = d), espesor hacia abajo
            gl.applyMatrix4(new THREE.Matrix4().set(ux, 0, nx, ox, 0, 1, 0, yb, uz, 0, nz, oz, 0, 0, 0, 1));
            B.concreto.push(prep(gl, [0.42, 0.44, 0.47]));
            // baranda de barrotes por el borde, con pasamanos
            const camino = borde.slice(1, -1), Pb = [], Ub = []; let s = 0;
            const lados = [[[-w / 2, 0.05], camino[0]], ...camino.slice(0, -1).map((p, k) => [p, camino[k + 1]]), [camino[camino.length - 1], [w / 2, 0.05]]];
            for (const [p, q] of lados) { const pw = P2W(p[0], p[1]), qw = P2W(q[0], q[1]), l = Math.hypot(q[0] - p[0], q[1] - p[1]);
              Pb.push(pw[0], yb, pw[1], qw[0], yb, qw[1], qw[0], yb + 1.05, qw[1], pw[0], yb, pw[1], qw[0], yb + 1.05, qw[1], pw[0], yb + 1.05, pw[1]);
              Ub.push(s / 0.5, 0, (s + l) / 0.5, 0, (s + l) / 0.5, 1, s / 0.5, 0, (s + l) / 0.5, 1, s / 0.5, 1); s += l;
              const gp = new THREE.BoxGeometry(0.05, 0.05, l + 0.04); gp.lookAt(new THREE.Vector3(qw[0] - pw[0], 0, qw[1] - pw[1])); gp.translate((pw[0] + qw[0]) / 2, yb + 1.06, (pw[1] + qw[1]) / 2); B.partes.push(prep(gp, [0.14, 0.15, 0.16])); }
            const gb = new THREE.BufferGeometry(); gb.setAttribute('position', new THREE.Float32BufferAttribute(Pb, 3)); gb.setAttribute('uv', new THREE.Float32BufferAttribute(Ub, 2)); gb.computeVertexNormals(); B.baranda.push(prep(gb));
            // HUERTA DEL BALCÓN
            const jard = Math.max(2, Math.round(w / 1.05)), TER = [0.6, 0.31, 0.19], MAD = [0.4, 0.27, 0.16];
            for (let k = 0; k < jard; k++) { // jardineras por dentro de la baranda, siguiendo la curva
              const t = -w / 2 + (k + 0.5) * w / jard, sF = 1 - (2 * t / w) ** 2, d = D + C * sF - 0.32, p = P2W(t, d), ang = Math.atan2(-8 * C * t / (w * w), 1);
              const gj = new THREE.BoxGeometry(w / jard - 0.08, 0.42, 0.34); gj.rotateY(-Math.atan2(uz, ux) + ang * 0); gj.translate(p[0], yb + 0.21, p[1]);
              B.partes.push(prep(gj, rnd() < 0.6 ? TER : MAD));
              for (let m = 0; m < 3; m++) { // matas: hortalizas, aromáticas, tomates y flores
                const pm = P2W(t + (m - 1) * (w / jard) * 0.3, d + (rnd() - 0.5) * 0.1), tipo = rnd(), r = 0.14 + rnd() * 0.1, hh = r * (tipo < 0.25 ? 1.8 : 1.1);
                const cc = tipo < 0.25 ? [0.18, 0.36, 0.1] : tipo < 0.55 ? [0.3, 0.52, 0.16] : tipo < 0.75 ? [0.28, 0.4, 0.3] : [0.22, 0.42, 0.14];
                PL.push(prep(MATA.clone().scale(r, hh, r).translate(pm[0], yb + 0.42 + hh * 0.7, pm[1]), cc));
                if (tipo < 0.25) for (let q = 0; q < 3; q++) PL.push(prep(new THREE.IcosahedronGeometry(0.045, 0).translate(pm[0] + (rnd() - 0.5) * r, yb + 0.5 + rnd() * hh * 1.2, pm[1] + (rnd() - 0.5) * r), [0.78, 0.08, 0.05])); // tomates
                if (tipo > 0.85) for (let q = 0; q < 4; q++) PL.push(prep(new THREE.IcosahedronGeometry(0.035, 0).translate(pm[0] + (rnd() - 0.5) * r * 1.4, yb + 0.45 + hh * 1.3, pm[1] + (rnd() - 0.5) * r * 1.4), rnd() < 0.5 ? [0.95, 0.75, 0.1] : [0.6, 0.3, 0.75])); // flores
              }
            }
            // jardinera colgada por fuera de la baranda, al frente, con plantas que caen
            const pc = P2W(0, D + C + 0.14), gc = new THREE.BoxGeometry(Math.min(1.4, w * 0.4), 0.22, 0.22); gc.rotateY(-Math.atan2(uz, ux)); gc.translate(pc[0], yb + 0.95, pc[1]); B.partes.push(prep(gc, TER));
            for (let m = 0; m < 4; m++) { const pm = P2W((m - 1.5) * Math.min(1.4, w * 0.4) / 4, D + C + 0.16); PL.push(prep(MATA.clone().scale(0.13, 0.32, 0.13).translate(pm[0], yb + 0.82, pm[1]), [0.2, 0.42, 0.12])); }
            // matera grande con planta alta en una esquina
            const pe = P2W((rnd() < 0.5 ? -1 : 1) * (w / 2 - 0.35), 0.4);
            B.partes.push(prep(new THREE.CylinderGeometry(0.24, 0.18, 0.5, 12).translate(pe[0], yb + 0.25, pe[1]), TER));
            PL.push(prep(MATA.clone().scale(0.3, 0.6, 0.3).translate(pe[0], yb + 0.95, pe[1]), [0.16, 0.33, 0.1]));
          }
        }
      }
      // cubierta y cara interior del antepecho (la huerta de la terraza la pone huertas_techo.js)
      let tri = []; try { tri = THREE.ShapeUtils.triangulateShape(W.map(q => new THREE.Vector2(q[0], q[1])), []); } catch (e) {}
      if (tri.length) { const P = []; for (const t of tri) for (const k of (sgn > 0 ? [t[0], t[2], t[1]] : t)) P.push(W[k][0], h - 0.45, W[k][1]); const gr = new THREE.BufferGeometry(); gr.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); gr.computeVertexNormals(); B.concreto.push(prep(gr, [0.55, 0.55, 0.56])); }
      for (let i = 0; i < n; i++) { const a = W[i], b = W[(i + 1) % n], L = Math.hypot(b[0] - a[0], b[1] - a[1]); if (L < 0.05) continue; const ux = (b[0] - a[0]) / L, uz = (b[1] - a[1]) / L, ix = -uz * sgn * 0.2, iz = ux * sgn * 0.2;
        const g = new THREE.BufferGeometry(); const A = [a[0] + ix, a[1] + iz], Bq = [b[0] + ix, b[1] + iz];
        g.setAttribute('position', new THREE.Float32BufferAttribute([A[0], h - 0.45, A[1], A[0], h, A[1], Bq[0], h, Bq[1], A[0], h - 0.45, A[1], Bq[0], h, Bq[1], Bq[0], h - 0.45, Bq[1], A[0], h, A[1], a[0], h, a[1], b[0], h, b[1], A[0], h, A[1], b[0], h, b[1], Bq[0], h, Bq[1]], 3)); g.computeVertexNormals(); B.concreto.push(prep(g, [0.62, 0.62, 0.62])); }
      if (PL.length && !LIV) { const m = new THREE.Mesh(mergeGeometries(PL), M.plantas); m.visible = false; m.receiveShadow = true; grupo.add(m); cercanas.push({ m, x: cx, y: h / 2, z: cz }); }
    }
    for (const [k, L] of Object.entries(B)) { if (!L.length) continue; const m = new THREE.Mesh(mergeGeometries(L), M[k]); m.castShadow = !LIV; m.receiveShadow = !LIV; grupo.add(m); }
  };
  return api;
}

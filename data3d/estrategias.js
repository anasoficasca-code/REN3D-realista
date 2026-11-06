/* ============ ESTRATEGIAS DE LA PROPUESTA (modo Kennedy) ============
   Nombres y numeración del Excel de las 9 estrategias; ubicaciones de data3d/estrategias.json (tools/estrategias_build.py):
   E3 Corabastos reducido (Corabastos) · E4 Orgánicos y hongos (distrito biotecnológico) · E5 Corredor biótico (humedales)
   E8 Red de huertas (huertas en lotes baldíos, en cubiertas de vivienda en altura y en viviendas, del shapefile de lotes).
   E1 Bavaria Común la dibuja data3d/bavaria_plan.js. E2, E6, E7 y E9 no tienen una ubicación única: desde la leyenda se abre su
   red de actores. Las capas sobre techos (cubiertas, viviendas) se pintan a la altura de cada edificio; las demás a ras del suelo. */
export async function iniciarEstrategias({ THREE, T3, lw, Y0 = 2.0 }) {
  const D = await (await fetch('data3d/estrategias.json?v=3')).json();
  const esc = D.escala || 0.5, grupo = new THREE.Group(); grupo.name = 'estrategias'; T3.scene.add(grupo);
  const CAPA = {};
  const W2 = (flat) => { const n = flat.length / 2, W = []; for (let k = 0; k < n; k++) W.push(lw(flat[k * 2] * esc, flat[k * 2 + 1] * esc)); return W; };
  for (const e of D.estrategias) {
    const gr = new THREE.Group(); gr.visible = false; grupo.add(gr); // al iniciar, todas apagadas
    for (const c of e.capas) {
      const P = [], I = [], L = []; let vc = 0;
      const anillo = (flat, y) => {
        const W = W2(flat), n = W.length;
        let tri = []; try { tri = THREE.ShapeUtils.triangulateShape(W.map(q => new THREE.Vector2(q[0], q[1])), []); } catch (er) { return; }
        const b = vc; for (const q of W) { P.push(q[0], y, q[1]); vc++; } for (const t of tri) I.push(b + t[0], b + t[1], b + t[2]);
        for (let k = 0; k < n; k++) { const a = W[k], d = W[(k + 1) % n]; L.push(a[0], y + 0.05, a[1], d[0], y + 0.05, d[1]); }
      };
      for (const l of c.lotes) anillo(l, Y0 + 0.35);                                   // a ras del suelo
      for (const t of c.techos || []) anillo(t.slice(0, -1), t[t.length - 1] / 10 + 0.3); // sobre el techo de cada edificio del lote
      const col = new THREE.Color(c.c), techo = (c.techos || []).length > 0;
      const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); g.setIndex(I);
      const relleno = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: techo ? 0.55 : 0.4, side: THREE.DoubleSide, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -4, polygonOffsetUnits: -8 }));
      relleno.renderOrder = 4; relleno.frustumCulled = false;
      const gl = new THREE.BufferGeometry(); gl.setAttribute('position', new THREE.Float32BufferAttribute(L, 3));
      const borde = new THREE.LineSegments(gl, new THREE.LineBasicMaterial({ color: col.clone().multiplyScalar(techo ? 0.75 : 1), transparent: true, opacity: 0.95, depthWrite: false }));
      borde.renderOrder = 5; borde.frustumCulled = false; gr.add(relleno, borde);
    }
    CAPA[e.id] = { gr, e };
  }

  // etiquetas en los sitios grandes y pocos (Corabastos, distrito, humedales, lotes baldíos); las huertas en techos van en la leyenda
  const css = document.createElement('style'); css.textContent = `
.es-et{position:fixed;z-index:8;transform:translate(-50%,-100%);pointer-events:none;padding:4px 9px;border-radius:9px;background:rgba(8,16,26,.86);border:1.5px solid var(--c);color:#e2f3ff;font:700 11px system-ui,-apple-system,"Segoe UI",sans-serif;white-space:nowrap}
.es-et b{color:var(--c);margin-right:5px}.es-et small{display:block;font-weight:500;color:#94a3b8;font-size:10px}.es-et::after{content:'';position:absolute;left:50%;top:100%;width:1.5px;height:12px;background:var(--c)}
@media(max-width:760px){.es-et{font-size:10px;padding:3px 7px}}`;
  document.head.appendChild(css);
  const ET = [];
  for (const e of D.estrategias) for (const c of e.capas) {
    if ((c.techos || []).length || c.lotes.length > 30) continue;
    const vistos = [];
    for (const l of c.lotes) {
      const n = l.length / 2; let x = 0, y = 0, a = 0;
      for (let k = 0; k < n; k++) { const p = [l[k * 2] * esc, l[k * 2 + 1] * esc], q = [l[((k + 1) % n) * 2] * esc, l[((k + 1) % n) * 2 + 1] * esc]; a += p[0] * q[1] - q[0] * p[1]; x += p[0]; y += p[1]; }
      if (Math.abs(a) / 2 < 3000) continue; x /= n; y /= n;
      if (vistos.some(v => Math.hypot(v[0] - x, v[1] - y) < 700)) continue; vistos.push([x, y]);
      const d = document.createElement('div'); d.className = 'es-et'; d.style.setProperty('--c', c.c); d.innerHTML = `<b>${e.id}</b>${e.n}${c.n !== e.n ? `<small>${c.n}</small>` : ''}`; document.body.appendChild(d);
      const w = lw(x, y); ET.push({ d, id: e.id, p: new THREE.Vector3(w[0], Y0 + 14, w[1]) });
    }
  }
  const v = new THREE.Vector3();
  const bucle = () => {
    const cam = T3.camera, W = innerWidth, H = innerHeight;
    for (const t of ET) {
      if (!CAPA[t.id].gr.visible) { t.d.style.display = 'none'; continue; }
      v.copy(t.p).project(cam); const fuera = v.z > 1 || v.x < -1.1 || v.x > 1.1 || v.y < -1.1 || v.y > 1.1;
      t.d.style.display = fuera ? 'none' : 'block'; if (!fuera) { t.d.style.left = ((v.x + 1) / 2 * W).toFixed(1) + 'px'; t.d.style.top = ((1 - v.y) / 2 * H).toFixed(1) + 'px'; }
    }
    requestAnimationFrame(bucle);
  };
  requestAnimationFrame(bucle);
  // las 9 estrategias del Excel, con o sin ubicación en el mapa
  const NOM = D.nombres || {}, COL = { E2: '#38bdf8', E6: '#e879f9', E7: '#facc15', E9: '#fb7185' };
  const lista = Object.keys(NOM).filter(k => k !== 'E1').sort((a, b) => +a.slice(1) - +b.slice(1)).map(k => {
    const e = D.estrategias.find(x => x.id === k);
    return e ? { id: k, n: e.n, c: e.c, det: e.capas.map(c => c.n).join(' · ') + ` · ${(e.area / 1e4).toLocaleString('es-CO', { maximumFractionDigits: 1 })} ha` }
      : { id: k, n: NOM[k], c: COL[k] || '#94a3b8', sinLugar: true, det: 'Sin una ubicación única en el mapa · toca para ver su red de actores' };
  });
  return {
    lista,
    ver: (id, on) => { if (CAPA[id]) CAPA[id].gr.visible = on; },
    // sitios de huerta en el suelo (lotes baldíos) para las colmenas y lombrices de la red biótica
    sitios: () => { const e = D.estrategias.find(x => x.id === 'E8'); const c = e && e.capas.find(x => /baldío/i.test(x.n)); return c ? c.lotes.map(l => ({ id: 'E8', n: 'Huerta en lote baldío', poly: W2(l) })) : []; }
  };
}

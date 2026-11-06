/* ============ REDES DE ACTORES (capa) ============
   data3d/actores.json (tools/actores_build.py, del Excel "Kennedy_9_Estrategias_Cada_Pestana_Actores_y_Relaciones").
   Por estrategia, 100 nodos y 112 relaciones etiquetadas. Se dibuja en 3D flotando sobre el territorio:
   - 13 procesos en anillo, cada uno con su ciclo de 5 roles propuestos (diagnóstico, acuerdos, ejecución, control, persona usuaria)
   - roles previos en el centro (más arriba); organismos, entorno, recursos e infraestructura en un anillo exterior más bajo
   - nodos con el color de su clase; relaciones con el color de su etiqueta (INF, AUT, CTRL, RET, DEP, CONS, BIO, MAT, AMB)
   E1 flota sobre Bavaria, E3 sobre Corabastos y E5 sobre el humedal El Burro; las demás (sin un lugar único) donde se mira.
   Los roles y vínculos propuestos son hipótesis: no equivalen a personas identificadas ni a relaciones comprobadas. */
const CLASE = {
  'Rol previo': { c: '#f59e0b', r: 5.5 }, 'Rol humano propuesto': { c: '#60a5fa', r: 3.6 }, 'Organismo': { c: '#34d399', r: 4.6 },
  'Entorno': { c: '#94a3b8', r: 4.6 }, 'Recurso': { c: '#22d3ee', r: 4.6 }, 'Infraestructura': { c: '#c084fc', r: 4.6 }
};
const TAGC = { INF: '#7dd3fc', CONS: '#a78bfa', AUT: '#f472b6', CTRL: '#fbbf24', RET: '#34d399', DEP: '#fb923c', BIO: '#86efac', AMB: '#cbd5e1', MAT: '#22d3ee' };

export async function iniciarActores({ THREE, T3, lw, OX, OZ, Y0 = 2.0 }) {
  const [A, BV, CO] = await Promise.all(['data3d/actores.json?v=1', 'data3d/bavaria.json?v=2', 'data3d/corabastos.json'].map(u => fetch(u).then(r => r.json()).catch(() => null)));
  if (!A) return null;
  const centro = (P) => { let x = 0, y = 0; for (const p of P) { x += p[0]; y += p[1]; } return lw(x / P.length, y / P.length); };
  const ANCLA = { E1: BV ? centro(BV.sitio) : null, E3: CO ? centro(CO.poly) : null, E5: [OX, OZ] };
  const esc = (s) => String(s || '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const grupo = new THREE.Group(); grupo.visible = false; T3.scene.add(grupo);
  const ST = { e: 'E1', on: false, tags: new Set(Object.keys(TAGC)), sel: null, proc: null, ancla: null };
  let R = null; // red construida: { E, P (pos por id), nodos, rel, mallas, ... }

  /* ---------- estilos y panel ---------- */
  const css = document.createElement('style'); css.textContent = `
#ar-pan{position:fixed;z-index:21;right:14px;top:14px;bottom:14px;width:min(400px,calc(100vw - 28px));overflow:auto;scrollbar-width:thin;padding:14px 15px;border-radius:16px;background:rgba(8,16,26,.94);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);border:1px solid rgba(125,211,252,.3);color:#e2f3ff;font:12px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif;display:none}
#ar-pan.on{display:block}
#ar-pan .cab{display:flex;align-items:flex-start;gap:10px}#ar-pan h4{margin:0;font-size:16px}#ar-pan .cab em{display:block;font-style:normal;color:#94a3b8;font-size:11px}
#ar-pan .x{margin-left:auto;flex:none;width:30px;height:30px;border:none;border-radius:8px;background:rgba(255,255,255,.07);color:#cbd5e1;font:700 16px system-ui;cursor:pointer}
#ar-pan .av{margin:8px 0;padding:7px 9px;border-radius:9px;background:rgba(251,191,36,.08);border:1px solid rgba(251,191,36,.25);color:#fde68a;font-size:10.5px}
#ar-pan h5{margin:12px 0 5px;font-size:9.5px;letter-spacing:.16em;color:#94a3b8;display:flex;justify-content:space-between}#ar-pan h5 span{letter-spacing:.02em;color:#64748b;font-weight:500}
#ar-pan .est{display:grid;grid-template-columns:repeat(3,1fr);gap:4px}
#ar-pan .est button{min-height:40px;padding:4px 6px;border:1px solid rgba(255,255,255,.08);border-radius:9px;background:rgba(255,255,255,.04);color:#cbd5e1;font:600 10.5px/1.2 system-ui,sans-serif;text-align:left;cursor:pointer}
#ar-pan .est button b{display:block;color:#7dd3fc;font-size:10px}#ar-pan .est button.on{background:#7dd3fc;color:#04121c;border-color:#7dd3fc}#ar-pan .est button.on b{color:#04121c}
#ar-pan .ley{display:flex;flex-wrap:wrap;gap:4px}
#ar-pan .ley button{display:flex;align-items:center;gap:5px;height:26px;padding:0 8px;border:none;border-radius:999px;background:rgba(255,255,255,.05);color:#cbd5e1;font:600 10.5px system-ui,sans-serif;cursor:pointer}
#ar-pan .ley button.off{opacity:.35}#ar-pan .ley i{width:9px;height:9px;border-radius:50%}#ar-pan .ley i.l{width:14px;height:3px;border-radius:2px}
#ar-pan .pr{display:flex;justify-content:space-between;gap:8px;padding:5px 6px;border-radius:7px;cursor:pointer;font-size:11.5px}#ar-pan .pr:hover,#ar-pan .pr.on{background:rgba(125,211,252,.1)}#ar-pan .pr small{color:#64748b}
#ar-pan .fi{margin-top:6px;padding:9px 10px;border-radius:10px;background:rgba(125,211,252,.07);border:1px solid rgba(125,211,252,.22)}
#ar-pan .fi h6{margin:0 0 3px;font-size:13px}#ar-pan .fi p{margin:2px 0;color:#cbd5e1;font-size:11.5px}
#ar-pan .re{padding:6px 0;border-bottom:1px solid rgba(255,255,255,.06);font-size:11px}#ar-pan .re b{font-weight:650}#ar-pan .re small{display:block;color:#94a3b8;font-size:10.5px}
#ar-pan .tg{display:inline-block;padding:0 5px;border-radius:4px;color:#04121c;font:800 9px system-ui;margin-right:5px}
#ar-tip{position:fixed;z-index:22;pointer-events:none;max-width:260px;padding:6px 9px;border-radius:9px;background:rgba(4,10,18,.94);border:1px solid rgba(125,211,252,.3);color:#e2f3ff;font:11px system-ui,sans-serif;display:none}
#ar-tip small{display:block;color:#94a3b8}
.ar-et{position:fixed;z-index:9;transform:translate(-50%,-50%);pointer-events:none;padding:2px 7px;border-radius:7px;background:rgba(8,16,26,.8);color:#bfdbfe;font:600 10px system-ui,sans-serif;white-space:nowrap}
.ar-et.t{font-size:12px;color:#e2f3ff;border:1px solid rgba(125,211,252,.4)}
#ar-btn{width:100%;margin-top:6px;height:30px;border:none;border-radius:8px;background:rgba(255,255,255,.06);color:#cbd5e1;font:700 10px system-ui,sans-serif;letter-spacing:.06em;cursor:pointer}#ar-btn.on{background:#7dd3fc;color:#04121c}
@media(max-width:760px){#ar-pan{top:auto;height:58vh;right:8px;left:8px;width:auto;bottom:calc(max(10px,env(safe-area-inset-bottom)) + 4px)}}`;
  document.head.appendChild(css);
  const pan = document.createElement('div'); pan.id = 'ar-pan'; document.body.appendChild(pan);
  const tip = document.createElement('div'); tip.id = 'ar-tip'; document.body.appendChild(tip);
  let ETQ = [];

  /* ---------- construir la red de una estrategia ---------- */
  const esfera = new THREE.SphereGeometry(1, 14, 10);
  function construir() {
    for (const c of [...grupo.children]) { grupo.remove(c); c.geometry && c.geometry !== esfera && c.geometry.dispose(); }
    ETQ.forEach(e => e.d.remove()); ETQ = [];
    const E = A.estrategias.find(x => x.id === ST.e); if (!E) return;
    const t = T3.orbit.target, an = ANCLA[E.id] || [t.x, t.z]; ST.ancla = an;
    const H = Y0 + 190, P = {}, procs = [];
    for (const n of E.nodos) if (n.cl === 'Rol humano propuesto' && !procs.includes(n.proc)) procs.push(n.proc);
    const prev = E.nodos.filter(n => n.cl === 'Rol previo'), env = E.nodos.filter(n => !['Rol previo', 'Rol humano propuesto'].includes(n.cl));
    env.sort((a, b) => a.cl.localeCompare(b.cl));
    const RP = 175;
    procs.forEach((p, i) => {
      const a = i / procs.length * Math.PI * 2, cx = an[0] + Math.cos(a) * RP, cz = an[1] + Math.sin(a) * RP;
      const roles = E.nodos.filter(n => n.cl === 'Rol humano propuesto' && n.proc === p);
      roles.forEach((n, k) => { const b = a + Math.PI + k / roles.length * Math.PI * 2; P[n.id] = [cx + Math.cos(b) * 24, H + (k % 2 ? 6 : -6), cz + Math.sin(b) * 24]; });
      const d = document.createElement('div'); d.className = 'ar-et'; d.textContent = p; document.body.appendChild(d); ETQ.push({ d, p: [cx + Math.cos(a) * 46, H + 26, cz + Math.sin(a) * 46], proc: p });
    });
    prev.forEach((n, i) => { const a = i / prev.length * Math.PI * 2; P[n.id] = [an[0] + Math.cos(a) * 68, H + 48, an[1] + Math.sin(a) * 68]; });
    env.forEach((n, i) => { const a = (i + 0.5) / env.length * Math.PI * 2; P[n.id] = [an[0] + Math.cos(a) * 285, H - 70, an[1] + Math.sin(a) * 285]; });
    const tit = document.createElement('div'); tit.className = 'ar-et t'; tit.textContent = E.id + ' · ' + E.n; document.body.appendChild(tit); ETQ.push({ d: tit, p: [an[0], H + 95, an[1]] });
    // nodos (una malla instanciada por clase)
    const porClase = {};
    for (const n of E.nodos) (porClase[n.cl] = porClase[n.cl] || []).push(n);
    const mallas = [];
    for (const [cl, L] of Object.entries(porClase)) {
      const k = CLASE[cl] || { c: '#e2e8f0', r: 4 }, col = new THREE.Color(k.c);
      const m = new THREE.InstancedMesh(esfera, new THREE.MeshStandardMaterial({ color: col, emissive: col.clone().multiplyScalar(0.55), roughness: 0.5 }), L.length);
      const o = new THREE.Object3D(); L.forEach((n, i) => { o.position.set(...P[n.id]); o.scale.setScalar(k.r); o.updateMatrix(); m.setMatrixAt(i, o.matrix); });
      m.frustumCulled = false; m.userData = { L, k }; grupo.add(m); mallas.push(m);
    }
    // relaciones (líneas con color por etiqueta; transparencia según filtro y selección)
    const pos = new Float32Array(E.rel.length * 6), col = new Float32Array(E.rel.length * 8);
    E.rel.forEach((r, i) => { const a = P[r.o], b = P[r.d]; if (!a || !b) return; pos.set([a[0], a[1], a[2], b[0], b[1], b[2]], i * 6); });
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('color', new THREE.BufferAttribute(col, 4));
    const lineas = new THREE.LineSegments(g, new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, depthWrite: false })); lineas.renderOrder = 9; lineas.frustumCulled = false; grupo.add(lineas);
    // pulsos de quien actúa a quien recibe
    const pp = new Float32Array(E.rel.length * 3), pc = new Float32Array(E.rel.length * 4), pg = new THREE.BufferGeometry();
    pg.setAttribute('position', new THREE.BufferAttribute(pp, 3)); pg.setAttribute('color', new THREE.BufferAttribute(pc, 4));
    const pulsos = new THREE.Points(pg, new THREE.PointsMaterial({ size: 4, sizeAttenuation: false, vertexColors: true, transparent: true, depthWrite: false })); pulsos.frustumCulled = false; grupo.add(pulsos);
    // tallo: une la red con el lugar del territorio
    const tg = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(an[0], Y0, an[1]), new THREE.Vector3(an[0], H - 70, an[1])]);
    grupo.add(new THREE.Line(tg, new THREE.LineDashedMaterial({ color: 0x7dd3fc, dashSize: 6, gapSize: 4, transparent: true, opacity: 0.8 })).computeLineDistances());
    R = { E, P, mallas, lineas, pulsos, H, procs };
    colorear(); volar();
  }
  function colorear() {
    if (!R) return; const { E } = R, c = R.lineas.geometry.attributes.color.array, s = ST.sel, pr = ST.proc;
    const nodoP = (id) => { const n = E.nodos.find(x => x.id === id); return n && n.proc === pr; };
    E.rel.forEach((r, i) => {
      const col = new THREE.Color(TAGC[r.tag] || '#e2e8f0'), on = ST.tags.has(r.tag), foco = s ? (r.o === s || r.d === s) : pr ? (nodoP(r.o) || nodoP(r.d)) : true;
      const al = !on ? 0 : foco ? 0.95 : 0.12;
      c.set([col.r, col.g, col.b, al, col.r, col.g, col.b, al], i * 8);
    });
    R.lineas.geometry.attributes.color.needsUpdate = true;
    for (const m of R.mallas) { const k = m.userData.k, o = new THREE.Object3D(); m.userData.L.forEach((n, i) => { const f = s ? (n.id === s || E.rel.some(r => (r.o === s && r.d === n.id) || (r.d === s && r.o === n.id))) : pr ? n.proc === pr : true; o.position.set(...R.P[n.id]); o.scale.setScalar(k.r * (n.id === s ? 1.8 : f ? 1 : 0.55)); o.updateMatrix(); m.setMatrixAt(i, o.matrix); }); m.instanceMatrix.needsUpdate = true; }
  }
  function volar() {
    if (!R) return; const an = ST.ancla, t = new THREE.Vector3(an[0], R.H - 10, an[1]), p1 = new THREE.Vector3(an[0] - 330, R.H + 300, an[1] + 520);
    if (innerWidth > 760) { const dir = t.clone().sub(p1).setY(0).normalize(), der = new THREE.Vector3(-dir.z, 0, dir.x); t.addScaledVector(der, 170); p1.addScaledVector(der, 170); }
    T3.anim = { t: 0, dur: 1.6, p0: T3.camera.position.clone(), p1, c0: T3.orbit.target.clone(), c1: t };
  }

  /* ---------- panel ---------- */
  const tagChip = (t) => `<span class="tg" style="background:${TAGC[t] || '#e2e8f0'}">${t}</span>`;
  function pintar() {
    const E = A.estrategias.find(x => x.id === ST.e); if (!E) return;
    const cuenta = {}; for (const r of E.rel) cuenta[r.tag] = (cuenta[r.tag] || 0) + 1;
    const cl = {}; for (const n of E.nodos) cl[n.cl] = (cl[n.cl] || 0) + 1;
    const nodo = ST.sel && E.nodos.find(n => n.id === ST.sel);
    let ficha = '';
    if (nodo) {
      const rs = E.rel.filter(r => r.o === nodo.id || r.d === nodo.id), nom = (id) => (E.nodos.find(n => n.id === id) || {}).n || id;
      ficha = `<h5>NODO ELEGIDO <span>${esc(nodo.id)}</span></h5><div class="fi"><h6>${esc(nodo.n)}</h6><p><i style="display:inline-block;width:9px;height:9px;border-radius:50%;background:${(CLASE[nodo.cl] || {}).c}"></i> ${esc(nodo.cl)} · ${esc(nodo.proc)}</p><p>${esc(nodo.fn)}</p><p style="color:#fde68a">${esc(nodo.est)}${nodo.orig ? ' · ' + esc(nodo.orig) : ''}</p></div>
        <h5>SUS RELACIONES <span>${rs.length}</span></h5>` + rs.map(r => `<div class="re">${tagChip(r.tag)}<b>${esc(nom(r.o))} → ${esc(nom(r.d))}</b><small>${esc(r.rel)}</small><small>Se activa si: ${esc(r.act)}</small><small>Si falla: ${esc(r.falla)}</small><small>Evidencia pendiente: ${esc(r.ev)} · ${esc(r.est)}</small></div>`).join('');
    }
    pan.innerHTML = `<div class="cab"><div><h4>Redes de actores</h4><em>${A.estrategias.length} estrategias · ${esc(A.fuente)}</em></div><button class="x" aria-label="Cerrar">×</button></div>
      <div class="av">${A.avisos.map(esc).join(' ')}</div>
      <h5>ESTRATEGIA <span>${E.nodos.length} nodos · ${E.rel.length} relaciones</span></h5>
      <div class="est">${A.estrategias.map(x => `<button data-e="${x.id}" class="${x.id === ST.e ? 'on' : ''}"><b>${x.id}</b>${esc(x.n)}</button>`).join('')}</div>
      <h5>NODOS POR CLASE</h5><div class="ley">${Object.entries(cl).map(([k, v]) => `<button><i style="background:${(CLASE[k] || {}).c}"></i>${esc(k)} · ${v}</button>`).join('')}</div>
      <h5>RELACIONES POR ETIQUETA <span>toca para filtrar</span></h5><div class="ley">${Object.keys(TAGC).filter(t => cuenta[t]).map(t => `<button data-t="${t}" class="${ST.tags.has(t) ? '' : 'off'}" title="${esc((A.tags[t] || {}).n)}: ${esc((A.tags[t] || {}).cuando)}"><i class="l" style="background:${TAGC[t]}"></i>${t} ${esc((A.tags[t] || {}).n)} · ${cuenta[t]}</button>`).join('')}</div>
      ${ficha}
      <h5>PROCESOS <span>toca para resaltar</span></h5>${(R ? R.procs : []).map(p => `<div class="pr ${p === ST.proc ? 'on' : ''}" data-p="${esc(p)}"><span>${esc(p)}</span><small>${E.nodos.filter(n => n.proc === p).length} roles</small></div>`).join('')}
      <p style="margin-top:10px;font-size:10px;color:#64748b">Toca un nodo en el territorio para ver su ficha y sus relaciones. ${ANCLA[ST.e] ? 'Esta red flota sobre el lugar de la estrategia.' : 'Esta estrategia no tiene un lugar único: la red flota donde estás mirando.'}</p>`;
    pan.querySelector('.x').onclick = () => alternar(false);
    pan.querySelectorAll('.est button').forEach(b => b.onclick = () => { ST.e = b.dataset.e; ST.sel = null; ST.proc = null; construir(); pintar(); });
    pan.querySelectorAll('.ley button[data-t]').forEach(b => b.onclick = () => { const t = b.dataset.t; if (ST.tags.has(t)) ST.tags.delete(t); else ST.tags.add(t); colorear(); pintar(); });
    pan.querySelectorAll('.pr').forEach(d => d.onclick = () => { ST.proc = ST.proc === d.dataset.p ? null : d.dataset.p; ST.sel = null; colorear(); pintar(); });
  }
  function alternar(on) {
    ST.on = on; grupo.visible = on; pan.classList.toggle('on', on); const b = document.getElementById('ar-btn'); if (b) b.classList.toggle('on', on);
    if (on) { const bp = document.getElementById('bp-pan'); if (bp) bp.classList.remove('on'); construir(); pintar(); } else { ETQ.forEach(e => e.d.style.display = 'none'); tip.style.display = 'none'; }
  }

  /* ---------- botón en el panel de la simulación ---------- */
  const poner = () => { const izq = document.getElementById('gs-izq'), ag = document.getElementById('gs-ag'); if (!izq || document.getElementById('ar-btn')) return; const b = document.createElement('button'); b.id = 'ar-btn'; b.textContent = 'Redes de actores'; b.onclick = () => alternar(!ST.on); (ag ? ag.parentElement : izq).insertAdjacentElement('afterend', b); };
  poner(); setTimeout(poner, 1500);

  /* ---------- puntero: nodo bajo el cursor y clic ---------- */
  const cvs = T3.renderer.domElement, v = new THREE.Vector3(); let pd = null;
  const cercano = (e) => { if (!R || !ST.on) return null; const r = cvs.getBoundingClientRect(); let best = null, bd = 14; for (const n of R.E.nodos) { const p = R.P[n.id]; v.set(p[0], p[1], p[2]).project(T3.camera); if (v.z > 1) continue; const x = (v.x + 1) / 2 * r.width + r.left, y = (1 - v.y) / 2 * r.height + r.top, d = Math.hypot(x - e.clientX, y - e.clientY); if (d < bd) { bd = d; best = n; } } return best; };
  cvs.addEventListener('pointermove', (e) => { const n = cercano(e); if (!n) { tip.style.display = 'none'; return; } tip.style.display = 'block'; tip.style.left = (e.clientX + 14) + 'px'; tip.style.top = (e.clientY + 12) + 'px'; tip.innerHTML = `<b>${esc(n.n)}</b><small>${esc(n.cl)} · ${esc(n.proc)}</small><small>${esc(n.fn)}</small>`; });
  cvs.addEventListener('pointerdown', (e) => { pd = [e.clientX, e.clientY]; });
  cvs.addEventListener('pointerup', (e) => { if (!pd || Math.hypot(e.clientX - pd[0], e.clientY - pd[1]) > 6) return; const n = cercano(e); if (n) { ST.sel = ST.sel === n.id ? null : n.id; ST.proc = null; colorear(); pintar(); } });

  /* ---------- bucle: etiquetas y pulsos ---------- */
  const bucle = () => {
    if (ST.on && R) {
      const W = innerWidth, Hh = innerHeight;
      for (const e of ETQ) { v.set(...e.p).project(T3.camera); const fuera = v.z > 1 || Math.abs(v.x) > 1.05 || Math.abs(v.y) > 1.05; e.d.style.display = fuera ? 'none' : 'block'; if (!fuera) { e.d.style.left = ((v.x + 1) / 2 * W).toFixed(1) + 'px'; e.d.style.top = ((1 - v.y) / 2 * Hh).toFixed(1) + 'px'; e.d.style.opacity = !ST.proc || !e.proc || e.proc === ST.proc ? 1 : 0.35; } }
      const pp = R.pulsos.geometry.attributes.position.array, pc = R.pulsos.geometry.attributes.color.array, lc = R.lineas.geometry.attributes.color.array, t = performance.now() / 1000;
      R.E.rel.forEach((r, i) => { const a = R.P[r.o], b = R.P[r.d]; if (!a || !b) return; const u = (t * 0.35 + i * 0.137) % 1; pp[i * 3] = a[0] + (b[0] - a[0]) * u; pp[i * 3 + 1] = a[1] + (b[1] - a[1]) * u; pp[i * 3 + 2] = a[2] + (b[2] - a[2]) * u; pc[i * 4] = lc[i * 8]; pc[i * 4 + 1] = lc[i * 8 + 1]; pc[i * 4 + 2] = lc[i * 8 + 2]; pc[i * 4 + 3] = lc[i * 8 + 3]; });
      R.pulsos.geometry.attributes.position.needsUpdate = true; R.pulsos.geometry.attributes.color.needsUpdate = true;
    }
    requestAnimationFrame(bucle);
  };
  requestAnimationFrame(bucle);
  return { alternar, ver: (id) => { ST.e = id; if (ST.on) { construir(); pintar(); } } };
}

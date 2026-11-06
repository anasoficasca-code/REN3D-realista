/* ============ REDES DE ACTORES: botón del simulador ============
   La red de actores de las 9 estrategias tiene su propia página (actores.html, con el estilo de la red de especies de
   humedalburro). Este módulo solo pone el botón "Redes de actores" en el panel de la simulación y abre esa página
   (en otra pestaña, para no perder el estado de la simulación) con la estrategia elegida. */
export async function iniciarActores() {
  let e = 'E1';
  const abrir = (id) => { if (id) e = id; window.open('actores.html?e=' + encodeURIComponent(e), 'red-actores'); };
  const poner = () => {
    const izq = document.getElementById('gs-izq'), ag = document.getElementById('gs-ag');
    if (!izq || document.getElementById('ar-btn')) return;
    const css = document.createElement('style'); css.textContent = '#ar-btn{width:100%;margin-top:6px;height:30px;border:none;border-radius:8px;background:rgba(255,255,255,.06);color:#cbd5e1;font:700 10px system-ui,sans-serif;letter-spacing:.06em;cursor:pointer}#ar-btn:hover{background:rgba(125,211,252,.18);color:#e0f2fe}';
    document.head.appendChild(css);
    const b = document.createElement('button'); b.id = 'ar-btn'; b.textContent = 'Redes de actores ↗'; b.title = 'Abre la red de actores de las 9 estrategias en otra pestaña'; b.onclick = () => abrir();
    (ag ? ag.parentElement : izq).insertAdjacentElement('afterend', b);
  };
  poner(); setTimeout(poner, 1500);
  // misma interfaz que antes: la leyenda de estrategias llama ver(id) y alternar(true)
  return { ver: (id) => { e = id; }, alternar: (on) => { if (on) abrir(); }, abrir };
}

import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

/**
 * PostFX · cadena de posproceso "render de masterplan" para el 3D de Kennedy.
 * Basada en la cadena de https://github.com/alejagoguti-cpu/hotel-la-fontana-masterplan (src/scene/PostFX.js):
 *  - MSAA en el render target (bordes limpios)
 *  - GTAO: oclusión ambiental de contacto (esquinas, aleros, base de edificios, bajo los árboles)
 *  - Bloom suave solo en brillos fuertes
 *  - Gradación: contraste, saturación, balance cálido, sombras frescas y viñeta
 *  - Tono ACES (lo aplica OutputPass con renderer.toneMapping)
 * En GPU integrada se apaga la oclusión (era lo más caro) y se baja el antialiasing.
 */
const GradeShader = {
  uniforms: {
    tDiffuse: { value: null },
    uContrast: { value: 1.05 },
    uSaturation: { value: 1.1 },
    uWarm: { value: new THREE.Vector3(1.0, 1.0, 0.985) },
    uVignette: { value: 0.14 },
    uGrain: { value: 0.006 },
    uTime: { value: 0 },
    uLift: { value: 0.03 }
  },
  vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
  fragmentShader: `
    uniform sampler2D tDiffuse; uniform float uContrast, uSaturation, uVignette, uGrain, uTime, uLift; uniform vec3 uWarm;
    varying vec2 vUv;
    float hash(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233))) * 43758.5453); }
    void main(){
      vec4 c = texture2D(tDiffuse, vUv);
      vec3 col = c.rgb * uWarm;
      float l = dot(col, vec3(0.2126, 0.7152, 0.0722));
      col = mix(vec3(l), col, uSaturation);
      col = (col - 0.18) * uContrast + 0.18;
      col += uLift * (1.0 - smoothstep(0.0, 0.35, col)) * vec3(0.9, 0.95, 1.05);
      vec2 d = vUv - 0.5;
      col *= 1.0 - uVignette * smoothstep(0.25, 0.85, dot(d, d) * 2.2);
      col += (hash(vUv * 1000.0 + uTime) - 0.5) * uGrain * (0.3 + l);
      gl_FragColor = vec4(max(col, 0.0), c.a);
    }`
};

export class PostFX {
  constructor(renderer, scene, camera) {
    this.renderer = renderer;
    const w = innerWidth, h = innerHeight;
    let gpu = '';
    try { const gl = renderer.getContext(); const ext = gl.getExtension('WEBGL_debug_renderer_info'); gpu = ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : ''; } catch (e) { /* sin datos */ }
    this.gpu = gpu;
    this.low = /Intel|UHD|HD Graphics|Iris|Mali|Adreno|PowerVR|SwiftShader|llvmpipe|Microsoft Basic/i.test(gpu);

    const rt = new THREE.WebGLRenderTarget(w, h, { type: THREE.HalfFloatType, samples: this.low ? 2 : 4 });
    this.composer = new EffectComposer(renderer, rt);
    this.composer.setPixelRatio(renderer.getPixelRatio());
    this.composer.setSize(w, h);
    this.composer.addPass(new RenderPass(scene, camera));

    if (!this.low) {
      this.ao = new GTAOPass(scene, camera, w, h);
      this.ao.output = GTAOPass.OUTPUT.Default;
      this.ao.blendIntensity = 0.8;
      this.ao.updateGtaoMaterial({ radius: 2.2, distanceExponent: 1.4, thickness: 3.0, scale: 1.0, samples: 10, distanceFallOff: 1.0 });
      this.ao.updatePdMaterial({ lumaPhi: 10, depthPhi: 2, normalPhi: 3, radius: 6, rings: 2, samples: 10 });
      this.composer.addPass(this.ao);
    }

    this.bloom = new UnrealBloomPass(new THREE.Vector2(w, h), 0.16, 0.4, 0.95);
    this.composer.addPass(this.bloom);
    this.grade = new ShaderPass(GradeShader);
    this.composer.addPass(this.grade);
    this.composer.addPass(new OutputPass());
  }

  setSize(w, h) {
    this.composer.setSize(w, h);
    if (this.ao) this.ao.setSize(w, h);
  }

  render(dt) {
    this.grade.uniforms.uTime.value += dt;
    this.composer.render(dt);
  }
}

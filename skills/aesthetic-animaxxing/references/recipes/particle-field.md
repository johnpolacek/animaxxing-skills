# Recipe: particle field

A canvas that bleeds out past a target element, with a list of particles stepped by the GSAP ticker. Behaviour lives in emitters (called each frame while attached) and in per-particle update hooks; GSAP tweens on the plain particle objects work too, since the ticker runs the core update before the field's own step. The field only ticks while it has something to draw and is on screen, so an idle button costs nothing.

`attachParticleEffect` wires a field to a target for the life of a component and returns the controls the framework skill's controller calls. The controller decides when; this module never does.

Dependencies: `gsap`.

## Markup

The canvas sits in a wrapper with the target, offset by the effect's bleed, colored from the tokens, out of the accessibility tree and pointer flow. `z-index` above the target for `layer: "over"` effects, below for `"under"`.

```html
<div class="relative isolate" data-particle-button>
  <canvas aria-hidden="true" class="pointer-events-none absolute z-10 text-foreground" style="left:-180px; top:-180px"></canvas>
  <button class="relative z-20 …">Get Animaxxed</button>
</div>
```

Add the wrapper's `data-*` hook to the pre-paint hiding list; the effect's `enter` reveals the target.

## field.ts

```ts
import gsap from "gsap";

export type Shape = "dot" | "spark" | "ring" | "square" | "star" | "outline" | "streak";

export type Particle = {
  x: number;
  y: number;
  vx: number;
  vy: number;
  /** Radius for dots and rings, half-width for squares, stroke width for sparks, half-length for streaks, spread for outlines. */
  size: number;
  alpha: number;
  shape: Shape;
  rotation: number;
  /** Radians per second. */
  spin: number;
  /** Fraction of velocity kept after one second. 1 keeps it all. */
  drag: number;
  /** Pixels per second squared, downward positive. */
  gravity: number;
  /** Total seconds to live, or Infinity while something else owns the particle. */
  life: number;
  age: number;
  /** Alpha falls to zero over the particle's life. */
  fade: boolean;
  /** Size falls to zero over the particle's life. */
  shrink: boolean;
  /** Sideways sway: amplitude in px/s and frequency in Hz. */
  wobble: number;
  wobbleFreq: number;
  phase: number;
  update?: (p: Particle, dt: number, time: number) => void;
};

export type Box = { x: number; y: number; w: number; h: number };
export type Emitter = (dt: number, time: number) => void;

const DEFAULTS: Omit<Particle, "x" | "y"> = {
  vx: 0, vy: 0, size: 2, alpha: 1, shape: "dot", rotation: 0, spin: 0, drag: 1, gravity: 0,
  life: 1, age: 0, fade: true, shrink: false, wobble: 0, wobbleFreq: 0, phase: 0,
};

/** Longest step the simulation will take, so a stalled tab does not fling everything off screen. */
const MAX_STEP = 0.05;

export class ParticleField {
  readonly canvas: HTMLCanvasElement;
  readonly particles: Particle[] = [];
  readonly emitters = new Set<Emitter>();
  /** The target element's rectangle, in canvas CSS pixels. */
  readonly box: Box = { x: 0, y: 0, w: 0, h: 0 };
  /** Corner radius of the target, read from its computed style. */
  radius = 0;
  color = "#000";
  time = 0;

  private readonly ctx: CanvasRenderingContext2D;
  private readonly target: HTMLElement;
  private readonly bleed: number;
  private width = 0;
  private height = 0;
  private running = false;
  private onScreen = true;

  constructor(canvas: HTMLCanvasElement, target: HTMLElement, bleed: number) {
    const ctx = canvas.getContext("2d");
    if (!ctx) throw new Error("ParticleField needs a 2d canvas context");
    this.canvas = canvas;
    this.ctx = ctx;
    this.target = target;
    this.bleed = bleed;
    this.sync();
  }

  /** Re-measure the target and resize the canvas around it. */
  sync(): void {
    const { offsetWidth: w, offsetHeight: h } = this.target;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    this.width = w + this.bleed * 2;
    this.height = h + this.bleed * 2;
    this.box.x = this.bleed;
    this.box.y = this.bleed;
    this.box.w = w;
    this.box.h = h;
    this.canvas.width = Math.round(this.width * dpr);
    this.canvas.height = Math.round(this.height * dpr);
    this.canvas.style.width = `${this.width}px`;
    this.canvas.style.height = `${this.height}px`;
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    this.radius = parseFloat(getComputedStyle(this.target).borderTopLeftRadius) || 0;
    this.color = getComputedStyle(this.canvas).color;
  }

  spawn(init: Partial<Particle> & { x: number; y: number }): Particle {
    const p: Particle = { ...DEFAULTS, ...init };
    this.particles.push(p);
    this.start();
    return p;
  }

  /** Let every managed particle finish within `within` seconds. */
  release(within = 0.3): void {
    for (const p of this.particles) {
      if (p.life === Infinity || p.life - p.age > within) {
        p.life = p.age + within;
        p.fade = true;
      }
    }
  }

  addEmitter(emitter: Emitter): void { this.emitters.add(emitter); this.start(); }
  removeEmitter(emitter: Emitter): void { this.emitters.delete(emitter); }

  setOnScreen(onScreen: boolean): void {
    this.onScreen = onScreen;
    if (onScreen) this.start(); else this.stop();
  }

  start(): void {
    if (this.running || !this.onScreen) return;
    if (this.particles.length === 0 && this.emitters.size === 0) return;
    this.running = true;
    gsap.ticker.add(this.tick);
  }

  stop(): void {
    if (!this.running) return;
    this.running = false;
    gsap.ticker.remove(this.tick);
  }

  destroy(): void {
    this.stop();
    this.emitters.clear();
    this.particles.length = 0;
    this.ctx.clearRect(0, 0, this.width, this.height);
  }

  private readonly tick = (_time: number, deltaMs: number) => {
    const dt = Math.min(deltaMs / 1000, MAX_STEP);
    this.time += dt;
    for (const emitter of this.emitters) emitter(dt, this.time);
    this.step(dt);
    this.draw();
    if (this.particles.length === 0 && this.emitters.size === 0) this.stop();
  };

  private step(dt: number): void {
    const list = this.particles;
    let keep = 0;
    for (let i = 0; i < list.length; i++) {
      const p = list[i]!;
      p.age += dt;
      if (p.age >= p.life) continue;
      if (p.drag !== 1) {
        const keepVelocity = Math.pow(p.drag, dt);
        p.vx *= keepVelocity;
        p.vy *= keepVelocity;
      }
      p.vy += p.gravity * dt;
      p.x += p.vx * dt;
      p.y += p.vy * dt;
      if (p.wobble !== 0) p.x += Math.sin(this.time * p.wobbleFreq * Math.PI * 2 + p.phase) * p.wobble * dt;
      p.rotation += p.spin * dt;
      p.update?.(p, dt, this.time);
      list[keep++] = p;
    }
    list.length = keep;
  }

  private draw(): void {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.width, this.height);
    ctx.fillStyle = this.color;
    ctx.strokeStyle = this.color;
    ctx.lineCap = "round";
    for (const p of this.particles) {
      const progress = p.life === Infinity ? 0 : p.age / p.life;
      const alpha = p.alpha * (p.fade ? 1 - progress : 1);
      const size = p.size * (p.shrink ? 1 - progress : 1);
      if (alpha <= 0.005 || size <= 0.05) continue;
      ctx.globalAlpha = Math.min(alpha, 1);
      switch (p.shape) {
        case "dot":
          ctx.beginPath(); ctx.arc(p.x, p.y, size, 0, Math.PI * 2); ctx.fill();
          break;
        case "ring":
          ctx.lineWidth = 1; ctx.beginPath(); ctx.arc(p.x, p.y, size, 0, Math.PI * 2); ctx.stroke();
          break;
        case "spark": {
          // A streak trailing the direction of travel; a still spark is a dot.
          const speed = Math.hypot(p.vx, p.vy);
          if (speed < 1) { ctx.beginPath(); ctx.arc(p.x, p.y, size, 0, Math.PI * 2); ctx.fill(); break; }
          const tail = Math.min(speed * 0.04, 18);
          ctx.lineWidth = size;
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p.x - (p.vx / speed) * tail, p.y - (p.vy / speed) * tail);
          ctx.stroke();
          break;
        }
        case "streak":
          // A level hairline, centred on the particle.
          ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(p.x - size, p.y); ctx.lineTo(p.x + size, p.y); ctx.stroke();
          break;
        case "square":
          ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.rotation);
          ctx.fillRect(-size, -size, size * 2, size * 2);
          ctx.restore();
          break;
        case "star":
          // Four thin rays crossing at the centre, like a lens glint.
          ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.rotation);
          ctx.lineWidth = 1; ctx.beginPath();
          ctx.moveTo(-size, 0); ctx.lineTo(size, 0); ctx.moveTo(0, -size); ctx.lineTo(0, size);
          ctx.stroke(); ctx.restore();
          break;
        case "outline": {
          // The target's rounded rectangle, pushed outward by `size`.
          const { x, y, w, h } = this.box;
          ctx.lineWidth = 1.5; ctx.beginPath();
          ctx.roundRect(x - size, y - size, w + size * 2, h + size * 2, this.radius + size);
          ctx.stroke();
          break;
        }
      }
    }
    ctx.globalAlpha = 1;
  }
}

export type EdgePoint = { x: number; y: number; nx: number; ny: number };

/** Length of a rounded rectangle's outline. */
export function perimeterLength(box: Box, radius: number): number {
  const r = Math.min(radius, box.w / 2, box.h / 2);
  return 2 * (box.w - 2 * r) + 2 * (box.h - 2 * r) + 2 * Math.PI * r;
}

/** A point on a rounded rectangle's outline at `t` in [0, 1), clockwise from the top-left corner, with the outward normal. */
export function perimeterPoint(box: Box, radius: number, t: number): EdgePoint {
  const r = Math.min(radius, box.w / 2, box.h / 2);
  const { x, y, w, h } = box;
  const sw = w - 2 * r;
  const sh = h - 2 * r;
  const arc = (Math.PI * r) / 2;
  const total = 2 * sw + 2 * sh + 4 * arc;
  let d = (((t % 1) + 1) % 1) * total;

  if (d < sw) return { x: x + r + d, y, nx: 0, ny: -1 };
  d -= sw;
  if (d < arc) { const a = -Math.PI / 2 + d / r; return { x: x + w - r + Math.cos(a) * r, y: y + r + Math.sin(a) * r, nx: Math.cos(a), ny: Math.sin(a) }; }
  d -= arc;
  if (d < sh) return { x: x + w, y: y + r + d, nx: 1, ny: 0 };
  d -= sh;
  if (d < arc) { const a = d / r; return { x: x + w - r + Math.cos(a) * r, y: y + h - r + Math.sin(a) * r, nx: Math.cos(a), ny: Math.sin(a) }; }
  d -= arc;
  if (d < sw) return { x: x + w - r - d, y: y + h, nx: 0, ny: 1 };
  d -= sw;
  if (d < arc) { const a = Math.PI / 2 + d / r; return { x: x + r + Math.cos(a) * r, y: y + h - r + Math.sin(a) * r, nx: Math.cos(a), ny: Math.sin(a) }; }
  d -= arc;
  if (d < sh) return { x, y: y + h - r - d, nx: -1, ny: 0 };
  d -= sh;
  const a = Math.PI + d / r;
  return { x: x + r + Math.cos(a) * r, y: y + r + Math.sin(a) * r, nx: Math.cos(a), ny: Math.sin(a) };
}
```

## attach.ts

Keeps the field sized to the target, re-reads its colour when the theme changes, pauses it off screen, and treats pointer hover and keyboard focus as one state. Returns the controls and a `destroy` for unmount.

```ts
import gsap from "gsap";
import { ParticleField } from "./field";

/* Swap for the project's helper if it has one. */
function prefersReducedMotion(): boolean {
  if (typeof window === "undefined") return true;
  const choice = document.documentElement.dataset.motion;
  if (choice === "reduced") return true;
  if (choice === "full") return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export type ParticleEffectInstance = {
  /** Builds the entrance, starting after `delay` seconds. The timeline reveals the target itself. */
  enter(delay: number): gsap.core.Timeline;
  /** Stops the ambient loop and lets the particles die. */
  exit(): void;
  /** Everything at once: the biggest burst the effect has, then silence. */
  blast(): void;
  /** Restarts the ambient loop after an exit or blast. */
  idle(): void;
  hover(on: boolean): void;
  destroy(): void;
};

export type ParticleEffectDefinition<Instance extends ParticleEffectInstance = ParticleEffectInstance> = {
  /** Whether the canvas sits under or over the target. */
  layer?: "under" | "over";
  /** How far the canvas extends past the target on each side, in px. */
  bleed: number;
  create(field: ParticleField, target: HTMLElement): Instance;
};

export type ParticleEffectControls = {
  enter(delay?: number): void;
  exit(): void;
  blast(): void;
  idle(): void;
  /** Tear everything down. Call on unmount. */
  destroy(): void;
};

export function attachParticleEffect(
  root: HTMLElement,
  canvas: HTMLCanvasElement,
  target: HTMLElement,
  effect: ParticleEffectDefinition,
): ParticleEffectControls {
  const field = new ParticleField(canvas, target, effect.bleed);
  const instance = effect.create(field, target);
  let entrance: gsap.core.Timeline | null = null;
  let ready = false;

  const resize = new ResizeObserver(() => field.sync());
  resize.observe(target);
  // Theme changes land on <html>; re-read the particle colour when they do.
  const theme = new MutationObserver(() => field.sync());
  theme.observe(document.documentElement, { attributes: true });
  const visibility = new IntersectionObserver(([entry]) => field.setOnScreen(entry?.isIntersecting ?? true));
  visibility.observe(root);

  const on = () => { if (ready) instance.hover(true); };
  const off = () => { if (ready) instance.hover(false); };
  target.addEventListener("pointerenter", on);
  target.addEventListener("pointerleave", off);
  target.addEventListener("focus", on);
  target.addEventListener("blur", off);

  return {
    enter(delay = 0) {
      entrance?.kill();
      if (prefersReducedMotion()) {
        gsap.set(target, { autoAlpha: 1, clearProps: "transform" });
        ready = true;
        return;
      }
      entrance = instance.enter(delay);
      entrance.eventCallback("onComplete", () => { ready = true; });
    },
    exit() {
      ready = false;
      entrance?.kill();
      entrance = null;
      instance.exit();
      gsap.to(target, { autoAlpha: 0, duration: 0.2, overwrite: "auto" });
    },
    blast() {
      ready = false;
      entrance?.kill();
      entrance = null;
      if (!prefersReducedMotion()) instance.blast();
    },
    idle() {
      if (!prefersReducedMotion()) instance.idle();
      ready = true;
    },
    destroy() {
      target.removeEventListener("pointerenter", on);
      target.removeEventListener("pointerleave", off);
      target.removeEventListener("focus", on);
      target.removeEventListener("blur", off);
      resize.disconnect();
      theme.disconnect();
      visibility.disconnect();
      entrance?.kill();
      entrance = null;
      instance.destroy();
      field.destroy();
      ready = false;
    },
  };
}
```

In React, wrap the same body in `useGSAP` with the component's scope and return `controls.destroy` as the cleanup; `contextSafe` the `enter`, `blast`, and `idle` calls so their tweens join the context. In Svelte or Vue, call it in the mount hook and destroy in the unmount hook. The framework skill says which.

## Wiring

```ts
const controls = attachParticleEffect(wrapper, canvas, button, reactor);
watchPageTransition(wrapper, {
  onEntering: () => { controls.enter(1.25); gsap.set(wrapper, { autoAlpha: 1 }); },
  onExiting: () => controls.exit(),
});
button.addEventListener("click", () => controls.blast());
// unmount: controls.destroy()
```

The wrapper starts hidden by the pre-paint rule; `enter` hides the target itself at time zero, so the wrapper can be released at once and only the canvas shows until the target assembles.

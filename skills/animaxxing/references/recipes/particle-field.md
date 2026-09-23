# Recipe: particle field

Failure contract: apply [effect restoration](../effect-restoration.md) when adapting this module. The framework controller chooses recovery timing; this effect must undo even partial setup.

A canvas that bleeds out past a target element, with a list of particles stepped by the GSAP ticker. Behaviour lives in emitters (called each frame while attached) and in per-particle update hooks; GSAP tweens on the plain particle objects work too, since the ticker runs the core update before the field's own step. The field only ticks while it has something to draw and is on screen, so an idle button costs nothing.

`attachParticleEffect` wires a field to a target for the life of a component and returns the controls the framework skill's controller calls. The controller decides when; this module never does.

Dependencies: `gsap`.

## Markup

The canvas sits in a wrapper with the target, offset by the effect's bleed, colored through the canvas's CSS `color`, out of the accessibility tree and pointer flow. `z-index` above the target for `layer: "over"` effects, below for `"under"`.

```html
<div class="relative isolate" data-particle-button>
  <canvas aria-hidden="true" class="pointer-events-none absolute z-10 text-inherit" style="left:-180px; top:-180px"></canvas>
  <button class="relative z-20 …">Continue</button>
</div>
```

Plain CSS equivalent for the positioning classes above (under-layer example):

```css
[data-particle-button] { position: relative; isolation: isolate; }
[data-particle-button] canvas {
  pointer-events: none; position: absolute; z-index: 10; color: inherit;
}
[data-particle-button] button { position: relative; z-index: 20; }
```

The canvas inherits the wrapper's text color by default; set its `color` to an existing brand token when needed for contrast. No palette or token name is required. The framework controller handles any pre-paint hiding and wrapper reveal.

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
  /** Transient particle budget; outlines and owned particles are exempt. */
  density = 1;

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
    const structural = p.life === Infinity || p.shape === "outline";
    if (!structural && this.density < 1 && Math.random() > this.density) return p;
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

Sizes the field, tracks theme changes, pauses off screen, and combines hover, keyboard focus, and touch presses. Returns phase controls and `destroy`.

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

/** Editable coarse-pointer budget. 1 keeps all transient particles. */
export const COARSE_POINTER_DENSITY = 0.6;

/** Focus visibility alone does not identify keyboard input. */
function isFocusVisible(el: Element): boolean {
  try { return el.matches(":focus-visible"); } catch { return true; }
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
  /** Intensifies the effect while hovered, keyboard-focused, or touch-pressed. */
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
  let instance: ParticleEffectInstance;
  try {
    instance = effect.create(field, target);
  } catch (error) {
    // Nothing else is attached yet; stop the field and clear anything it drew.
    field.destroy();
    throw error;
  }
  let entrance: gsap.core.Timeline | null = null;
  let ready = false;

  const resize = new ResizeObserver(() => field.sync());
  resize.observe(target);
  // Theme changes land on <html>; re-read the particle colour when they do.
  const theme = new MutationObserver(() => field.sync());
  theme.observe(document.documentElement, { attributes: true });
  const visibility = new IntersectionObserver(([entry]) => field.setOnScreen(entry?.isIntersecting ?? true));
  visibility.observe(root);
  // Re-evaluate when the primary pointer changes.
  const coarse = window.matchMedia("(pointer: coarse)");
  const applyDensity = () => { field.density = coarse.matches ? COARSE_POINTER_DENSITY : 1; };
  applyDensity();
  coarse.addEventListener("change", applyDensity);

  const listeners = new AbortController();
  const { signal } = listeners;
  let keyboardInput = false;
  let hovering = false;
  let pressing = false;
  let hot = false;
  const syncHot = () => {
    if (!ready) return;
    const focused = keyboardInput && document.activeElement === target && isFocusVisible(target);
    const on = !prefersReducedMotion() && (hovering || pressing || focused);
    if (on === hot) return;
    hot = on;
    instance.hover(on);
  };
  // Capture modality before focus fires, including focus after touch release.
  document.addEventListener("pointerdown", () => { keyboardInput = false; syncHot(); }, { capture: true, signal });
  document.addEventListener("keydown", (e) => {
    if (e.altKey || e.ctrlKey || e.metaKey || ["Shift", "Control", "Alt", "Meta"].includes(e.key)) return;
    keyboardInput = true;
    syncHot();
  }, { capture: true, signal });
  target.addEventListener("pointerenter", (e) => {
    if (e.pointerType !== "touch") { hovering = true; syncHot(); }
  }, { signal });
  target.addEventListener("pointerdown", (e) => {
    if (e.pointerType === "touch") { pressing = true; syncHot(); }
  }, { signal });
  target.addEventListener("pointerup", (e) => {
    if (e.pointerType === "touch") { pressing = false; syncHot(); }
  }, { signal });
  const release = (e: PointerEvent) => {
    if (e.pointerType === "touch") pressing = false; else hovering = false;
    syncHot();
  };
  target.addEventListener("pointercancel", release, { signal });
  target.addEventListener("pointerleave", release, { signal });
  target.addEventListener("focus", syncHot, { signal });
  target.addEventListener("blur", syncHot, { signal });

  return {
    enter(delay = 0) {
      entrance?.kill();
      if (prefersReducedMotion()) {
        gsap.set(target, { autoAlpha: 1, clearProps: "transform" });
        ready = true;
        return;
      }
      entrance = instance.enter(delay);
      entrance.eventCallback("onComplete", () => { ready = true; syncHot(); });
    },
    exit() {
      ready = false;
      entrance?.kill();
      entrance = null;
      instance.exit();
      gsap.to(target, { autoAlpha: 0, duration: prefersReducedMotion() ? 0 : 0.2, overwrite: "auto" });
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
      syncHot();
    },
    destroy() {
      listeners.abort();
      coarse.removeEventListener("change", applyDensity);
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

## Controller contract

`attachParticleEffect(wrapper, canvas, target, effect)` returns `enter`, `exit`, `blast`, `idle`, and `destroy` controls. These controls return void; they are surface effects, not navigation-completion promises. The framework controller owns their GSAP context and calls `destroy` to release observers, listeners, timelines, and the ticker.

The target is prepared by `enter`; reveal a hidden wrapper separately so its canvas can show while the target assembles. Use the framework skill for first-paint readiness and lifecycle subscriptions.

## Input and density

- Hover uses `pointerType`; touch presses end on `pointerup`, `pointercancel`, or `pointerleave`. The controller owns click blasts.
- Keyboard focus requires keyboard input and `:focus-visible`. Text fields match `:focus-visible` after taps too.
- Programmatic focus follows the last input modality. Pointer-derived focus stays cold; keyboard-derived focus remains accessible.
- `COARSE_POINTER_DENSITY` thins transient particles. Outlines and `life: Infinity` particles are exempt; runner counts stay unchanged.
- Reduced motion blocks hot activation. Unchanged input states do not repeat bursts.

# Recipe: particle effects

Four treatments on the [particle field](particle-field.md). Each defines how its element assembles on entrance, what plays while it idles, what happens under the pointer, and what a blast looks like. The framework skill's controller runs the phases through `attachParticleEffect`; these modules never decide when.

| Effect | Element | Layer | Bleed | Idle |
|---|---|---|---|---|
| `marquee` | secondary call to action (outline) | over | 160 | six lights chase the outline; glints |
| `reactor` | primary call to action (solid) | under | 180 | embers rise from the button; a slow heartbeat outline |
| `resolve` | card | over | 140 | one light wanders the outline; glints |
| `slipstream` | an onward link (Next →) | over | 160 | hairlines drift past left to right |

Dependencies: `gsap`, `./field`.

```ts
import gsap from "gsap";
import { perimeterLength, perimeterPoint, type ParticleField } from "./field";
import type { ParticleEffectDefinition, ParticleEffectInstance } from "./attach";

const rnd = gsap.utils.random;
export type ButtonEffect = ParticleEffectDefinition<ParticleEffectInstance> & { layer: "under" | "over" };
```

## marquee

Lights gather from all around and land evenly along the outline, the button pops in, the sign ignites with a burst, and the runners set off.

```ts
const RUNNERS = 6;
/** Runner speed along the outline, px/s. */
const RUNNER_SPEED = 110;
/** How much faster the runners go under the pointer. */
const RUNNER_RUSH = 4;

export const marquee: ButtonEffect = {
  layer: "over",
  bleed: 160,
  create(field, button) {
    const runners: { t: number }[] = [];
    const state = { rush: 1, hovering: false };
    let twinkleIn = 0.4;
    let sprayAcc = 0;

    const ambient = (dt: number) => {
      const { box, radius } = field;
      const total = perimeterLength(box, radius);
      for (const run of runners) {
        run.t = (run.t + (RUNNER_SPEED * state.rush * dt) / total) % 1;
        const pt = perimeterPoint(box, radius, run.t);
        // The head is bright; each frame leaves a dot that fades, so the faster the runner the longer its tail.
        field.spawn({ x: pt.x, y: pt.y, size: 2.8, alpha: 1, life: 0.4 * (0.6 + state.rush / RUNNER_RUSH), shrink: true });
      }
      if (state.hovering) {
        // Sparkler: fine sparks fly off the outline while the pointer is on it.
        sprayAcc += 90 * dt;
        while (sprayAcc >= 1) {
          sprayAcc -= 1;
          const pt = perimeterPoint(box, radius, Math.random());
          const speed = rnd(60, 180);
          const jitter = rnd(-0.6, 0.6);
          field.spawn({
            x: pt.x, y: pt.y,
            vx: (pt.nx + jitter * pt.ny) * speed, vy: (pt.ny - jitter * pt.nx) * speed,
            size: rnd(0.8, 1.6), alpha: rnd(0.6, 1), life: rnd(0.3, 0.7), drag: 0.08, gravity: 60, shape: "spark",
          });
        }
      }
      twinkleIn -= dt;
      if (twinkleIn <= 0) {
        twinkleIn = rnd(0.25, 0.7) / (state.hovering ? 3 : 1);
        twinkle(perimeterPoint(box, radius, Math.random()));
      }
    };

    function twinkle(pt: { x: number; y: number }) {
      const size = rnd(4, 9);
      field.spawn({
        x: pt.x, y: pt.y, size, shape: "star", rotation: rnd(0, Math.PI), spin: rnd(-1.5, 1.5), life: rnd(0.45, 0.8), fade: false,
        update: (p) => { const k = Math.sin((p.age / p.life) * Math.PI); p.size = size * k; p.alpha = k; },
      });
    }

    function idle() {
      runners.length = 0;
      for (let k = 0; k < RUNNERS; k++) runners.push({ t: k / RUNNERS });
      field.addEmitter(ambient);
    }

    function flash(count: number, speed: [number, number]) {
      const { box, radius } = field;
      for (let i = 0; i < count; i++) {
        const pt = perimeterPoint(box, radius, i / count + rnd(-0.01, 0.01));
        const v = rnd(speed[0], speed[1]);
        field.spawn({ x: pt.x, y: pt.y, vx: pt.nx * v, vy: pt.ny * v, size: rnd(1, 2.2), life: rnd(0.35, 0.7), drag: 0.04, shape: "spark" });
      }
    }

    return {
      enter(delay) {
        field.sync();
        field.particles.length = 0;
        runners.length = 0;
        const { box, radius } = field;
        const cx = box.x + box.w / 2;
        const cy = box.y + box.h / 2;
        const tl = gsap.timeline({ delay });
        gsap.set(button, { autoAlpha: 0, scale: 0.5, transformOrigin: "50% 50%" });

        const count = 72;
        for (let i = 0; i < count; i++) {
          const target = perimeterPoint(box, radius, i / count);
          const angle = rnd(0, Math.PI * 2);
          const dist = rnd(180, 340);
          const p = field.spawn({ x: cx + Math.cos(angle) * dist, y: cy + Math.sin(angle) * dist, size: rnd(1.4, 2.8), alpha: 0, life: Infinity, fade: false });
          tl.to(
            p,
            {
              x: target.x, y: target.y, alpha: 1, duration: rnd(0.55, 0.85), ease: "power3.inOut",
              onComplete: () => { p.life = 0.5; p.age = 0; p.fade = true; p.shrink = true; },
            },
            rnd(0, 0.25),
          );
        }
        tl.to(button, { autoAlpha: 1, scale: 1, duration: 0.5, ease: "back.out(1.7)" }, 0.55);
        tl.call(() => { flash(40, [80, 200]); idle(); }, [], 0.95);
        return tl;
      },
      exit() { field.removeEmitter(ambient); runners.length = 0; field.release(0.25); },
      blast() {
        field.removeEmitter(ambient);
        runners.length = 0;
        flash(90, [350, 900]);
        for (let i = 0; i < 12; i++) twinkle(perimeterPoint(field.box, field.radius, Math.random()));
      },
      idle,
      hover(on) {
        state.hovering = on;
        gsap.to(state, { rush: on ? RUNNER_RUSH : 1, duration: on ? 0.35 : 0.8, ease: on ? "power3.out" : "power2.inOut", overwrite: true });
        if (on) flash(36, [120, 260]);
      },
      destroy() { field.removeEmitter(ambient); gsap.killTweensOf(state); },
    };
  },
};
```

## reactor

Sparks spiral in from a wide ring and collapse into the button; it pops in and the collapse rebounds outward as a shockwave. Idle, it breathes embers.

```ts
const EMBER_RATE = { idle: 9, hover: 70 };
const EMBER_RISE = { idle: 55, hover: 220 };
const PULSE_EVERY = 2.6;

export const reactor: ButtonEffect = {
  layer: "under",
  bleed: 180,
  create(field, button) {
    const state = { rate: EMBER_RATE.idle, rise: EMBER_RISE.idle, hovering: false };
    let emberAcc = 0;
    let pulseIn = 1.2;

    const ambient = (dt: number) => {
      const { box } = field;
      // Embers start inside the button, hidden behind it, and surface as they rise past its top edge.
      emberAcc += state.rate * dt;
      while (emberAcc >= 1) {
        emberAcc -= 1;
        field.spawn({
          x: box.x + rnd(4, box.w - 4), y: box.y + rnd(2, box.h - 2),
          vx: rnd(-10, 10) * (state.hovering ? 3 : 1), vy: -rnd(state.rise * 0.6, state.rise * 1.3),
          size: rnd(1.2, 2.8), alpha: rnd(0.7, 1), life: rnd(1.1, 2.1), gravity: -12,
          wobble: rnd(6, 16), wobbleFreq: rnd(1.5, 4), phase: rnd(0, Math.PI * 2),
        });
      }
      pulseIn -= dt;
      if (pulseIn <= 0) {
        pulseIn = PULSE_EVERY;
        if (!state.hovering) shockwave(28, 1.3, 0.35);
      }
    };

    function shockwave(spread: number, duration: number, alpha: number) {
      field.spawn({
        x: 0, y: 0, shape: "outline", size: 0, alpha, life: duration,
        update: (p) => { p.size = spread * gsap.parseEase("power2.out")(p.age / p.life); },
      });
    }

    function erupt(count: number, speed: [number, number]) {
      const { box, radius } = field;
      for (let i = 0; i < count; i++) {
        const pt = perimeterPoint(box, radius, Math.random());
        const v = rnd(speed[0], speed[1]);
        const jitter = rnd(-0.5, 0.5);
        const square = Math.random() < 0.35;
        field.spawn({
          x: pt.x, y: pt.y,
          vx: (pt.nx + jitter * pt.ny) * v, vy: (pt.ny - jitter * pt.nx) * v - 40,
          size: square ? rnd(1.5, 3) : rnd(1, 2.4), shape: square ? "square" : "dot",
          rotation: rnd(0, Math.PI), spin: rnd(-12, 12), life: rnd(0.5, 1.1), drag: 0.12, gravity: 320,
        });
      }
    }

    return {
      enter(delay) {
        field.sync();
        field.particles.length = 0;
        const { box } = field;
        const cx = box.x + box.w / 2;
        const cy = box.y + box.h / 2;
        const tl = gsap.timeline({ delay });
        gsap.set(button, { autoAlpha: 0, scale: 0.5, transformOrigin: "50% 50%" });

        const count = 110;
        for (let i = 0; i < count; i++) {
          const orbit = { radius: rnd(200, 320), angle: rnd(0, Math.PI * 2) };
          const landing = { x: rnd(-box.w * 0.4, box.w * 0.4), y: rnd(-box.h * 0.4, box.h * 0.4) };
          const p = field.spawn({ x: cx + Math.cos(orbit.angle) * orbit.radius, y: cy + Math.sin(orbit.angle) * orbit.radius, size: rnd(1, 2.4), alpha: 0, life: Infinity, fade: false, shape: "spark" });
          const turn = rnd(1.2, 2.4) * (Math.random() < 0.5 ? -1 : 1);
          tl.to(
            orbit,
            {
              radius: 0, angle: orbit.angle + turn, duration: rnd(0.6, 0.9), ease: "power3.in",
              onUpdate() {
                const k = 1 - orbit.radius / 320;
                const nx = cx + landing.x * k + Math.cos(orbit.angle) * orbit.radius;
                const ny = cy + landing.y * k + Math.sin(orbit.angle) * orbit.radius;
                // Velocity only orients the spark's tail; position is set here.
                p.vx = (nx - p.x) * 60; p.vy = (ny - p.y) * 60;
                p.x = nx; p.y = ny;
                p.alpha = Math.min(1, this.progress() * 3);
              },
              onComplete: () => { p.life = 0.12; p.age = 0; p.fade = true; p.vx = 0; p.vy = 0; },
            },
            rnd(0, 0.2),
          );
        }
        tl.to(button, { autoAlpha: 1, scale: 1, duration: 0.45, ease: "back.out(2.2)" }, 0.82);
        tl.call(() => { shockwave(60, 0.7, 0.9); erupt(44, [140, 320]); }, [], 0.84);
        tl.call(() => shockwave(90, 0.9, 0.5), [], 0.96);
        tl.call(() => field.addEmitter(ambient), [], 1.05);
        return tl;
      },
      exit() { field.removeEmitter(ambient); field.release(0.25); },
      blast() {
        field.removeEmitter(ambient);
        shockwave(120, 0.6, 1);
        gsap.delayedCall(0.08, () => shockwave(160, 0.7, 0.6));
        gsap.delayedCall(0.16, () => shockwave(200, 0.8, 0.3));
        erupt(140, [400, 1000]);
      },
      idle() { field.addEmitter(ambient); },
      hover(on) {
        state.hovering = on;
        gsap.to(state, { rate: on ? EMBER_RATE.hover : EMBER_RATE.idle, rise: on ? EMBER_RISE.hover : EMBER_RISE.idle, duration: on ? 0.3 : 0.9, ease: on ? "power3.out" : "power2.inOut", overwrite: true });
        gsap.to(button, { scale: on ? 1.04 : 1, duration: 0.3, ease: on ? "back.out(2)" : "power2.out", overwrite: "auto" });
        if (on) { shockwave(40, 0.5, 0.8); erupt(56, [160, 360]); }
      },
      destroy() { field.removeEmitter(ambient); gsap.killTweensOf(state); },
    };
  },
};
```

## resolve

Particles stream in from far off and settle into a dot grid over the card's face, row by row like a scan; the card fades up beneath them and the grid dissolves.

```ts
/** Spacing of the dot grid the card resolves from, in px. */
const GRID = 16;
const CARD_RUNNERS = { idle: 1, hover: 4 };
const CARD_RUNNER_SPEED = { idle: 50, hover: 260 };

export const resolve: ButtonEffect = {
  layer: "over",
  bleed: 140,
  create(field, card) {
    const runners: { t: number }[] = [];
    const state = { speed: CARD_RUNNER_SPEED.idle, hovering: false };
    let glintIn = 0.6;
    let sprayAcc = 0;

    const ambient = (dt: number) => {
      const { box, radius } = field;
      const total = perimeterLength(box, radius);
      for (const run of runners) {
        run.t = (run.t + (state.speed * dt) / total) % 1;
        const pt = perimeterPoint(box, radius, run.t);
        field.spawn({ x: pt.x, y: pt.y, size: state.hovering ? 2.4 : 1.8, life: state.hovering ? 0.45 : 0.6, shrink: true });
      }
      if (state.hovering) {
        sprayAcc += 40 * dt;
        while (sprayAcc >= 1) {
          sprayAcc -= 1;
          const pt = perimeterPoint(box, radius, Math.random());
          const speed = rnd(40, 120);
          field.spawn({ x: pt.x, y: pt.y, vx: pt.nx * speed, vy: pt.ny * speed, size: rnd(0.8, 1.4), life: rnd(0.3, 0.6), drag: 0.1, shape: "spark" });
        }
      }
      glintIn -= dt;
      if (glintIn <= 0) {
        glintIn = rnd(0.6, 1.6) / (state.hovering ? 4 : 1);
        glint(perimeterPoint(box, radius, Math.random()));
      }
    };

    function glint(pt: { x: number; y: number }) {
      const size = rnd(3, 7);
      field.spawn({
        x: pt.x, y: pt.y, size, shape: "star", rotation: rnd(0, Math.PI), spin: rnd(-1, 1), life: rnd(0.4, 0.7), fade: false,
        update: (p) => { const k = Math.sin((p.age / p.life) * Math.PI); p.size = size * k; p.alpha = k; },
      });
    }

    function setRunners(count: number) {
      runners.length = 0;
      for (let k = 0; k < count; k++) runners.push({ t: k / count });
    }

    function flash(count: number, speed: [number, number]) {
      const { box, radius } = field;
      for (let i = 0; i < count; i++) {
        const pt = perimeterPoint(box, radius, i / count + rnd(-0.01, 0.01));
        const v = rnd(speed[0], speed[1]);
        field.spawn({ x: pt.x, y: pt.y, vx: pt.nx * v, vy: pt.ny * v, size: rnd(1, 2), life: rnd(0.3, 0.6), drag: 0.05, shape: "spark" });
      }
    }

    function idle() { setRunners(CARD_RUNNERS.idle); field.addEmitter(ambient); }

    return {
      enter(delay) {
        field.sync();
        field.particles.length = 0;
        runners.length = 0;
        const { box } = field;
        const cx = box.x + box.w / 2;
        const cy = box.y + box.h / 2;
        const tl = gsap.timeline({ delay });
        gsap.set(card, { autoAlpha: 0, scale: 0.94, transformOrigin: "50% 50%" });

        const cols = Math.max(2, Math.floor(box.w / GRID));
        const rows = Math.max(2, Math.floor(box.h / GRID));
        const padX = (box.w - (cols - 1) * GRID) / 2;
        const padY = (box.h - (rows - 1) * GRID) / 2;
        const settle = 0.75;
        for (let r = 0; r < rows; r++) {
          for (let c = 0; c < cols; c++) {
            const tx = box.x + padX + c * GRID;
            const ty = box.y + padY + r * GRID;
            const angle = rnd(0, Math.PI * 2);
            const dist = rnd(160, 420);
            const p = field.spawn({ x: cx + Math.cos(angle) * dist, y: cy + Math.sin(angle) * dist, size: rnd(1, 1.8), alpha: 0, life: Infinity, fade: false });
            tl.to(
              p,
              {
                x: tx, y: ty, alpha: rnd(0.6, 1), duration: rnd(0.45, 0.7), ease: "power3.inOut",
                onComplete: () => { p.life = 0.45; p.age = 0; p.fade = true; p.shrink = true; },
              },
              (r / rows) * 0.25 + rnd(0, 0.06),
            );
          }
        }
        tl.to(card, { autoAlpha: 1, scale: 1, duration: 0.45, ease: "power3.out" }, settle);
        tl.call(() => { flash(24, [40, 120]); idle(); }, [], settle + 0.25);
        return tl;
      },
      exit() { field.removeEmitter(ambient); runners.length = 0; field.release(0.25); },
      blast() { field.removeEmitter(ambient); runners.length = 0; flash(60, [250, 700]); },
      idle,
      hover(on) {
        state.hovering = on;
        setRunners(on ? CARD_RUNNERS.hover : CARD_RUNNERS.idle);
        gsap.to(state, { speed: on ? CARD_RUNNER_SPEED.hover : CARD_RUNNER_SPEED.idle, duration: on ? 0.3 : 0.7, ease: on ? "power3.out" : "power2.inOut", overwrite: true });
        if (on) flash(28, [80, 200]);
      },
      destroy() { field.removeEmitter(ambient); gsap.killTweensOf(state); },
    };
  },
};
```

Cards in a grid enter with `index * 0.09` stagger on `idle`, so the route's own items have landed before the grid resolves.

## slipstream

The link rides a slipstream: hairlines rush past it from left to right. It arrives from the left through a gust and docks with a puff of sparks off the arrow. Idle, a line or two drifts past; under the pointer the wind picks up and the link leans into it. Pressed, everything blows off to the right.

```ts
const STREAK_RATE = { idle: 5, hover: 60 };
const STREAK_SPEED = { idle: 90, hover: 520 };
/** How far, in px, the link leans into the wind under the pointer. */
const LEAN = 4;

export const slipstream: ButtonEffect = {
  layer: "over",
  bleed: 160,
  create(field, button) {
    const state = { rate: STREAK_RATE.idle, speed: STREAK_SPEED.idle, hovering: false };
    let streakAcc = 0;
    let sparkIn = 1;

    /** One level hairline crossing the band, left to right. */
    function streak(x: number, speed: number, life = rnd(0.5, 0.9), alpha = rnd(0.3, 0.7)) {
      const { box } = field;
      field.spawn({ x, y: box.y + rnd(-6, box.h + 6), vx: speed, size: gsap.utils.clamp(3, 28, speed * 0.04), alpha, life, shape: "streak", shrink: true });
    }

    /** Sparks leaving the arrow's tip at the right edge. */
    function tip(count: number, speed: [number, number]) {
      const { box } = field;
      for (let i = 0; i < count; i++) {
        const v = rnd(speed[0], speed[1]);
        field.spawn({ x: box.x + box.w - 4, y: box.y + box.h / 2 + rnd(-4, 4), vx: v, vy: rnd(-v * 0.18, v * 0.18), size: rnd(0.8, 1.6), life: rnd(0.3, 0.6), drag: 0.1, shape: "spark" });
      }
    }

    const ambient = (dt: number) => {
      const { box } = field;
      streakAcc += state.rate * dt;
      while (streakAcc >= 1) {
        streakAcc -= 1;
        streak(box.x - rnd(20, 120), state.speed * rnd(0.7, 1.3));
      }
      sparkIn -= dt;
      if (sparkIn <= 0) {
        sparkIn = rnd(0.8, 2.2) / (state.hovering ? 8 : 1);
        tip(state.hovering ? 3 : 1, [state.speed, state.speed * 2]);
      }
    };

    function idle() { field.addEmitter(ambient); }

    return {
      enter(delay) {
        field.sync();
        field.particles.length = 0;
        const { box } = field;
        const tl = gsap.timeline({ delay });
        gsap.set(button, { autoAlpha: 0, x: -48 });
        for (let i = 0; i < 44; i++) {
          tl.call(() => streak(box.x - rnd(40, 160), rnd(500, 900), rnd(0.35, 0.6), rnd(0.4, 0.9)), [], rnd(0, 0.35));
        }
        tl.to(button, { autoAlpha: 1, x: 0, duration: 0.55, ease: "power4.out" }, 0.1);
        tl.call(() => { tip(14, [200, 480]); idle(); }, [], 0.5);
        return tl;
      },
      exit() { field.removeEmitter(ambient); field.release(0.25); },
      blast() {
        field.removeEmitter(ambient);
        const { box } = field;
        for (let i = 0; i < 60; i++) streak(box.x + rnd(-80, box.w), rnd(700, 1400), rnd(0.3, 0.6), rnd(0.5, 1));
        tip(50, [500, 1200]);
      },
      idle,
      hover(on) {
        state.hovering = on;
        gsap.to(state, { rate: on ? STREAK_RATE.hover : STREAK_RATE.idle, speed: on ? STREAK_SPEED.hover : STREAK_SPEED.idle, duration: on ? 0.3 : 0.8, ease: on ? "power3.out" : "power2.inOut", overwrite: true });
        gsap.to(button, { x: on ? LEAN : 0, duration: 0.3, ease: on ? "back.out(2)" : "power2.out", overwrite: "auto" });
        if (on) tip(10, [200, 500]);
      },
      destroy() { field.removeEmitter(ambient); gsap.killTweensOf(state); },
    };
  },
};
```

On press, `blast()` and tween the link `x: 64, autoAlpha: 0` while the framework skill's navigation proceeds.

## Wiring

```ts
const primary = attachParticleEffect(primaryWrap, primaryCanvas, primaryButton, reactor);
const secondary = attachParticleEffect(secondaryWrap, secondaryCanvas, secondaryButton, marquee);
watchPageTransition(hero, {
  onEntering: () => { secondary.enter(1.25); primary.enter(1.4); gsap.set([primaryWrap, secondaryWrap], { autoAlpha: 1 }); },
  onExiting: () => { primary.exit(); secondary.exit(); },
});
```

A new treatment is the same shape: `layer`, `bleed`, and `create(field, target)` returning `enter`, `exit`, `blast`, `idle`, `hover`, `destroy`. Keep every treatment monochrome (the field draws in the canvas's `color`) and every ambient cheap enough to run at rest.

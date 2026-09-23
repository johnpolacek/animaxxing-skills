# Recipe: SVG effects

Failure contract: apply [effect restoration](../effect-restoration.md) when adapting this module. The framework controller chooses recovery timing; this effect must undo even partial setup.

Three SVG effects: strokes that draw themselves in and out, an icon that morphs between two shapes, and a mark that travels along a path. They work on the project's own SVG and keep its stroke colors, widths, and fills.

The framework skill's controller calls the draw builders during intro or outro, the morph toggle on user input, and the path follower at settled; it calls each `revert` on unmount. This module never decides when.

Dependencies: `gsap`, `gsap/DrawSVGPlugin`, `gsap/MorphSVGPlugin`, `gsap/MotionPathPlugin`, all free since 3.13. Register only the ones used.

```ts
import gsap from "gsap";
import { DrawSVGPlugin } from "gsap/DrawSVGPlugin";
import { MorphSVGPlugin } from "gsap/MorphSVGPlugin";
import { MotionPathPlugin } from "gsap/MotionPathPlugin";

gsap.registerPlugin(DrawSVGPlugin, MorphSVGPlugin, MotionPathPlugin);

/* Swap for the project's helper if it has one. */
function prefersReducedMotion(): boolean {
  if (typeof window === "undefined") return true;
  const choice = document.documentElement.dataset.motion;
  if (choice === "reduced") return true;
  if (choice === "full") return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export type Teardown = () => void;
export type SvgEffect = { timeline: gsap.core.Timeline; revert: Teardown };
type Register = (fn: () => void) => void;

/**
 * Runs setup inside a GSAP context. Everything GSAP creates during setup is
 * reverted with the context. `dispose` registers writers to stop before the
 * revert; `after` registers restores to run once it is done. Teardown runs
 * once, attempts every step, and rolls back a setup that threw.
 */
function own(setup: (dispose: Register, after: Register) => void): Teardown {
  const ctx = gsap.context(() => {});
  const disposers: Array<() => void> = [];
  const restores: Array<() => void> = [];
  let done = false;
  const teardown = () => {
    if (done) return;
    done = true;
    let failure: unknown;
    const attempt = (fn: () => void) => {
      try {
        fn();
      } catch (error) {
        failure ??= error;
      }
    };
    disposers.splice(0).reverse().forEach(attempt);
    attempt(() => ctx.revert());
    restores.splice(0).reverse().forEach(attempt);
    if (failure) throw failure;
  };
  try {
    ctx.add(() => setup((fn) => disposers.push(fn), (fn) => restores.push(fn)));
  } catch (error) {
    teardown();
    throw error;
  }
  return teardown;
}

/** Records attributes and inline properties, and returns a restore for after the revert. */
function snapshot(elements: Element[], attributes: string[], props: string[]): () => void {
  const saved = elements.map((element) => ({
    attributes: attributes.map((name) => element.getAttribute(name)),
    props: props.map((prop) => (element as SVGElement).style.getPropertyValue(prop)),
  }));
  return () =>
    elements.forEach((element, i) => {
      const record = saved[i];
      if (!record) return;
      if (props.length) gsap.set(element, { clearProps: props.join(",") });
      attributes.forEach((name, j) => {
        const value = record.attributes[j];
        if (value === null || value === undefined) element.removeAttribute(name);
        else element.setAttribute(name, value);
      });
      props.forEach((prop, j) => {
        const value = record.props[j];
        if (value) (element as SVGElement).style.setProperty(prop, value);
        else (element as SVGElement).style.removeProperty(prop);
      });
    });
}

const STROKE_PROPS = ["stroke-dasharray", "stroke-dashoffset", "visibility", "opacity"];
```

## drawIn and drawOut

Strokes draw along their length, in document order. Works on `path`, `line`, `polyline`, `polygon`, `rect`, `circle`, and `ellipse` with a visible stroke. Filled shapes need a stroke or a separate outline to draw.

```ts
export type DrawOptions = { duration?: number; stagger?: number; delay?: number; onComplete?: () => void };

function draw(
  targets: gsap.DOMTarget,
  from: string,
  to: string,
  ease: string,
  { duration = 0.8, stagger = 0.12, delay = 0, onComplete }: DrawOptions,
): SvgEffect {
  const strokes = gsap.utils.toArray<SVGGeometryElement>(targets);
  const timeline = gsap.timeline({ delay, paused: true });
  if (onComplete) timeline.eventCallback("onComplete", onComplete);
  const revert = own((dispose, after) => {
    after(snapshot(strokes, [], STROKE_PROPS));
    dispose(() => timeline.kill());
    if (prefersReducedMotion()) {
      timeline.set(strokes, { drawSVG: to });
    } else {
      timeline.fromTo(strokes, { drawSVG: from }, { drawSVG: to, duration, stagger, ease });
    }
    // Render the start now, so the controller's pre-paint hiding can be released without a flash.
    timeline.progress(0).play();
  });
  return { timeline, revert };
}

/** Strokes draw from nothing to whole. Reduced motion shows them whole at once. */
export function drawIn(targets: gsap.DOMTarget, options: DrawOptions = {}): SvgEffect {
  return draw(targets, "0%", "100%", "power2.inOut", options);
}

/** Strokes retract toward their end. Reduced motion removes them at once. */
export function drawOut(targets: gsap.DOMTarget, options: DrawOptions = {}): SvgEffect {
  return draw(targets, "0% 100%", "100% 100%", "power2.in", options);
}
```

A drawn stroke's settled state is the SVG's own; `revert` returns it there once the controller is done with the effect.

## morphToggle

An icon path morphs between its own shape and an alternate, such as menu to close or play to pause. The toggle follows the control's state; the control keeps its own label and `aria-pressed` or `aria-expanded`.

```html
<button aria-expanded="false" aria-label="Menu">
  <svg viewBox="0 0 24 24" aria-hidden="true"><path id="menu-icon" d="M4 7h16M4 12h16M4 17h16" /></svg>
</button>
<svg hidden><path id="close-icon" d="M6 6l12 12M18 6L6 18" /></svg>
```

```ts
export type MorphToggle = { set: (alternate: boolean) => void; revert: Teardown };

export function morphToggle(
  path: SVGPathElement,
  alternate: SVGPathElement | string,
  { duration = 0.35, ease = "power2.inOut" }: { duration?: number; ease?: string } = {},
): MorphToggle {
  let tween: gsap.core.Tween | undefined;
  let showing = false;
  let active = true;
  const original = path.getAttribute("d") ?? "";
  const revert = own((dispose, after) => {
    after(snapshot([path], ["d"], []));
    dispose(() => {
      active = false;
      tween?.kill();
    });
  });
  const set = (next: boolean) => {
    if (!active || next === showing) return;
    showing = next;
    tween?.kill();
    const shape = next ? alternate : original;
    tween = gsap.to(path, { morphSVG: { shape }, duration: prefersReducedMotion() ? 0 : duration, ease });
  };
  return { set, revert };
}
```

Paths with very different point counts morph cleanly but can twist; draw both shapes with the same number of segments and starting corner for the tidiest move.

## followPath

A small mark travels along a path on a loop, such as a dot along a route or a spark along a circuit trace. Ambient: one per surface, never under reduced motion.

```ts
export type FollowOptions = {
  /** Seconds per lap. */
  duration?: number;
  /** Turn the mark to face its direction of travel. */
  autoRotate?: boolean;
};
export type Follower = { pause: () => void; play: () => void; revert: Teardown };

export function followPath(
  mark: SVGGraphicsElement | HTMLElement,
  path: SVGPathElement,
  { duration = 6, autoRotate = false }: FollowOptions = {},
): Follower {
  if (prefersReducedMotion()) return { pause: () => {}, play: () => {}, revert: () => {} };
  let tween: gsap.core.Tween | undefined;
  const revert = own((_dispose, after) => {
    after(snapshot([mark], ["transform"], ["transform", "translate", "rotate", "scale", "transform-origin"]));
    tween = gsap.to(mark, {
      motionPath: { path, align: path, alignOrigin: [0.5, 0.5], autoRotate },
      duration,
      ease: "none",
      repeat: -1,
    });
  });
  return { pause: () => tween?.pause(), play: () => tween?.play(), revert };
}
```

The controller pauses the follower when its surface scrolls out of view, as it does for other ambient effects.

## Controller contract

| Builder | Phase | Returns | Reduced motion |
|---|---|---|---|
| `drawIn` | Intro; strokes hidden by the pre-paint mechanism until built | `{ timeline, revert }` | Whole at once, completion fires |
| `drawOut` | Outro | `{ timeline, revert }` | Removed at once, completion fires |
| `morphToggle` | Settled; `set()` on each state change | `{ set, revert }` | Instant swap |
| `followPath` | Settled | `{ pause, play, revert }` | No-op |

- SVG markers for pre-paint hiding use `data-draw`; `drawIn` renders its start before the controller releases them.
- Call `revert` on unmount or before another effect animates the same element. `morphToggle` restores the original `d`.

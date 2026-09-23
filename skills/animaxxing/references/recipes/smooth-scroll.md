# Recipe: smooth scroll

Failure contract: apply [effect restoration](../effect-restoration.md) when adapting this module. The framework controller chooses recovery timing; this effect must undo even partial setup.

Eased scrolling for the whole document, kept in step with ScrollTrigger. Two engines share one set of controls. Lenis smooths the window's own scroll and needs no markup change. GSAP's ScrollSmoother moves a content wrapper and adds `data-speed` and `data-lag` effects. Pick one per site. Under reduced motion both return native controls, so callers never branch.

The framework skill's controller creates the scroller once per document, from the persistent shell, and destroys it when the shell unmounts. It stops the scroller through an outro, moves it after a route swap, and resizes it once the incoming page's triggers exist. Its `references/smooth-scroll.md` owns that sequence. This module never listens for navigation.

Dependencies: `gsap`, `gsap/ScrollTrigger`. `lenisScroll` needs `lenis` (1.3 or later) and its stylesheet, `lenis/dist/lenis.css`, which stops the page while the scroller is stopped. `smootherScroll` needs `gsap/ScrollSmoother`, free since 3.13. Check the installed Lenis version and types before trusting option names; they change between minors.

Keep native behavior: keyboard, scrollbar, find-in-page, and focus scrolling still work, and touch stays native unless you opt into `syncTouch`. Scroll areas inside the page that should not be smoothed take `data-lenis-prevent`. Lenis's `anchors: true` eases in-page hash links on plain pages; leave it off where a router handles hash links.

## scroll-controls.ts

```ts
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

/* Swap for the project's helper if it has one. */
export function prefersReducedMotion(): boolean {
  if (typeof window === "undefined") return true;
  const choice = document.documentElement.dataset.motion;
  if (choice === "reduced") return true;
  if (choice === "full") return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export type ScrollTarget = number | string | HTMLElement;
export type ScrollToOptions = {
  /** Jump instead of easing, as after a route swap or a history restore. */
  immediate?: boolean;
  /** Pixels added to the target position; negative clears a fixed header. */
  offset?: number;
};

export type SmoothScroll = {
  /**
   * Holds the page still, as through an outro or under a curtain. A stopped
   * ScrollSmoother pushes a native scroll back on the next scroll event, so
   * sync a router's scroll with `scrollTo` in the same task it lands.
   */
  stop(): void;
  start(): void;
  /** Scrolls to a position, a selector, or an element, even while stopped. */
  scrollTo(target: ScrollTarget, options?: ScrollToOptions): void;
  /** Re-measures after content changes size, then refreshes ScrollTrigger. */
  resize(): void;
  /** Idempotent. Restores native scrolling and removes everything the engine added. */
  destroy(): void;
};

/** A target's document position in px, or undefined when a selector matches nothing. */
export function resolveTarget(target: ScrollTarget): number | undefined {
  if (typeof target === "number") return target;
  const element = typeof target === "string" ? document.querySelector(target) : target;
  return element ? element.getBoundingClientRect().top + window.scrollY : undefined;
}

/**
 * Native scrolling behind the same controls: the reduced-motion path of both
 * engines. Stop and start do nothing, since reduced-motion outros are instant.
 */
export function nativeScroll(): SmoothScroll {
  return {
    stop() {},
    start() {},
    scrollTo(target, { immediate = false, offset = 0 } = {}) {
      const top = resolveTarget(target);
      if (top === undefined) return;
      window.scrollTo({ top: top + offset, behavior: immediate || prefersReducedMotion() ? "instant" : "smooth" });
    },
    resize() {
      ScrollTrigger.refresh();
    },
    destroy() {},
  };
}
```

## lenis-scroll.ts

```ts
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Lenis, { type LenisOptions } from "lenis";
import { nativeScroll, prefersReducedMotion, type SmoothScroll } from "./scroll-controls";

/**
 * Lenis on the window, stepped by GSAP's ticker so ScrollTrigger reads the
 * same frame. `options` pass through to Lenis; `lerp` or `duration` set the feel.
 * GSAP's lag smoothing is left as the app set it.
 */
export function lenisScroll(options: LenisOptions = {}): SmoothScroll {
  if (prefersReducedMotion()) return nativeScroll();
  // The helper above already decided, including the app's own motion setting; Lenis would read only the OS.
  const lenis = new Lenis({ ...options, autoRaf: false, respectReducedMotion: false });
  const tick = (time: number) => lenis.raf(time * 1000);
  let offScroll: (() => void) | undefined;
  let destroyed = false;
  const destroy = () => {
    if (destroyed) return;
    destroyed = true;
    gsap.ticker.remove(tick);
    offScroll?.();
    lenis.destroy();
  };
  try {
    offScroll = lenis.on("scroll", ScrollTrigger.update);
    gsap.ticker.add(tick);
  } catch (error) {
    destroy();
    throw error;
  }
  return {
    stop: () => lenis.stop(),
    start: () => lenis.start(),
    scrollTo(target, { immediate = false, offset = 0 } = {}) {
      lenis.scrollTo(target, { immediate, offset, force: true });
    },
    resize() {
      lenis.resize();
      ScrollTrigger.refresh();
    },
    destroy,
  };
}
```

## smoother-scroll.ts

ScrollSmoother needs a fixed wrapper around a content element that holds the page. Fixed and sticky UI, such as a header or a curtain, sits outside the wrapper, since the content is moved with a transform. Create it before any ScrollTrigger on the page.

```html
<header>…</header>
<div id="smooth-wrapper"><div id="smooth-content">…page…</div></div>
```

```ts
import gsap from "gsap";
import { ScrollSmoother } from "gsap/ScrollSmoother";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { nativeScroll, prefersReducedMotion, type SmoothScroll } from "./scroll-controls";

gsap.registerPlugin(ScrollTrigger, ScrollSmoother);

export type SmootherOptions = {
  /** Seconds the content takes to catch up with the scrollbar. */
  smooth?: number;
  /** Reads `data-speed` and `data-lag` inside the content. */
  effects?: boolean;
  /** Smoothing on touch, in seconds; `false` keeps touch native. */
  smoothTouch?: number | false;
};

export function smootherScroll(
  wrapper: HTMLElement,
  content: HTMLElement,
  { smooth = 1, effects = true, smoothTouch = false }: SmootherOptions = {},
): SmoothScroll {
  if (prefersReducedMotion()) return nativeScroll();
  // create() writes scroll-behavior on <html> and <body> and kill() leaves it; put it back on destroy.
  const roots = [document.documentElement, document.body];
  const behaviors = roots.map((root) => root.style.getPropertyValue("scroll-behavior"));
  const restoreBehavior = () =>
    roots.forEach((root, i) => {
      const value = behaviors[i];
      if (value) root.style.setProperty("scroll-behavior", value);
      else root.style.removeProperty("scroll-behavior");
    });
  let smoother: ScrollSmoother;
  try {
    smoother = ScrollSmoother.create({ wrapper, content, smooth, effects, smoothTouch });
  } catch (error) {
    restoreBehavior();
    throw error;
  }
  let destroyed = false;
  return {
    stop: () => smoother.paused(true),
    start: () => smoother.paused(false),
    scrollTo(target, { immediate = false, offset = 0 } = {}) {
      const element = typeof target === "string" ? document.querySelector(target) : target;
      // A stale hash matches nothing; do nothing, as the other engines do.
      if (element === null) return;
      const top = typeof element === "number" ? element : smoother.offset(element, "top top");
      smoother.scrollTo(top + offset, !immediate);
    },
    resize: () => ScrollTrigger.refresh(),
    destroy() {
      if (destroyed) return;
      destroyed = true;
      // kill() reverts the wrapper's and content's inline styles and removes its listeners.
      smoother.kill();
      restoreBehavior();
    },
  };
}
```

## Wiring

```ts
// In the persistent shell, once per document, before any page creates a ScrollTrigger:
const scroller = lenisScroll({ lerp: 0.1 });
// Outro:        scroller.stop();
// After swap:   scroller.scrollTo(window.scrollY, { immediate: true });   // once the router's own scroll has landed
// Intro built:  scroller.resize(); scroller.start();
// Shell unmount: scroller.destroy();
```

## Controller contract

| Builder | Create | Returns | Reduced motion |
|---|---|---|---|
| `lenisScroll` | Once per document, from the persistent shell | controls | Native controls; nothing created |
| `smootherScroll` | Same, before any ScrollTrigger exists | controls | Native controls; wrapper stays plain |

- One scroller per document. Page-level effects never create or destroy it.
- A stopped ScrollSmoother refuses native scrolls: its next scroll event puts the page back. When a router scrolls while the smoother is stopped, sync with `scrollTo(window.scrollY, { immediate: true })` in the same task, such as a microtask after its commit, never a frame later. Lenis adopts native jumps while stopped.
- The controller stops it for an outro and a covered swap, and starts it once the incoming page settles.
- After a swap or a history restore, once the router or browser has scrolled, call `scrollTo(window.scrollY, { immediate: true })` so the engine and the native scroll agree. Then `resize()` once the incoming triggers exist.
- ScrollTrigger effects need no custom `scroller`: Lenis moves the window, and ScrollSmoother registers itself as the default.
- Reduced motion is read when the scroller is created. When the app's motion setting changes, the controller destroys and recreates it.

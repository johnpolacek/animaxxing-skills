# Recipe: scroll effects

Failure contract: apply [effect restoration](../effect-restoration.md) when adapting this module. The framework controller chooses recovery timing; this effect must undo even partial setup.

Seven scroll-linked effects: reveals as content arrives, a scrubbed statement that fills in as it is read, parallax layers, a pinned scene, a horizontal run, a progress rule, and a velocity skew. Each builder returns an idempotent teardown (the horizontal run also returns its animation). Use the official `gsap-scrolltrigger` skill for API details; this module covers the effects and their restoration.

The framework skill's controller creates these once the owner is visible and measurable, refreshes ScrollTrigger after fonts, media, data, or scroll restoration change layout, and calls teardown on unmount; this module never decides when, never listens for navigation, and never kills triggers it did not create.

Dependencies: `gsap`, `gsap/ScrollTrigger`. `scrubStatement` also needs `gsap/SplitText` (3.13+, which registers with the active context).

Setup: `scrubStatement` with `by: "chars"` follows [stable typography for character animation](../text-stability.md#stable-typography-for-character-animation); the default word split keeps natural kerning. Verify the split-to-unsplit boundary with the [cleanup checks](../verification.md#splittext-cleanup-stability).

```ts
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { SplitText } from "gsap/SplitText";

gsap.registerPlugin(ScrollTrigger, SplitText);

/* Swap for the project's helper if it has one. */
function prefersReducedMotion(): boolean {
  if (typeof window === "undefined") return true;
  const choice = document.documentElement.dataset.motion;
  if (choice === "reduced") return true;
  if (choice === "full") return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

/** Seconds the scrubbed playhead takes to catch up with the scrollbar. `true` locks it. */
const SCRUB = 0.6;
/** Where a reveal fires: the item's top crosses this line of the viewport. */
const REVEAL_START = "top 85%";
/** Opacity of unread words in a scrubbed statement. */
const UNREAD = 0.15;
/** Largest velocity skew, degrees. */
const MAX_SKEW = 8;
/** Scroll velocity (px/s) per degree of skew. */
const SKEW_PER = 300;

export type Teardown = () => void;
export type Scroller = Element | string | undefined;

type Register = (fn: () => void) => void;

/**
 * Runs setup inside a GSAP context. Everything GSAP creates during setup
 * (sets, tweens, triggers, pins, splits) is reverted with the context.
 * `dispose` registers writers to stop before the revert; `after` registers
 * restores to run once it is done. Teardown runs once, attempts every step,
 * and also rolls back a setup that threw.
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

/** Inline properties a scrubbed scene may leave behind. */
const SCENE_PROPS = ["transform", "translate", "rotate", "scale", "opacity", "visibility", "filter", "clip-path"];

/**
 * Records these inline properties on each element and returns a restore.
 * Reverting a scrubbed, pinned timeline can leave start values inline
 * (always with `invalidateOnRefresh`), so scenes restore explicitly after
 * the context reverts. `clearProps` also resets GSAP's cached transform.
 */
function snapshotStyles(elements: HTMLElement[], props = SCENE_PROPS): () => void {
  const saved = elements.map((element) => props.map((prop) => element.style.getPropertyValue(prop)));
  return () =>
    elements.forEach((element, i) => {
      gsap.set(element, { clearProps: props.join(",") });
      props.forEach((prop, j) => {
        const value = saved[i]?.[j];
        if (value) element.style.setProperty(prop, value);
      });
    });
}
```

## revealOnScroll

Items rise into place in small batches as they cross into view, once. Items already past the line when the builder runs (a reload or restored scroll position) reveal at once, so nothing above the fold stays hidden.

```ts
export type RevealOptions = {
  start?: string;
  /** Rise distance in px. */
  y?: number;
  duration?: number;
  stagger?: number;
  scroller?: Scroller;
};

export function revealOnScroll(
  targets: gsap.DOMTarget,
  { start = REVEAL_START, y = 16, duration = 0.42, stagger = 0.09, scroller }: RevealOptions = {},
): Teardown {
  const items = gsap.utils.toArray<HTMLElement>(targets);
  if (!items.length || prefersReducedMotion()) return () => {};
  return own((dispose) => {
    // Reveal tweens start later, outside the context, so they are tracked here.
    const live = new Set<gsap.core.Tween>();
    dispose(() => live.forEach((tween) => tween.kill()));
    gsap.set(items, { autoAlpha: 0, y });
    ScrollTrigger.batch(items, {
      start,
      once: true,
      scroller,
      onEnter: (batch) => {
        const tween = gsap.to(batch, {
          autoAlpha: 1,
          y: 0,
          duration,
          stagger,
          ease: "power3.out",
          overwrite: "auto",
          onComplete: () => {
            live.delete(tween);
            gsap.set(batch, { clearProps: "transform,opacity,visibility" });
          },
        });
        live.add(tween);
      },
    });
  });
}
```

## scrubStatement

A display statement fills in word by word as it scrolls through the reading zone, and empties again on the way back. Display copy only: every word stays legible at `UNREAD`, but ordinary reading text must not depend on scroll position.

```ts
export type StatementOptions = { by?: "words" | "chars"; scrub?: number | boolean; scroller?: Scroller };

export function scrubStatement(
  element: HTMLElement,
  { by = "words", scrub = SCRUB, scroller }: StatementOptions = {},
): Teardown {
  if (prefersReducedMotion()) return () => {};
  return own(() => {
    const split = SplitText.create(element, { type: by === "chars" ? "words,chars" : "words", aria: "auto" });
    const pieces = (by === "chars" ? split.chars : split.words) as HTMLElement[];
    gsap.fromTo(
      pieces,
      { opacity: UNREAD },
      {
        opacity: 1,
        ease: "none",
        stagger: 0.1,
        scrollTrigger: { trigger: element, start: "top 80%", end: "bottom 45%", scrub, scroller },
      },
    );
  });
}
```

## parallax

Layers drift at different rates while their section crosses the viewport. Each target reads its travel in px from `data-parallax` (negative moves against the scroll); the section, not the moving layer, is the trigger.

```html
<section class="hero-media">
  <img data-parallax="-40" src="…" alt="…" />
  <p data-parallax="24">…</p>
</section>
```

```ts
export type ParallaxOptions = { scrub?: number | boolean; scroller?: Scroller };

export function parallax(section: HTMLElement, { scrub = true, scroller }: ParallaxOptions = {}): Teardown {
  const layers = gsap.utils.toArray<HTMLElement>("[data-parallax]", section);
  if (!layers.length || prefersReducedMotion()) return () => {};
  return own(() => {
    layers.forEach((layer) => {
      const travel = Number(layer.dataset.parallax) || 0;
      gsap.fromTo(
        layer,
        { y: -travel },
        {
          y: travel,
          ease: "none",
          scrollTrigger: { trigger: section, start: "top bottom", end: "bottom top", scrub, scroller },
        },
      );
    });
  });
}
```

Give the section `overflow: clip` (or `hidden`) when a layer's travel would show past its edge. Keep travel small enough that no reading text leaves its box.

## pinnedScene

Pins a section for a stretch of scroll and scrubs a timeline the caller builds, such as steps that swap, an image that scales to fill, or a diagram that assembles. `length` is the pinned distance in section heights.

```ts
export type SceneOptions = { length?: number; scrub?: number | boolean; scroller?: Scroller };

export function pinnedScene(
  section: HTMLElement,
  build: (timeline: gsap.core.Timeline, section: HTMLElement) => void,
  { length = 1, scrub = SCRUB, scroller }: SceneOptions = {},
): Teardown {
  if (prefersReducedMotion()) return () => {};
  return own((_dispose, after) => {
    after(snapshotStyles(gsap.utils.toArray<HTMLElement>("*", section)));
    const timeline = gsap.timeline({
      defaults: { ease: "none" },
      scrollTrigger: {
        trigger: section,
        start: "top top",
        end: () => `+=${section.offsetHeight * length}`,
        pin: true,
        scrub,
        scroller,
        anticipatePin: 1,
      },
    });
    build(timeline, section);
  });
}
```

```ts
// Example: three stacked steps; each fades up as the previous one leaves.
pinnedScene(section, (tl, root) => {
  const steps = gsap.utils.toArray<HTMLElement>("[data-step]", root);
  steps.slice(1).forEach((step, i) => {
    tl.to(steps[i], { autoAlpha: 0, y: -24 }).from(step, { autoAlpha: 0, y: 24 }, "<");
  });
}, { length: 2 });
```

Write the static CSS as the readable fallback (all steps stacked and visible); the build positions them for the scene with `set`/`from` tweens, which the context reverts. Build with transforms, opacity, filter, and clip-path; teardown restores those inline properties on the section's descendants, so the scene owns them while it runs.

## horizontalRun

Pins a section and translates its track sideways as the page scrolls down. The static CSS is a native horizontal scroller, so the run works without JavaScript and under reduced motion. Keyboard focus inside the track scrolls the page to that item instead of letting the clipped section scroll itself.

```html
<section class="run"><div class="run-track">…cards…</div></section>
```

```css
.run { overflow-x: auto; }
.run-track { display: flex; width: max-content; }
```

```ts
export type RunOptions = { scrub?: number | boolean; scroller?: Scroller };
export type Run = { revert: Teardown; animation: gsap.core.Tween | undefined };

export function horizontalRun(
  section: HTMLElement,
  track: HTMLElement,
  { scrub = SCRUB, scroller }: RunOptions = {},
): Run {
  if (prefersReducedMotion()) return { revert: () => {}, animation: undefined };
  let animation: gsap.core.Tween | undefined;
  const revert = own((dispose, after) => {
    after(snapshotStyles([track]));
    /** The section's content box, so padding stays visible at both ends of the run. */
    const viewport = () => {
      const style = getComputedStyle(section);
      return section.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight);
    };
    const distance = () => Math.max(0, track.scrollWidth - viewport());
    section.scrollLeft = 0;
    gsap.set(section, { overflow: "hidden" });
    animation = gsap.to(track, {
      x: () => -distance(),
      ease: "none",
      scrollTrigger: {
        trigger: section,
        start: "top top",
        end: () => `+=${distance()}`,
        pin: true,
        scrub,
        scroller,
        anticipatePin: 1,
        invalidateOnRefresh: true,
      },
    });
    const trigger = animation.scrollTrigger;
    const onFocus = (event: FocusEvent) => {
      const item = event.target as HTMLElement;
      const travel = distance();
      section.scrollLeft = 0;
      if (!trigger || !travel) return;
      const left = item.getBoundingClientRect().left - track.getBoundingClientRect().left;
      const x = gsap.utils.clamp(0, travel, left - (viewport() - item.offsetWidth) / 2);
      trigger.scroll(trigger.start + (x / travel) * (trigger.end - trigger.start));
    };
    section.addEventListener("focusin", onFocus);
    dispose(() => section.removeEventListener("focusin", onFocus));
  });
  return { revert, animation };
}
```

Nested effects inside the track pass `animation` as their trigger's `containerAnimation`; the controller creates them after the run and reverts them first. On narrow or coarse-pointer tiers the controller may skip the run and keep the native scroller.

## scrollProgress

A rule that grows with reading progress through the whole page, or through one `section`. It reports state rather than decorating, so it also runs under reduced motion, locked to the scrollbar without smoothing.

```ts
export type ProgressOptions = { section?: HTMLElement; scroller?: Scroller };

export function scrollProgress(bar: HTMLElement, { section, scroller }: ProgressOptions = {}): Teardown {
  const reduced = prefersReducedMotion();
  return own(() => {
    gsap.fromTo(
      bar,
      { scaleX: 0 },
      {
        scaleX: 1,
        ease: "none",
        transformOrigin: "0% 50%",
        scrollTrigger: section
          ? { trigger: section, start: "top top", end: "bottom bottom", scrub: reduced ? true : 0.3, scroller }
          : { start: 0, end: "max", scrub: reduced ? true : 0.3, scroller },
      },
    );
  });
}
```

Mark the bar `aria-hidden="true"`; it duplicates the scrollbar.

## velocitySkew

Targets lean with the speed of the scroll and spring back upright when it stops. Ambient: one surface per page, such as an image column or a card grid.

```ts
export type SkewOptions = { max?: number; scroller?: Scroller };

export function velocitySkew(targets: gsap.DOMTarget, { max = MAX_SKEW, scroller }: SkewOptions = {}): Teardown {
  const items = gsap.utils.toArray<HTMLElement>(targets);
  if (!items.length || prefersReducedMotion()) return () => {};
  return own((dispose) => {
    const clamp = gsap.utils.clamp(-max, max);
    const lean = { skew: 0 };
    // Recorded so the context restores each target's original transform.
    gsap.set(items, { skewY: 0, transformOrigin: "50% 50%" });
    const setSkew = gsap.quickSetter(items, "skewY", "deg");
    let settle: gsap.core.Tween | undefined;
    dispose(() => settle?.kill());
    ScrollTrigger.create({
      scroller,
      onUpdate: (self) => {
        const skew = clamp(self.getVelocity() / -SKEW_PER);
        if (Math.abs(skew) <= Math.abs(lean.skew)) return;
        lean.skew = skew;
        settle?.kill();
        settle = gsap.to(lean, {
          skew: 0,
          duration: 0.8,
          ease: "power3.out",
          onUpdate: () => setSkew(lean.skew),
        });
      },
    });
  });
}
```

## Controller contract

| Builder | Create | Returns | Reduced motion |
|---|---|---|---|
| `revealOnScroll` | Initial state, before paint, for targets that are not route items | teardown | No-op; content visible |
| `scrubStatement`, `parallax`, `velocitySkew` | Settled, once text and media are measurable | teardown | No-op; static |
| `pinnedScene` | Settled, after fonts and media above it have sized | teardown | No-op; stacked fallback |
| `horizontalRun` | Settled, same as a scene | `{ revert, animation }` | No-op; native scroller |
| `scrollProgress` | Settled | teardown | Runs, unsmoothed |

- Create triggers in document order, including pins, so later start positions account for earlier pin spacing. Build them on a fresh visit; on a re-shown preserved page, refresh instead.
- Keep scenes and runs alive through outro and end state; reverting a pin mid-outro jumps the page. Revert on unmount, inner `containerAnimation` effects first.
- Reveal targets may use the framework's pre-paint mechanism under the `data-scroll-reveal` marker. Keep them out of route intro targets so two owners never animate one element.
- A custom scroller or smooth-scroll library supplies `scroller` and its own `scrollerProxy`; the app owns that setup.
- Reduced motion is read at build time. When the preference changes, the controller tears down and rebuilds.

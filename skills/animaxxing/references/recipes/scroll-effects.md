# Recipe: scroll effects

Seven scroll-linked effects: reveals, a scrubbed statement, parallax, a pinned scene, a horizontal run, a progress rule, and a velocity skew.

Lifecycle: the framework controller builds these once the owner is measurable, refreshes ScrollTrigger when fonts, media, data, or scroll restoration change layout, and calls each idempotent teardown on unmount. Builders never kill triggers they did not create. Partial setup rolls back per [effect restoration](../effect-restoration.md).

Dependencies: `gsap`, `gsap/ScrollTrigger`. `scrubStatement` also needs `gsap/SplitText`.

Setup: `scrubStatement` with `by: "chars"` needs [stable typography](../text-stability.md#stable-typography-for-character-animation); words keep natural kerning. Verify the revert with the [cleanup checks](../verification.md#splittext-cleanup-stability).

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
 * Runs setup in its own GSAP context, which reverts its tweens, triggers, pins, and splits (SplitText 3.13+).
 * Returns a once-only teardown that also rolls back a throw. `dispose` stops writers before the revert; `after` restores after it.
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
  let failure: { error: unknown } | undefined;
  // Catch inside add: GSAP restores its current context only when add returns.
  ctx.add(() => {
    try {
      setup((fn) => disposers.push(fn), (fn) => restores.push(fn));
    } catch (error) {
      failure = { error };
    }
  });
  if (failure) {
    teardown();
    throw failure.error;
  }
  return teardown;
}

/** Inline properties a scrubbed scene may leave behind. */
const SCENE_PROPS = ["transform", "translate", "rotate", "scale", "opacity", "visibility", "filter", "clip-path"];

/**
 * Records these inline properties and returns a restore. Reverting a scrubbed, pinned
 * timeline can leave start values inline; `clearProps` also resets GSAP's cached transform.
 */
function snapshotStyles(elements: HTMLElement[], props = SCENE_PROPS): () => void {
  const saved = elements.map((element) => props.map((prop) => element.style.getPropertyValue(prop)));
  return () =>
    elements.forEach((element, i) => {
      gsap.set(element, { clearProps: props.join(",") });
      props.forEach((prop, j) => {
        const value = saved[i]?.[j];
        if (value) element.style.setProperty(prop, value);
        else element.style.removeProperty(prop);
      });
    });
}
```

## revealOnScroll

Items rise in batches as they cross into view, once. Items already past `start` (reload, restored scroll) reveal at once. Waiting items are transparent, not hidden, so they stay in the accessibility tree and tab order; focus reveals one at once.

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
    // Opacity only: visibility would drop waiting items from the accessibility tree and the tab order.
    gsap.set(items, { opacity: 0, y });
    ScrollTrigger.batch(items, {
      start,
      once: true,
      scroller,
      onEnter: (batch) => {
        const tween = gsap.to(batch, {
          opacity: 1,
          y: 0,
          duration,
          stagger,
          ease: "power3.out",
          overwrite: "auto",
          onComplete: () => {
            live.delete(tween);
            gsap.set(batch, { clearProps: "transform,opacity" });
          },
        });
        live.add(tween);
      },
    });
    // Focus can reach an item before it crosses the line; a focused item is never invisible.
    const onFocus = (event: FocusEvent) => {
      const item = event.currentTarget as HTMLElement;
      // Only the reveal's own properties; other effects on the item keep running.
      gsap.killTweensOf(item, "opacity,y");
      gsap.set(item, { clearProps: "transform,opacity" });
    };
    items.forEach((item) => item.addEventListener("focusin", onFocus));
    dispose(() => items.forEach((item) => item.removeEventListener("focusin", onFocus)));
  });
}
```

## scrubStatement

A display statement fills in word by word through the reading zone and empties on the way back. Display copy only; reading text must not depend on scroll position.

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

Layers drift at different rates while their section crosses the viewport. `data-parallax` sets each layer's travel in px (negative moves against the scroll); the section is the trigger.

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

Clip the section's overflow when travel would show past its edge. Keep reading text inside its box.

## pinnedScene

Pins a section and scrubs a timeline the caller builds, such as swapping steps or an assembling diagram. `length` is the pinned distance in section heights.

```ts
export type SceneOptions = { length?: number; scrub?: number | boolean; scroller?: Scroller };

export function pinnedScene(
  section: HTMLElement,
  build: (timeline: gsap.core.Timeline, section: HTMLElement) => void,
  { length = 1, scrub = SCRUB, scroller }: SceneOptions = {},
): Teardown {
  if (prefersReducedMotion()) return () => {};
  return own((_dispose, after) => {
    const saved = new Map(gsap.utils.toArray<HTMLElement>("*", section).map((element) => [element, snapshotStyles([element])]));
    let animated: Set<unknown> | undefined;
    // Restore only what the scene animates; other effects inside it keep their inline values. A failed build restores all.
    after(() => saved.forEach((restore, element) => (!animated || animated.has(element)) && restore()));
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
    animated = new Set(timeline.getChildren(true, true, false).flatMap((tween) => (tween as gsap.core.Tween).targets()));
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

Write the static CSS as the readable fallback, all steps stacked and visible; `build` positions them with tweens the context reverts. Animate transforms, opacity, filter, and clip-path only: teardown restores those on the scene's tween targets and leaves other effects' inline values alone.

## horizontalRun

Pins a section and translates its track sideways as the page scrolls. The static CSS is a native horizontal scroller, the fallback without JavaScript. Keyboard focus in the track scrolls the page to that item.

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
      // Pressing a card focuses it too; only keyboard focus should scroll the page.
      if (!trigger || !travel || !item.matches(":focus-visible")) return;
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

Nested effects pass `animation` as their `containerAnimation`; create them after the run and revert them first. Narrow or coarse-pointer tiers may keep the native scroller.

## scrollProgress

A rule that grows with reading progress through the page or one `section`. It reports state, so it runs under reduced motion too.

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

Targets lean with scroll speed and spring back when it stops. Ambient: one surface per page, never reading text.

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

- Create triggers in document order, pins included, so later starts account for earlier pin spacing. Build on a fresh visit; refresh a re-shown preserved page instead.
- Keep scenes and runs alive through outro and end state; reverting a pin mid-outro jumps the page. Revert on unmount, inner `containerAnimation` effects first.
- Reveal targets may use the pre-paint mechanism under a `data-scroll-reveal` marker. Keep them out of route intro targets.
- A custom scroller passes `scroller`; the app owns its `scrollerProxy`.

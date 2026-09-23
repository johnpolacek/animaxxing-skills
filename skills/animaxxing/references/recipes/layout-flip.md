# Recipe: layout Flip

Failure contract: apply [effect restoration](../effect-restoration.md) when adapting this module. The framework controller chooses recovery timing; this effect must undo even partial setup.

Layout changes that move instead of jumping, with GSAP's Flip: a grid that refiles when filtered, a list that reorders, a card that opens into a panel, and an element that morphs from one page into its counterpart on the next. Each records the old layout, lets the DOM change, and animates from the old boxes to the new ones with transforms. Flip clears its inline styles when it finishes, so CSS owns the settled layout.

The framework skill's controller decides when the layout changes and when the new one has rendered. In a framework, that is after a state update commits; in plain DOM, it is right after the change. Its `references/transition-archetypes.md` covers the cross-route handoff: where the outgoing page captures, who holds the state, and when the incoming page plays. This module never navigates or re-renders.

Dependencies: `gsap`, `gsap/Flip`, free since 3.13.

```ts
import gsap from "gsap";
import { Flip } from "gsap/Flip";

gsap.registerPlugin(Flip);

/* Swap for the project's helper if it has one. */
function prefersReducedMotion(): boolean {
  if (typeof window === "undefined") return true;
  const choice = document.documentElement.dataset.motion;
  if (choice === "reduced") return true;
  if (choice === "full") return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export type FlipOptions = {
  duration?: number;
  ease?: string;
  stagger?: number;
  /** Other properties to carry between states, such as "borderRadius,backgroundColor"; they change instantly otherwise. */
  props?: string;
  onComplete?: () => void;
};
```

## captureLayout

Record the items, change the layout, then `play()` once the new layout has rendered. Items that stay slide and resize to their new boxes. Items that appear fade and grow in. Items that go fade and shrink out, but only if the change hides them with `display: none`; a node removed from the DOM cannot animate. Keep leaving items in the document until the Flip completes, or accept that they vanish.

```ts
export type LayoutFlip = {
  /** Animates from the recorded layout to the current one. Call after the change renders. */
  play(): gsap.core.Timeline;
};

export function captureLayout(
  targets: gsap.DOMTarget,
  { duration = 0.5, ease = "power2.inOut", stagger = 0, props, onComplete }: FlipOptions = {},
): LayoutFlip {
  const items = gsap.utils.toArray<HTMLElement>(targets);
  const state = Flip.getState(items, props ? { props } : undefined);
  return {
    play() {
      if (prefersReducedMotion()) {
        const tl = gsap.timeline();
        if (onComplete) tl.eventCallback("onComplete", onComplete);
        return tl.set(items, {});
      }
      return Flip.from(state, {
        // Same nodes before and after, so Flip never matches a stale copy.
        targets: items,
        duration,
        ease,
        stagger,
        scale: true,
        absoluteOnLeave: true,
        onEnter: (entering) =>
          gsap.fromTo(entering, { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1, duration: duration * 0.8, ease: "power2.out", overwrite: "auto" }),
        onLeave: (leaving) => gsap.to(leaving, { opacity: 0, scale: 0.9, duration: duration * 0.6, ease: "power2.in", overwrite: "auto" }),
        onComplete,
      });
    },
  };
}
```

A new item that the framework renders after the capture is not in `items`. Pass a selector that also matches it to a second `captureLayout` before the change, or animate it with an ordinary entrance after the Flip.

## captureShared and playShared

A morph between two elements that stand for the same thing, such as a thumbnail and the hero it opens into. Give both the same `data-flip-id`. Capture the old one's box while it is still laid out, then play from that state onto the new one once it has rendered at its final size.

```ts
/** Records the element's box and props for a morph into its counterpart. */
export function captureShared(element: HTMLElement, props?: string): Flip.FlipState {
  return Flip.getState(element, props ? { props } : undefined);
}

export type SharedOptions = FlipOptions & {
  /** Lifts the target out of flow for the morph. Only when its container holds its size. */
  absolute?: boolean;
  /** Stacking order during the morph, so the moving element passes over its neighbors. */
  zIndex?: number;
};

/**
 * Morphs `target` from a captured state. `targets` keeps Flip on the new
 * element even when the original is still in the DOM, hidden by the router.
 */
export function playShared(
  state: Flip.FlipState,
  target: HTMLElement,
  { duration = 0.7, ease = "power3.inOut", absolute = false, zIndex = 10, onComplete }: SharedOptions = {},
): gsap.core.Timeline {
  if (prefersReducedMotion()) {
    // The target is already visible at its final size; nothing to write.
    const tl = gsap.timeline();
    if (onComplete) tl.eventCallback("onComplete", onComplete);
    return tl.set(target, {});
  }
  return Flip.from(state, { targets: target, duration, ease, scale: true, absolute, zIndex, onComplete });
}
```

`scale: true` keeps the morph to transforms. When the two boxes have different aspect ratios, morph a wrapper with `overflow: hidden` and let the image inside use `object-fit: cover`, so the picture does not stretch.

## Wiring

```ts
// Plain DOM filter:
const flip = captureLayout(grid.querySelectorAll("[data-card]"));
grid.dataset.filter = "prints";          // CSS hides the rest with display: none
flip.play();

// React: capture, commit synchronously, then play.
// const flip = captureLayout(cards);
// flushSync(() => setFilter("prints"));
// flip.play();
```

## Controller contract

| Builder | Capture | Play | Reduced motion |
|---|---|---|---|
| `captureLayout` | Just before the change, while the old layout is on screen | After the new layout renders | New layout at once; completion fires |
| `captureShared` / `playShared` | In the outgoing outro, before anything hides the element | In the incoming intro, with the target visible at its final size | Target shown at once; completion fires |

- Capture and play in the same document. A full page load between them loses the state; use a cross-document View Transition there instead.
- One owner per element. Do not Flip an element while a route intro or scroll effect is moving it, and do not mark a shared element as a page item too.
- A second change mid-Flip needs nothing special: capturing again records the in-between boxes and completes the running Flip, so the new one starts from where things are.
- `kill()` on a running Flip leaves its inline styles. To stop one, call `.revert()`: a Flip timeline's revert jumps to the end, clears them, and fires its completion once.

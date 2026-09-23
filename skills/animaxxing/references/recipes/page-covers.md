# Recipe: page covers

Full-screen covers in the persistent shell, outside any route, so they survive the swap they hide: a curtain over a route swap, and a first-visit preloader that follows real readiness.

Lifecycle: the shell's controller runs them per its [contract](#controller-contract); the framework skill's `references/transition-archetypes.md` owns the sequence, navigation locks, and recovery. Partial setup rolls back per [effect restoration](../effect-restoration.md).

Dependencies: `gsap`.

## Markup

```html
<!-- In the persistent shell, after the page content. -->
<div class="curtain" aria-hidden="true">
  <div class="curtain-panel"></div><div class="curtain-panel"></div><div class="curtain-panel"></div>
</div>

<div class="preloader" role="progressbar" aria-label="Loading" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0">
  <span data-preloader-count>0</span>
  <span class="preloader-bar" data-preloader-bar></span>
</div>
```

```css
.curtain { position: fixed; inset: 0; z-index: 50; display: flex; pointer-events: none; }
.curtain-panel { flex: 1; background: currentColor; visibility: hidden; }
.preloader { position: fixed; inset: 0; z-index: 60; display: grid; place-items: center; background: Canvas; }
.preloader-bar { position: absolute; left: 0; bottom: 0; width: 100%; height: 2px; background: currentColor; transform: scaleX(0); transform-origin: 0 50%; }
```

Color panels and preloader with existing brand tokens. For a curtain from the left or right, stack panels with `flex-direction: column`. Render the preloader only on visits that run it; the framework's first-paint script decides.

```ts
import gsap from "gsap";

/* Swap for the project's helper if it has one. */
function prefersReducedMotion(): boolean {
  if (typeof window === "undefined") return true;
  const choice = document.documentElement.dataset.motion;
  if (choice === "reduced") return true;
  if (choice === "full") return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export type Teardown = () => void;
type Register = (fn: () => void) => void;

/**
 * Runs setup in a GSAP context. `dispose` stops writers before the revert; `after` restores once it is done.
 * Teardown runs once, attempts every step, and rolls back a setup that threw.
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

/** Records inline properties and returns a restore that also resets GSAP's cached transform. */
function snapshotStyles(elements: HTMLElement[], props: string[]): () => void {
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

const COVER_PROPS = ["transform", "translate", "visibility", "opacity", "pointer-events"];
```

## curtain

Staggered panels sweep in from one edge to cover the viewport, then out the far edge. Covered panels take pointer events, so a second click cannot reach the swapping page. A cover requested mid-reveal turns back from where the panels are.

```ts
export type CurtainOptions = {
  /** The edge the panels come from. They leave by the opposite edge. */
  from?: "bottom" | "top" | "left" | "right";
  duration?: number;
  stagger?: number;
};

export type Curtain = {
  /** Sweeps the panels in. Swap the route when it completes. */
  cover(): gsap.core.Timeline;
  /** Sweeps the panels out, uncovering the incoming page. */
  reveal(): gsap.core.Timeline;
  /** Stops either sweep and restores the panels. */
  revert: Teardown;
};

export function curtain(
  panels: gsap.DOMTarget,
  { from = "bottom", duration = 0.6, stagger = 0.06 }: CurtainOptions = {},
): Curtain {
  const items = gsap.utils.toArray<HTMLElement>(panels);
  const axis = from === "bottom" || from === "top" ? "yPercent" : "xPercent";
  /** Offstage on the entry side is +100 for bottom and right, -100 for top and left. */
  const entry = from === "bottom" || from === "right" ? 100 : -100;
  let current: gsap.core.Timeline | undefined;
  const sweep = () => {
    current?.kill();
    current = gsap.timeline({ defaults: { overwrite: "auto" } });
    return current;
  };
  const revert = own((dispose, after) => {
    after(snapshotStyles(items, COVER_PROPS));
    dispose(() => current?.kill());
    gsap.set(items, { visibility: "hidden" });
  });
  return {
    cover() {
      const tl = sweep();
      // Reduced motion never flashes a full-screen panel; the framework's swap cover handles the gap.
      if (prefersReducedMotion()) return tl.set(items, { visibility: "hidden", pointerEvents: "none" });
      const resting = items.filter((item) => getComputedStyle(item).visibility === "hidden");
      if (resting.length > 0) tl.set(resting, { [axis]: entry });
      return tl
        .set(items, { visibility: "visible", pointerEvents: "auto" })
        .to(items, { [axis]: 0, duration, ease: "power3.inOut", stagger });
    },
    reveal() {
      const tl = sweep();
      if (prefersReducedMotion()) return tl.set(items, { visibility: "hidden", pointerEvents: "none" });
      return tl
        .to(items, { [axis]: -entry, duration, ease: "power3.inOut", stagger })
        .set(items, { visibility: "hidden", pointerEvents: "none", [axis]: entry });
    },
    revert,
  };
}
```

## preloader

The count eases toward reported readiness and never runs backward. `finish()` completes the count and lifts the preloader, which then leaves the accessibility tree. The controller reports progress from fonts, critical images, and data under a deadline, never from a fake timer.

```ts
export type PreloaderOptions = {
  /** Seconds the count takes to catch up with reported progress. */
  catchUp?: number;
};

export type Preloader = {
  /** Reports readiness from 0 to 1. Lower values than already shown are ignored. */
  progress(ratio: number): void;
  /** Counts to 100, then lifts the preloader. Start the first intro as it completes, or overlap its end. */
  finish(): gsap.core.Timeline;
  revert: Teardown;
};

export function preloader(root: HTMLElement, { catchUp = 0.5 }: PreloaderOptions = {}): Preloader {
  const count = root.querySelector<HTMLElement>("[data-preloader-count]");
  const bar = root.querySelector<HTMLElement>("[data-preloader-bar]");
  const shown = { value: 0 };
  let target = 0;
  let ease: gsap.QuickToFunc | undefined;
  let exit: gsap.core.Timeline | undefined;
  const render = () => {
    const percent = Math.round(shown.value * 100);
    if (count) count.textContent = String(percent);
    if (bar) gsap.set(bar, { scaleX: shown.value });
    root.setAttribute("aria-valuenow", String(percent));
  };
  const revert = own((dispose, after) => {
    const text = count?.textContent ?? "";
    const valueNow = root.getAttribute("aria-valuenow");
    after(snapshotStyles([root], COVER_PROPS));
    if (bar) after(snapshotStyles([bar], ["transform"]));
    after(() => {
      if (count) count.textContent = text;
      if (valueNow === null) root.removeAttribute("aria-valuenow");
      else root.setAttribute("aria-valuenow", valueNow);
    });
    dispose(() => {
      exit?.kill();
      gsap.killTweensOf(shown);
    });
    ease = gsap.quickTo(shown, "value", { duration: catchUp, ease: "power2.out", onUpdate: render });
    render();
  });
  return {
    progress(ratio) {
      const next = gsap.utils.clamp(0, 1, ratio);
      if (next <= target || exit) return;
      target = next;
      if (prefersReducedMotion() || !ease) {
        shown.value = target;
        render();
      } else ease(target);
    },
    finish() {
      exit?.kill();
      gsap.killTweensOf(shown);
      target = 1;
      exit = gsap.timeline({ defaults: { overwrite: "auto" } });
      if (prefersReducedMotion()) {
        shown.value = 1;
        render();
        return exit.set(root, { autoAlpha: 0 });
      }
      return exit
        .to(shown, { value: 1, duration: 0.35, ease: "power2.out", onUpdate: render })
        .to(root, { yPercent: -100, duration: 0.7, ease: "power4.inOut" }, "+=0.1")
        .set(root, { autoAlpha: 0 });
    },
    revert,
  };
}
```

## Wiring

```ts
// Example: the shell's controller, on a client navigation.
const outro = gsap.timeline();
outro.add(buildPageOutro(page, () => {}));             // optional item exit first
outro.add(cover.cover(), "-=0.15");                     // then the curtain closes
outro.eventCallback("onComplete", () => router.go());   // swap under the cover
// Incoming page prepared and hidden at its initial state:
cover.reveal().eventCallback("onComplete", () => markSettled());
```

## Controller contract

| Builder | Create | Returns | Reduced motion |
|---|---|---|---|
| `curtain` | Once, from the persistent shell | `{ cover, reveal, revert }` | Panels never show; timelines complete next frame. The controller uses its ordinary swap cover |
| `preloader` | First paint of a visit that shows it | `{ progress, finish, revert }` | Count jumps to reported values; `finish` hides at once |

- Run `cover()` on the shell's own timeline, never inside a page's GSAP context, and swap when it completes. Where each page builds its own outro, run the cover as a sibling offset into it and swap once both complete. A cover nested in a page timeline must leave that parent before the page's context reverts, or the revert reopens the curtain.
- Call `reveal()` only after every incoming target has its size and start styles.
- Back and forward take the intro-only path: no cover, and `reveal()` only if the curtain is still closed.
- A preloader is a deliberate hold under the framework's initialization contract; it counts as the prepared intro, so the framework owns its deadline and recovery.
- Keep the curtain's panels out of the accessibility tree. The preloader's `role="progressbar"` reports its value while visible; the controller sets `aria-busy` on the content it covers.

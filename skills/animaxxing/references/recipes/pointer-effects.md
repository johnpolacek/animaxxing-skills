# Recipe: pointer effects

Four pointer effects: magnetic pull, 3D tilt, a cursor follower, and a drag-and-throw track. The first three are mouse-only decoration that ignores touch and pen, so nothing sticks after a tap. The drag track works with mouse, touch, and keyboard.

Lifecycle: the framework controller builds these once the target is mounted and visible and calls the idempotent teardown on unmount. Partial setup rolls back per [effect restoration](../effect-restoration.md).

Dependencies: `gsap`. `dragTrack` also needs `gsap/Draggable` and `gsap/InertiaPlugin`.

```ts
import gsap from "gsap";
import { Draggable } from "gsap/Draggable";
import { InertiaPlugin } from "gsap/InertiaPlugin";

gsap.registerPlugin(Draggable, InertiaPlugin);

/* Swap for the project's helper if it has one. */
function prefersReducedMotion(): boolean {
  if (typeof window === "undefined") return true;
  const choice = document.documentElement.dataset.motion;
  if (choice === "reduced") return true;
  if (choice === "full") return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

/** True when the primary input can hover precisely. Events are still filtered per pointer. */
function finePointer(): boolean {
  return window.matchMedia("(hover: hover) and (pointer: fine)").matches;
}

/** Seconds a follower takes to catch the pointer. */
const FOLLOW = 0.45;
const FOLLOW_EASE = "power3.out";

export type Teardown = () => void;
type Register = (fn: () => void) => void;

/**
 * Runs setup in its own GSAP context and returns a once-only teardown that also rolls back a throw.
 * `dispose` stops writers and listeners before the context reverts; `after` restores after it.
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

/** Inline properties these effects write. */
const MOTION_PROPS = ["transform", "translate", "rotate", "scale", "opacity", "visibility"];

/**
 * Records inline properties and returns a restore. Reverting `quickTo` can leave its last
 * value inline, so restore after the context reverts. `clearProps` also resets GSAP's cache.
 */
function snapshotStyles(elements: HTMLElement[], props = MOTION_PROPS): () => void {
  const saved = elements.map((element) => props.map((prop) => element.style.getPropertyValue(prop)));
  return () =>
    elements.forEach((element, i) => {
      gsap.set(element, { clearProps: props.filter((prop) => !prop.startsWith("--")).join(",") });
      props.forEach((prop, j) => {
        const value = saved[i]?.[j];
        if (value) element.style.setProperty(prop, value);
        else element.style.removeProperty(prop);
      });
    });
}

/** Adds a listener and registers its removal. */
function listen<K extends keyof HTMLElementEventMap>(
  dispose: Register,
  target: HTMLElement | Document,
  type: K,
  handler: (event: HTMLElementEventMap[K]) => void,
): void {
  target.addEventListener(type, handler as EventListener);
  dispose(() => target.removeEventListener(type, handler as EventListener));
}
```

## magnetic

The target leans toward the mouse and settles back on leave. An optional `[data-magnetic-inner]` child travels further for depth.

```html
<a class="cta" href="/start"><span data-magnetic-inner>Start</span></a>
```

```ts
export type MagneticOptions = {
  /** Share of the pointer's offset from center the target follows. */
  strength?: number;
  /** Extra share for the inner element, relative to the target. */
  inner?: number;
};

export function magnetic(target: HTMLElement, { strength = 0.3, inner = 0.5 }: MagneticOptions = {}): Teardown {
  if (prefersReducedMotion() || !finePointer()) return () => {};
  return own((dispose, after) => {
    const label = target.querySelector<HTMLElement>("[data-magnetic-inner]");
    after(snapshotStyles(label ? [target, label] : [target]));
    const to = (el: HTMLElement, prop: "x" | "y") => gsap.quickTo(el, prop, { duration: FOLLOW, ease: FOLLOW_EASE });
    const xTo = to(target, "x");
    const yTo = to(target, "y");
    const innerX = label ? to(label, "x") : undefined;
    const innerY = label ? to(label, "y") : undefined;
    let center = { x: 0, y: 0 };

    listen(dispose, target, "pointerenter", (event) => {
      if (event.pointerType !== "mouse") return;
      // Measure once per visit; the target's own movement must not shift its center.
      const rect = target.getBoundingClientRect();
      const x = Number(gsap.getProperty(target, "x"));
      const y = Number(gsap.getProperty(target, "y"));
      center = { x: rect.left - x + rect.width / 2, y: rect.top - y + rect.height / 2 };
    });
    listen(dispose, target, "pointermove", (event) => {
      if (event.pointerType !== "mouse") return;
      const dx = (event.clientX - center.x) * strength;
      const dy = (event.clientY - center.y) * strength;
      xTo(dx);
      yTo(dy);
      innerX?.(dx * inner);
      innerY?.(dy * inner);
    });
    listen(dispose, target, "pointerleave", () => {
      xTo(0);
      yTo(0);
      innerX?.(0);
      innerY?.(0);
    });
  });
}
```

Keep `strength` low enough that the target stays under the pointer.

## tilt

A card tilts toward the mouse in 3D and exposes the pointer position as `--pointer-x` and `--pointer-y` (0% to 100%) for an app-drawn highlight.

```css
/* Optional highlight; the app picks the color. */
.card { background-image: radial-gradient(circle at var(--pointer-x, 50%) var(--pointer-y, 50%), rgb(255 255 255 / 0.12), transparent 40%); }
```

```ts
export type TiltOptions = { max?: number; perspective?: number };

export function tilt(card: HTMLElement, { max = 8, perspective = 800 }: TiltOptions = {}): Teardown {
  if (prefersReducedMotion() || !finePointer()) return () => {};
  return own((dispose, after) => {
    after(snapshotStyles([card], [...MOTION_PROPS, "--pointer-x", "--pointer-y"]));
    gsap.set(card, { transformPerspective: perspective });
    const rx = gsap.quickTo(card, "rotationX", { duration: FOLLOW, ease: FOLLOW_EASE });
    const ry = gsap.quickTo(card, "rotationY", { duration: FOLLOW, ease: FOLLOW_EASE });
    let rect = card.getBoundingClientRect();

    listen(dispose, card, "pointerenter", (event) => {
      if (event.pointerType === "mouse") rect = card.getBoundingClientRect();
    });
    listen(dispose, card, "pointermove", (event) => {
      if (event.pointerType !== "mouse") return;
      const px = gsap.utils.clamp(0, 1, (event.clientX - rect.left) / rect.width);
      const py = gsap.utils.clamp(0, 1, (event.clientY - rect.top) / rect.height);
      ry((px - 0.5) * 2 * max);
      rx((0.5 - py) * 2 * max);
      card.style.setProperty("--pointer-x", `${px * 100}%`);
      card.style.setProperty("--pointer-y", `${py * 100}%`);
    });
    listen(dispose, card, "pointerleave", () => {
      rx(0);
      ry(0);
      card.style.removeProperty("--pointer-x");
      card.style.removeProperty("--pointer-y");
    });
  });
}
```

Keep `max` small on cards with reading text.

## cursorFollower

An accent that trails the mouse beside the native cursor, never replacing it. It grows over `[data-cursor="grow"]`, disappears over `[data-cursor="hide"]` (such as text fields), and squashes on press. `data-cursor-state` on the follower mirrors the state for CSS.

```html
<div class="cursor" aria-hidden="true"></div>
```

```css
.cursor {
  position: fixed; left: 0; top: 0; z-index: 50;
  width: 12px; height: 12px; border-radius: 50%;
  background: currentColor; pointer-events: none;
  visibility: hidden;
}
```

```ts
const CURSOR_SCALE: Record<string, number> = { grow: 3, hide: 0 };

export function cursorFollower(cursor: HTMLElement): Teardown {
  if (prefersReducedMotion() || !finePointer()) return () => {};
  return own((dispose, after) => {
    after(snapshotStyles([cursor]));
    after(() => delete cursor.dataset.cursorState);
    gsap.set(cursor, { xPercent: -50, yPercent: -50, autoAlpha: 0 });
    const xTo = gsap.quickTo(cursor, "x", { duration: FOLLOW * 0.5, ease: FOLLOW_EASE });
    const yTo = gsap.quickTo(cursor, "y", { duration: FOLLOW * 0.5, ease: FOLLOW_EASE });
    // quickTo takes one real property; "scale" is an alias, so drive both axes.
    const scaleXTo = gsap.quickTo(cursor, "scaleX", { duration: 0.3, ease: "power2.out" });
    const scaleYTo = gsap.quickTo(cursor, "scaleY", { duration: 0.3, ease: "power2.out" });
    const scaleTo = (value: number) => {
      scaleXTo(value);
      scaleYTo(value);
    };
    let visible = false;
    let state = "";
    let pressed = false;
    const scale = () => (CURSOR_SCALE[state] ?? 1) * (pressed ? 0.75 : 1);

    listen(dispose, document, "pointermove", (event) => {
      if (event.pointerType !== "mouse") return;
      const next = (event.target as Element | null)?.closest<HTMLElement>("[data-cursor]")?.dataset.cursor ?? "";
      if (!visible) {
        // Appear at the pointer, not sliding in from the corner.
        gsap.set(cursor, { x: event.clientX, y: event.clientY, autoAlpha: 1 });
        visible = true;
      }
      xTo(event.clientX);
      yTo(event.clientY);
      if (next !== state) {
        state = next;
        cursor.dataset.cursorState = state;
        scaleTo(scale());
      }
    });
    listen(dispose, document, "pointerdown", (event) => {
      if (event.pointerType !== "mouse") return;
      pressed = true;
      scaleTo(scale());
    });
    listen(dispose, document, "pointerup", () => {
      pressed = false;
      scaleTo(scale());
    });
    // Hide when the mouse leaves the window; it reappears at the pointer on return.
    listen(dispose, document.documentElement, "pointerleave", () => {
      visible = false;
      gsap.set(cursor, { autoAlpha: 0 });
    });
  });
}
```

## dragTrack

A row to drag sideways and throw, snapping to the nearest item. The static CSS is a native horizontal scroller, the fallback without JavaScript. Dragging a link does not follow it; a click does. Touch drags claim only horizontal movement, so vertical swipes still scroll. Keyboard focus slides an item into view.

```html
<div class="drag-viewport"><div class="drag-track">…items…</div></div>
```

```css
.drag-viewport { overflow-x: auto; }
.drag-track { display: flex; width: max-content; }
```

```ts
export type DragTrackOptions = { snap?: boolean };
export type DragTrack = { revert: Teardown; draggable: Draggable | undefined };

export function dragTrack(viewport: HTMLElement, track: HTMLElement, { snap = true }: DragTrackOptions = {}): DragTrack {
  const reduced = prefersReducedMotion();
  let draggable: Draggable | undefined;
  const revert = own((dispose, after) => {
    // Draggable writes its own inline styles for touch and selection.
    after(snapshotStyles([track], [...MOTION_PROPS, "touch-action", "user-select", "cursor"]));
    viewport.scrollLeft = 0;
    gsap.set(viewport, { overflow: "hidden" });
    const items = Array.from(track.children) as HTMLElement[];
    const minX = () => Math.min(0, viewport.clientWidth - track.scrollWidth);
    const clampX = (x: number) => gsap.utils.clamp(minX(), 0, x);
    const stops = () => items.map((item) => clampX(-item.offsetLeft));
    const nearest = (x: number) => gsap.utils.snap(stops(), x);
    // Draggable applies `snap` only through a throw, so without inertia the release lands on the nearest item here.
    const land = () => {
      if (!draggable) return;
      gsap.set(track, { x: nearest(draggable.x) });
      draggable.update();
    };

    [draggable] = Draggable.create(track, {
      type: "x",
      bounds: { minX: minX(), maxX: 0 },
      inertia: !reduced,
      edgeResistance: 0.85,
      dragClickables: true,
      zIndexBoost: false,
      snap: snap ? { x: nearest } : undefined,
      onDragEnd: reduced && snap ? land : undefined,
    });
    const drag = draggable;
    dispose(() => drag.kill());
    // Stops a throw still in flight and the velocity tracker, both of which kill() leaves running.
    dispose(() => {
      gsap.killTweensOf(track);
      InertiaPlugin.untrack(track);
    });
    // Links and images start a native drag that swallows the gesture.
    listen(dispose, track, "dragstart", (event) => event.preventDefault());
    // Focus scrolls the clipped viewport natively; the track's transform does that job.
    listen(dispose, viewport, "scroll", () => {
      viewport.scrollLeft = 0;
    });

    const resize = new ResizeObserver(() => {
      drag.applyBounds({ minX: minX(), maxX: 0 });
      gsap.set(track, { x: clampX(Number(gsap.getProperty(track, "x"))) });
      drag.update();
    });
    resize.observe(viewport);
    resize.observe(track);
    dispose(() => resize.disconnect());

    let slide: gsap.core.Tween | undefined;
    dispose(() => slide?.kill());
    listen(dispose, track, "focusin", (event) => {
      // Pressing a link focuses it too; only keyboard focus should slide the track.
      if (!(event.target as Element).matches(":focus-visible")) return;
      const item = items.find((candidate) => candidate.contains(event.target as Node));
      if (!item) return;
      const x = clampX(-(item.offsetLeft - (viewport.clientWidth - item.offsetWidth) / 2));
      slide?.kill();
      slide = gsap.to(track, { x, duration: reduced ? 0 : 0.4, ease: "power3.out", onUpdate: () => drag.update() });
    });
  });
  return { revert, draggable };
}
```

## Controller contract

| Builder | Create | Returns | Coarse pointer or reduced motion |
|---|---|---|---|
| `magnetic`, `tilt` | Settled, once the target's layout is final | teardown | No-op |
| `cursorFollower` | Once per document, from the persistent shell | teardown | No-op; follower stays hidden |
| `dragTrack` | Settled, once item widths are final | `{ revert, draggable }` | Drag and snap still work; reduced motion drops the throw |

- Stop magnetic and tilt before an outro moves the same target.
- One pointer response per control: not `magnetic` or `tilt` plus a particle hot state.
- The fine-pointer check runs at build; per-event `pointerType` filtering covers hybrid devices.
- Revert the drag track before its items change; rebuild after they render.

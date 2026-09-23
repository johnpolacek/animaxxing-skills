# Recipe: component motion

Failure contract: apply [effect restoration](../effect-restoration.md) when adapting this module. The framework controller chooses recovery timing; this effect must undo even partial setup.

Four pieces of component motion: a full-screen menu that wipes in and staggers its links, enter and exit for a native `<dialog>`, an accordion panel that grows to its content, and a tab indicator that slides onto the active tab. The app keeps its own markup, styling, and state: `aria-expanded`, `inert`, the focus trap, `hidden`, `open`, and `aria-selected` stay where they are. These builders only move inline styles between the states the app has already chosen, and each teardown puts those styles back.

The [motion vocabulary](../motion-vocabulary.md#tokens) bans tweening `width` and `height`. `disclosure` is the one sanctioned exception, and its rules are stated there. Everything else is transforms, opacity, clip, and one custom property.

The framework skill's controller creates each builder once the component is mounted, calls `open`, `close`, or `moveTo` when the app's state changes, and calls `revert` on unmount; this module never decides when. Every timeline returned here completes and fires its callbacks, under reduced motion too, so the app can hang state changes on `onComplete`.

Dependencies: `gsap`.

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
 * Runs setup inside a GSAP context. Everything GSAP creates during setup is
 * reverted with the context. `dispose` registers writers and listeners to
 * stop before the revert; `after` registers restores to run once it is done.
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
  target: HTMLElement,
  type: K,
  handler: (event: HTMLElementEventMap[K]) => void,
): void {
  target.addEventListener(type, handler as EventListener);
  dispose(() => target.removeEventListener(type, handler as EventListener));
}

/**
 * One timeline in flight per component. Starting the next kills the one
 * running, and the next tweens from current values, so a close picks up an
 * open from wherever it is instead of jumping to either end.
 */
function relay() {
  let current: gsap.core.Timeline | undefined;
  return {
    next(): gsap.core.Timeline {
      current?.kill();
      current = gsap.timeline({ defaults: { overwrite: "auto" } });
      return current;
    },
    kill(): void {
      current?.kill();
    },
  };
}

type Edge = "top" | "bottom" | "left" | "right";
```

## menuOverlay

A full-screen panel wipes in from one edge, then its links rise in one after another. Closing runs the links out and the wipe back from wherever the open has reached. At rest the panel is `visibility: hidden`, so its links are out of the tab order and the accessibility tree; the wipe is a `clip-path` inset, so the panel never leaves its position.

The app owns the trigger's `aria-expanded`, `inert` on the rest of the page, the focus trap, and Escape. It calls `open()` after setting that state and moves focus into the panel when the timeline completes; it calls `close()` on Escape or the close control and returns focus to the trigger when that completes. Do not hide the panel with `display: none` or `hidden`; the builder needs it laid out.

```css
.menu { position: fixed; inset: 0; z-index: 40; visibility: hidden; }
```

```ts
export type MenuOverlayOptions = {
  /** Selector, within the panel, for the items that stagger in. */
  links?: string;
  /** The edge the panel wipes in from. */
  from?: Edge;
  duration?: number;
  stagger?: number;
};

export type MenuOverlay = {
  /** Wipes the panel in, then staggers the links. Move focus inside when it completes. */
  open(): gsap.core.Timeline;
  /** Links out, then the wipe back, from wherever the open is. Return focus to the trigger when it completes. */
  close(): gsap.core.Timeline;
  revert: Teardown;
};

/** Pixels the links rise from and return to. */
const LINK_Y = 16;

export function menuOverlay(
  panel: HTMLElement,
  { links = "a", from = "top", duration = 0.5, stagger = 0.05 }: MenuOverlayOptions = {},
): MenuOverlay {
  const run = relay();
  /** Percent of the panel still clipped, on the edge opposite `from`. Tweened as a number so a computed clip never has to be parsed. */
  const clip = { inset: 100 };
  const insets: Record<Edge, () => string> = {
    top: () => `inset(0% 0% ${clip.inset}% 0%)`,
    bottom: () => `inset(${clip.inset}% 0% 0% 0%)`,
    left: () => `inset(0% ${clip.inset}% 0% 0%)`,
    right: () => `inset(0% 0% 0% ${clip.inset}%)`,
  };
  const paint = () => {
    panel.style.clipPath = insets[from]();
  };
  let items: HTMLElement[] = [];
  const revert = own((dispose, after) => {
    after(snapshotStyles([panel], ["visibility", "clip-path"]));
    dispose(run.kill);
    gsap.set(panel, { visibility: "hidden" });
    paint();
    items = Array.from(panel.querySelectorAll<HTMLElement>(links));
    after(snapshotStyles(items, ["opacity", "visibility", "transform", "translate"]));
    gsap.set(items, { autoAlpha: 0, y: LINK_Y });
  });
  return {
    open() {
      const tl = run.next().set(panel, { visibility: "visible" });
      if (prefersReducedMotion()) return tl.set(clip, { inset: 0, onUpdate: paint }).set(items, { autoAlpha: 1, y: 0 });
      return tl
        .to(clip, { inset: 0, duration, ease: "power3.inOut", onUpdate: paint })
        .to(items, { autoAlpha: 1, y: 0, duration: 0.4, ease: "power2.out", stagger }, "-=0.2");
    },
    close() {
      const tl = run.next();
      if (prefersReducedMotion()) {
        return tl.set(items, { autoAlpha: 0, y: LINK_Y }).set(clip, { inset: 100, onUpdate: paint }).set(panel, { visibility: "hidden" });
      }
      return tl
        .to(items, { autoAlpha: 0, y: LINK_Y, duration: 0.2, ease: "power2.in", stagger: { each: stagger / 2, from: "end" } })
        .to(clip, { inset: 100, duration: duration * 0.8, ease: "power3.inOut", onUpdate: paint }, "-=0.1")
        .set(panel, { visibility: "hidden" });
    },
    revert,
  };
}
```

Links become visible, and focusable, as each one arrives; a close control that should be usable at once goes outside the `links` selector. Under reduced motion the panel and links appear and vanish whole.

## dialogMotion

Enter and exit for a native `<dialog>`. `open()` calls `showModal()` and fades the backdrop while the panel scales in (or slides in from an edge for a drawer or sheet). `close(returnValue)` runs the exit first and calls `dialog.close(returnValue)` when it lands, so `returnValue`, the `close` event, and the native focus return all behave as usual. Escape fires the dialog's `cancel` event; the builder prevents the instant close and runs the exit instead.

Focus stays native: `showModal()` moves it into the dialog, and `dialog.close()` returns it to the element that had it. The dialog's contents stay focusable while hidden because the entrance uses `opacity`, never `visibility`. The backdrop is a pseudo-element GSAP cannot reach, so the builder tweens `--dialog-backdrop` on the dialog and the app's CSS reads it; `::backdrop` inherits from its dialog in current browsers.

```css
dialog::backdrop { background: rgb(0 0 0 / 0.5); opacity: var(--dialog-backdrop, 1); }
/* A drawer: the app positions it; the builder only slides it. */
dialog.drawer { margin: 0 0 0 auto; height: 100%; max-height: none; }
```

```ts
export type DialogPlacement = "center" | Edge;
export type DialogMotionOptions = {
  /** `center` scales in; an edge slides the dialog in from that side. */
  placement?: DialogPlacement;
  duration?: number;
};

export type DialogMotion = {
  /** Calls `showModal()` unless already open, then animates the backdrop and panel in. */
  open(): gsap.core.Timeline;
  /** Animates out, then calls `dialog.close(returnValue)`. */
  close(returnValue?: string): gsap.core.Timeline;
  revert: Teardown;
};

const DIALOG_PROPS = ["opacity", "transform", "translate", "--dialog-backdrop"];
const ONSTAGE = { opacity: 1, x: 0, y: 0, xPercent: 0, yPercent: 0, scale: 1, "--dialog-backdrop": 1 };
const OFFSTAGE: Record<DialogPlacement, gsap.TweenVars> = {
  center: { scale: 0.96, y: 8 },
  top: { yPercent: -100 },
  bottom: { yPercent: 100 },
  left: { xPercent: -100 },
  right: { xPercent: 100 },
};

export function dialogMotion(dialog: HTMLDialogElement, { placement = "center", duration = 0.3 }: DialogMotionOptions = {}): DialogMotion {
  const run = relay();
  const hidden = { opacity: 0, "--dialog-backdrop": 0 };
  const exit = placement === "center" ? { scale: 0.98 } : OFFSTAGE[placement];
  let rest = () => {};
  const close = (returnValue?: string) => {
    const tl = run.next();
    if (!dialog.open) return tl;
    const finish = () => {
      if (dialog.open) dialog.close(returnValue);
    };
    if (prefersReducedMotion()) return tl.call(finish);
    return tl.to(dialog, { ...hidden, ...exit, duration: duration * 0.7, ease: "power2.in" }).call(finish);
  };
  const revert = own((dispose, after) => {
    rest = snapshotStyles([dialog], DIALOG_PROPS);
    after(rest);
    dispose(run.kill);
    // Browsers let a page cancel Escape once per user activation; an uncancelable
    // cancel closes at once and the close listener below still tidies up.
    listen(dispose, dialog, "cancel", (event) => {
      if (!event.cancelable) return;
      event.preventDefault();
      close();
    });
    // Every close, animated or not, ends at the dialog's own styles. The event is a
    // task after close(); a reopen already in flight by then keeps its start state.
    listen(dispose, dialog, "close", () => {
      if (dialog.open) return;
      run.kill();
      rest();
    });
  });
  return {
    open() {
      const tl = run.next();
      if (!dialog.open) {
        // Hidden before its first paint; focus still lands inside because opacity keeps the contents focusable.
        gsap.set(dialog, { ...hidden, ...OFFSTAGE[placement] });
        dialog.showModal();
      }
      if (prefersReducedMotion()) return tl.set(dialog, ONSTAGE);
      return tl.to(dialog, { ...ONSTAGE, duration, ease: "power3.out" });
    },
    close,
    revert,
  };
}
```

Anything that closes the dialog directly, such as a `<form method="dialog">` submit or the app's own `dialog.close()`, closes instantly and still ends clean; route it through `close(value)` when the exit matters. `revert` never closes the dialog; the app owns its `open` state.

## disclosure

An accordion panel grows from 0 to its content height and back. This is the sanctioned exception to the layout-property ban, under these rules: one panel per builder, the end height is measured from the content at call time (`height: "auto"`), `overflow: hidden` is applied only while the height moves, and the inline height is cleared once open so the content can reflow. The tween is the panel's own box; siblings move because layout moves them.

The app owns `aria-expanded` on the trigger and the panel's `hidden`. Show the panel, then call `open()`; call `close()`, then apply `hidden` when it completes so the closed content leaves the tab order. A panel that is not rendered at build is collapsed inline, so removing `hidden` paints nothing until `open()` runs. Padding on the panel itself stays visible at height 0; pad an inner element.

```ts
export type DisclosureOptions = { duration?: number; ease?: string };

export type Disclosure = {
  /** After the app shows the panel: grows from the current height to the content height, then clears the inline height. */
  open(): gsap.core.Timeline;
  /** Collapses to 0 and leaves `height: 0; overflow: hidden` inline. Apply `hidden` when it completes. */
  close(): gsap.core.Timeline;
  revert: Teardown;
};

const COLLAPSED = { height: 0, overflow: "hidden" };

export function disclosure(panel: HTMLElement, { duration = 0.3, ease = "power2.inOut" }: DisclosureOptions = {}): Disclosure {
  const run = relay();
  let rest = () => {};
  const revert = own((dispose, after) => {
    rest = snapshotStyles([panel], ["height", "overflow"]);
    after(rest);
    dispose(run.kill);
    // Hidden, or inside a closed <details>: collapse now so showing it reveals nothing early.
    const rendered = panel.checkVisibility ? panel.checkVisibility() : panel.getClientRects().length > 0;
    if (!rendered) gsap.set(panel, COLLAPSED);
  });
  return {
    open() {
      const tl = run.next();
      if (prefersReducedMotion()) return tl.call(rest);
      // The sanctioned layout tween: "auto" measures the content when the tween starts.
      return tl.set(panel, { overflow: "hidden" }).to(panel, { height: "auto", duration, ease }).call(rest);
    },
    close() {
      const tl = run.next();
      if (prefersReducedMotion()) return tl.set(panel, COLLAPSED);
      return tl.set(panel, { overflow: "hidden" }).to(panel, { height: 0, duration, ease });
    },
    revert,
  };
}
```

With `<details>`, wrap the content after the `<summary>` in one panel element and keep the element's own `open` state: prevent the summary's default, set `open` before `open()`, and clear it when `close()` completes (see Wiring). Where the app already animates `::details-content` in CSS, do not add this on top. Under reduced motion the panel snaps between its two rest states and both timelines complete.

## tabIndicator

An underline or pill slides and resizes onto the selected tab using transforms only: `x` from its own resting position and `scaleX` from its own resting width, so the indicator's CSS decides its color, thickness, and radius. Positions are measured physically, so a tab list in RTL needs nothing extra. A `ResizeObserver` on the list and its tabs re-fits the indicator when widths change.

The app owns `aria-selected`, the roving `tabindex`, and arrow-key handling; it calls `moveTo(tab)` when selection changes (or on focus, if it activates tabs on focus). At build the indicator sits under the tab that is `aria-selected="true"`, if any.

```css
.tablist { position: relative; }
.tab-indicator { position: absolute; inset-inline-start: 0; bottom: 0; width: 40px; height: 2px; background: currentColor; }
```

```ts
export type TabIndicatorOptions = { duration?: number; ease?: string };

export type TabIndicator = {
  /** Slides and resizes the indicator onto `tab`. Call it when the selected tab changes. */
  moveTo(tab: HTMLElement): gsap.core.Timeline;
  revert: Teardown;
};

export function tabIndicator(
  indicator: HTMLElement,
  tablist: HTMLElement,
  { duration = 0.3, ease = "power3.out" }: TabIndicatorOptions = {},
): TabIndicator {
  const run = relay();
  let active: HTMLElement | undefined;
  /** Transforms from the indicator's resting box onto the tab's, in viewport coordinates. */
  const fit = (tab: HTMLElement) => {
    const box = indicator.getBoundingClientRect();
    const target = tab.getBoundingClientRect();
    // With the origin at the left edge, only x moves that edge and only scaleX changes the width.
    const left = box.left - Number(gsap.getProperty(indicator, "x"));
    const width = box.width / Number(gsap.getProperty(indicator, "scaleX"));
    return { x: target.left - left, scaleX: target.width / width };
  };
  const revert = own((dispose, after) => {
    after(snapshotStyles([indicator], ["transform", "translate", "transform-origin"]));
    dispose(run.kill);
    gsap.set(indicator, { transformOrigin: "0% 50%" });
    active = tablist.querySelector<HTMLElement>('[aria-selected="true"]') ?? undefined;
    if (active) gsap.set(indicator, fit(active));
    let primed = false;
    const resize = new ResizeObserver(() => {
      // The first delivery only reports initial sizes; the indicator is already placed.
      if (!primed) {
        primed = true;
        return;
      }
      if (active) run.next().set(indicator, fit(active));
    });
    resize.observe(tablist);
    tablist.querySelectorAll<HTMLElement>('[role="tab"]').forEach((tab) => resize.observe(tab));
    dispose(() => resize.disconnect());
  });
  return {
    moveTo(tab) {
      active = tab;
      const tl = run.next();
      if (prefersReducedMotion()) return tl.set(indicator, fit(tab));
      return tl.to(indicator, { ...fit(tab), duration, ease });
    },
    revert,
  };
}
```

Under reduced motion the indicator jumps onto the tab. Revert before the tabs change and rebuild after the new ones render; the observer only knows the tabs present at build.

## Wiring

```ts
// Example: the app's handlers; the builders were created by the framework controller at settled.
toggle.addEventListener("click", () => {
  const opening = toggle.getAttribute("aria-expanded") !== "true";
  toggle.setAttribute("aria-expanded", String(opening));
  main.inert = opening;
  if (opening) menu.open().eventCallback("onComplete", () => firstLink.focus());
  else menu.close().eventCallback("onComplete", () => toggle.focus());
});

openButton.addEventListener("click", () => modal.open());
okButton.addEventListener("click", () => modal.close("ok")); // Escape is handled for you.

trigger.addEventListener("click", () => {
  const opening = trigger.getAttribute("aria-expanded") !== "true";
  trigger.setAttribute("aria-expanded", String(opening));
  if (opening) {
    panel.hidden = false;
    accordion.open();
  } else accordion.close().eventCallback("onComplete", () => (panel.hidden = true));
});

// <details>: keep its own state, animate around it.
summary.addEventListener("click", (event) => {
  event.preventDefault();
  if (details.open) detailsMotion.close().eventCallback("onComplete", () => (details.open = false));
  else {
    details.open = true;
    detailsMotion.open();
  }
});

tablist.addEventListener("click", (event) => {
  const tab = (event.target as Element).closest<HTMLElement>('[role="tab"]');
  if (tab) selectTab(tab); // the app's own selection; it calls indicator.moveTo(tab)
});
```

## Controller contract

| Builder | Create | Returns | Reduced motion |
|---|---|---|---|
| `menuOverlay` | Settled, once the panel is laid out | `{ open, close, revert }` | Panel and links appear or vanish whole; both timelines complete |
| `dialogMotion` | Settled, once per `<dialog>` | `{ open, close, revert }` | `open()` shows at once; `close()` closes on the next tick |
| `disclosure` | Settled, once per panel | `{ open, close, revert }` | Height snaps; the inline height is still cleared once open |
| `tabIndicator` | Settled, once tab widths are final | `{ moveTo, revert }` | Jumps onto the tab |

- State first, motion second, in the same task: set `aria-expanded`, `inert`, `hidden`, or `open`, then call the builder. Hang the closing state change on the returned timeline's `onComplete`.
- `open()` and `close()` may interrupt each other at any point; the next call tweens from where things are. Nothing here navigates, changes attributes, or moves focus; `dialog.close()` is the one exception and it is the dialog's own.
- A menu in the persistent shell belongs to the shell's controller, not a page's GSAP context; a context reverted at unmount would strip its rest styles.
- Revert before the panel, dialog, or tabs are removed from the DOM.

# Recipe: counters and marquees

A number that counts up to its value and a seamless looping marquee. Both start from markup that reads correctly without JavaScript.

Lifecycle: see the [controller contract](#controller-contract); the controller calls each `revert` on unmount. Partial setup rolls back per [effect restoration](../effect-restoration.md).

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
 * Runs setup in its own GSAP context and returns a once-only teardown that also rolls back a throw.
 * `dispose` undoes writers, observers, and DOM additions before the context reverts; `after` restores after it.
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

/** Records inline properties and returns a restore for after the revert. */
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
```

## countUp

The element's text is its final value. Each frame keeps its separators, decimals, prefix, and suffix, so `1,204`, `98.6%`, and `$3.2M` count correctly. Pass `locale` when the figure's formatting differs from the page's `lang`. Width is reserved at the final value, and assistive technology reads only the final value.

```html
<span class="stat" data-count>12,480</span>
```

```css
/* Equal-width digits keep the count from jittering. */
.stat { font-variant-numeric: tabular-nums; }
```

```ts
export type CountOptions = {
  from?: number;
  duration?: number;
  delay?: number;
  /** Locale of the figure's formatting, for reading and writing it. Defaults to the document's `lang`. */
  locale?: string;
  onComplete?: () => void;
};
export type Count = { timeline: gsap.core.Timeline; revert: Teardown };

/** `locale`, else the document's `lang`. An unsupported or malformed tag, such as `en_US`, falls back to the browser's. */
function numberLocale(locale: string | undefined): string | undefined {
  const tag = locale ?? (document.documentElement.lang || undefined);
  try {
    return tag && Intl.NumberFormat.supportedLocalesOf(tag).length > 0 ? tag : undefined;
  } catch {
    return undefined;
  }
}

/** The locale's decimal mark: "." for en, "," for de. */
function decimalMark(locale: string | undefined): string {
  return new Intl.NumberFormat(locale).formatToParts(1.5).find((part) => part.type === "decimal")?.value ?? ".";
}

/** Splits "$3.2M" into "$", 3.2, "M" and keeps the decimals shown. */
function parseFigure(text: string, decimal: string) {
  const match = text.match(/^(\D*?)(-?[\d.,\s]*\d)(.*)$/s);
  if (!match) return undefined;
  const [, prefix = "", digits = "", suffix = ""] = match;
  // A mark that appears twice is grouping in another convention, not a decimal point.
  const at = digits.indexOf(decimal) === digits.lastIndexOf(decimal) ? digits.lastIndexOf(decimal) : -1;
  const whole = at >= 0 ? digits.slice(0, at) : digits;
  const fraction = at >= 0 ? digits.slice(at + 1).replace(/\D/g, "") : "";
  const value = Number(`${whole.replace(/\D/g, "") || 0}.${fraction || 0}`) * (digits.trim().startsWith("-") ? -1 : 1);
  return { prefix, suffix, value, decimals: fraction.length };
}

/** Visually hidden, still read by assistive technology. */
const VISUALLY_HIDDEN = { position: "absolute", width: "1px", height: "1px", overflow: "hidden", clipPath: "inset(50%)", whiteSpace: "nowrap" };

export function countUp(
  element: HTMLElement,
  { from = 0, duration = 1.6, delay = 0, locale, onComplete }: CountOptions = {},
): Count {
  const finalText = element.textContent ?? "";
  const figureLocale = numberLocale(locale);
  const figure = parseFigure(finalText.trim(), decimalMark(figureLocale));
  const timeline = gsap.timeline({ delay, defaults: { overwrite: "auto" } });
  if (onComplete) timeline.eventCallback("onComplete", onComplete);
  const revert = own((dispose, after) => {
    after(snapshotStyles([element], ["min-width", "display"]));
    after(() => {
      element.textContent = finalText;
    });
    dispose(() => timeline.kill());
    if (!figure || prefersReducedMotion()) return;
    const format = new Intl.NumberFormat(figureLocale, {
      minimumFractionDigits: figure.decimals,
      maximumFractionDigits: figure.decimals,
    });
    // Reserve the final width before the digits change.
    const width = element.getBoundingClientRect().width;
    gsap.set(element, { display: "inline-block", minWidth: `${width}px` });
    // The counting digits are hidden from assistive technology, which reads the final value from its twin.
    const shown = document.createElement("span");
    shown.setAttribute("aria-hidden", "true");
    const spoken = document.createElement("span");
    spoken.textContent = finalText;
    Object.assign(spoken.style, VISUALLY_HIDDEN);
    element.replaceChildren(shown, spoken);
    const write = (n: number) => {
      shown.textContent = `${figure.prefix}${format.format(n)}${figure.suffix}`;
    };
    const counter = { n: from };
    write(from);
    timeline.to(counter, {
      n: figure.value,
      duration,
      ease: "power3.out",
      onUpdate: () => write(counter.n),
      onComplete: () => {
        element.textContent = finalText;
      },
    });
  });
  return { timeline, revert };
}
```

Unusual formats (fractions, ranges, several numbers) are left alone; mark one number per element.

## marquee

A row scrolls sideways forever. Clones fill the container and are `aria-hidden` and `inert`, so each item is announced and focused once. It slows on mouse hover and pauses on focus inside and off screen.

```html
<div class="marquee" aria-label="Clients">
  <ul class="marquee-row">…items…</ul>
</div>
```

```css
.marquee { overflow: hidden; }
.marquee-row { display: flex; width: max-content; flex: none; }
.marquee-inner { display: flex; width: max-content; } /* Added by the builder around the rows. */
```

```ts
export type MarqueeOptions = {
  /** Travel in px per second. */
  speed?: number;
  /** -1 moves left, 1 moves right. */
  direction?: -1 | 1;
  /** Speed multiplier while the mouse is over the marquee. */
  hoverSpeed?: number;
};
export type Marquee = { pause: () => void; play: () => void; revert: Teardown };

export function marquee(
  container: HTMLElement,
  row: HTMLElement,
  { speed = 60, direction = -1, hoverSpeed = 0.25 }: MarqueeOptions = {},
): Marquee {
  if (prefersReducedMotion()) return { pause: () => {}, play: () => {}, revert: () => {} };
  let loop: gsap.core.Tween | undefined;
  let paused = false;
  let visible = true;
  let focused = false;
  const sync = () => {
    if (!loop) return;
    if (paused || !visible || focused) loop.pause();
    else loop.play();
  };

  const revert = own((dispose) => {
    // Wrap the row and its clones in one strip that moves; the row itself is never transformed.
    const strip = document.createElement("div");
    strip.className = "marquee-inner";
    row.before(strip);
    strip.append(row);
    dispose(() => {
      strip.before(row);
      strip.remove();
    });

    const build = () => {
      loop?.kill();
      strip.querySelectorAll("[data-marquee-clone]").forEach((clone) => clone.remove());
      gsap.set(strip, { x: 0 });
      const width = row.offsetWidth;
      if (!width) return;
      const copies = Math.ceil(container.clientWidth / width) + 1;
      for (let i = 0; i < copies; i++) {
        const clone = row.cloneNode(true) as HTMLElement;
        clone.dataset.marqueeClone = "";
        clone.setAttribute("aria-hidden", "true");
        clone.inert = true;
        clone.querySelectorAll("[id]").forEach((node) => node.removeAttribute("id"));
        clone.removeAttribute("id");
        strip.append(clone);
      }
      const start = direction < 0 ? 0 : -width;
      loop = gsap.fromTo(strip, { x: start }, { x: start + direction * width, duration: width / speed, ease: "none", repeat: -1 });
      sync();
    };
    build();
    dispose(() => loop?.kill());

    // Rebuild when the row or container changes width, once per frame at most.
    let frame = 0;
    const resize = new ResizeObserver(() => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(build);
    });
    resize.observe(container);
    resize.observe(row);
    dispose(() => {
      cancelAnimationFrame(frame);
      resize.disconnect();
    });

    const seen = new IntersectionObserver(([entry]) => {
      visible = entry?.isIntersecting ?? true;
      sync();
    });
    seen.observe(container);
    dispose(() => seen.disconnect());

    let slow: gsap.core.Tween | undefined;
    dispose(() => slow?.kill());
    const ease = (scale: number) => {
      slow?.kill();
      if (loop) slow = gsap.to(loop, { timeScale: scale, duration: 0.4, ease: "power2.out" });
    };
    const on = <K extends keyof HTMLElementEventMap>(type: K, handler: (event: HTMLElementEventMap[K]) => void) => {
      container.addEventListener(type, handler);
      dispose(() => container.removeEventListener(type, handler));
    };
    on("pointerenter", (event) => {
      if (event.pointerType === "mouse") ease(hoverSpeed);
    });
    on("pointerleave", () => ease(1));
    on("focusin", () => {
      focused = true;
      sync();
    });
    on("focusout", (event) => {
      focused = container.contains(event.relatedTarget as Node | null);
      sync();
    });
  });

  return {
    pause: () => {
      paused = true;
      sync();
    },
    play: () => {
      paused = false;
      sync();
    },
    revert,
  };
}
```

The endless loop needs a user pause (WCAG 2.2.2): wire `pause` and `play` to a visible control.

## Controller contract

| Builder | Phase | Returns | Reduced motion |
|---|---|---|---|
| `countUp` | Intro, or when the figure scrolls into view | `{ timeline, revert }` | Final value shown; completion fires |
| `marquee` | Settled, once fonts and images in the row have loaded | `{ pause, play, revert }` | No-op; row static, wrapping or scrolling natively in CSS |

- A counted figure needs no pre-paint hiding when built at initial state: it writes the start value before paint.
- Rebuild the marquee after its items change.

# Recipe: split entrances

The framework skill's controller calls these during intro and outro; this module never decides when. Each builder returns a timeline the controller can compose, kill, or await. Display type only.

Dependencies: `gsap`, `gsap/SplitText` (free since 3.13). `scrambleIn`/`Out` also need `gsap/ScrambleTextPlugin`.

```ts
import gsap from "gsap";
import { SplitText } from "gsap/SplitText";

gsap.registerPlugin(SplitText);

/* Swap for the project's helper if it has one. */
function prefersReducedMotion(): boolean {
  if (typeof window === "undefined") return true;
  const choice = document.documentElement.dataset.motion;
  if (choice === "reduced") return true;
  if (choice === "full") return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

const DURATION = { micro: 0.14, component: 0.2, page: 0.28 } as const;
const EASE = { entrance: "power2.out", exit: "power2.in", shift: "power2.inOut" } as const;
const STAGGER = { tight: 0.03, loose: 0.05 } as const;
const WEIGHT = { rest: 400, display: 800 } as const;

export type MotionOptions = { delay?: number; onComplete?: () => void };
export type SplitRunner = (target: HTMLElement | null, options?: MotionOptions) => gsap.core.Timeline;

function build(options: MotionOptions): gsap.core.Timeline {
  const timeline = gsap.timeline({ delay: options.delay ?? 0, defaults: { overwrite: "auto" } });
  if (options.onComplete) timeline.eventCallback("onComplete", options.onComplete);
  return timeline;
}

/**
 * Splits, runs `choreograph`, and puts the element back together afterwards.
 * The settled state is applied first so an interrupted run cannot leave text
 * stranded mid-flight. `aria: "auto"` labels the element with the original
 * string and hides the pieces, so a screen reader hears the sentence.
 */
function withSplit(
  element: HTMLElement | null,
  options: MotionOptions,
  config: SplitText.Vars,
  choreograph: (split: SplitText, tl: gsap.core.Timeline) => void,
  settled: gsap.TweenVars = { autoAlpha: 1 },
): gsap.core.Timeline {
  const tl = build(options);
  if (!element) return tl;
  if (prefersReducedMotion()) return tl.set(element, settled);

  const split = SplitText.create(element, { aria: "auto", ...config });
  tl.set(element, { autoAlpha: 1 });
  choreograph(split, tl);
  tl.eventCallback("onComplete", () => {
    const previous = options.onComplete;
    split.revert();
    previous?.();
  });
  return tl;
}

/** Pins each character to the width it needs at its heaviest, so the weight axis can move without reflow. */
function pinWidths(chars: Element[], atWeight: number): void {
  for (const char of chars) {
    const element = char as HTMLElement;
    const previous = element.style.fontWeight;
    element.style.fontWeight = String(atWeight);
    const { width } = element.getBoundingClientRect();
    element.style.fontWeight = previous;
    element.style.display = "inline-block";
    element.style.width = `${width}px`;
    element.style.textAlign = "center";
  }
}

/** Characters rise into place behind their own masks. The house entrance. */
export const charsRiseIn: SplitRunner = (element, options = {}) =>
  withSplit(element, options, { type: "chars", mask: "chars", smartWrap: true }, (split, tl) => {
    tl.from(split.chars, { yPercent: 115, duration: 0.5, ease: "power3.out", stagger: STAGGER.tight });
  });

/** Characters spring up with an elastic settle. Unmasked: the overshoot would clip. */
export const charsSpringIn: SplitRunner = (element, options = {}) =>
  withSplit(element, options, { type: "chars", smartWrap: true }, (split, tl) => {
    tl.from(split.chars, {
      yPercent: 115,
      autoAlpha: 0,
      duration: 1.1,
      ease: "elastic.out(1, 0.5)",
      stagger: STAGGER.tight,
    });
  });

/** And back down, in the same order. */
export const charsFallOut: SplitRunner = (element, options = {}) =>
  withSplit(
    element,
    options,
    { type: "chars", mask: "chars", smartWrap: true },
    (split, tl) => {
      tl.to(split.chars, { yPercent: -115, duration: DURATION.component, ease: "power2.in", stagger: STAGGER.tight }).set(
        element,
        { autoAlpha: 0 },
      );
    },
    { autoAlpha: 0 },
  );

/** Characters arrive out of order, like a dealer flicking cards. */
export const charsCascadeIn: SplitRunner = (element, options = {}) =>
  withSplit(element, options, { type: "chars", smartWrap: true }, (split, tl) => {
    tl.from(split.chars, {
      autoAlpha: 0,
      y: -18,
      rotation: () => gsap.utils.random(-14, 14),
      duration: 0.45,
      ease: "back.out(1.8)",
      stagger: { each: 0.02, from: "random" },
    });
  });

export const charsCascadeOut: SplitRunner = (element, options = {}) =>
  withSplit(
    element,
    options,
    { type: "chars", smartWrap: true },
    (split, tl) => {
      tl.to(split.chars, {
        autoAlpha: 0,
        y: 18,
        rotation: () => gsap.utils.random(-14, 14),
        duration: DURATION.component,
        ease: "power2.in",
        stagger: { each: 0.015, from: "random" },
      }).set(element, { autoAlpha: 0 });
    },
    { autoAlpha: 0 },
  );

/** Each character tips over its own top edge. */
export const charsFlipIn: SplitRunner = (element, options = {}) =>
  withSplit(element, options, { type: "chars", smartWrap: true }, (split, tl) => {
    tl.from(split.chars, {
      autoAlpha: 0,
      rotationX: -90,
      transformOrigin: "50% 0%",
      transformPerspective: 600,
      duration: 0.5,
      ease: "back.out(1.4)",
      stagger: STAGGER.tight,
    });
  });

export const charsFlipOut: SplitRunner = (element, options = {}) =>
  withSplit(
    element,
    options,
    { type: "chars", smartWrap: true },
    (split, tl) => {
      tl.to(split.chars, {
        autoAlpha: 0,
        rotationX: 90,
        transformOrigin: "50% 100%",
        transformPerspective: 600,
        duration: DURATION.component,
        ease: "power2.in",
        stagger: STAGGER.tight,
      }).set(element, { autoAlpha: 0 });
    },
    { autoAlpha: 0 },
  );

/** Characters converge from wherever they were thrown. */
export const charsScatterIn: SplitRunner = (element, options = {}) =>
  withSplit(element, options, { type: "chars", smartWrap: true }, (split, tl) => {
    tl.from(split.chars, {
      autoAlpha: 0,
      x: () => gsap.utils.random(-120, 120),
      y: () => gsap.utils.random(-60, 60),
      rotation: () => gsap.utils.random(-45, 45),
      scale: 0.6,
      duration: 0.6,
      ease: "power3.out",
      stagger: { each: 0.012, from: "center" },
    });
  });

export const charsScatterOut: SplitRunner = (element, options = {}) =>
  withSplit(
    element,
    options,
    { type: "chars", smartWrap: true },
    (split, tl) => {
      tl.to(split.chars, {
        autoAlpha: 0,
        x: () => gsap.utils.random(-120, 120),
        y: () => gsap.utils.random(-60, 60),
        rotation: () => gsap.utils.random(-45, 45),
        scale: 0.6,
        duration: DURATION.page,
        ease: "power2.in",
        stagger: { each: 0.012, from: "edges" },
      }).set(element, { autoAlpha: 0 });
    },
    { autoAlpha: 0 },
  );

/**
 * A weight wave through the line: each character dips to the far end of the
 * axis and comes back. Widths are pinned first so letters breathe in place.
 */
export const charsWeightWave: SplitRunner = (element, options = {}) => {
  const settledWeight = element ? Number(getComputedStyle(element).fontWeight) || WEIGHT.rest : WEIGHT.rest;
  const farWeight = settledWeight >= 600 ? WEIGHT.rest : WEIGHT.display;
  return withSplit(
    element,
    options,
    { type: "chars", smartWrap: true },
    (split, tl) => {
      pinWidths(split.chars, Math.max(settledWeight, farWeight));
      tl.fromTo(
        split.chars,
        { fontWeight: settledWeight },
        { fontWeight: farWeight, duration: 0.3, ease: EASE.shift, stagger: { each: 0.03, from: "start" } },
      ).to(
        split.chars,
        { fontWeight: settledWeight, duration: 0.4, ease: EASE.shift, stagger: { each: 0.03, from: "start" } },
        0.18,
      );
    },
    { autoAlpha: 1 },
  );
};

/** Words swing in from alternating sides. */
export const wordsSlideIn: SplitRunner = (element, options = {}) =>
  withSplit(element, options, { type: "words" }, (split, tl) => {
    tl.from(split.words, {
      autoAlpha: 0,
      x: (index: number) => (index % 2 === 0 ? -40 : 40),
      duration: DURATION.page,
      ease: EASE.entrance,
      stagger: STAGGER.loose,
    });
  });

export const wordsSlideOut: SplitRunner = (element, options = {}) =>
  withSplit(
    element,
    options,
    { type: "words" },
    (split, tl) => {
      tl.to(split.words, {
        autoAlpha: 0,
        x: (index: number) => (index % 2 === 0 ? 40 : -40),
        duration: DURATION.component,
        ease: EASE.exit,
        stagger: STAGGER.tight,
      }).set(element, { autoAlpha: 0 });
    },
    { autoAlpha: 0 },
  );

/** Whole lines wiped up behind masks. The most editorial of the family. */
export const linesMaskIn: SplitRunner = (element, options = {}) =>
  withSplit(element, options, { type: "lines", mask: "lines" }, (split, tl) => {
    tl.from(split.lines, { yPercent: 110, duration: DURATION.page, ease: "power3.out", stagger: STAGGER.loose });
  });

export const linesMaskOut: SplitRunner = (element, options = {}) =>
  withSplit(
    element,
    options,
    { type: "lines", mask: "lines" },
    (split, tl) => {
      tl.to(split.lines, { yPercent: -110, duration: DURATION.component, ease: "power2.in", stagger: STAGGER.tight }).set(
        element,
        { autoAlpha: 0 },
      );
    },
    { autoAlpha: 0 },
  );
```

## Scramble

Needs `ScrambleTextPlugin` registered. Display only: reading text must never look like it is being typed.

```ts
export const scrambleIn: SplitRunner = (element, options = {}) => {
  const tl = build(options);
  if (!element) return tl;
  const text = element.textContent ?? "";
  if (prefersReducedMotion()) return tl.set(element, { autoAlpha: 1 });
  return tl.set(element, { autoAlpha: 1 }).to(element, {
    duration: 0.9,
    ease: "none",
    scrambleText: { text, chars: "01{}/<>()=;", speed: 0.6, revealDelay: 0.15 },
  });
};

export const scrambleOut: SplitRunner = (element, options = {}) => {
  const tl = build(options);
  if (!element) return tl;
  if (prefersReducedMotion()) return tl.set(element, { autoAlpha: 0 });
  const text = element.textContent ?? "";
  return tl
    .to(element, { duration: 0.5, ease: "none", scrambleText: { text: text.replace(/\S/g, "0"), chars: "01{}/<>()=;", speed: 0.8 } })
    .to(element, { autoAlpha: 0, duration: DURATION.micro, ease: EASE.exit })
    .call(() => { element.textContent = text; });
};
```

## Wiring

```ts
// In the framework skill's page controller:
const intro = gsap.timeline();
intro.add(charsRiseIn(heading), 0);
intro.add(linesMaskIn(lede), 0.2);
// The outro is the paired exit, in reverse order:
const outro = gsap.timeline();
outro.add(linesMaskOut(lede), 0).add(charsFallOut(heading), 0.05);
```

Give a split heading its own pre-paint hiding rule rather than marking it as a page item too, or the page's stagger and the split's rise will fight over one element.

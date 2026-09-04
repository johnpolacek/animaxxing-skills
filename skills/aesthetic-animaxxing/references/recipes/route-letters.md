# Recipe: route intro and outro

The framework skill's controller calls `buildPageIntro` during intro and `buildPageOutro` during outro; this module never decides when, never touches the router, and never listens for clicks. It reads `data-page-transition` on the page's items, writes `data-transition-state` on the container so surface effects can follow along, and returns a timeline.

Dependencies: `gsap`, `gsap/SplitText`.

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

const ITEM_SELECTOR = "[data-page-transition]";
const LETTERS = "letters";
const SIDE_LETTERS = "letters-sides";
const HORIZONTAL_SLIDE = "slide-horizontal";
/** Seconds the page holds before the headline letters begin to implode. */
const LETTERS_DELAY = 0.75;
/** How far a headline letter starts from its place. Scales with the viewport. */
const SPREAD_X = () => window.innerWidth * 0.6;
const SPREAD_Y = () => window.innerHeight * 0.6;
const SHIFT = { component: 8, page: 16 } as const;

type LetterSplit = ReturnType<typeof SplitText.create>;
const activeSplits = new WeakMap<HTMLElement, LetterSplit>();

function pageItems(container: HTMLElement): HTMLElement[] {
  const items = Array.from(container.querySelectorAll<HTMLElement>(ITEM_SELECTOR));
  return items.length > 0 ? items : [container];
}
const ofKind = (items: HTMLElement[], kind: string) => items.filter((item) => item.dataset.pageTransition === kind);
/** Alternate letters come from opposite sides, so a line zips together. */
const sideOffset = (index: number) => (index % 2 === 0 ? -1 : 1) * SPREAD_X();

function splitLetters(item: HTMLElement): LetterSplit {
  revertLetters(item);
  const split = SplitText.create(item, { type: "chars", smartWrap: true, aria: "auto" });
  activeSplits.set(item, split);
  return split;
}

function revertLetters(item: HTMLElement): void {
  const split = activeSplits.get(item);
  if (!split) return;
  gsap.killTweensOf(split.chars);
  split.revert();
  activeSplits.delete(item);
}

export function buildPageIntro(container: HTMLElement, onComplete?: () => void): gsap.core.Timeline {
  const items = pageItems(container);
  const letters = ofKind(items, LETTERS);
  const sideLetters = ofKind(items, SIDE_LETTERS);
  const allLetters = [...letters, ...sideLetters];
  const slide = ofKind(items, HORIZONTAL_SLIDE);
  const standard = items.filter((item) => !allLetters.includes(item) && !slide.includes(item));
  const timeline = gsap.timeline({ defaults: { overwrite: "auto" } });

  const finish = () => {
    allLetters.forEach(revertLetters);
    if (allLetters.length > 0) gsap.set(allLetters, { autoAlpha: 1, clearProps: "transform,willChange" });
    container.dataset.transitionState = "idle";
    onComplete?.();
  };
  timeline.eventCallback("onComplete", finish);
  timeline.eventCallback("onInterrupt", () => allLetters.forEach(revertLetters));

  if (prefersReducedMotion()) {
    container.dataset.transitionState = "entering";
    if (slide.length > 0) gsap.set(slide, { transition: "none" });
    timeline.set(items, { autoAlpha: 1, clearProps: "transform,willChange" });
    if (slide.length > 0) timeline.set(slide, { clearProps: "transition" });
    return timeline;
  }

  // Prepare the incoming DOM while the container is still behind the CSS
  // waiting barrier. Only release the barrier after every item is hidden.
  if (standard.length > 0) gsap.set(standard, { autoAlpha: 0, y: 16 });
  if (slide.length > 0) gsap.set(slide, { autoAlpha: 0, x: -SHIFT.page, transition: "none" });
  const splits = letters.map((item) => {
    const split = splitLetters(item);
    gsap.set(item, { autoAlpha: 1, y: 0 });
    gsap.set(split.chars, {
      autoAlpha: 0,
      x: () => gsap.utils.random(-SPREAD_X(), SPREAD_X()),
      y: () => gsap.utils.random(-SPREAD_Y(), SPREAD_Y()),
      rotation: () => gsap.utils.random(-90, 90),
      scale: 0.5,
    });
    return split;
  });
  const sideSplits = sideLetters.map((item) => {
    const split = splitLetters(item);
    gsap.set(item, { autoAlpha: 1, y: 0 });
    gsap.set(split.chars, { autoAlpha: 0, x: (index: number) => sideOffset(index), y: 0 });
    return split;
  });
  container.dataset.transitionState = "entering";

  timeline.addLabel("enter", 0).set(items, { willChange: "transform, opacity" }, "enter");
  for (const split of splits) {
    timeline.to(
      split.chars,
      { autoAlpha: 1, x: 0, y: 0, rotation: 0, scale: 1, duration: 0.75, ease: "power4.out", stagger: { each: 0.02, from: "random" } },
      `enter+=${LETTERS_DELAY}`,
    );
  }
  for (const split of sideSplits) {
    timeline.to(
      split.chars,
      { autoAlpha: 1, x: 0, duration: 0.6, ease: "power4.out", stagger: { each: 0.012, from: "center" } },
      `enter+=${LETTERS_DELAY + 0.14}`,
    );
  }
  if (standard.length > 0) {
    timeline.to(
      standard,
      { autoAlpha: 1, y: 0, duration: 0.42, ease: "power3.out", stagger: 0.09 },
      letters.length > 0 ? `enter+=${LETTERS_DELAY + 0.14}` : "enter",
    );
  }
  if (slide.length > 0) {
    timeline.to(
      slide,
      { autoAlpha: 1, x: 0, duration: 0.2, ease: "power2.out" },
      letters.length > 0 ? `enter+=${LETTERS_DELAY + 0.23}` : "enter+=0.09",
    );
  }
  return timeline.set(items, { clearProps: "transform,transition,willChange" }, timeline.duration());
}

export function buildPageOutro(container: HTMLElement, onComplete: () => void): gsap.core.Timeline {
  const items = pageItems(container).reverse();
  const letters = ofKind(items, LETTERS);
  const sideLetters = ofKind(items, SIDE_LETTERS);
  const allLetters = [...letters, ...sideLetters];
  const slide = ofKind(items, HORIZONTAL_SLIDE);
  const standard = items.filter((item) => !allLetters.includes(item) && !slide.includes(item));
  allLetters.forEach(revertLetters);

  const timeline = gsap.timeline({
    defaults: { overwrite: "auto" },
    onComplete: () => {
      allLetters.forEach(revertLetters);
      if (allLetters.length > 0) gsap.set(allLetters, { autoAlpha: 0 });
      // Survives the route swap and overrides any inline styles a context
      // cleanup restores. The CSS rule for "waiting" keeps the page sealed.
      container.dataset.transitionState = "waiting";
      onComplete();
    },
  });
  timeline.eventCallback("onInterrupt", () => allLetters.forEach(revertLetters));
  container.dataset.transitionState = "exiting";
  if (slide.length > 0) gsap.set(slide, { transition: "none" });

  if (prefersReducedMotion()) return timeline.set(items, { autoAlpha: 0 });

  const splits = letters.map(splitLetters);
  const sideSplits = sideLetters.map(splitLetters);
  if (slide.length > 0) gsap.set(slide, { y: 0 });
  timeline.addLabel("exit", 0).set(items, { willChange: "transform, opacity" }, "exit");
  standard.forEach((item, index) => {
    timeline.to(item, { autoAlpha: 0, y: -8, duration: 0.22, ease: "power2.in" }, `exit+=${index * 0.055}`);
  });
  if (slide.length > 0) {
    timeline.to(slide, { autoAlpha: 0, x: SHIFT.component, duration: 0.14, ease: "power2.in" }, "exit");
  }
  for (const split of splits) {
    timeline.to(
      split.chars,
      {
        autoAlpha: 0,
        x: () => gsap.utils.random(-SPREAD_X(), SPREAD_X()),
        y: () => gsap.utils.random(-SPREAD_Y(), SPREAD_Y()),
        rotation: () => gsap.utils.random(-90, 90),
        scale: 1.6,
        duration: 0.28,
        ease: "power2.in",
        stagger: { each: 0.012, from: "edges" },
      },
      standard.length > 0 ? "exit+=0.1" : "exit",
    );
  }
  for (const split of sideSplits) {
    timeline.to(
      split.chars,
      { autoAlpha: 0, x: (index: number) => sideOffset(index), duration: 0.24, ease: "power2.in", stagger: { each: 0.008, from: "center" } },
      "exit",
    );
  }
  return timeline;
}
```

## Wiring

The framework skill's route boundary owns the container and the phases. Typical shape, in whatever lifecycle the framework skill prescribes:

```ts
// On mount of a route (initial state is the CSS pre-paint rule):
const intro = buildPageIntro(container, () => focusIfNeeded());

// When an internal link is followed and the outro must finish first:
intro.kill();
buildPageOutro(container, () => router.go(href));

// Back and forward: intro only, never an outro.
// On unmount: kill whichever timeline is live. The splits revert on interrupt.
```

The controller must also:

- Set the page container `tabIndex={-1}` and move focus to it after the intro only when a navigation left focus on `<body>`.
- Kill the intro before starting the outro. `onInterrupt` reverts the splits.
- Mark the container `data-transition-state="waiting"` immediately when a surface effect has already cleared the page (the hero's blast-off) so the swap happens without a second outro.
- Ship the pre-paint CSS in [motion-vocabulary.md](../motion-vocabulary.md#pre-paint-hiding) with the framework skill's no-script path.

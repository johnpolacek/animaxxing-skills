# Recipe: the wave

Splits a heading into letters and, every few seconds, ripples a small move across them left to right, one letter at a time, the way a crowd does the wave. Each pass uses a different move, and every letter ends exactly where it started, so the text never drifts. The canonical ambient.

The framework skill's controller calls `startWave` at settled (on `idle`) and the returned stop function on outro and unmount; this module never decides when.

Dependencies: `gsap`, `gsap/SplitText`. Rethink Sans variable for the weight moves.

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

/** Delay between neighbouring letters starting their move. */
const RIPPLE = 0.03;
/** Each letter is back at rest this many seconds after it starts. */
const LETTER_TIME = 0.25;

const rnd = gsap.utils.random;
type Move = (chars: HTMLElement[]) => gsap.core.Timeline;

/**
 * One out-and-back tween per letter, staggered along the line. The repeat
 * and yoyo live inside the stagger so each letter turns around on its own
 * schedule; at the top level they would send the wave back in reverse.
 */
function ripple(chars: HTMLElement[], vars: gsap.TweenVars, ease = "sine.inOut") {
  return gsap
    .timeline()
    .to(chars, { ...vars, duration: LETTER_TIME / 2, ease, stagger: { each: RIPPLE, yoyo: true, repeat: 1 } })
    .set(chars, { clearProps: "transform,opacity,fontWeight" });
}

/** A one-way tween per letter for moves that end where they began anyway. */
function sweep(chars: HTMLElement[], vars: gsap.TweenVars, ease = "power2.inOut") {
  return gsap
    .timeline()
    .to(chars, { ...vars, duration: LETTER_TIME, ease, stagger: RIPPLE })
    .set(chars, { clearProps: "transform,opacity,fontWeight" });
}

/** The heading sits at 800, so every weight move is a dip away from bold and back. */
const MOVES: Move[] = [
  // Hop: each letter lifts and lands.
  (chars) => ripple(chars, { y: -14 }, "power2.out"),
  // Breathe: a swell from the baseline.
  (chars) => ripple(chars, { scale: 1.07, transformOrigin: "50% 100%" }),
  // Lean: a nod to the right and back.
  (chars) => ripple(chars, { rotation: 7, transformOrigin: "50% 100%" }),
  // Flip: a full turn about the vertical axis, no perspective, so the letter folds to a line and back.
  (chars) => sweep(chars, { rotationY: 360, transformOrigin: "50% 50%" }),
  // Lighten: the weight axis eases down to medium and back.
  (chars) => ripple(chars, { fontWeight: 500 }),
  // Hairline: weight drops to the floor while the letter stretches to keep its footprint.
  (chars) => ripple(chars, { fontWeight: 400, scaleX: 1.14, transformOrigin: "50% 100%" }, "power2.inOut"),
  // Ink: weight snaps to thin, then fills back in to bold.
  (chars) =>
    gsap
      .timeline()
      .fromTo(chars, { fontWeight: 400 }, { fontWeight: 800, duration: LETTER_TIME, ease: "power2.out", stagger: RIPPLE, immediateRender: false })
      .set(chars, { clearProps: "fontWeight" }),
  // Shear: a quick italic slant.
  (chars) => ripple(chars, { skewX: 12 }, "power2.inOut"),
  // Squash: pressed flat and released.
  (chars) => ripple(chars, { scaleY: 0.82, transformOrigin: "50% 100%" }, "power2.inOut"),
  // Twist: each letter swells with its own small twist, then back.
  (chars) => ripple(chars, { scale: 1.1, rotation: () => rnd(-12, 12), transformOrigin: "50% 50%" }, "power2.inOut"),
];

/** Pins each letter to its resting width so weight changes cannot reflow the line. */
function pinWidths(chars: HTMLElement[]): void {
  const widths = chars.map((char) => char.getBoundingClientRect().width);
  chars.forEach((char, i) => {
    char.style.display = "inline-block";
    char.style.width = `${widths[i] ?? 0}px`;
    char.style.textAlign = "center";
  });
}

export type WaveOptions = {
  /** Seconds from the start of one wave to the start of the next. */
  period?: number;
};

/**
 * Starts waving the heading's letters. Returns a stop function; pass
 * `keepSplit` when another animation is about to split the same element
 * and needs the current markup left in place.
 */
export function startWave(heading: HTMLElement, { period = 4 }: WaveOptions = {}): (keepSplit?: boolean) => void {
  if (prefersReducedMotion()) return () => {};
  const split = SplitText.create(heading, { type: "chars,words" });
  const chars = split.chars as HTMLElement[];
  chars.sort((a, b) => a.getBoundingClientRect().left - b.getBoundingClientRect().left);
  pinWidths(chars);
  gsap.set(chars, { willChange: "transform, opacity" });

  // Shuffle so each cycle plays in a fresh order, never repeating one across the seam.
  let deck = gsap.utils.shuffle([...MOVES]);
  let index = 0;
  let current: gsap.core.Timeline | undefined;

  const wave = () => {
    const move = deck[index];
    index++;
    if (index >= deck.length) {
      deck = gsap.utils.shuffle([...MOVES]);
      if (deck[0] === move && deck.length > 1) deck.push(deck.shift() as Move);
      index = 0;
    }
    current?.kill();
    current = move ? move(chars) : undefined;
  };

  const clock = gsap.delayedCall(period, () => {
    wave();
    clock.restart(true);
  });

  return (keepSplit = false) => {
    clock.kill();
    current?.kill();
    if (!keepSplit) split.revert();
  };
}
```

## Wiring

```ts
let stopWave = () => {};
watchPageTransition(heading, {
  onIdle: () => { stopWave = startWave(heading, { period: 1.5 }); },   // splits reverted by then
  onExiting: () => { stopWave(); },                                     // hand the letters back before the outro splits them
});
// On a blast-off, stop with keepSplit: stopWave(true), since blastOff splits the same heading itself.
// On unmount: stopWave().
```

If the heading can scroll off screen, stop and restart it from an `IntersectionObserver` so the ticker rests.

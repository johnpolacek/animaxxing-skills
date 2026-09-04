# Motion vocabulary

Read this to pick motion. The framework skill decides when each phase runs; this file decides what it looks like.

## Tokens

Three durations, three eases, three distances. See the motion tokens in [tokens.md](tokens.md#motion-tokens). Every primitive picks one of each. Transforms, `autoAlpha`, `clip-path`, blur, and `fontWeight` only; never `width`, `height`, `top`, `left`, `color`, or `display`. Timeline defaults are `{ overwrite: "auto" }`.

Reduced motion snaps to the settled state through a `set()`, so the timeline still completes and every callback still fires.

```ts
export function prefersReducedMotion(): boolean {
  if (typeof window === "undefined") return true;
  const choice = document.documentElement.dataset.motion;
  if (choice === "reduced") return true;
  if (choice === "full") return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}
```

`data-motion` on `<html>` is an optional app-level override (`full` or `reduced`) so reduced motion can be reviewed without changing system settings. Every builder reads the helper when it builds, so an override applies to the next animation at once. If the project already has a helper, use it everywhere instead.

## The shelf: paired entrances and exits

Named in/out pairs, each built the same way. Pick from the shelf by watching them, then promote the one a screen uses under a name that says what it is for.

```ts
import gsap from "gsap";

type MotionOptions = { delay?: number; stagger?: number; onComplete?: () => void };
type MotionTarget = gsap.TweenTarget;
type Pair = (target: MotionTarget, options?: MotionOptions) => gsap.core.Timeline;

function build(options: MotionOptions): gsap.core.Timeline {
  const tl = gsap.timeline({ delay: options.delay ?? 0, defaults: { overwrite: "auto" } });
  if (options.onComplete) tl.eventCallback("onComplete", options.onComplete);
  return tl;
}

/** Builds an in/out pair from vars, with the reduced path handled once. */
function pair(from: gsap.TweenVars, to: gsap.TweenVars, settledIn: gsap.TweenVars, outVars: gsap.TweenVars): [Pair, Pair] {
  const entrance: Pair = (target, options = {}) => {
    const tl = build(options);
    if (prefersReducedMotion()) return tl.set(target, { autoAlpha: 1, ...settledIn });
    return tl.fromTo(target, from, { ...to, stagger: options.stagger ?? 0 });
  };
  const exit: Pair = (target, options = {}) => {
    const tl = build(options);
    if (prefersReducedMotion()) return tl.set(target, { autoAlpha: 0 });
    return tl.to(target, { ...outVars, stagger: options.stagger ?? 0 });
  };
  return [entrance, exit];
}

const SETTLED = { x: 0, y: 0, scale: 1, rotationX: 0, filter: "blur(0px)" };
```

| Pair | From | In | Out | When |
|---|---|---|---|---|
| `fadeIn` / `fadeOut` | `{ autoAlpha: 0 }` | `{ autoAlpha: 1, duration: 0.2, ease: "power2.out" }` | `{ autoAlpha: 0, duration: 0.14, ease: "power2.in" }` | The plainest thing there is. |
| `riseIn` / `riseOut` | `{ autoAlpha: 0, y: 8 }` | `{ autoAlpha: 1, y: 0, 0.2, power2.out }` | `{ autoAlpha: 0, y: -4, 0.14, power2.in }` | The workhorse: anything just committed. |
| `dropIn` / `dropOut` | `{ autoAlpha: 0, y: -8 }` | `{ y: 0, 0.2, power2.out }` | `{ y: 4, 0.14, power2.in }` | Things that interrupt: a status, a banner. |
| `slideInLeft` / `slideOutLeft` | `{ autoAlpha: 0, x: -16 }` | `{ x: 0, 0.2, power2.out }` | `{ x: -8, 0.14, power2.in }` | A pane from the left edge. Mirror for right. |
| `scaleIn` / `scaleOut` | `{ autoAlpha: 0, scale: 0.96 }` | `{ scale: 1, 0.2, power2.out }` | `{ scale: 0.98, 0.14, power2.in }` | Reads as focus, not zoom. |
| `popIn` / `popOut` | `{ autoAlpha: 0, scale: 0.4 }` | `{ scale: 1, 0.2, "back.out(2.4)" }` | `{ scale: 0.6, 0.14, "back.in(2)" }` | Small and infrequent. |
| `wipeUp` / `wipeDown` | `{ clipPath: "inset(0% 0% 100% 0%)" }` | `{ clipPath: "inset(0% 0% 0% 0%)", 0.28, power2.out }` | `{ clipPath: "inset(100% 0% 0% 0%)", 0.2, power2.in }` | The most editorial. Settled vars: the open inset. |
| `wipeAcross` / `wipeBack` | `{ clipPath: "inset(0% 100% 0% 0%)" }` | same, 0.28 | `{ clipPath: "inset(0% 0% 0% 100%)", 0.2 }` | Rules, bars, code lines. |
| `flipIn` / `flipOut` | `{ autoAlpha: 0, rotationX: -60, transformPerspective: 800, transformOrigin: "50% 0%" }` | `{ rotationX: 0, 0.28, power2.out }` | `{ rotationX: 25, 0.2, power2.in }` | The loudest. Almost never. |
| `focusIn` / `focusOut` | `{ autoAlpha: 0, filter: "blur(8px)" }` | `{ filter: "blur(0px)", 0.28, power2.out }` | `{ filter: "blur(6px)", 0.2, power2.in }` | Costly to paint; one element at a time. |
| `weightIn` / `weightOut` | `{ autoAlpha: 0, fontWeight: 400, y: 4 }` | `{ fontWeight: 800, y: 0, 0.28, power2.inOut }` | `{ fontWeight: 400, 0.2, power2.inOut }` | Type that gains its weight as it arrives. Settled: `{ fontWeight: 800, y: 0 }`. |

The wipes pass `autoAlpha: 1` in both from and to, so the element is visible and only the clip moves.

## Split families

Display type only: a masthead, a landing statement, a section title, a card heading. Never reading text; a paragraph must not assemble itself in front of a reader unless it is the hero subhead, which is the one exception and has its own recipe.

| Family | Split | Move | Role |
|---|---|---|---|
| `charsRiseIn` | chars, masked | `yPercent: 115 → 0`, 0.5s, `power3.out`, stagger 0.03 | The house entrance. |
| `charsSpringIn` | chars, unmasked | `yPercent: 115`, `autoAlpha`, 1.1s, `elastic.out(1, 0.5)` | The wordmark. Unmasked because the overshoot would clip. |
| `charsCascadeIn` / `Out` | chars | `y: -18`, random `rotation ±14`, `back.out(1.8)`, stagger 0.02 from random | A dealer flicking cards. |
| `charsFlipIn` / `Out` | chars | `rotationX: -90` about the top edge | Each letter tips over. |
| `charsScatterIn` / `Out` | chars | random `x ±120`, `y ±60`, `rotation ±45`, `scale 0.6`, `power3.out`, stagger from center | Letters converge from wherever they were thrown. The route version scales the spread to the viewport. |
| `charsWeightWave` | chars, widths pinned | `fontWeight` dips to the far end of the axis and back, stagger 0.03 | A wave of weight through a line. |
| `wordsSlideIn` / `Out` | words | `x ±40` alternating sides, `power2.out`, stagger 0.05 | Words zip together. |
| `linesMaskIn` / `Out` | lines, masked | `yPercent: 110 → 0`, 0.28s, `power3.out`, stagger 0.05 | Whole lines wiped up behind masks. |
| `scrambleIn` / `Out` | none | ScrambleText over `01{}/<>()=;` | Text resolving out of noise. Display only; needs ScrambleTextPlugin. |

Every family splits with `aria: "auto"` and reverts when its timeline completes, so the DOM a reader lands on is the DOM the author wrote. Under reduced motion nothing is split; the text is simply already there. Code is in [split-entrances.md](recipes/split-entrances.md).

Weight moves pin each character to its width at the heaviest weight it will reach, `display: inline-block; text-align: center`, so the axis can move without letters shoving each other along the line.

## Route grammar

Pages opt their major elements into the route transition with a `data-page-transition` attribute. On a route change the old elements leave in reverse document order, then the tree swaps, then the incoming elements enter in document order. A page with no marked elements is treated as one whole-page item.

| Value | Entrance | Exit |
|---|---|---|
| `""` (standard) | `autoAlpha 0, y 16 → 0`, 0.42s, `power3.out`, stagger 0.09. Starts at `enter+=0.89` when the page has letters, else at `enter`. | `autoAlpha 0, y -8`, 0.22s, `power2.in`, each item 0.055s after the previous. |
| `letters` | Split to chars. Each starts at random `x ±60vw`, `y ±60vh`, `rotation ±90`, `scale 0.5`, hidden. After a 0.75s hold, 0.75s `power4.out`, stagger 0.02 from random. | Chars fly back out to the same spread at `scale 1.6`, 0.28s, `power2.in`, stagger 0.012 from edges, 0.1s after the standard items start. |
| `letters-sides` | Chars alternate from `x ∓60vw`, no vertical spread. 0.6s `power4.out`, stagger 0.012 from center, starting 0.14s after the letters. | Same sides, 0.24s, stagger 0.008 from center. |
| `slide-horizontal` | `autoAlpha 0, x -16 → 0`, 0.2s, `power2.out`, 0.09s after the standard items. Its own CSS transition is suspended for the tween. | `x 8`, 0.14s, `power2.in`. |

Reduced motion: `set(items, { autoAlpha: 1 })` on enter, `set(items, { autoAlpha: 0 })` on exit. Code is in [route-letters.md](recipes/route-letters.md).

### Transition state

The page container reports its phase on `data-transition-state`:

| Value | Framework phase | Meaning |
|---|---|---|
| `entering` | intro | The intro timeline is running. Surface effects that play alongside it start here. |
| `idle` | settled | Intro complete, splits reverted, temporary styles cleared. Effects that need the letters back (the wave) start here. |
| `exiting` | outro | The outro is running. Every effect winds down. |
| `waiting` | end state | The outro finished. The page is sealed until the framework swaps it. |

A component watches the attribute with a `MutationObserver` rather than guessing at timings:

```ts
export function watchPageTransition(
  el: HTMLElement,
  handlers: { onEntering?: () => void; onIdle: () => void; onExiting?: () => void },
): () => void {
  let idle = false;
  let entering = false;
  const observer = new MutationObserver((records) => {
    for (const record of records) {
      const target = record.target as HTMLElement;
      if (!target.contains(el)) continue;
      const state = target.dataset.transitionState;
      if (state === "entering" && !entering) { entering = true; handlers.onEntering?.(); }
      else if (state === "idle" && !idle) { idle = true; handlers.onIdle(); }
      else if (state === "exiting" && idle) { idle = false; entering = false; handlers.onExiting?.(); }
    }
  });
  observer.observe(document.body, { attributes: true, subtree: true, attributeFilter: ["data-transition-state"] });
  const current = el.closest<HTMLElement>("[data-transition-state]")?.dataset.transitionState;
  if (current === "entering") { entering = true; handlers.onEntering?.(); }
  else if (current === "idle") { idle = true; handlers.onIdle(); }
  return () => observer.disconnect();
}
```

The framework skill's controller writes the attribute; it is the same state the framework skill tells you to store somewhere explicit.

### Pre-paint hiding

Marked items must not paint in their settled state before the intro sets them. Hide every hook in CSS and let GSAP reveal them:

```css
[data-page-transition],
[data-speak-intro],
[data-hero-actions],
[data-particle-card],
[data-shell-intro],
[data-logo-intro],
[data-footer-intro] {
  visibility: hidden;
}

/* Keep the page sealed while the framework swaps trees. */
[data-transition-state="waiting"] {
  visibility: hidden !important;
}
```

Add every `data-*` hook a surface effect uses to the list. `autoAlpha: 1` clears `visibility` as well as opacity, which is why every entrance uses it.

This rule alone breaks the page without JavaScript. The framework skill gives the no-script path (a `<noscript>` override, a class set by the first script, or a server flag); use it. Do not ship the rule without one.

## Ambient motion

Loops that run while a surface idles: the letter wave on a headline, embers off a button, a runner on a card outline. Rules:

- One ambient per surface. The hero headline waves; the buttons breathe; nothing else moves at rest.
- Start on `idle`, stop on `exiting`, destroy on unmount.
- Pause off screen. The particle field does this through an `IntersectionObserver`; the wave should be stopped by the same signal if the headline can scroll away.
- Every cycle ends exactly where it started. The wave clears its transforms; embers die.
- Never under reduced motion. The helper returns before anything is split or spawned.

## Surface effects

Where each recipe belongs:

| Surface | Intro | Settled | Outro |
|---|---|---|---|
| Hero headline | route `letters` | `startWave(heading, { period: 1.5 })` | `blastOff` (on a call to action) or route exit |
| Hero subhead | `speakIn(el, { emphasis, delay: 0.3 })` after the letters land | finishes persist | `blastOff` throws the words |
| Primary call to action | `reactor.enter(delay)` | embers | `blast()` when pressed, `exit()` on route exit |
| Secondary call to action | `marquee.enter(delay)` | runners | same |
| Card | `resolve.enter(index * 0.09)` on idle | one runner, glints | `exit()` |
| Onward link | `slipstream.enter()` on idle | drifting hairlines | `blast()` when pressed |
| Command block or giant field | `ignite.enter(0.75 + index * 0.25)` on entering | embers off the rule | `blast()` on copy or submit, `exit()` on route exit |
| Wordmark | `charsSpringIn` plus underline `scaleX 0 → 1` | still | never; the shell persists |
| Everything else | route standard rise | still | route exit |

Timing on the hero, for reference: letters land from 0.75s; the subhead starts speaking at 1.05s; the buttons enter at speak start plus 0.2s and 0.35s; the wave starts on `idle`. Pressing a call to action runs `blastOff`, waits 0.6s, and hands off to navigation with the page already cleared.

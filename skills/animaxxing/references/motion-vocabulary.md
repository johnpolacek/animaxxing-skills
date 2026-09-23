# Motion vocabulary

Read this to select and adapt reusable effects. The framework skill decides when each phase runs. Existing design or an explicitly selected style determines which surfaces receive them; none of the recipes requires the Animaxxing layout or palette.

## Tokens

The examples use three durations, three eases, and three distances. These are editable starting points: micro 0.14s / 4px, component 0.2s / 8px, page 0.28s / 16px; entrance `power2.out`, exit `power2.in`, shift `power2.inOut`. Reuse the consuming app's motion values where appropriate. Recipe-specific display sequences can run longer. No token file is required. Transforms, `autoAlpha`, `clip-path`, blur, and `fontWeight` only; never `width`, `height`, `top`, `left`, `color`, or `display`. Timeline defaults are `{ overwrite: "auto" }`.

Reduced motion uses a `set()` to reach the documented entrance or exit state, so the timeline still completes and every callback still fires.

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

Table entries abbreviate `duration` and `ease`; they are not copyable object literals. Every entrance merges `autoAlpha: 1` into its destination and every exit merges `autoAlpha: 0`. Wipes keep `autoAlpha: 1` at both ends and animate only the clip. Pass the matching settled vars to `pair`.

## Split families

Use character effects on display type such as headings. Keep ordinary reading text immediately readable; use speak-in only for selected short display copy. Keep the existing type scale and font family.

| Family | Split | Move | Role |
|---|---|---|---|
| `charsRiseIn` | chars, masked | `yPercent: 115 → 0`, 0.5s, `power3.out`, stagger 0.03 | Masked character reveal. Check [mask ink clearance](text-stability.md#apparent-weight-change-from-clipped-glyph-ink) for tight type. |
| `charsSpringIn` | chars, unmasked | `yPercent: 115`, `autoAlpha`, 1.1s, `elastic.out(1, 0.5)` | An elastic character entrance. Unmasked because the overshoot would clip. |
| `charsCascadeIn` / `Out` | chars | `y: -18`, random `rotation ±14`, `back.out(1.8)`, stagger 0.02 from random | A dealer flicking cards. |
| `charsFlipIn` / `Out` | chars | `rotationX: -90` about the top edge | Each letter tips over. |
| `charsScatterIn` / `Out` | chars | random `x ±120`, `y ±60`, `rotation ±45`, `scale 0.6`, `power3.out`, stagger from center | Letters converge from wherever they were thrown. The route version scales the spread to the viewport. |
| `charsWeightWave` | chars, widths pinned | `fontWeight` dips to the far end of the axis and back, stagger 0.03 | A wave of weight through a line. |
| `wordsSlideIn` / `Out` | words | `x ±40` alternating sides, `power2.out`, stagger 0.05 | Words zip together. |
| `linesMaskIn` / `Out` | lines, masked | `yPercent: 110 → 0`, 0.28s, `power3.out`, stagger 0.05 | Whole lines wiped up behind masks. |
| `scrambleIn` / `Out` | none | ScrambleText over `01{}/<>()=;` | Text resolving out of noise. Display only; needs ScrambleTextPlugin. |

Split entrances use `aria: "auto"` and revert when their timeline completes. Under reduced motion nothing is split; the text is simply already there. Code is in [split-entrances.md](recipes/split-entrances.md).

Weight moves require a variable face. The table and recipe examples use 400–800; adapt endpoints and the resting weight to the loaded axis, or choose effects without weight motion. Do not change the font to enable an effect. Weight moves pin each character to its width at the heaviest weight it will reach, `display: inline-block; text-align: center`, so the axis can move without letters shoving each other along the line.

## Route grammar

When a page transition is requested, its selected elements opt in with a `data-page-transition` attribute. These markers belong to the route recipe and do not require a particular page layout. The outro orders items in reverse document order; the intro uses document order. The framework controller determines the swap timing. A page with no marked elements is treated as one whole-page item.

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

These are optional labels for the framework controller's existing phase state. It invokes surface controls directly; recipes do not observe the document or own phase transitions.

### Pre-paint hiding

The framework controller applies its pre-paint/no-script mechanism to the recipe's targets: `data-page-transition`, `data-speak-intro`, `data-hero-actions`, `data-particle-card`, and any shell/logo/footer intro hooks used. Keep them hidden only until their initial values are ready; `autoAlpha: 1` reveals them. A hidden particle wrapper also needs an explicit reveal because revealing its child cannot reveal the wrapper.

Register recipe rollback before hiding or splitting. Restore partial DOM/style changes through [effect restoration](effect-restoration.md); removing a CSS marker alone is insufficient. The matching installed framework skill’s `references/initialization.md` owns deadlines and late-work guards.

If the controller uses `waiting` for its swap barrier, it owns that rule and its release. Do not add unconditional hiding CSS or a separate readiness mechanism here.

## Scroll grammar

Scroll effects tie motion to the reader's position instead of a page phase. Pick at most one scrubbed treatment per viewport; reading text never moves with the scroll. Code is in [scroll-effects.md](recipes/scroll-effects.md).

| Effect | Move | Role |
|---|---|---|
| `revealOnScroll` | `opacity 0, y 16 → 0`, 0.42s, `power3.out`, stagger 0.09, batched, once | The workhorse below the fold: sections, cards, figures. |
| `scrubStatement` | words `opacity 0.15 → 1`, scrubbed through the reading zone | One display statement filling in as it is read. |
| `parallax` | `y ∓ data-parallax` px, scrubbed across the section | Depth between media and captions. Small travel. |
| `pinnedScene` | caller's timeline, pinned for `length` section heights | Steps, a product reveal, a diagram assembling. The loudest; one per page. |
| `horizontalRun` | track `x → -overflow`, pinned | A gallery or timeline run sideways. Native scroller when skipped. |
| `scrollProgress` | `scaleX 0 → 1` from the left edge | A hairline reporting position. Runs under reduced motion. |
| `velocitySkew` | `skewY` up to ±8°, springs back in 0.8s | Ambient energy on media columns. Never on reading text. |

Scrubbed effects smooth with `scrub: 0.6` by default; parallax locks to the scrollbar. Reveals hide at initial state and the rest build at settled, as in the [controller contract](recipes/scroll-effects.md#controller-contract).

## Figures, marquees, and SVG

| Effect | Move | Role |
|---|---|---|
| `drawIn` / `drawOut` | DrawSVG `0% → 100%`, 0.8s, `power2.inOut`, stagger 0.12 | Lines, diagrams, and signatures drawing themselves. |
| `morphToggle` | MorphSVG to the alternate shape, 0.35s, `power2.inOut` | Menu to close, play to pause. Follows the control's state. |
| `followPath` | MotionPath along a path, 6s a lap, linear | A mark tracing a route. Ambient. |
| `countUp` | 0 to the element's own value, 1.6s, `power3.out` | Statistics landing on their figure. Width reserved. |
| `marquee` | Row loops by its own width at 60px/s | Logos, tags, or a running headline. Needs a pause control. |

Code is in [svg-effects.md](recipes/svg-effects.md) and [counters-and-marquees.md](recipes/counters-and-marquees.md).

## Covers, layout, and scroll feel

| Effect | Move | Role |
|---|---|---|
| `curtain` | Panels `yPercent 100 → 0 → -100`, 0.6s each way, `power3.inOut`, stagger 0.06 | A full-screen wipe hiding a route swap. From the persistent shell; the loudest transition there is. |
| `preloader` | Count eases to reported readiness; lifts `yPercent -100`, 0.7s, `power4.inOut` | First visit only, while real dependencies arrive. |
| `captureLayout` | Flip from old boxes to new, 0.5s, `power2.inOut`; entering items fade and grow, leaving items fade and shrink | Filters, reorders, and panels that open in place. |
| `captureShared` / `playShared` | Flip from one element's box onto its counterpart, 0.7s, `power3.inOut` | A thumbnail becoming the next page's hero. One per navigation. |
| `lenisScroll` / `smootherScroll` | Eased document scrolling | The whole site's feel. Once per document, never per page. |

A curtain and a shared-element morph never share a navigation: the curtain would hide the element the morph needs. The framework skill's `references/transition-archetypes.md` and `references/smooth-scroll.md` own their timing. Code is in [page-covers.md](recipes/page-covers.md), [layout-flip.md](recipes/layout-flip.md), and [smooth-scroll.md](recipes/smooth-scroll.md).

## Resize

Width changes can invalidate split positions and the wave's pinned character widths; height-only changes from mobile browser chrome do not. Keep text readable during a resize. Particle fields remeasure through their own observers.

The framework controller decides whether to rebuild an affected effect or replay an entrance. Supply fresh measurements when called; no recipe remounts the page or resets page state. Reduced motion stays settled.

## Input and devices

Particle treatments and pointer effects use pointer states; text and scroll effects are input-independent.

- [The field helper](recipes/particle-field.md#input-and-density) combines hover, keyboard focus, and touch presses. Controls work cold.
- Tune `COARSE_POINTER_DENSITY` for transient particles; preserve outlines and owned particles.
- [Pointer effects](recipes/pointer-effects.md): `magnetic`, `tilt`, and `cursorFollower` answer the mouse only and never gate a control. `dragTrack` works with mouse, touch, and keyboard.
- One pointer response per control: magnetic, tilt, or a particle hot state.
- The installed framework skill's `references/devices.md` owns viewport tiers, orientation handling, and CPU budgets.

## Ambient motion

Loops that run while a surface idles: the letter wave on a headline, embers off a button, a runner on a card outline. Rules:

- Avoid competing ambient effects on the same target. A style can select a wave for a headline or particles for a button, but neither is required.
- Expose controls for the framework controller to call at settled, outro, and unmount; it owns those signals.
- Pause off screen. The particle field does this through an `IntersectionObserver`; the wave's `pause()` and the follower's `pause()` answer the same signal when their surface can scroll away.
- Let the user stop any loop that runs past five seconds ([WCAG 2.2.2](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide)). The wave, particle controls, follower, and marquee expose `pause` and `play` (`resume` on the wave) for the page's pause control or motion setting.
- On small screens, lower particle density and limit wave character counts.
- Every cycle ends exactly where it started. The wave clears its transforms; embers die.
- Never under reduced motion. The helper returns before anything is split or spawned.

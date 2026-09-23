---
name: animaxxing
description: "Build GSAP text, scroll, pointer, SVG, and particle effects without restyling: split-text entrances, scattering headlines, speak-in, letter waves, scroll reveals, scrubbed statements, parallax, pinned scenes, horizontal runs, magnetic buttons, tilt cards, cursor followers, drag-and-throw tracks, SVG line drawing and icon morphs, count-up figures, marquees, particle controls, and blast-off exits. Use for Animaxxing motion or hover effects that stick on touch. Pair with the matching GSAP framework skill for lifecycle timing. Not for branding, layout redesign, routing, or isolated GSAP API questions."
license: MIT
metadata:
  short-description: Reusable GSAP text, scroll, pointer, SVG, and particle motion for any brand
---

# Animaxxing

Portable vanilla TypeScript and GSAP recipes drawn from Animaxxing. Keep the project's fonts, colors, layout, and component styling. No style skill, design tokens, or particular font family is required.

Read the matching `gsap-<framework>` skill first (including `gsap-vanilla` for plain sites). It owns **mount → initial state → intro → settled → outro → end state → unmount**, initialization, navigation, recovery, interruption, and cleanup timing. This skill supplies effect builders its controller calls. Install the matching framework skill if unavailable; do not invent framework lifecycle guidance here.

## Setup and adaptation

- Check installed GSAP docs/types. SplitText recipes require 3.13+ (`SplitText.create`, `smartWrap`, `mask`, `aria`); scroll recipes need ScrollTrigger; drag tracks need Draggable and InertiaPlugin; SVG recipes need DrawSVG, MorphSVG, or MotionPath. Register only the plugins used. Use the official GSAP skills for API details as needed.
- Select only effects the request calls for. A particle button does not imply a page transition, a font change, or a complete hero sequence.
- Recipe constants are editable defaults, not brand rules. Adapt timing, stagger, spread, and intensity to the surface. Use each recipe's documented options; expose additional constants in the copied module if the app needs runtime configuration.
- Weight effects require a loaded variable weight axis, not Rethink Sans. Match endpoints and resting weight to the existing face; the examples use 400–800. Choose transform-only effects or omit weight moves when that capability is absent.
- Particle canvases use their computed CSS `color`; inherit or assign an existing brand color with suitable contrast. Keep existing control geometry and focus styling.
- Use `style-animaxxing` only when its visual design is requested. It selects and configures these recipes for the full Animaxxing look.

## Read only what you need

| Task | Reference |
|---|---|
| Choose in/out effects, configure defaults, coordinate with the controller | [Motion vocabulary](references/motion-vocabulary.md) |
| Loading flashes, auth-dependent content, or layout shifts | Matching installed framework skill's `references/initialization.md`, **Data readiness and layout stability** |
| Character animation: font readiness, kerning, masks, stable split/revert | [Text stability](references/text-stability.md) |
| Character, word, line, or scramble entrances/exits | [Split entrances](references/recipes/split-entrances.md) |
| Page items, including scattering headlines | [Route letters](references/recipes/route-letters.md) |
| Short display copy arriving at speaking pace | [Speak-in](references/recipes/speak-in.md) |
| Ambient headline ripple | [Wave](references/recipes/wave.md) |
| Scroll reveals, scrubbed statements, parallax, pinned scenes, horizontal runs, progress, velocity skew | [Scroll effects](references/recipes/scroll-effects.md) |
| Magnetic buttons, tilt cards, cursor follower, drag-and-throw tracks | [Pointer effects](references/recipes/pointer-effects.md) |
| Line drawing, icon morphs, a mark following a path | [SVG effects](references/recipes/svg-effects.md) |
| Count-up figures, looping marquees | [Counters and marquees](references/recipes/counters-and-marquees.md) |
| Dispersal on a call to action | [Blast-off](references/recipes/blast-off.md) |
| Particle buttons, cards, links, or command fields | [Particle effects](references/recipes/particle-effects.md) plus [field/attach helpers](references/recipes/particle-field.md) |
| Touch, focus, stuck hover, mobile particle budgets | [Input and devices](references/motion-vocabulary.md#input-and-devices) |
| Roll back partial setup and restore modified content | [Effect restoration](references/effect-restoration.md) |
| Verify effects and reuse on another brand | [Verification](references/verification.md), then the framework's relevant checks |

## Recipe contract

Copy only the selected recipe and its named local helpers. Return shapes differ: timelines, `{ timeline, revert }`, stop functions, and particle controls are documented per recipe; do not assume one universal interface.

| Framework phase | Effect responsibility |
|---|---|
| initial state | Targets prepared under the framework's pre-paint/no-script mechanism |
| intro | Entrance builder or `enter(delay)` |
| settled | Clear temporary styles; optional `idle()` or wave |
| outro | Exit builder, `exit()`, or `blastOff(...)` |
| end state | Notify completion; controller decides the next action |
| unmount | Controller calls the recipe's stop, `destroy`, or `revert` handle |

- Apply the [effect restoration contract](references/effect-restoration.md) when copying a recipe, including failure before a handle returns.
- Builders do not navigate, mount, remount, or subscribe to page lifecycle changes. The framework controller calls them and owns phase state.
- An effect's invisible start does not make incomplete application data ready. The framework controller supplies resolved targets or reserved independent regions; do not use an entrance to disguise temporary guest/empty content.
- Retain required split markup only while an effect needs it (speak-in finishes and an active wave are exceptions to immediate revert). Revert on the controller's cleanup boundary; preserve accessible text and nested controls.
- Use `overwrite: "auto"`; clear temporary styles and `will-change` when their phase ends.
- Reduced motion reaches the documented settled or exit state and preserves completion callbacks. Use the project's preference helper, including any app override; no ambient motion under reduced motion.
- Killing a parent timeline never reaches a nested builder's interrupt callback. When the controller composes builders into one timeline, it kills the parent and then calls each builder's revert, such as `revertText` for split runners.
- Avoid competing effects on a target. Expose controls so the owner can pause ambient motion off screen and stop it on exit. Loops that run past five seconds also need a user-facing pause (WCAG 2.2.2).
- Particle input and density follow the [field contract](references/recipes/particle-field.md#input-and-density). Controls must work without hover.
- Width changes can invalidate split measurements; report those requirements to the framework controller. Recipes do not prescribe page remounts.

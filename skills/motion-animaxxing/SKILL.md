---
name: motion-animaxxing
description: "Build reusable GSAP text and particle effects while preserving the project's design: split-text entrances, scattering headlines, speak-in copy, letter waves, particle buttons/cards, and blast-off exits. Use for Animaxxing motion, expressive animation, or these individual effects without a restyle. Pair with the matching GSAP framework skill for lifecycle ownership. Not for choosing a brand, redesigning layout, framework routing, or isolated GSAP API questions."
license: MIT
metadata:
  short-description: Reusable GSAP text and particle motion for any brand
---

# Animaxxing Motion

Portable vanilla TypeScript and GSAP recipes drawn from Animaxxing. Keep the project's fonts, colors, layout, and component styling. No aesthetic skill, design tokens, or particular font family is required.

Read the matching `gsap-<framework>` skill first (including `gsap-vanilla` for plain sites). It owns **mount → initial state → intro → settled → outro → end state → unmount**, navigation, interruption, and cleanup timing. This skill supplies effect builders its controller calls. Install the matching framework skill if unavailable; do not invent framework lifecycle guidance here.

## Setup and adaptation

- Check installed GSAP docs/types. SplitText recipes require 3.13+ (`SplitText.create`, `smartWrap`, `mask`, `aria`); register only the plugins used. Use the official GSAP skills for API details as needed.
- Select only effects the request calls for. A particle button does not imply a page transition, a font change, or a complete hero sequence.
- Recipe constants are editable defaults, not brand rules. Adapt timing, stagger, spread, and intensity to the surface. Use each recipe's documented options; expose additional constants in the copied module if the app needs runtime configuration.
- Weight effects require a loaded variable weight axis, not Rethink Sans. Match endpoints and resting weight to the existing face; the examples use 400–800. Choose transform-only effects or omit weight moves when that capability is absent.
- Particle canvases use their computed CSS `color`; inherit or assign an existing brand color with suitable contrast. Keep existing control geometry and focus styling.
- Use `aesthetic-animaxxing` only when its visual design is requested. It selects and configures these recipes for the full Animaxxing look.

## Read only what you need

| Task | Reference |
|---|---|
| Choose in/out effects, configure defaults, coordinate with the controller | [Motion vocabulary](references/motion-vocabulary.md) |
| Character animation: font readiness, kerning, masks, stable split/revert | [Text stability](references/text-stability.md) |
| Character, word, line, or scramble entrances/exits | [Split entrances](references/recipes/split-entrances.md) |
| Page items, including scattering headlines | [Route letters](references/recipes/route-letters.md) |
| Short display copy arriving at speaking pace | [Speak-in](references/recipes/speak-in.md) |
| Ambient headline ripple | [Wave](references/recipes/wave.md) |
| Dispersal on a call to action | [Blast-off](references/recipes/blast-off.md) |
| Particle buttons, cards, links, or command fields | [Particle effects](references/recipes/particle-effects.md) plus [field/attach helpers](references/recipes/particle-field.md) |
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

- Builders do not navigate, mount, remount, or subscribe to page lifecycle changes. The framework controller calls them and owns phase state.
- Retain required split markup only while an effect needs it (speak-in finishes and an active wave are exceptions to immediate revert). Revert on the controller's cleanup boundary; preserve accessible text and nested controls.
- Use `overwrite: "auto"`; clear temporary styles and `will-change` when their phase ends.
- Reduced motion reaches the documented settled or exit state and preserves completion callbacks. Use the project's preference helper, including any app override; no ambient motion under reduced motion.
- Avoid competing effects on a target. Expose controls so the owner can pause ambient motion off screen and stop it on exit. Pointer states need keyboard parity.
- Width changes can invalidate split measurements; report those requirements to the framework controller. Recipes do not prescribe page remounts.

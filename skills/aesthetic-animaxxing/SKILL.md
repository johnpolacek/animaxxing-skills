---
name: aesthetic-animaxxing
description: "Apply the Animaxxing look: monochrome editorial design, Rethink Sans and JetBrains Mono, poster type, hairlines, and GSAP text/particle motion. Use for 'animaxx it', the Animaxxing aesthetic, or a requested Swiss-style monochrome redesign. Pair with the matching GSAP framework skill for lifecycle ownership. Not for preserving a different brand, framework routing, or isolated GSAP API questions."
license: MIT
metadata:
  short-description: The Animaxxing look, monochrome editorial type and motion
---

# Animaxxing Aesthetic

The look of [Animaxxing](https://github.com/johnpolacek/animaxxing): black, white, neutral gray, oversized sans against small uppercase mono, hairline rules, scattering letters, and particle-assembled controls.

Read the matching `gsap-<framework>` skill first (including `gsap-vanilla` for plain sites). It owns **mount → initial state → intro → settled → outro → end state → unmount**, navigation, interruption, and cleanup timing. This skill supplies the visual recipes its controller calls.

## Setup

- Apply a full restyle only when the request authorizes it; preserve an existing brand otherwise. An explicit Animaxxing redesign needs no further confirmation.
- Check installed GSAP docs/types. SplitText recipes require 3.13+ (`SplitText.create`, `smartWrap`, `mask`, `aria`); register only the plugins used.
- Load variable Rethink Sans (400–800) and JetBrains Mono (100–800) through the project's font pipeline. Weight-axis motion requires variable faces.
- Use plain CSS tokens, or their Tailwind v4 mapping if the project uses it.

## Apply and load progressively

For a full restyle, work in this order; for a focused change, load only the relevant reference.

| Task | Reference |
|---|---|
| Colors, fonts, scales, spacing, focus, light/dark themes | [Tokens](references/tokens.md) |
| Poster/Statement/Label/Annotation/BodyCopy roles; header, grid, rail, ledgers, cards | [Typography and layout](references/typography-and-layout.md) |
| Choose in/out motion, route markers, surface effects, or responsive behavior | [Motion vocabulary](references/motion-vocabulary.md) |
| Character, word, line, or scramble entrances/exits | [Split entrances](references/recipes/split-entrances.md) |
| Page items with `data-page-transition`, including scattering headlines | [Route letters](references/recipes/route-letters.md) |
| Hero subhead arriving at speaking pace | [Speak-in](references/recipes/speak-in.md) |
| Ambient headline ripple | [Wave](references/recipes/wave.md) |
| Hero dispersal on a call to action | [Blast-off](references/recipes/blast-off.md) |
| Particle buttons, cards, links, or command fields | [Particle effects](references/recipes/particle-effects.md) plus [field/attach helpers](references/recipes/particle-field.md) |
| Check the changed look and effects | [Verification](references/verification.md), then the framework's relevant checks |

## Design constraints

- Neutral token colors only; no decorative shadows or gradients. Use hairlines by default, 2px borders for controls/cards, and tight radii.
- Flush left, ragged right. Poster type may crop deliberately; reading text and annotations never crop. Annotations stay at least 11px; uppercase mono is for metadata, not body copy.
- Reading text stays still. Display text can scatter, split, or wave; the hero subhead is the speak-in exception.
- Ordinary UI motion uses the duration/ease/distance tokens; display recipes specify their own larger moves. Animate transforms, `autoAlpha`, clipping, blur, or variable weight without changing layout geometry.
- Before character animation, follow [stable typography](references/typography-and-layout.md#stable-typography-for-character-animation). Check glyph appearance and positions across revert, including mask clipping; height alone cannot prove stability.

## Recipe contract

Recipes are vanilla TypeScript plus GSAP. Copy only the selected recipe and its named local helpers. Return shapes differ: timelines, `{ timeline, revert }`, stop functions, and particle controls are documented per recipe; do not assume one universal interface.

| Framework phase | Visual responsibility |
|---|---|
| initial state | Targets prepared under the framework's pre-paint/no-script mechanism |
| intro | Entrance builder or `enter(delay)` |
| settled | Clear temporary styles; optional `idle()` or wave |
| outro | Exit builder, `exit()`, or `blastOff(...)` |
| end state | Notify completion; controller decides the next action |
| unmount | Controller calls the recipe's stop, `destroy`, or `revert` handle |

- Builders do not navigate, mount, remount, or subscribe to page lifecycle changes. The framework controller calls them and owns phase state.
- Retain required split markup only while an effect needs it (speak-in finishes and the active wave are exceptions to immediate revert). Revert on the controller's cleanup boundary; preserve accessible text and nested controls.
- Use `overwrite: "auto"`; clear temporary styles and `will-change` when their phase ends.
- Reduced motion reaches the same readable state and preserves completion callbacks. Use the project's preference helper, including any app override; no ambient motion under reduced motion.
- One ambient effect per display surface. Expose controls so the owner can pause it off screen and stop it on exit. Pointer states need keyboard parity.
- Width changes can invalidate split measurements; report those requirements to the framework controller. Recipes do not prescribe page remounts.

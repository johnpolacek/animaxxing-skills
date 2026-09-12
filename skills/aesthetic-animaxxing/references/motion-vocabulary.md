# Motion art direction

Motion is part of the Animaxxing look: big display gestures, quiet reading text, and controls that assemble from particles. This file selects and configures effects. Load `motion-animaxxing` for their implementation and the matching framework skill for **mount → initial state → intro → settled → outro → end state → unmount**.

## Intensity

- **Full treatment:** use the surface mapping below. One ambient effect per display surface; reading copy stays still, with the hero subhead as the speak-in exception.
- **Minimal motion:** keep tokens, typography, and composition. Prefer brief fades or rises and omit scattering, speak-in, waves, particles, and blast-off. Ordinary reading text remains immediately readable.
- **No animation:** render the same settled composition without splits, canvases, or GSAP. Do not add initial hiding or phase markers for effects that will not run.

The user's requested intensity takes precedence. System or app reduced motion also suppresses display and ambient effects; the motion skill and framework controller own readable endpoints and completion behavior.

## Recipe selection

Install and load `motion-animaxxing`, then read only the selected reference inside that skill. Do not assume its installation directory is adjacent to this one.

| Visual choice | Reference in `motion-animaxxing` |
|---|---|
| Ordinary fade/rise/wipe pairs and route marker values | `references/motion-vocabulary.md` |
| Masked display entrance; elastic wordmark | `references/recipes/split-entrances.md` |
| Scattering headline and coordinated page items | `references/recipes/route-letters.md` |
| Spoken hero subhead | `references/recipes/speak-in.md` |
| Ambient heading wave | `references/recipes/wave.md` |
| Hero dispersal | `references/recipes/blast-off.md` |
| Button/card/link/field treatments | `references/recipes/particle-effects.md` and `particle-field.md` in the same directory |

## Configuration for this look

Use the ordinary motion values in [tokens](tokens.md#motion-tokens). The motion recipes carry matching example defaults; when composing them, keep the selected values in the consuming app's motion module. Display recipes deliberately use longer sequences and larger spreads.

Rethink Sans display type rests at 800, so the wave's example dips through 400–500 and returns to 800. Speak-in's `broken` finish uses 400–800. These are settings for this aesthetic; the reusable recipes can use other supported font ranges. Particle canvases use `color: var(--foreground)` from the theme, with sufficient contrast against the surface.

Use the route recipe's `letters` treatment for the main display headline and standard rise for supporting page items. The framework controller applies the recipe's target markers, initial visibility, and cleanup; this aesthetic does not add a second readiness or navigation mechanism.

## Surface effects

For the full treatment, select these recipes from `motion-animaxxing`. These are art-direction choices mapped onto the framework skill's phases; its controller owns execution timing.

| Surface | Intro | Settled | Outro |
|---|---|---|---|
| Hero headline | route `letters` | `startWave(heading, { period: 1.5 })` | `blastOff` (on a call to action) or route exit |
| Hero subhead | `speakIn(el, { emphasis, delay: 0.3 })` after the letters land | finishes persist | `blastOff` throws the words |
| Primary call to action | `reactor.enter(delay)` | embers | `blast()` when pressed, `exit()` on route exit |
| Secondary call to action | `marquee.enter(delay)` | runners | same |
| Card | `resolve.enter(index * 0.09)` on idle | one runner, glints | `exit()` |
| Onward link | `slipstream.enter()` on idle | drifting hairlines | `blast()` when pressed |
| Command block or giant field | `ignite.enter(0.75 + index * 0.25)` on entering | embers off the rule | `blast()` on copy or submit, `exit()` on route exit |
| Wordmark | `charsSpringIn` plus underline `scaleX 0 → 1` | still | none when the framework keeps the shell persistent |
| Everything else | route standard rise | still | route exit |

Timing on the hero, for reference: letters land from 0.75s; the subhead starts speaking at 1.05s; the buttons enter at speak start plus 0.2s and 0.35s; the wave starts on `idle`. The blast-off visual disperses the hero; its completion handle belongs to the framework controller. Do not substitute a fixed navigation timer for completion.

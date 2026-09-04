---
name: aesthetic-animaxxing
description: "Apply the Animaxxing aesthetic: monochrome editorial design set in Rethink Sans and JetBrains Mono, poster-scale type, hairline rules, tight radii, and a GSAP motion vocabulary of split-text entrances, paragraphs that speak in word by word, letter waves, particle-assembled buttons, and a blast-off outro. Use when a user asks for the Animaxxing look, says 'animaxx it', or wants a monochrome, black-and-white, Swiss or International Typographic Style redesign with type-led motion. Provides design tokens, typography and layout grammar, and portable vanilla TypeScript plus GSAP effect recipes. Pair with the gsap-<framework> skill, which owns mount, initial state, intro, settled, outro, end state, and unmount; this skill owns how each phase looks. Not for the GSAP API itself, framework routing, or a project whose existing brand must be kept."
license: MIT
metadata:
  short-description: The Animaxxing look, monochrome editorial type and motion
---

# Animaxxing Aesthetic

One look, carried as tokens, type roles, a layout grammar, a motion vocabulary, and portable effect recipes. It is the look of [animaxxing.com](https://github.com/johnpolacek/animaxxing): black, white, and neutral gray; oversized Rethink Sans against small uppercase JetBrains Mono; hairline rules; letters that scatter in from off screen; buttons that assemble out of particles.

This skill composes with one framework skill. Install both and read the framework skill first:

- The framework skill (`gsap-nextjs`, `gsap-astro`, `gsap-sveltekit`, `gsap-nuxt`, `gsap-react-router`, `gsap-tanstack-router`, or `gsap-vanilla`) owns the lifecycle: **mount → initial state → intro → settled → outro → end state → unmount**, navigation timing, interruption, and cleanup.
- This skill owns what each phase looks like. Its recipes hand the framework skill's controller `enter()` and `exit()` builders and never decide when they run.

## Start with the project

1. Read the framework skill for this project and follow its setup. Keep the project's package manager, language, file layout, and component conventions.
2. Read the installed GSAP version. The recipes need GSAP 3.13 or later: `SplitText.create`, `smartWrap`, `mask`, and `aria` on SplitText, all in the free build. Prefer the bundled docs and types over memory.
3. Load Rethink Sans (variable, weight 400 to 800) and JetBrains Mono (100 to 800) from Google Fonts, or however the project loads fonts. The weight-axis recipes need the variable face; a static 800 cut renders the look but not the motion.
4. If the project already has a brand, confirm the user wants it replaced. This skill is a complete look, not a layer over one.
5. If Tailwind is present, use the `@theme` mapping in the tokens reference. Otherwise use the plain CSS custom properties. Both are given.

## The look

Monochrome only: `--canvas`, `--foreground`, `--muted`, `--border`, `--surface`, and an inverse band, in a light and a dark scheme. No color, no shadows, no gradients. Type does the work: fluid poster type measured in container-query units, tight negative tracking, leading under 1; supporting copy small and quiet; labels in uppercase mono, tracked out. Everything flush left and ragged right. Hairlines separate; a 2px border is the strong weight. Radii are tight. The dark scheme follows the operating system unless the user pins one with `data-theme`.

## The motion

Three durations (0.14, 0.2, 0.28 seconds), three eases (`power2.out` in, `power2.in` out, `power2.inOut` shift), tiny distances (4, 8, 16 px). Motion signals that something changed; it is not the thing being read. Display type earns bigger moves: letters scatter in from up to sixty percent of the viewport, paragraphs arrive one word at a time at speaking pace, headings ripple like a crowd wave. The variable weight axis is a motion property. Transforms, `autoAlpha`, `clip-path`, blur, and `fontWeight` only. Splits always revert. Ambient loops run on display surfaces only, pause off screen, and never run under reduced motion.

## Apply in this order

1. **Tokens.** Colors, fonts, type scale, spacing, radii, borders, focus, selection. [tokens.md](references/tokens.md).
2. **Type roles.** Poster, Statement, Label, Annotation, BodyCopy, and the crop. [typography-and-layout.md](references/typography-and-layout.md).
3. **Layout grammar.** Sticky hairline header, twelve-column grid, numbered chapters rail, ruled ledgers, chips and buttons, cards. Same reference.
4. **Route grammar.** Mark page items with `data-page-transition` (standard rise, `letters`, `letters-sides`, `slide-horizontal`), hide them before first paint, and let the framework skill's controller run the intro and outro builders. [motion-vocabulary.md](references/motion-vocabulary.md) and [route-letters.md](references/recipes/route-letters.md).
5. **Surface effects,** only where the page has a display surface for them. Hero: scatter-in headline, speak-in subhead, wave, blast-off on the call to action. Calls to action: `reactor` or `marquee`. Cards: `resolve`. An onward link: `slipstream`. A command or a giant field: `ignite`.

## Recipe contract

Every recipe is one vanilla TypeScript module with GSAP as its only dependency. It exports builders that return a `gsap.core.Timeline`, or an effect instance:

```ts
{ enter(delay: number): gsap.core.Timeline; exit(): void; blast(): void; idle(): void; hover(on: boolean): void; destroy(): void }
```

Recipes never read the router, never mount or unmount, never own cleanup timing, and never add document-level listeners. The framework skill's controller wires them:

| Framework phase | Recipe call |
|---|---|
| initial state | `gsap.set(target, { autoAlpha: 0 })`, or the pre-paint CSS rule |
| intro | `enter(delay)` / `buildPageIntro(container)` |
| settled | `idle()`; splits reverted; inline transforms cleared |
| outro | `exit()` / `buildPageOutro(container)` / `blastOff(...)` |
| end state | completion callback fires once, then the framework proceeds |
| unmount | `destroy()` / `revert()` |

Each recipe file carries a local `prefersReducedMotion()`; replace it with the project's helper if one exists so an app-level override is honored.

## Read only what you need

- Colors, fonts, scale, spacing, radii, focus: [tokens.md](references/tokens.md)
- Type roles, header, grid, rail, chips, cards, shell: [typography-and-layout.md](references/typography-and-layout.md)
- Durations, eases, the in/out shelf, split families, route grammar, pre-paint hiding, reduced motion: [motion-vocabulary.md](references/motion-vocabulary.md)
- Recipes:
  - Character, word, and line entrances: [split-entrances.md](references/recipes/split-entrances.md)
  - The page intro and outro with scattering letters: [route-letters.md](references/recipes/route-letters.md)
  - A paragraph spoken in word by word: [speak-in.md](references/recipes/speak-in.md)
  - The letter wave: [wave.md](references/recipes/wave.md)
  - The hero outro: [blast-off.md](references/recipes/blast-off.md)
  - The particle canvas and its attach helper: [particle-field.md](references/recipes/particle-field.md)
  - Button, card, and link particle treatments: [particle-effects.md](references/recipes/particle-effects.md)
- Before calling work done: [verification.md](references/verification.md)

## Rules

- Neutral grays only, consumed through the tokens. Never a raw hex value in a component, never a hue.
- No shadows, gradients, justified text, or centered blocks. Alignment edges carry the composition.
- Hairline is the default separator. Reserve the 2px border for chips, buttons, and cards.
- Uppercase mono for metadata; never for body copy. Annotation type stays above 11px and is never cropped.
- Poster type may be cropped at a deliberate boundary. Reading type is never cropped.
- Motion signals change. Reading text never assembles itself; display text may.
- Timeline defaults `overwrite: "auto"`. Every split uses `aria: "auto"` and reverts when its phase ends.
- Set `will-change` only while animating, then clear it with the other temporary styles at settled.
- Pre-paint hiding of marked items needs the framework skill's no-script path; the CSS rule alone is not enough.
- Reduced motion snaps to the settled state and still fires every completion callback.
- One ambient effect per surface, paused off screen, stopped on exit, destroyed on unmount.
- Pointer states have keyboard parity: `hover(true)` on focus, `hover(false)` on blur.

## Verification

Follow [verification.md](references/verification.md), then the framework skill's own verification.

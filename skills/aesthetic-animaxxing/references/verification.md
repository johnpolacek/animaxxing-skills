# Verification

Reference demo: [Animaxxing](https://github.com/johnpolacek/animaxxing). Until an aesthetic suite exists in animaxxing-skills-test, verify the changed surfaces there or in the consuming app, alongside the framework skill's relevant checks.

## Tokens and type

In a real browser, at settled:

- Computed text, background, and border colors remain neutral and use the theme tokens.
- Both faces loaded: `document.fonts.check('800 1em "Rethink Sans"')` and `document.fonts.check('400 1em "JetBrains Mono"')` are true.
- Display type is `font-weight: 800`. Nothing asks for 900.
- Labels and annotations are uppercase mono; body copy is not.
- Annotation type computes to at least 11px at every breakpoint.
- The dark scheme follows `prefers-color-scheme`, and `data-theme` overrides it in both directions.
- The focus ring is visible on every interactive element by keyboard, and clears any particle canvas.

## Motion

- Entrance splits are reverted at settled. Only an active wave or speak-in finishes retain required markup; both release it at their documented cleanup boundary.
- No inline `transform`, `will-change`, or `transition` remains on route items at settled.
- If the controller uses `data-transition-state`, it reports `entering → idle` for intro and `exiting → waiting` for outro. It never reports completion while the relevant timeline still runs.
- Particle canvases: one per treated element, positioned at `-bleed`, `pointer-events: none`, `aria-hidden`, colored from the tokens. The GSAP ticker drops each field once its particles are gone and no emitter is attached.
- Hover and focus produce the same state on treated elements.
- Reduced motion (`prefers-reduced-motion: reduce`, or `data-motion="reduced"` on `<html>`): every route item is visible immediately, no splits, no particles, no wave, and every completion callback still fires.
- Off screen: scroll a treated element out of view and confirm its field stops ticking.

## SplitText cleanup stability

Use [stable typography diagnosis](typography-and-layout.md#stable-typography-for-character-animation) with the actual font, tracking, text, and container width:

1. Capture the unsplit baseline after fonts load and persistent target CSS is applied. Record computed font/variation/feature settings, tracking, leading, kerning, and ligatures.
2. At the existing completion boundary, measure immediately before revert, immediately after it, and on the next frame. Capture both painted states at equal scale; temporarily holding at that boundary is acceptable, removing cleanup is not.
3. Compare non-space character positions with DOM `Range` rectangles, re-querying text nodes after revert. Check heading height, line membership, and glyph edges/dots/descenders. Wrapper rectangles alone cannot distinguish mask padding from glyph movement.
4. Repeat at desktop/mobile widths and near a line-break threshold, with reduced motion and interruption. Separate intended weight/tilt changes from cleanup-induced movement. Confirm accessible text and nested controls survive.
5. If masks were expanded, inspect both hidden reveal endpoints and the exit endpoint for ink leakage. Keep timing fixed; adjust travel only when leakage is observed.

Record viewport, browser, font readiness, maximum position deltas, height, wrapping, and visual observations. A repeatable multi-pixel snap fails even with stable height; tiny subpixel rounding without visible movement is not a universal failure. Do not round measurements to whole pixels.

## Layout

- Nothing is centered or justified. Alignment edges line up down the page.
- Poster type is cropped, not shrunk, where it overflows its column; reading type is never clipped.
- The twelve-column grid, the rail, and the ledgers hold at the narrow breakpoint: the rail becomes chips, rows fold their figures under the title.
- Layout boxes do not move during any phase. Only transforms move pixels.

## Report

Say which checks ran in a browser and which were static review. Do not claim the look was verified from code alone.

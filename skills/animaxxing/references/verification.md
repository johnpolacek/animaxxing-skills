# Verification

Reference demo: [Animaxxing](https://github.com/johnpolacek/animaxxing). It exercises these recipes with `style-animaxxing`; it is not a required design. Until a motion suite exists in animaxxing-skills-test, verify changed recipes there or in the consuming app, alongside the framework skill's relevant checks.

## Portability

- An effect-only request preserves the app's fonts, palette, layout, and component styling. No style-specific tokens or fonts are needed to copy a recipe and its named helpers.
- Particle color follows the canvas's computed `color`, including theme changes; its contrast works on the actual background.
- Weight effects use a loaded variable face and its supported axis range. Confirm the configured resting weight matches the target. For a static face, choose a transform-only effect or omit weight moves.
- Selected timing, spread, intensity, and stagger suit the actual surface and viewport. Layout boxes remain stable through the effect.

## Motion

- Entrance splits are reverted at settled. Only an active wave or speak-in finishes retain required markup; both release it at their documented cleanup boundary.
- No inline `transform`, `will-change`, or `transition` remains on route items at settled.
- If the controller uses `data-transition-state`, it reports `entering → idle` for intro and `exiting → waiting` for outro. It never reports completion while the relevant timeline still runs.
- Particle canvases: one per treated element, positioned at `-bleed`, `pointer-events: none`, `aria-hidden`, colored from the consuming app's chosen canvas `color`. The GSAP ticker drops each field once its particles are gone and no emitter is attached.
- Hover and focus produce the same state on treated elements.
- Reduced motion (`prefers-reduced-motion: reduce`, or `data-motion="reduced"` on `<html>`): entrances reach the readable settled state immediately, exits reach their documented end state, no splits, no particles, no wave, and every completion callback still fires.
- Off screen: scroll a treated element out of view and confirm its field stops ticking.

## Effect failure and restoration

- Throw before writes, after initial styles, and after a split or particle resource is created. Confirm partial setup rolls back even without a returned handle.
- Stop owned timelines, delayed calls, tickers, observers, and listeners before restoration. Invoke teardown twice; it remains safe and cannot recreate motion.
- Compare original nodes, text, links, ARIA, and application-owned inline styles after rollback. Check hidden ancestors and masks, not just opacity.
- Resolve deferred font/media work after the framework recovers; no new split, hidden frame, or decorative completion may run.
- Use the matching installed framework skill's `references/initialization.md` failure matrix for disabled JavaScript, blocked bundles, deadlines, navigation, and completion ownership. These checks also apply with another brand's fonts and CSS.

## SplitText cleanup stability

Use [stable typography diagnosis](text-stability.md#stable-typography-for-character-animation) with the actual font, tracking, text, and container width:

1. Capture the unsplit baseline after fonts load and persistent target CSS is applied. Record computed font/variation/feature settings, tracking, leading, kerning, and ligatures.
2. At the existing completion boundary, measure immediately before revert, immediately after it, and on the next frame. Capture both painted states at equal scale; temporarily holding at that boundary is acceptable, removing cleanup is not.
3. Compare non-space character positions with DOM `Range` rectangles, re-querying text nodes after revert. Check heading height, line membership, and glyph edges/dots/descenders. Wrapper rectangles alone cannot distinguish mask padding from glyph movement.
4. Repeat at desktop/mobile widths and near a line-break threshold, with reduced motion and interruption. Separate intended weight/tilt changes from cleanup-induced movement. Confirm accessible text and nested controls survive.
5. If masks were expanded, inspect both hidden reveal endpoints and the exit endpoint for ink leakage. Keep timing fixed; adjust travel only when leakage is observed.

Record viewport, browser, font readiness, maximum position deltas, height, wrapping, and visual observations. A repeatable multi-pixel snap fails even with stable height; tiny subpixel rounding without visible movement is not a universal failure. Do not round measurements to whole pixels.

## Report

Say which checks ran in a browser and which were static review. Do not claim animation behavior was verified from code alone.

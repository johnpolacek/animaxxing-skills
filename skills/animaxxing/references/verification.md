# Verification

Automated suite: `motion/` in [animaxxing-skills-test](https://github.com/johnpolacek/animaxxing-skills-test) type-checks the scroll, pointer, SVG, and counter and marquee recipes straight from this skill and runs their checks in Chromium (`pnpm test:motion`). Run it after changing those recipes.

Reference demo: [Animaxxing](https://github.com/johnpolacek/animaxxing). It exercises the text and particle recipes with `style-animaxxing`; it is not a required design. Verify changes to those recipes there or in the consuming app, alongside the framework skill's relevant checks.

## Portability

- An effect-only request preserves the app's fonts, palette, layout, and component styling. No style-specific tokens or fonts are needed to copy a recipe and its named helpers.
- Particle color follows the canvas's computed `color`, including theme changes; its contrast works on the actual background.
- Weight effects use a loaded variable face and its supported axis range. Confirm the configured resting weight matches the target. For a static face, choose a transform-only effect or omit weight moves.
- Selected timing, spread, intensity, and stagger suit the actual surface and viewport. Layout boxes remain stable through the effect.
- In a data-driven app, exercise the framework's data-readiness checks: temporary guest/empty content must not flash before the selected effect starts. Confirm reserved regions keep visible siblings still.

## Motion

- Entrance splits are reverted at settled. Only an active wave or speak-in finishes retain required markup; both release it at their documented cleanup boundary.
- No inline `transform`, `will-change`, or `transition` remains on route items at settled.
- If the controller uses `data-transition-state`, it reports `entering → idle` for intro and `exiting → waiting` for outro. It never reports completion while the relevant timeline still runs.
- Particle canvases: one per treated element, positioned at `-bleed`, `pointer-events: none`, `aria-hidden`, colored from the consuming app's chosen canvas `color`. The GSAP ticker drops each field once its particles are gone and no emitter is attached.
- Mouse hover and keyboard focus share a hot state; leaving one input preserves the other.
- Touch buttons and text fields: flare while pressed, cool on release or swipe cancellation. Tap-derived focus stays cold.
- Keyboard input after touch restores focus treatment. Repeated keys must not repeat bursts.
- Coarse input thins transient particles while preserving outlines and owned particles. Runner counts stay unchanged.
- At phone width with 4x CPU throttling, lower budgets if idle frame pacing fails.
- Reduced motion (`prefers-reduced-motion: reduce`, or `data-motion="reduced"` on `<html>`): entrances reach the readable settled state immediately, exits reach their documented end state, no splits, no particles, no wave, and every completion callback still fires.
- Off screen: scroll a treated element out of view and confirm its field stops ticking.

## Scroll

- Reload mid-page and restore via back: reveal targets above the fold are visible, never stuck hidden.
- Scroll down and back through every scrubbed effect; each returns exactly to its start values.
- Pinned scenes and runs: no jump entering or leaving the pin; content below lands in place.
- Resize across a breakpoint and refresh: pin lengths and run distance recompute; nothing overlaps.
- Tab through a horizontal run: each focused item scrolls into view; the section never scrolls itself.
- Tear down mid-pin: pin spacer removed, inline styles and `overflow` restored, page scroll stays usable.
- Reduced motion: no pins, splits, or scrubbing; static fallbacks readable; progress rule still tracks.
- With a custom scroller, every trigger receives it and cleanup leaves the app's proxy intact.

## Pointer

- Magnetic, tilt, and follower respond to the mouse and ignore touch and pen; nothing sticks after a tap.
- Leaving the target returns it exactly to rest; teardown leaves no inline transform or `--pointer-*`.
- The follower appears at the pointer, never sliding in from the corner, and hides when the mouse leaves the window.
- Drag a track of links: it moves and snaps, the drag does not follow the link, and a plain click does.
- On touch, horizontal drags move the track and vertical swipes still scroll the page.
- Keyboard focus slides the focused item into view; a mouse press on an item does not.
- Revert during a throw: the track stops and its inline styles and the viewport's `overflow` restore.
- Reduced motion: no magnetic, tilt, or follower; the track drags and snaps without a throw.

## SVG, counters, and marquees

- Drawn strokes start hidden without a flash and end at the SVG's own appearance after revert.
- A morphed icon returns to its original `d` on revert; `set()` after revert does nothing.
- Counted figures keep their prefix, suffix, separators, and decimals, and end on the exact source text.
- Neighbors of a counted figure do not shift while it counts; assistive technology reads the final value.
- Marquee clones are `aria-hidden` and `inert` with no duplicate ids; each item is announced and focused once.
- The marquee loops without a visible seam, slows on hover, pauses on focus, off screen, and on `pause()`.
- Resizing rebuilds the clones to fill; revert restores the original markup exactly.
- Reduced motion: strokes whole, figures final, no follower, marquee static; completion callbacks still fire.

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

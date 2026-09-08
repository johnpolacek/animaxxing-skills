# Verification

The framework skill's verification still applies: initial state before reveal, one settled state, outro before unmount, reduced motion, cleanup. Run it. Then check the look.

## Tokens and type

In a real browser, at settled:

- Every computed `color`, `background-color`, and `border-color` on the page is neutral: red, green, and blue channels equal. One query catches strays:

  ```js
  [...document.querySelectorAll("*")].flatMap((el) => {
    const s = getComputedStyle(el);
    return [s.color, s.backgroundColor, s.borderTopColor].filter((c) => {
      const m = c.match(/\d+/g);
      return m && !(m[0] === m[1] && m[1] === m[2]);
    }).map((c) => [el, c]);
  });
  ```

- Both faces loaded: `document.fonts.check('800 1em "Rethink Sans"')` and `document.fonts.check('400 1em "JetBrains Mono"')` are true.
- Display type is `font-weight: 800`. Nothing asks for 900.
- Labels and annotations are uppercase mono; body copy is not.
- Annotation type computes to at least 11px at every breakpoint.
- The dark scheme follows `prefers-color-scheme`, and `data-theme` overrides it in both directions.
- The focus ring is visible on every interactive element by keyboard, and clears any particle canvas.

## Motion

- No split wrapper spans remain in the DOM at settled. `document.querySelectorAll('[data-page-transition] div[style*="display: inline-block"]')` is empty once the intro is done, and the wave is the only split alive on the page.
- No inline `transform`, `will-change`, or `transition` remains on route items at settled.
- `data-transition-state` moves `entering → idle` on load and `idle → exiting → waiting` on navigation, and never skips to `idle` with the intro still running.
- Particle canvases: one per treated element, positioned at `-bleed`, `pointer-events: none`, `aria-hidden`, colored from the tokens. The GSAP ticker drops each field once its particles are gone and no emitter is attached.
- Hover and focus produce the same state on treated elements.
- Reduced motion (`prefers-reduced-motion: reduce`, or `data-motion="reduced"` on `<html>`): every route item is visible immediately, no splits, no particles, no wave, and every completion callback still fires.
- Off screen: scroll a treated element out of view and confirm its field stops ticking.

## SplitText cleanup stability

Use the [shared typography diagnosis](typography-and-layout.md#stable-typography-for-character-animation). In a browser, test the actual font, weight, tracking, text, and container width:

1. Record the unsplit baseline with the required fonts loaded and persistent target CSS applied. Record computed font family, weight, size, style, variation/feature settings, tracking, line-height, `font-kerning`, `text-rendering`, and ligatures on split characters and restored text. Confirm the intended rendered font is ready; unchanged weight alone does not establish unchanged appearance.
2. Instrument the existing completion boundary: sample immediately before `split.revert()` after entrance transforms have reached their final values, immediately after it in the same callback, and on the next animation frame. Capture frames of the final split state immediately before cleanup and the restored state immediately after it. For a controlled capture, hold just before the existing cleanup callback, capture, then execute cleanup and capture again without advancing other motion. A video may miss the exact boundary; DOM measurements in one callback do not capture painted glyphs. Do not remove cleanup to obtain a passing result.
3. Compare corresponding non-space character positions, heading height, and which characters belong to each line. Use DOM `Range` rectangles over the text nodes for matching character offsets in both split and restored markup; re-query text nodes after revert because old nodes are detached. Compare positions relative to the heading as well as its viewport position. Wrapper rectangles alone can include mask padding; heading width alone can stay fixed while glyphs move inside it. Compare equally scaled frame crops for clipped letter edges, dots, punctuation, and descenders; stable bounding boxes do not prove stable glyph appearance.
4. Repeat at desktop and narrow mobile widths, including near a line-break threshold. Under reduced motion, confirm the same settled typography and readable text with no unnecessary splits. Interrupt/restart the intro and navigate away where applicable; ensure the controller clears stale splits and preserves accessibility. For intentional outro movement or weight/tilt finishes, distinguish the designed end-state change from the spacing change caused by restoring markup; inspect the restored settled state on cancellation.
5. With any expanded masks, capture the initial hidden state of both forward and backward reveals (including positive and negative travel), and the hidden exit endpoint before revert. No ink should peek through. Check at desktop and mobile sizes; verify mask padding does not change spacing, line wrapping, or heading height. Keep timing fixed; adjust hidden travel only if leakage is observed.
6. Confirm a screen reader gets the complete heading while split and after restoration (`aria: "auto"` for plain headings); preserve accessible links/semantics for nested interactive content. Verify wrappers are removed at the controller's intended cleanup boundary.

Record maximum horizontal/vertical deltas, height, line membership, viewport, browser, and font readiness alongside visual observation. A repeatable multi-pixel snap fails even with unchanged height. Roughly 0.1 CSS px of rounding with stable wrapping and no visible movement can be negligible; it is not a universal tolerance for every zoom, device, or font. Do not round measurements to whole pixels or demand exact zero.

Regression evidence: AI Film Camp commit `ca79bb8` kept the `charsRiseIn`-style `type: "chars"`, `mask: "chars"`, `smartWrap: true` animation and completion-time revert in `apps/web/components/learn/lesson-stepper.tsx`, adding scoped typography CSS in `lesson-stepper.module.css`. The reported browser measurements for “Small idea. Big feeling.” went from about 2.7px horizontal movement with no height change to about 0.1px after the CSS fix. The separate commit `41bf113` added a scoped class to `split.masks` with `padding: 0.15em; margin: -0.15em` in the same files. The reported computed weight stayed 500 and the font was loaded; individual masks clipped ink under tight tracking/leading, and their removal made the glyphs appear heavier. The user confirmed the mask fix resolved the appearance. Treat both as case evidence, not measurements of every recipe or font.

## Layout

- Nothing is centered or justified. Alignment edges line up down the page.
- Poster type is cropped, not shrunk, where it overflows its column; reading type is never clipped.
- The twelve-column grid, the rail, and the ledgers hold at the narrow breakpoint: the rail becomes chips, rows fold their figures under the title.
- Layout boxes do not move during any phase. Only transforms move pixels.

## Report

Say which checks ran in a browser and which were static review. Do not claim the look was verified from code alone.

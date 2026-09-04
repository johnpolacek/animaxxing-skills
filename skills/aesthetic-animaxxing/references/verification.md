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

## Layout

- Nothing is centered or justified. Alignment edges line up down the page.
- Poster type is cropped, not shrunk, where it overflows its column; reading type is never clipped.
- The twelve-column grid, the rail, and the ledgers hold at the narrow breakpoint: the rail becomes chips, rows fold their figures under the title.
- Layout boxes do not move during any phase. Only transforms move pixels.

## Report

Say which checks ran in a browser and which were static review. Do not claim the look was verified from code alone.

# Verification

Reference demo: [Animaxxing](https://github.com/johnpolacek/animaxxing). Until a style suite exists in animaxxing-skills-test, verify the changed design there or in the consuming app. For selected animation, also run `animaxxing`'s `references/verification.md` and the framework skill's relevant checks; those own effect behavior, SplitText cleanup stability, and lifecycle verification.

## Tokens and type

In a real browser, at settled:

- Computed text, background, and border colors remain neutral and use the theme tokens.
- Both faces loaded: `document.fonts.check('800 1em "Rethink Sans"')` and `document.fonts.check('400 1em "JetBrains Mono"')` are true.
- Display type is `font-weight: 800`. Nothing asks for 900.
- Labels and annotations are uppercase mono; body copy is not.
- Annotation type computes to at least 11px at every breakpoint.
- The dark scheme follows `prefers-color-scheme`, and `data-theme` overrides it in both directions.
- The focus ring is visible on every interactive element by keyboard, and clears any particle canvas.

## Layout

- Nothing is centered or justified. Alignment edges line up down the page.
- Poster type is cropped, not shrunk, where it overflows its column; reading type is never clipped.
- The twelve-column grid, the rail, and the ledgers hold at the narrow breakpoint: the rail becomes chips, rows fold their figures under the title.
- Without Tailwind, load [plain CSS](plain-css.md) and the token declarations alone. Check chips, actions, cards, ledgers, the rail, and form focus below `sm`, between `sm` and `lg`, and above `lg`. Their typography, spacing, colors, and responsive layout match the Tailwind treatment without GSAP.
- Layout boxes do not move during any phase. Only transforms move pixels.

## Readability

- Static styling remains readable without GSAP or a motion skill, including headings, cards, navigation, and footer.
- Selected animation delegates the failure matrix to the installed framework skill's `references/initialization.md`. Recovered content keeps the design, links, and intentional hidden states.

## Motion art direction

- The selected intensity matches the request. A static or minimal-motion restyle does not automatically acquire scattering, speak-in, waves, or particles.
- For the full treatment, the chosen effects match [the surface mapping](motion-vocabulary.md#surface-effects). Reading text stays still apart from the selected hero subhead; effects do not compete on a display surface.
- Particle colors follow the chosen theme and maintain contrast. Reduced motion preserves the same readable design.
- Touch treatments release after taps; pointer-derived focus does not sustain them.
- If the `animaxxing` curve is used, it is registered once before any builder, appears only on the large moves listed in [the signature curve](motion-vocabulary.md#signature-curve), and micro and component motion keep the token eases.
- For character animation, use the motion skill's text stability checks; visual design is not verified by heading height alone.

## Report

Say which checks ran in a browser and which were static review. Do not claim the look was verified from code alone.

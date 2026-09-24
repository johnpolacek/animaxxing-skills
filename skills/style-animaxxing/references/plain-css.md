# Plain-CSS typography and layout

Use this instead of the Tailwind class strings in [typography and layout](typography-and-layout.md). Load the plain-CSS declarations from [tokens](tokens.md) first, including the fonts and spacing variables. These examples require neither Tailwind nor GSAP. Rename selectors to fit the app; compose the base and modifier classes together, such as `chip chip-solid` or `display card-heading`.

The responsive equivalents use Tailwind's default `sm` (40rem), `md` (48rem), and `lg` (64rem). If the app changes those breakpoints, change both forms together. The small reset below replaces the base styles the examples normally receive from Tailwind Preflight; scope it to a wrapper with `class="animaxxing-style"`.

```css
.animaxxing-style { line-height: 1.5; }
body.animaxxing-style { margin: 0; }
.animaxxing-style, .animaxxing-style *,
.animaxxing-style *::before, .animaxxing-style *::after { box-sizing: border-box; }
.animaxxing-style :where(h1, h2, h3, h4, p, figure) { margin: 0; }
.animaxxing-style :where(button, input, textarea) { font: inherit; color: inherit; }
.animaxxing-style button { border: 0 solid currentColor; background: transparent; }
.animaxxing-style a { color: inherit; text-decoration: none; }
.animaxxing-style img { display: block; max-width: 100%; height: auto; }

/* Type roles; a poster's column establishes its cqi measurement. */
.poster-column { container-type: inline-size; }
.poster, .statement, .body-copy, .display, .card-heading { font-family: var(--font-sans); }
.poster {
  font-size: clamp(3.25rem, 18cqi, 15rem); font-weight: 800;
  line-height: 0.84; letter-spacing: -0.045em; text-wrap: balance;
}
.poster-align-ink { margin-inline-start: -0.055em; }
.statement {
  max-width: 18ch; font-size: clamp(2.75rem, 7cqi, 4.5rem); font-weight: 800;
  line-height: 0.95; letter-spacing: -0.03em; text-wrap: balance;
}
.label, .annotation, .mono-label, .mono-note, .figure { font-family: var(--font-mono); text-transform: uppercase; }
.label, .annotation { color: var(--muted); }
.label, .mono-label { font-size: 0.75rem; line-height: 1rem; letter-spacing: 0.02em; }
.annotation, .mono-note, .figure { font-size: 0.6875rem; line-height: 1rem; letter-spacing: 0.08em; }
.annotation { max-width: 46ch; }
.mono-label { font-weight: 700; letter-spacing: 0.08em; }
.figure { font-variant-numeric: tabular-nums; }
.body-copy { max-width: 68ch; font-size: 1rem; line-height: 1.5rem; text-wrap: pretty; }
.body-copy-narrow { max-width: 42ch; }
.support { color: var(--muted); }
.support-inverse { color: color-mix(in srgb, var(--inverse-foreground) 75%, transparent); }
.display { font-weight: 800; line-height: 0.84; letter-spacing: -0.045em; }
.card-heading { font-size: 2.25rem; font-weight: 800; text-transform: uppercase; letter-spacing: -0.03em; }
.crop { overflow: hidden; }
.crop-start { display: flex; justify-content: flex-end; }

/* CHIP, SMALL_CHIP, BUTTON_SOLID, and BUTTON_OUTLINE. */
.animaxxing-style .chip, .animaxxing-style .small-chip {
  display: inline-flex; align-items: center; height: 3rem; gap: 0.625rem;
  border: 2px solid currentColor; border-radius: var(--radius-xl); padding-inline: 1.25rem;
  font-family: var(--font-sans); font-size: 13px; font-weight: 800;
  text-transform: uppercase; letter-spacing: 0.04em;
}
.animaxxing-style .small-chip {
  height: 2.5rem; gap: 0; border-radius: var(--radius-lg); padding-inline: 1rem;
  font-size: 0.75rem; line-height: 1rem; border-color: var(--foreground); color: var(--foreground);
}
.animaxxing-style .chip-solid { border-color: var(--inverse); background: var(--inverse); color: var(--inverse-foreground); }
.animaxxing-style .chip-outline { border-color: var(--foreground); color: var(--foreground); }
.animaxxing-style .chip-quiet { border-color: var(--border); color: var(--muted); }
.animaxxing-style .button-solid, .animaxxing-style .button-outline {
  display: inline-flex; align-items: center; cursor: pointer; border-radius: var(--radius-lg);
  padding: 0.75rem 1.5rem; font-family: var(--font-sans); font-size: 2.25rem;
  line-height: 2.5rem; font-weight: 800; text-transform: uppercase; letter-spacing: -0.02em;
}
.animaxxing-style .button-solid { background: var(--inverse); color: var(--inverse-foreground); }
.animaxxing-style .button-outline { border: 2px solid var(--foreground); background: transparent; color: var(--foreground); }
.chip, .small-chip, .button-solid, .button-outline, .rail-link, .card {
  transition-property: color, background-color, border-color, outline-color, text-decoration-color, fill, stroke;
  transition-duration: 150ms; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
.animaxxing-style :focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
.animaxxing-style :is(.button-solid, .button-outline, .card):focus-visible { outline-offset: 4px; }
@media (hover: hover) {
  .animaxxing-style :is(.chip-solid, .button-solid):hover { background: var(--inverse-hover); }
  .animaxxing-style :is(.chip-outline, .small-chip, .button-outline):hover { background: var(--surface-hover); }
  .animaxxing-style .chip-quiet:hover { border-color: var(--foreground); color: var(--foreground); }
}

/* Shell and page sections. Put .shell-row or .section-inner inside its outer element. */
.shell-header { padding: var(--spacing-gutter-lg) var(--spacing-gutter) 0; }
.shell-row { display: flex; align-items: center; justify-content: space-between; gap: 1rem; min-height: 2.25rem; width: 100%; max-width: 80rem; margin-inline: auto; }
.animaxxing-style .wordmark {
  position: relative; display: inline-block; font-family: var(--font-mono);
  font-size: 1rem; line-height: 1.5rem; text-transform: lowercase; letter-spacing: 0.08em; color: var(--muted);
}
.shell-footer { margin-top: auto; border-top: 1px solid var(--border); padding: 2.5rem var(--spacing-gutter); }
.page-main { display: flex; flex: 1; flex-direction: column; }
.page-section { padding: 2.5rem var(--spacing-gutter) 4rem; }
.section-inner { width: 100%; max-width: 80rem; margin-inline: auto; }
.sticky-strip { position: sticky; top: 0; z-index: 30; margin-inline: calc(-1 * var(--spacing-gutter)); border-bottom: 1px solid var(--border); background: var(--canvas); padding-inline: var(--spacing-gutter); }
.strip-row { display: flex; min-height: 3.5rem; align-items: center; column-gap: 2rem; padding-block: 0.5rem; }
.strip-nav { display: none; }
.strip-meta { margin-left: auto; }
.strip-action { margin-left: auto; }
.animaxxing-style .strip-nav a { color: var(--muted); }
@media (hover: hover) { .animaxxing-style .strip-nav a:hover { color: var(--foreground); } }

/* Twelve-column grid and chapters. */
.chapter-grid { display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); gap: 2rem 1.5rem; margin-top: 2rem; }
.chapters-rail, .chapter-body { grid-column: span 12 / span 12; min-width: 0; }
.chapters-rail { display: flex; overflow-x: auto; }
.animaxxing-style .rail-link { display: inline-flex; flex-shrink: 0; align-items: center; gap: 0.5rem; border-radius: var(--radius-lg); padding: 0.5rem 0.625rem; color: var(--muted); }
.animaxxing-style .rail-link[aria-current="page"] { color: var(--foreground); }
.poster-span { grid-column: span 8 / span 8; }
.photo-span { grid-column: span 4 / span 4; }

/* ROW: title occupies the flexible track; figures fold beneath it on narrow screens. */
.ledger-row { display: grid; grid-template-columns: 3rem minmax(0, 1fr); align-items: start; column-gap: 1.5rem; border-bottom: 1px solid var(--border); padding-block: 0.75rem; }
.ledger-figures { grid-column: 2; display: flex; flex-wrap: wrap; gap: 0.5rem; }
.ledger-figures > * { text-align: right; }

/* Cards: the whole .card is one anchor, without nested controls. */
.card-grid { display: grid; gap: 1.5rem; }
.animaxxing-style .card { display: block; height: 100%; cursor: pointer; border: 2px solid var(--border); border-radius: var(--radius-lg); background: var(--surface); padding: 1.5rem; }
.card-label { display: flex; justify-content: space-between; }
.card .card-heading { margin-top: 2rem; }
.card .body-copy { margin-top: 1rem; max-width: 36ch; color: var(--muted); }
.card .annotation { margin-top: 2rem; color: var(--foreground); }
@media (hover: hover) { .animaxxing-style .card:hover { border-color: var(--foreground); background: var(--surface-hover); } }

/* Forms keep a visible keyboard ring even without the particle treatment. */
.animaxxing-style .text-field { display: block; width: 100%; border: 0; border-bottom: 3px solid var(--foreground); background: transparent; padding-block: 0.75rem; font-family: var(--font-sans); font-weight: 800; color: var(--foreground); }
.text-field::placeholder { color: var(--border); opacity: 1; }
.animaxxing-style .text-field:focus-visible { outline: 2px solid var(--focus); outline-offset: 4px; }
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border-width: 0; }

@media (min-width: 40rem) {
  .card-heading { font-size: 3rem; }
  .animaxxing-style :is(.button-solid, .button-outline) { padding: 1rem 2rem; font-size: 3rem; line-height: 1; }
  .shell-header, .shell-footer, .page-section { padding-inline: var(--spacing-gutter-lg); }
  .animaxxing-style .wordmark { font-size: 1.125rem; line-height: 1.75rem; }
  .sticky-strip { margin-inline: calc(-1 * var(--spacing-gutter-lg)); padding-inline: var(--spacing-gutter-lg); }
  .card-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .animaxxing-style .card { padding: 2rem; }
}
@media (min-width: 48rem) {
  .strip-nav { display: flex; gap: 1rem; }
  .strip-action { margin-left: 0; }
}
@media (min-width: 64rem) {
  .chapters-rail { grid-column: span 1 / span 1; position: sticky; top: 5rem; height: calc(100vh - 6rem); transform: rotate(180deg); border-left: 1px solid var(--border); padding-left: 0.75rem; writing-mode: vertical-rl; }
  .chapter-body { grid-column: span 11 / span 11; }
  .animaxxing-style .rail-link { padding-block: 0.625rem; }
  .ledger-row { min-height: 2.5rem; grid-template-columns: 4rem minmax(0, 1fr) 14.5rem 5.5rem 5.5rem 4.5rem; align-items: center; padding-block: 0.625rem; }
  .ledger-figures { display: contents; }
  .card-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
```

Use `mono-label` together with `rail-link`, and `figure` on ledger values. `crop-start` accompanies `crop`. A form field also takes the chosen poster size; never crop its readable value. The Tailwind `outline-none!` is optional only when another visible focus treatment replaces it; this static CSS retains its own outline.

For character animation, replace balanced wrapping with normal wrapping on those targets and follow the installed `animaxxing` skill's `references/text-stability.md`. Static typography needs no motion dependency.

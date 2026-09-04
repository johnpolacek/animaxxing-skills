# Typography and layout

Read this to compose pages. The system runs on International Typographic Style contrast: oversized Rethink Sans statements against compact supporting copy, everything flush left and ragged right on a twelve-column grid ruled with hairlines.

Class strings below are Tailwind v4 against the tokens reference. Each carries a plain-CSS equivalent in prose where the mapping is not obvious.

## Type roles

Five roles name the contrast so compositions can be assembled without a hero component baking one arrangement in.

| Role | Element | Classes | Notes |
|---|---|---|---|
| Poster | `p` or heading | `font-sans text-poster font-extrabold text-balance` | Structural graphic type, fluid to its container. Never for text that must be read in full. Add `[margin-inline-start:-0.055em]` to pull the left side-bearing off so the glyph edge, not the box, aligns to the grid. |
| Statement | `p` or heading | `max-w-[18ch] font-sans text-statement font-extrabold text-balance` | One size down: an oversized statement that still reads as a sentence. |
| Label | `span` | `font-mono text-caption uppercase text-muted` | The metadata voice. Anchors a grid cell; never competes with it. |
| Annotation | `p` | `max-w-[46ch] font-mono text-annotation uppercase text-muted` | The smallest type. Kept above 11px, never cropped. |
| BodyCopy | `p` | `font-sans text-body text-pretty max-w-[68ch]` | Supporting copy at a comfortable measure. `max-w-[42ch]` for the narrow measure. |

Support tone: `text-muted` on canvas and surface; `text-inverse-foreground/75` on an inverted band.

**Crop.** Oversized type is clipped at a deliberate boundary instead of shrunk: wrap it in `overflow-hidden` (and `flex justify-end` to crop the start edge). Only display type is ever cropped.

## The display setting

Card headings, story titles, and any heading below poster scale share one setting:

```
DISPLAY = "font-sans font-extrabold leading-[0.84] tracking-[-0.045em] [font-kerning:none]"
```

Plain CSS: `font-weight: 800; line-height: 0.84; letter-spacing: -0.045em; font-kerning: none`. Kerning is off so split-text characters measure the same as the unsplit line.

Card headings: `font-sans text-4xl font-extrabold uppercase tracking-[-0.03em] sm:text-5xl`.

## Mono vocabulary

```
MONO_LABEL = "font-mono text-caption font-bold uppercase tracking-[0.08em]"
MONO_NOTE  = "font-mono text-annotation uppercase tracking-[0.08em]"
FIGURE     = MONO_NOTE + " tabular-nums"
```

Numbers in a ledger are `FIGURE`. Section numbers are two digits: `01 · Wikipedia`, `Ch. 01 / 04`. The middle dot is a real `·` with spaces either side.

## Chips and buttons

Strong border, tight radius, uppercase extrabold sans at a small size.

```
CHIP         = "inline-flex h-12 items-center gap-2.5 rounded-xl border-2 px-5 font-sans text-[13px] font-extrabold uppercase tracking-[0.04em] transition-colors"
CHIP_SOLID   = CHIP + " border-inverse bg-inverse text-inverse-foreground hover:bg-inverse-hover"
CHIP_OUTLINE = CHIP + " border-foreground text-foreground hover:bg-surface-hover"
CHIP_QUIET   = CHIP + " border-border text-muted hover:border-foreground hover:text-foreground"
SMALL_CHIP   = "inline-flex h-10 items-center rounded-lg border-2 border-foreground px-4 font-sans text-caption font-extrabold uppercase tracking-[0.04em] text-foreground transition-colors hover:bg-surface-hover"
```

Calls to action are the same shape at display size:

```
BUTTON_SOLID   = "inline-flex cursor-pointer items-center rounded-lg bg-inverse px-6 py-3 font-sans text-4xl font-extrabold uppercase tracking-[-0.02em] text-inverse-foreground transition-colors hover:bg-inverse-hover focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-focus sm:px-8 sm:py-4 sm:text-5xl"
BUTTON_OUTLINE = same, with "border-2 border-foreground bg-transparent text-foreground hover:bg-surface-hover" in place of the inverse fill
```

The primary action is solid and gets the `reactor` particle treatment; the secondary is outlined and gets `marquee`. Only one solid button per composition.

The `transition-colors` on chips and buttons is the one CSS transition in the system. GSAP never animates `color`, so they do not collide.

## Page grammar

### Site shell

Persistent chrome outside the route boundary: a header with the wordmark, then the page, then a hairline-ruled footer. The wordmark is lowercase mono, tracked out, muted, with a 1px underline drawn by `scaleX` on entrance. The footer carries the credit and the theme toggle at `text-caption` mono.

```
header: "px-gutter pt-gutter-lg sm:px-gutter-lg" > "mx-auto flex min-h-9 w-full max-w-7xl items-center justify-between gap-4"
wordmark: "relative inline-block font-mono text-base uppercase tracking-[0.08em] text-muted sm:text-lg"
footer: "mt-auto border-t border-border px-gutter py-10 sm:px-gutter-lg"
```

The shell enters once on first load and is untouched by route motion.

### Page section

```
main: "flex flex-1 flex-col"
section: "px-gutter pt-10 pb-16 sm:px-gutter-lg" > "mx-auto w-full max-w-7xl"
```

### Sticky header strip

A redesigned site's own chrome, inside the page:

```
header: "sticky top-0 z-30 -mx-gutter border-b border-border bg-canvas px-gutter sm:-mx-gutter-lg sm:px-gutter-lg"
row:    "flex min-h-14 items-center gap-x-8 py-2"
```

Left to right: the site's name as `MONO_LABEL` in foreground, a nav of `MONO_NOTE` links in muted that turn foreground on hover, a `FIGURE` clock or meta pushed right, and one `SMALL_CHIP` action. Below `md`, the nav hides and the chip takes the right edge.

### Twelve-column grid and the chapters rail

```
grid: "mt-8 grid grid-cols-12 gap-x-6 gap-y-8"
rail: "col-span-12 lg:col-span-1"
body: "col-span-12 lg:col-span-11"
```

The rail lists the page's chapters, numbered `01` to `04`. At `lg` it turns on its side: `lg:sticky lg:top-20 lg:h-[calc(100vh-6rem)] lg:rotate-180 lg:border-l lg:border-border lg:pl-3 lg:[writing-mode:vertical-rl]`. Below `lg` it is a row of chips that scrolls horizontally. The current chapter carries `aria-current="page"` and foreground color; the rest are muted.

```
RAIL_LINK = MONO_LABEL + " inline-flex shrink-0 items-center gap-2 rounded-lg px-2.5 py-2 transition-colors lg:py-2.5"
```

Poster headlines take eight columns; a photograph takes four and is cropped at the gutter.

### Ledgers

Dense lists are hairline-ruled rows, figures right, no zebra striping:

```
ROW = "grid grid-cols-[3rem_minmax(0,1fr)] items-start gap-x-6 border-b border-border py-3 lg:min-h-10 lg:grid-cols-[4rem_minmax(0,1fr)_14.5rem_5.5rem_5.5rem_4.5rem] lg:items-center lg:py-2.5"
```

The first story or item is set in `DISPLAY` type over its actions; the rest are rows. Below `lg` each row folds its figures into one `FIGURE` line under the title.

### Cards

```
card: "group block h-full cursor-pointer rounded-lg border-2 border-border bg-surface p-6 transition-colors hover:border-foreground hover:bg-surface-hover focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-focus sm:p-8"
```

Anatomy, top to bottom: a `Label` row (`01 · Source` left, `Soon` right when the card is a placeholder), the heading in the card display setting at `mt-8`, a `BodyCopy` blurb in muted at `mt-4` and `max-w-[36ch]`, and an `Annotation` call to action in foreground at `mt-8` ending in ` →`. The whole card is the link. Cards sit in `grid gap-6 sm:grid-cols-2 lg:grid-cols-3`.

### Forms

A text field is a rule, not a box: `block w-full border-b-[3px] border-foreground bg-transparent py-3 font-sans font-extrabold text-foreground placeholder:text-border outline-none!`, at whatever poster size the column allows. The keyboard ring is handled by the field's own `focus-visible` or by the particle treatment; suppress the browser outline only when one of those replaces it. Labels stay in the DOM as `sr-only` when the placeholder carries the visible label.

## Composition rules

- Flush left, ragged right. No justified text, no centered blocks.
- One poster or statement per view. Everything else supports it.
- Hairlines rule; strong borders outline interactive things.
- Numbers are tabular mono. Dates, times, counts, and chapter marks all read as figures.
- Photographs are monochrome, cropped hard at the grid, never rounded beyond `rounded-lg`.
- Empty space is a material. Section spacing is `--spacing-section`; do not fill it.

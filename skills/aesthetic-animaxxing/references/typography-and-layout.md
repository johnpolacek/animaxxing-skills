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
DISPLAY = "font-sans font-extrabold leading-[0.84] tracking-[-0.045em]"
```

Plain CSS: `font-weight: 800; line-height: 0.84; letter-spacing: -0.045em`. For character-animated targets, add the persistent typography setting below.

Card headings: `font-sans text-4xl font-extrabold uppercase tracking-[-0.03em] sm:text-5xl`.

## Stable typography for character animation

Read this before using any recipe that splits characters, especially `charsRiseIn`. [GSAP's Tips & Limitations](https://gsap.com/docs/v3/Plugins/SplitText/#tips--limitations) documents that character wrappers interrupt browser kerning. Splitting can change spacing; `split.revert()` restores natural kerning and can produce a horizontal snap even when heading height stays unchanged. `smartWrap` groups words to prevent mid-word breaks; character masks clip the reveal. Neither preserves kerning.

Make stable typography part of the target's base CSS, present before first paint and retained during splitting, after cleanup, and under reduced motion:

```html
<h2 class="character-headline">Small idea. Big feeling.</h2>
```

```css
/* Only headlines that use character animation, not all headings or body text. */
.character-headline {
  font-kerning: none;
  text-rendering: optimizeSpeed;
}
```

Tailwind equivalent: `[font-kerning:none] [text-rendering:optimizeSpeed]` on the same target. Use the project's own selector or CSS module name. This setting is permanent typography, not a tween or an animation-state class; do not toggle it in a builder, completion callback, or reduced-motion query. For `speakIn`, scope it to the persistent emphasis elements that receive inner character splits.

Keep `split.revert()` and the framework controller's interruption/unmount cleanup. Keeping wrappers indefinitely is not the default spacing fix. If natural kerning is essential, choose whole-word or whole-line animation without character splitting (for example `wordsSlideIn` or `linesMaskIn`), then verify the result.

### Diagnose the measured change

Change one cause at a time; do not apply every workaround:

| Evidence | Targeted response |
|---|---|
| Horizontal character-position changes across split/revert, with fonts ready and the same line breaks | Check computed kerning settings in both states; use the persistent CSS above. A stable heading box alone does not rule this out. |
| Font face or metrics change after splitting | Have the framework controller wait for the required fonts (`document.fonts.ready`), or use supported `autoSplit`/`onSplit` handling. Check the installed GSAP version and docs; returning the animation from `onSplit` lets the plugin manage re-splits. |
| Joined glyphs such as `fi`/`ffi` differ between states | Inspect ligatures separately. If confirmed, test persistent `font-variant-ligatures: none` on the affected target, or preserve shaping with words/lines. Do not disable ligatures globally or assume the rendering hint fixes every font/browser. |
| Line membership or heading height changes | Inspect available width, white space, tracking, and word grouping. GSAP warns against `text-wrap: balance` on split targets: omit the type roles' `text-balance` there and keep normal wrapping consistent across states. Use `smartWrap` for chars-only splits or words/lines grouping; re-split lines when width changes through the controller. |
| Text appears heavier after revert, or letter edges/descenders are clipped while masked | Compare computed font properties and font readiness first, then inspect glyph ink against each mask. Stable boxes and unchanged weight do not rule out clipping. Use the targeted mask fix below when demonstrated. |
| Weight effects jump when pinned character widths are removed | Compare pinned widths with the settled font's advances. Width pinning can stabilize the weight animation yet still change spacing on revert; verify that boundary separately. |

### Apparent weight change from clipped glyph ink

This is distinct from kerning: `mask: "chars"` with tight negative `letter-spacing` and `line-height` can clip letter edges and descenders. Removing masks exposes the complete glyph, making it look heavier without changing font weight or character positions. The kerning CSS above does not give masks extra room.

Before diagnosing a weight change, compare computed `font-family`, `font-weight`, `font-size`, `font-style`, `font-variation-settings`, and `font-feature-settings` on the split characters and restored text. Record tracking and line-height too. Confirm the intended font face is loaded (font readiness plus the browser's rendered-font inspection), not just that its CSS family is declared. If these are stable, compare captured glyphs and inspect mask overflow before blaming GPU compositing or trying `force3D`, layer promotion, or font-smoothing changes.

For confirmed mask clipping, add a class only to the affected split's masks immediately after creation, before building the reveal:

```ts
// split is the affected headline's existing character-masked SplitText instance.
for (const mask of split.masks) mask.classList.add("title-char-mask");
// With CSS Modules, pass the scoped token instead: styles.titleCharMask.
```

```css
.title-char-mask {
  /* Verified for the AI Film Camp headline; tune to the actual glyph ink. */
  padding: 0.15em;
  margin: -0.15em;
}
```

Padding expands the clipping area; matching negative margins compensate for the added space to preserve the layout footprint. `0.15em` is a verified value for that typography, not a universal constant or a new design token. Use only enough room for the actual font, size, tracking, and line-height, and measure spacing, wrapping, and height again. Keep clipping enabled so the reveal still works. Do not apply this to all split wrappers, unmasked characters, or headings globally.

Apply the class to each new affected split (inside `onSplit` if the controller uses auto re-splitting). In [split entrances](recipes/split-entrances.md), the optional `charMaskClass` passes this class to character masks only. Preserve durations, easing, stagger, `aria`, completion callbacks, and revert/unmount cleanup: the styled mask nodes disappear with revert. Unlike the permanent kerning CSS, this class belongs to temporary mask nodes.

Expanded masks may expose characters at the hidden endpoint. Check both forward and backward reveals, including opposite travel directions; do not assume `yPercent: 115` or `-115` still hides all ink. If a frame shows leakage, adjust only the hidden travel distance enough to clear the expanded mask, retaining animation timing, then repeat the checks.

See [cleanup verification](verification.md#splittext-cleanup-stability) for measurements and the observed regression.

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

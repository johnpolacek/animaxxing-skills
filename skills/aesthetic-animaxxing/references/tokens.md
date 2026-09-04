# Tokens

Read this to set up colors, fonts, type scale, spacing, radii, borders, focus, and selection. Two forms are given: plain CSS custom properties, and the Tailwind v4 `@theme inline` mapping that turns them into utilities.

## Colors

Monochrome only. Twelve semantic tokens, in a light and a dark scheme. Components consume them by name and never by hex.

Scheme precedence, highest first:

1. `data-theme="dark"` or `data-theme="light"` on `<html>`: an explicit user choice, written by a toggle and persisted (localStorage is fine).
2. `prefers-color-scheme`: the operating-system setting, used when no explicit choice exists.
3. Light.

```css
:root {
  color-scheme: light;

  --canvas: #ffffff;
  --foreground: #171717;
  --muted: #525252;
  --border: #d4d4d4;
  --surface: #fafafa;
  --surface-hover: #f0f0f0;
  --inverse: #171717;
  --inverse-hover: #404040;
  --inverse-foreground: #ffffff;
  --focus: #171717;
  --selection: #171717;
  --selection-foreground: #ffffff;
}

/* The operating-system setting, unless the user pinned the light scheme. */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;

    --canvas: #0a0a0a;
    --foreground: #ededed;
    --muted: #a3a3a3;
    --border: #262626;
    --surface: #171717;
    --surface-hover: #262626;
    --inverse: #ededed;
    --inverse-hover: #d4d4d4;
    --inverse-foreground: #0a0a0a;
    --focus: #ededed;
    --selection: #ededed;
    --selection-foreground: #0a0a0a;
  }
}

/* An explicit user choice wins at any operating-system setting. */
:root[data-theme="dark"] {
  color-scheme: dark;

  --canvas: #0a0a0a;
  --foreground: #ededed;
  --muted: #a3a3a3;
  --border: #262626;
  --surface: #171717;
  --surface-hover: #262626;
  --inverse: #ededed;
  --inverse-hover: #d4d4d4;
  --inverse-foreground: #0a0a0a;
  --focus: #ededed;
  --selection: #ededed;
  --selection-foreground: #0a0a0a;
}

body {
  background: var(--canvas);
  color: var(--foreground);
  font-family: var(--font-sans);
}
```

Roles:

| Token | Role |
|---|---|
| `canvas` | The page ground. |
| `foreground` | Text and rules at full strength. |
| `muted` | Supporting copy, labels, annotations. Meets AA on canvas and surface. |
| `border` | Hairlines and quiet outlines. |
| `surface`, `surface-hover` | Cards and panels one step off the canvas. |
| `inverse`, `inverse-hover`, `inverse-foreground` | The solid button and any inverted band. Supporting copy on an inverted band uses `inverse-foreground` at 75% opacity, because `muted` falls below AA there. |
| `focus` | The keyboard focus ring. |
| `selection`, `selection-foreground` | Text selection, inverted. |

Particle canvases read their color from `color` on the canvas element, so give the canvas `color: var(--foreground)` and they follow the scheme.

Blend colors only while the scheme switches, so a toggle does not flash. Add `theme-transitioning` to `<html>` for the switch and remove it 250ms later:

```css
:root.theme-transitioning,
:root.theme-transitioning *,
:root.theme-transitioning *::before,
:root.theme-transitioning *::after {
  transition-duration: 0.25s !important;
  transition-property: background-color, border-color, color, fill, outline-color, stroke, text-decoration-color !important;
  transition-timing-function: linear !important;
}

@media (prefers-reduced-motion: reduce) {
  :root.theme-transitioning,
  :root.theme-transitioning *,
  :root.theme-transitioning *::before,
  :root.theme-transitioning *::after {
    transition-duration: 0s !important;
  }
}
```

## Fonts

| Token | Face | Axis | Use |
|---|---|---|---|
| `--font-sans` | Rethink Sans, variable | `wght` 400 to 800 | Everything that is read, and all display type. |
| `--font-mono` | JetBrains Mono, variable | `wght` 100 to 800 | Labels, annotations, figures, code. |

800 is the top of Rethink Sans's axis. Asking for 900 clamps to the same rendering, so the system names the weight it gets: `font-weight: 800` for display, 600 for emphasis, 400 at rest. Animated weight stays inside 400 to 800.

Disable ligatures in code so figures stay tabular:

```css
code, pre { font-variant-ligatures: none; }
```

## Type scale

The two poster sizes are fluid and measured in `cqi`, so they respond to whatever column or frame they sit in and fall back to the viewport when no container is declared. Put `container-type: inline-size` on the column that owns a poster.

| Token | Size | Line height | Letter spacing | Role |
|---|---|---|---|---|
| `poster` | `clamp(3.25rem, 18cqi, 15rem)` | 0.84 | -0.045em | Structural graphic type. May be cropped. |
| `statement` | `clamp(2.75rem, 7cqi, 4.5rem)` | 0.95 | -0.03em | One size down; still reads as a sentence. Measure 18ch. |
| `display` | 2.25rem | 2.5rem | -0.02em | Card and section headings. |
| `title` | 1.5rem | 2rem | -0.01em | Subheadings. |
| `lead` | 1.125rem | 1.75rem | | Intro copy. |
| `body` | 1rem | 1.5rem | | Body copy. Measure 68ch, or 42ch narrow. |
| `caption` | 0.75rem | 1rem | 0.02em | Mono labels. |
| `annotation` | 0.6875rem | 1rem | 0.08em | Mono margin notes. The floor. |

## Spacing, radii, borders

| Token | Value |
|---|---|
| `--spacing-gutter` | 1.5rem |
| `--spacing-gutter-lg` | 2.5rem |
| `--spacing-section` | 4rem |
| `--radius-xs` | 0.125rem |
| `--radius-sm` | 0.25rem |
| `--radius-md` | 0.375rem |
| `--radius-lg` | 0.5rem |
| `--radius-xl` | 0.75rem |
| `--border-width-hairline` | 1px |
| `--border-width-strong` | 2px |

Radii are deliberately tight to keep the system editorial. Hairline is the default separator; strong is for chips, buttons, and cards.

## Focus and selection

```css
:focus-visible {
  outline: var(--border-width-strong) solid var(--focus);
  outline-offset: 2px;
}

::selection {
  background: var(--selection);
  color: var(--selection-foreground);
}

button { cursor: pointer; }
```

Interactive elements that sit on a canvas of their own use a wider offset so the ring clears the particles: `outline-offset: 4px`.

## Hatch

A fill made of diagonal hairlines cut out of a solid block. Used where a texture is needed without a second color.

```css
.hatch {
  background-color: var(--foreground);
  mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='8' height='8'%3E%3Cpath d='M-1 9L9-1M-1 1L1-1M7 9L9 7' stroke='black' stroke-width='1'/%3E%3C/svg%3E");
  mask-size: 8px 8px;
  mask-repeat: repeat;
}
```

## Tailwind v4 mapping

With Tailwind, the same tokens become utilities (`bg-canvas`, `text-muted`, `border-border`, `bg-inverse`, `text-poster`, `px-gutter`, `rounded-lg`, `border-hairline`):

```css
@import "tailwindcss";

@theme inline {
  --color-canvas: var(--canvas);
  --color-foreground: var(--foreground);
  --color-muted: var(--muted);
  --color-border: var(--border);
  --color-surface: var(--surface);
  --color-surface-hover: var(--surface-hover);
  --color-inverse: var(--inverse);
  --color-inverse-hover: var(--inverse-hover);
  --color-inverse-foreground: var(--inverse-foreground);
  --color-focus: var(--focus);
  --color-selection: var(--selection);
  --color-selection-foreground: var(--selection-foreground);

  --font-sans: var(--font-rethink-sans);
  --font-mono: var(--font-jetbrains-mono);

  --spacing-gutter: 1.5rem;
  --spacing-gutter-lg: 2.5rem;
  --spacing-section: 4rem;

  --radius-xs: 0.125rem;
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;

  --border-width-hairline: 1px;
  --border-width-strong: 2px;

  --text-poster: clamp(3.25rem, 18cqi, 15rem);
  --text-poster--line-height: 0.84;
  --text-poster--letter-spacing: -0.045em;

  --text-statement: clamp(2.75rem, 7cqi, 4.5rem);
  --text-statement--line-height: 0.95;
  --text-statement--letter-spacing: -0.03em;

  --text-annotation: 0.6875rem;
  --text-annotation--line-height: 1rem;
  --text-annotation--letter-spacing: 0.08em;

  --text-caption: 0.75rem;
  --text-caption--line-height: 1rem;
  --text-caption--letter-spacing: 0.02em;

  --text-body: 1rem;
  --text-body--line-height: 1.5rem;

  --text-lead: 1.125rem;
  --text-lead--line-height: 1.75rem;

  --text-title: 1.5rem;
  --text-title--line-height: 2rem;
  --text-title--letter-spacing: -0.01em;

  --text-display: 2.25rem;
  --text-display--line-height: 2.5rem;
  --text-display--letter-spacing: -0.02em;
}
```

`--font-rethink-sans` and `--font-jetbrains-mono` are whatever variables the project's font loader emits. Without a loader, set them from `@font-face` or the Google Fonts stylesheet: `--font-rethink-sans: "Rethink Sans", system-ui, sans-serif; --font-jetbrains-mono: "JetBrains Mono", ui-monospace, monospace;`.

## Motion tokens

Used by every recipe. Keep them in one module.

```ts
export const DURATION = { micro: 0.14, component: 0.2, page: 0.28 } as const;

export const EASE = {
  /** Entrances decelerate: fast at first, settled at the end. */
  entrance: "power2.out",
  /** Exits accelerate away and feel shorter than entrances. */
  exit: "power2.in",
  /** Position or state shifts that start and end at rest. */
  shift: "power2.inOut",
} as const;

export const SHIFT = { micro: 4, component: 8, page: 16 } as const;

export const STAGGER = { tight: 0.03, loose: 0.05 } as const;

/** Rethink Sans's whole animatable range. Above 800 clamps and renders identically. */
export const WEIGHT = { rest: 400, emphasis: 600, display: 800 } as const;
```

Micro motion runs 100 to 180ms, components 160 to 240ms, pages and major panels 220 to 320ms. A coordinated sequence rarely exceeds 500ms, which is why staggers are small. Display effects in the recipes run longer on purpose and are the exception, not the rule.

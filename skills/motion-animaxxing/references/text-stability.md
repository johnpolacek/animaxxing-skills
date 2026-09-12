# Text stability

Technical requirements for split text on the project's existing typography. No particular font, palette, or layout is required.

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
| Line membership or heading height changes | Inspect available width, white space, tracking, and word grouping. GSAP warns against `text-wrap: balance` on split targets: omit `text-wrap: balance` there and keep normal wrapping consistent across states. Use `smartWrap` for chars-only splits or words/lines grouping; re-split lines when width changes through the controller. |
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

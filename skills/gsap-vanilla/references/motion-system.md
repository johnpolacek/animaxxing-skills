# Lifecycle implementation

Read this to implement the five phases for pages and components without layout shift.

## The contract

**mount → initial state → intro → settled → outro → end state → unmount**

One controller owns a node from mount to unmount and exposes one current phase:

1. **Initial state.** In the DOM, final size reserved, measured, start values applied, not yet shown.
2. **Intro.** One timeline from initial values to settled.
3. **Settled.** Visible, stable, interactive, and controlled by normal CSS.
4. **Outro.** Still in the DOM while one timeline moves it toward removal.
5. **End state.** Still in the DOM, final values applied, completion run once. Safe to remove.

The user's request defines how each phase looks. If it only describes an intro or outro, implement the other phases as the minimum needed to enter and leave cleanly.

Store the current phase in a data attribute on the owned node. Do not infer it from opacity, DOM presence, or timeline progress.

## Setup

Create one module that imports GSAP and only the plugins the project uses, registers them once, and exports them. Other modules import from it. With a script-tag install, do the same in one file that runs first.

Give every owner a `gsap.context` scoped to its root element:

- Selectors inside the context match only inside that root.
- `revert()` on the context kills every tween, trigger, and split it created and restores inline styles.
- Wrap callbacks and event handlers that create GSAP work in `context.add` so they belong to the context.
- Store listeners, observers, and timers next to the context and remove them in the same cleanup.

Write setup so it is correct when it runs more than once on the same node. A bfcache restore, a same-document router revisiting a page, and a presence controller re-showing content all hand you a node that already holds settled values. Write initial state explicitly with `set` or `fromTo` rather than a `from` tween that trusts a fresh node, and make cleanup leave the node readable.

## Initial state

Build the final layout with normal CSS first. The initial state changes appearance, not layout. The element that owns geometry must exist before the animated node does.

- Mount content before measuring or animating it.
- Give images and media dimensions or an aspect ratio.
- Reserve async regions with a wrapper when their size is known.
- Prefer transforms, `autoAlpha`, masks, or clipping, which keep the layout box.

If the effect changes width, height, or position:

- Animate a transform on an inner element while an outer wrapper holds the settled size.
- For a real expand or collapse, measure start and end sizes first, animate the wrapper, and decide how surrounding content moves.
- For layout-to-layout changes, use Flip: capture the old state, apply the new layout, animate.
- When old and new content share one region, reserve the parent and overlap the children so only the parent affects layout.

Content must stay readable without JavaScript. The pre-paint hiding rule in [Page load and unload](page-load.md#initial-state-before-first-paint) is the only sanctioned way to hide before the intro.

## Intro and settled

Write reusable intro and outro builders only when behavior repeats. Each returns a timeline so the controller can compose, kill, reverse, or await it.

- Make settled the source of truth. It must not depend on a paused timeline.
- Clear temporary transform, visibility, transition, and `will-change` styles once settled.
- Run intro completion and settled callbacks once, including under reduced motion.
- On rapid state changes, replace, kill, or reverse the active timeline. Do not stack conflicting tweens.
- Update assistive text and state immediately. Animate the visual, not the meaning.

## Outro and end state

Start the outro from current rendered values. Keep the node in the DOM, laid out, and owned until the timeline completes.

- Reject duplicate outro requests or define which wins.
- If an intro is running, reverse it only when the outro is its exact inverse. Otherwise kill it and build the outro from current values.
- Disable pointer events when the visual can no longer support them, without removing the layout box.
- Run end-state work once. Only then remove, replace, hide, or navigate.
- Kill the active timeline on cleanup, but do not erase state a cover still needs.
- No `display: none`, `hidden` attribute, or DOM removal before the outro completes.

## Conditional show and hide

Toggling `hidden`, `display`, or removing a node ends it before an outro can play. Add a presence controller where that matters. It should:

- Show into initial state before the intro.
- Stay in the DOM through settled and outro.
- Keep the active timeline.
- On re-show during an outro, reverse only if that gives the intended intro. Otherwise kill, set from current values, and build a fresh intro.
- Hide or remove the node only after the end-state callback.
- Keep all five phases under reduced motion.

When content in a shared region changes size, decide who owns the region's geometry before showing either child. Overlap old and new inside a reserved wrapper, or animate a measured wrapper between known sizes. Do not let hide then show push surrounding content twice.

Do not use presence for content that can simply appear, or for page content a router already manages.

- Focus a panel when its intro completes, not when it is shown. An element at `visibility: hidden` refuses focus silently, and `autoAlpha: 0` is exactly that. Reduced motion completes synchronously, so the focus still lands.
- A dialog or menu that locks scroll, traps focus, or adds a key listener undoes all of it in its end-state callback, and again in `pagehide` in case the user leaves mid-open.

## Reduced and responsive motion

The OS preference is the default. Add a site override only if the product needs one.

Every effect needs initial, settled, and end states under reduced motion. Do not just shorten a disorienting effect. Skip travel, rotation, scale, parallax, and scrambling unless essential. A zero-duration timeline or an immediate `set` still fires completion for anything that depends on it.

Use `gsap.matchMedia()` for responsive and reduced-motion variants that must rebuild when conditions change. Create it inside the owner's context so it reverts with the owner.

A site-level override is not a media query, so `matchMedia` cannot see it. Read it in a shared `prefersReducedMotion()` helper that every timeline consults, mirror it as a root attribute so CSS can key on it, and rebuild `matchMedia` setups when it changes.

## Scroll

Use `gsap-scrolltrigger` for the API; these rules cover page lifetime and measurement.

- Create triggers in document order. Refresh after fonts, images, or dynamic content change layout, and after scroll restoration on a history navigation.
- Create triggers inside the owning context. Do not kill all triggers globally when one page leaves.
- A page can load already scrolled, by reload, hash, or history. Reveal-on-scroll targets above the restored position must not stay hidden. Let the trigger evaluate on creation and keep the pre-paint rule from outliving the initial phase.
- A `will-change` written from an `onToggle` callback is outside the context and survives its revert. Write it as a plain style and undo it in cleanup, or write it before the trigger is created.

Under reduced motion, go straight from initial to settled without unnecessary triggers. Keep outro and end callbacks that control navigation or removal.

## Text

Use SplitText when the effect needs per-character, word, or line targets.

- For character splits, keep scoped `font-kerning: none; text-rendering: optimizeSpeed` before, during, and after revert, including reduced motion. Wrappers disrupt kerning and can cause horizontal snapping; use words/lines if natural kerning is essential. See [SplitText limitations](https://gsap.com/docs/v3/Plugins/SplitText/#tips--limitations).
- Apparent weight changes can be clipped ink: check computed fonts/readiness, then mask edges, punctuation, and descenders. For confirmed clipping, add scoped mask padding with compensating negative margins; verify spacing and both hidden endpoints before trying compositing workarounds.
- Keep reading accessible with the plugin's ARIA support. If text contains links or controls, keep an unsplit accessible version instead of hiding them.
- Use word-aware wrapping for character animation. Use auto re-split for line animation that must survive width or font changes.
- Wait for fonts or use the re-split lifecycle when line measurement matters. Reserve settled height before splitting if wrappers could shift layout.
- With `autoSplit`, build the animation inside `onSplit` and return it. The plugin records the playhead before a re-split, restores it on the new lines, and waits for fonts itself.
- A split heading takes its timing from the page phase, not its own clock. Give it its own pre-paint rule rather than marking it as a page target, or the page's stagger and the split's rise fight over one element.
- Revert splits on interruption and unmount. Do not leave wrapper spans in stale content.

Revert when the owning phase no longer needs the split. Compare glyph appearance, character positions, wrapping, and height immediately before/after cleanup at desktop/mobile widths, with reduced motion and interruption. Stable boxes alone do not prove stable ink; distinguish subpixel rounding from visible movement.

## Interaction

Pointer motion needs keyboard parity. Pair hover with focus on interactive elements. Do not animate a non-interactive element like a control.

Keep gestures bounded, provide a non-gesture path, and dispose of interaction plugins with their owner. See `gsap-plugins` for Draggable, Observer, and Flip APIs.

## Layout stability and performance

- Prefer `x`, `y`, scale, rotation, and `autoAlpha` over layout properties.
- Use `clip-path`, filters, and variable-font axes deliberately; they can cost paint or shift layout.
- Batch reads before writes.
- The stable wrapper's box should not jump between mount, initial, settled, outro, end, and unmount. Intentional transforms move pixels; layout boxes do not.
- Set `will-change` just before animating and clear it after. Do not promote everything.
- Do not animate hundreds of nodes at once. Reduce targets, batch, or virtualize.
- Do not add a CSS transition on a property GSAP controls.

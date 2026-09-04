# Lifecycle implementation

Read this to implement the five phases for pages and components without layout shift.

## The contract

**mount → initial state → intro → settled → outro → end state → unmount**

One controller owns a node from mount to unmount and exposes one current phase:

1. **Initial state.** Mounted, final size reserved, measured, start values applied, not yet shown.
2. **Intro.** One timeline from initial values to settled.
3. **Settled.** Visible, stable, interactive, and controlled by normal CSS.
4. **Outro.** Still mounted while one timeline moves it toward removal.
5. **End state.** Still mounted, final values applied, completion run once. Safe to unmount.

The user's request defines how each phase looks. If it only describes an intro or outro, implement the other phases as the minimum needed to enter and leave cleanly.

Store the current phase in state, a ref, or a data attribute. Do not infer it from opacity, DOM presence, or timeline progress.

## Setup and React lifecycle

Create one client-only module that imports GSAP, `useGSAP`, and only the plugins the project uses, and registers them once. Other modules import from it.

Use `useGSAP` in components:

- Pass a root ref as `scope`.
- Use refs for single targets and scoped selectors for repeated ones.
- Add dependencies only when the animation must rebuild. A reused route component needs its params, or its loader data, as dependencies with `revertOnUpdate` so a param change reruns the lifecycle.
- Wrap callbacks and event handlers that create GSAP work in `contextSafe`.
- Return a teardown for listeners and other non-GSAP resources.

Never run GSAP or plugin code during server rendering. Under TanStack Start every route file can render on the server; keep GSAP inside effects.

Never call another component's `contextSafe` function from inside a `useGSAP` callback. GSAP nests contexts: a context whose function runs while another context's callback is executing becomes a child of that outer context, and the outer context's next revert kills it. In practice this means a page's setup must not synchronously trigger a shared overlay's builders. Hand off through a microtask, an effect, or an event instead.

Write setup so it is correct when it runs more than once on the same node. React development checks do this, and a route component reused across a param change hands you a node that already holds settled values. Async work started by the first run can still be in flight when the second run starts, so anything a setup triggers outside its own context, such as a shared cover, must be safe to request twice. So: explicit initial writes (`set` or `fromTo`) rather than `from` tweens that trust a fresh node, and cleanup that leaves the node readable. Use a ref guard only for work that should happen once per visit rather than once per setup.

## Initial state

Build the final layout with normal CSS first. The initial state changes appearance, not layout. The element that owns geometry must exist before the animated node mounts.

- Mount content before measuring or animating it.
- Give images and media dimensions or an aspect ratio.
- Reserve async and streamed regions with a wrapper when their size is known.
- Prefer transforms, `autoAlpha`, masks, or clipping, which keep the layout box.
- Set every target's initial values before starting the intro.
- Use `set()` then `to()`, or `fromTo()`, when the start must be exact.
- Wait for fonts before measuring line-based text, or use the plugin's re-split support.

If the effect changes width, height, or position:

- Animate a transform on an inner element while an outer wrapper holds the settled size.
- For a real expand or collapse, measure start and end sizes first, animate the wrapper, and decide how surrounding content moves.
- For layout-to-layout changes, use Flip: capture the old state, apply the new layout, animate.
- When old and new content share one region, reserve the parent and overlap the children so only the parent affects layout.

Content must stay readable without JavaScript. The pre-paint rule in [SSR and hydration](route-lifetime.md#ssr-and-hydration-with-tanstack-start) is the only sanctioned way to hide server-rendered content before the intro; client-only apps need none.

## Intro and settled

Write reusable intro and outro builders only when behavior repeats. Each returns a timeline so the controller can compose, kill, reverse, or await it.

- Centralize timeline defaults such as `overwrite`.
- Use labels and position parameters for sequencing, not accumulated delays.
- Start the intro only after all initial writes.
- Make settled the source of truth. It must not depend on a paused timeline.
- Clear temporary transform, visibility, transition, and `will-change` styles once settled.
- Run intro completion and settled callbacks once, including under reduced motion.
- On rapid state changes, replace, kill, or reverse the active timeline. Do not stack conflicting tweens.
- Update assistive text and state immediately. Animate the visual, not the meaning.

Keep builders next to their owner until the same behavior recurs. Do not build a named animation library in place of lifecycle ownership.

## Outro and end state

Start the outro from current rendered values. Keep the node mounted, laid out, and owned until the timeline completes.

- Reject duplicate outro requests or define which wins.
- If an intro is running, reverse it only when the outro is its exact inverse. Otherwise kill it and build the outro from current values.
- Disable pointer events when the visual can no longer support them, without removing the layout box.
- Run end-state work once. Only then resolve the blocker, unmount, replace, hide, or hand off.
- Kill the active timeline on cleanup, but do not erase state the route cover still needs.
- No `display: none`, conditional removal, or DOM replacement before the outro completes.

## Conditional show and hide

React unmounts conditional content before an outro can play. Add a presence controller where that matters. It should:

- Mount into initial state before the intro.
- Stay mounted through settled and outro.
- Keep the active timeline.
- On re-show during an outro, reverse only if that gives the intended intro. Otherwise kill, set from current values, and build a fresh intro.
- Remove the node only after the end-state callback.
- Keep all five phases under reduced motion.

When content in a shared region changes size, decide who owns the region's geometry before mounting either child. Overlap old and new inside a reserved wrapper, or animate a measured wrapper between known sizes. Do not let unmount then mount push surrounding content twice.

Do not use presence for content that can simply appear, or for routes the root controller already manages.

Two details that only show up in a browser:

- Focus a panel when its intro completes, not when it mounts. An element at `visibility: hidden` refuses focus silently, and `autoAlpha: 0` is exactly that. Reduced motion jumps to completion synchronously, so the focus still lands.
- When the outro ends and React is asked to unmount the children, clear only `will-change` from the wrapper. The unmount is queued, not immediate; clearing the collapsed height or visibility in the same tick flashes the content at full size for a frame.

A modal that is a child route is a presence controller whose unmount is a navigation. See [Conditional content](route-lifetime.md#conditional-content).

## Reduced and responsive motion

The OS preference is the default. Add an app override only if the product needs one.

Every effect needs initial, settled, and end states under reduced motion. Do not just shorten a disorienting effect. Skip travel, rotation, scale, parallax, and scrambling unless essential. A zero-duration timeline or an immediate `set` still fires completion for anything that depends on it, including the callback that lets a blocked navigation proceed.

Use `gsap.matchMedia()` for responsive and reduced-motion variants that must rebuild when conditions change. Revert it through the owning component. Do not nest a second GSAP context for the same setup.

An app-level override is not a media query, so `matchMedia` cannot see it. Read it in a shared `prefersReducedMotion()` helper that every timeline consults, mirror it as a root attribute so CSS can key on it, and for setups that live inside a `matchMedia` block either gate the block on the store through a hook dependency or accept that the block follows the OS alone and say so. Feed the router's `viewTransition` `types` function from the same decision.

## Scroll

Use ScrollTrigger when scroll drives timing or progress. Use plain timelines for things that just happen after mount.

- Use a one-shot trigger for reveals. Use `scrub` only when progress should track scroll.
- Batch nearby reveals that should arrive together.
- Create triggers in document order. Refresh after fonts, images, streamed data, or dynamic content change layout.
- Put ScrollTrigger on a top-level tween or timeline, never on child tweens.
- Animate a child of a pinned element, not the pinned element.
- Use linear easing for fake horizontal scroll.
- Remove markers before finishing.
- Create triggers inside the owning context. Do not kill all triggers globally when one page leaves. A layout route's triggers survive child navigations; a page's leave with it.
- A route reused with new params keeps its triggers against changed content. Refresh them after the new data renders.
- The router restores scroll in `onRendered`, after the page's layout effects. Triggers created in `useGSAP` measured before that; refresh from `onRendered`, and once more when the page settles if anything above a trigger changed height during the intro.
- A `useGSAP` context revert calls `revert()` on each trigger with no arguments, which ScrollTrigger treats as `kill(true)`: the pin spacer is removed and the pinned element's original inline styles are restored. Leaving a route mid-pin needs no extra cleanup. `gsap.matchMedia()` created inside the same setup registers with that context and is reverted with it; it is not a second context for the same setup.
- A `will-change` written from an `onToggle` callback is outside the context and survives its revert. Write it as a plain style and undo it in the matchMedia cleanup, or write it before the trigger is created.

Under reduced motion, go straight from initial to settled without unnecessary triggers. Keep outro and end callbacks that control navigation or unmount.

## Text

Use SplitText when the effect needs per-character, word, or line targets.

- Split only what animates.
- Keep reading accessible with the plugin's ARIA support. If text contains links or controls, keep an unsplit accessible version instead of hiding them.
- Use word-aware wrapping for character animation. Use auto re-split for line animation that must survive width or font changes.
- Wait for fonts or use the re-split lifecycle when line measurement matters. Reserve settled height before splitting if wrappers could shift layout.
- Keep a handle to the split's animation so re-split and cleanup can dispose of it. With `autoSplit`, build the animation inside `onSplit` and return it: the plugin records its playhead before a re-split and restores it on the new lines, and `revert()` undoes the tween's values. With line splitting and `autoSplit`, the plugin waits for fonts itself; no separate font wait is needed.
- A split heading inside a page takes its timing from the page phase, not its own clock. Hold at initial while the page is initial, rise when the page enters, drop when it leaves. Give it its own pre-paint rule rather than marking it as a page target, or the page's stagger and the split's rise fight over one element.
- Loader data changing in a reused route re-renders the heading's text node in place, which breaks a split that replaced it with spans. Revert before the data-dependent render and re-split after it, or key the split on the data.
- Revert splits on interruption and unmount. Do not leave wrapper spans in stale content.

Revert split markup only when the owning phase no longer needs it, and never in a way that changes line wrapping or height mid-transition.

## Interaction

Pointer motion needs keyboard parity. Pair hover with focus on interactive elements. Do not animate a non-interactive element like a control.

Use `quickTo` for high-frequency pointer values. Keep gestures and drags within bounds, offer a non-gesture path to the same action, and clean up plugin instances.

Use Flip for layout changes after capturing the old state. Use Observer only when normal controls cannot express the gesture.

## Layout stability and performance

- Prefer `x`, `y`, scale, rotation, and `autoAlpha` over layout properties.
- Use `clip-path`, filters, and variable-font axes deliberately; they can cost paint or shift layout.
- Batch reads before writes.
- The stable wrapper's box should not jump between mount, initial, settled, outro, end, and unmount. Intentional transforms move pixels; layout boxes do not.
- Size media, preload critical fonts, and refresh layout-dependent plugins only after sizes settle.
- Set `will-change` just before animating and clear it after. Do not promote everything.
- Do not animate hundreds of nodes at once. Reduce targets, batch, or virtualize.
- Test narrow and low-power devices.
- Do not add a CSS transition on a property GSAP controls.

Done means: settled DOM is readable and CSS-controlled, the node stays mounted through end state, and unmount moves nothing unexpectedly.

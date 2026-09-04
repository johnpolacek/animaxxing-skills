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

Store the current phase in a data attribute on the owned node, or in a ref mirrored to one. Do not infer it from opacity, DOM presence, or timeline progress.

## Setup and Vue lifecycle

Create one client-only module that imports GSAP and only the plugins the project uses, registers them once, and exports them. In Nuxt that is the `useGSAP` composable from `gsap-frameworks` or a `.client.ts` plugin. Other modules import from it.

Give every owner a `gsap.context` scoped to its root:

- Components: create it in `onMounted` with the template ref as scope and revert it in `onBeforeUnmount`. Under keepalive, revert in `onDeactivated` and rebuild in `onActivated`. Both unmount hooks run before a leave transition finishes, so neither is a place for outro work.
- Pages: the page's context owns settled-state work and reverts at leave start. The transition module owns a second context per `el` for the intro and the outro, created in `onBeforeEnter` or `onLeave` and reverted in `onAfterEnter` or `onAfterLeave`.
- Selectors inside a context match only inside its root. `revert()` kills every tween, trigger, and split it created and restores inline styles.
- Wrap event handlers and delayed callbacks that create GSAP work in `context.add` so they belong to the context.
- Store listeners, observers, and timers next to the context and remove them in the same cleanup.

Wait for the DOM before measuring. After a reactive change that alters the template, `await nextTick()` before reading sizes or refreshing ScrollTrigger. Content inside `<ClientOnly>` appears only after mount; watch its template ref.

Inside `<NuxtPage>` a page's `onMounted` runs when its Suspense resolves: on navigation that is at leave start or after the leave depending on `mode`, and on first load it is after hydration. Component-level setup belongs there; page-level phases belong to the transition hooks.

Write setup so it is correct when it runs more than once on the same node. `onActivated` under keepalive, development hot reload, and a presence controller re-showing content all hand you a node that already holds settled values. Write initial state explicitly with `set` or `fromTo` rather than a `from` tween that trusts a fresh node, and make cleanup leave the node readable.

## Initial state

Build the final layout with normal CSS first. The initial state changes appearance, not layout. The element that owns geometry must exist before the animated node does.

- Mount content before measuring or animating it.
- Give images and media dimensions or an aspect ratio; `<NuxtImg>` and `<NuxtPicture>` take `width` and `height`.
- Reserve async regions with a wrapper when their size is known. A `useAsyncData` region that resolves after mount is a component with its own controller.
- Prefer transforms, `autoAlpha`, masks, or clipping, which keep the layout box.
- Set every target's initial values before starting the intro.
- Use `set` then `to`, or `fromTo`, when the start must be exact.
- Wait for fonts before measuring line-based text, or use the plugin's re-split support.

If the effect changes width, height, or position:

- Animate a transform on an inner element while an outer wrapper holds the settled size.
- For a real expand or collapse, measure start and end sizes first, animate the wrapper, and decide how surrounding content moves.
- For layout-to-layout changes, use Flip: capture the old state, apply the new layout, `await nextTick()`, animate.
- When old and new content share one region, reserve the parent and overlap the children so only the parent affects layout.

Content must stay readable without JavaScript. The pre-paint rule in [SSR and first paint](navigation.md#ssr-and-first-paint) is the only sanctioned way to hide before the intro.

## Intro and settled

Write reusable intro and outro builders only when behavior repeats. Each returns a timeline so the controller can compose, kill, reverse, or await it, and each takes the `done` callback when a Vue hook drives it.

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

Start the outro from current rendered values. Keep the node in the DOM, laid out, and owned until the timeline completes.

- Reject duplicate outro requests or define which wins.
- If an intro is running, reverse it only when the outro is its exact inverse. Otherwise kill it and build the outro from current values.
- Disable pointer events when the visual can no longer support them, without removing the layout box.
- Run end-state work once. Only then call `done`, remove, hide, or navigate.
- Kill the active timeline on cleanup, but do not erase state a cover still needs.
- No `v-if` toggle, `v-show` off, `display: none`, or DOM removal before the outro completes.

## Conditional show and hide

Vue's `<Transition>` is the presence controller. Wrap the conditional node in `<Transition :css="false">` with the same JavaScript hooks pages use. It should:

- Show into initial state in `onBeforeEnter`, before the intro in `onEnter`.
- Stay in the DOM through settled and through `onLeave` until `done`.
- Keep the active timeline where the hooks can kill it.
- Keep all five phases under reduced motion and still call `done`.

Choose the toggle by what re-show during an outro should do. With `v-show`, the same element stays: Vue fires `onLeaveCancelled` and starts `onEnter` on it, so reverse is possible when it gives the intended intro. With `v-if`, Vue finishes the pending leave at once and mounts a fresh node, so build a fresh intro from initial state. Wrap a component only if it has a single root element.

`appear` is safe only on content that is not server-rendered. On SSR output it wraps the child in `<template>` and hides it until hydration.

Use `<TransitionGroup>` for lists. The same hooks run once per item with that item's `el`; read a `data-index` attribute for stagger, give every item a key, and set `:css="false"`. Its move animation is CSS-only, so use Flip when moves must be sequenced with GSAP.

When content in a shared region changes size, decide who owns the region's geometry before showing either child. Overlap old and new inside a reserved wrapper, or animate a measured wrapper between known sizes. Do not let hide then show push surrounding content twice.

Do not use presence for content that can simply appear, or for page content `<NuxtPage>` already manages.

Two details that only show up in a browser:

- Focus a panel when its intro completes, not when it is shown. An element at `visibility: hidden` refuses focus silently, and `autoAlpha: 0` is exactly that. Reduced motion completes synchronously, so the focus still lands.
- A dialog or menu that locks scroll, traps focus, or adds a key listener undoes all of it in its end-state callback, and again in `onBeforeUnmount` or `onDeactivated` in case its page leaves mid-open.

## Reduced and responsive motion

The OS preference is the default. Add a site override only if the product needs one.

Every effect needs initial, settled, and end states under reduced motion. Do not just shorten a disorienting effect. Skip travel, rotation, scale, parallax, and scrambling unless essential. A zero-duration timeline or an immediate `set` still fires completion, and every Vue hook still calls `done`.

Use `gsap.matchMedia()` for responsive and reduced-motion variants that must rebuild when conditions change. Create it inside the owner's context so it reverts with the owner.

A site-level override is not a media query, so `matchMedia` cannot see it. Keep it in `useState` or a store, read it in a shared `prefersReducedMotion()` helper that every builder consults, mirror it as a root attribute so CSS can key on it, and rebuild `matchMedia` setups when it changes. `experimental.viewTransition: true` already skips the browser side under the OS preference.

## Scroll

Use ScrollTrigger when scroll drives timing or progress. Use plain timelines for things that just happen after mount.

- Use a one-shot trigger for reveals. Use `scrub` only when progress should track scroll.
- Batch nearby reveals that should arrive together.
- Create triggers in document order. Refresh after fonts, images, or async data change layout, after `await nextTick()`, and after Nuxt's post-transition scroll.
- Put ScrollTrigger on a top-level tween or timeline, never on child tweens.
- Animate a child of a pinned element, not the pinned element.
- Use linear easing for fake horizontal scroll.
- Remove markers before finishing.
- Create triggers inside the owning context. Do not kill all triggers globally when one page leaves.
- Nuxt scrolls after the outro and one frame into the intro. Create page-level triggers in `onAfterEnter`, or after `page:transition:finish` plus a frame, and let them evaluate on creation so targets above the restored position are not left hidden.
- A page in keepalive storage measures zero. Kill triggers in `onDeactivated` and create them again in `onActivated` after the scroll settles.
- Reverting a pinned trigger removes its spacer. That happens at leave start, so hold the wrapper's height through the outro.
- A `will-change` written from an `onToggle` callback is outside the context and survives its revert. Write it as a plain style and undo it in cleanup, or write it before the trigger is created.

Under reduced motion, go straight from initial to settled without unnecessary triggers. Keep outro and end callbacks that control `done` or removal.

## Text

Use SplitText when the effect needs per-character, word, or line targets.

- Split only what animates.
- Keep reading accessible with the plugin's ARIA support. If text contains links or controls, keep an unsplit accessible version instead of hiding them.
- Use word-aware wrapping for character animation. Use auto re-split for line animation that must survive width or font changes.
- Wait for fonts or use the re-split lifecycle when line measurement matters. Reserve settled height before splitting if wrappers could shift layout.
- With `autoSplit`, build the animation inside `onSplit` and return it. The plugin records the playhead before a re-split, restores it on the new lines, and waits for fonts itself.
- A split heading takes its timing from the page phase, not its own clock. Give it its own pre-paint rule rather than marking it as a page target, or the page's stagger and the split's rise fight over one element.
- Split after hydration, never in server-rendered markup. Revert splits on interruption, on leave, and on deactivate. Do not leave wrapper spans in stale content.

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
- Do not add a CSS transition on a property GSAP controls, and do not leave Vue transition classes active on a GSAP-driven root; `css: false` prevents that.

Done means: settled DOM is readable and CSS-controlled, the node stays in the DOM through end state, every hook called `done`, and removal moves nothing unexpectedly.

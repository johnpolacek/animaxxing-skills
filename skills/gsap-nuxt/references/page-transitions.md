# Page transitions

Read this when changing route-level motion: the hooks, `done`, modes, what dies when the leave starts, first load, layouts, direction, and interruptions.

## What Nuxt gives you

`<NuxtPage>` renders `<RouterView>` → `<Transition>` → `<KeepAlive>` → `<Suspense>` → page. The `<Transition>` and `<KeepAlive>` layers exist only when configured. Nothing is on by default: `app.pageTransition`, `app.layoutTransition`, and `app.keepalive` all default to `false`.

`pageTransition` and `layoutTransition` take Vue `TransitionProps`: `name`, `mode`, `css`, `appear`, `duration`, the class props, and the JavaScript hooks. Three places set them, merged key by key with the first defined value winning:

1. `<NuxtPage :transition="...">` in `app.vue`. Keys set here cannot be overridden by a page.
2. `definePageMeta({ pageTransition })` in the page. It is a compiler macro: the object is hoisted out of the component, so hook functions must be imported or module-level, never closures over refs, template refs, or component state.
3. `app.pageTransition` in `nuxt.config`. JSON-serializable only, so no hooks; use it for `name`, `mode`, and `css` defaults.

Nuxt appends its own `onAfterLeave`, which fires the `page:transition:finish` app hook, alongside yours.

`pageTransition: false` in `definePageMeta` (or in `nuxt.config` with no prop) removes the `<Transition>` for that route: the old page unmounts at once and nothing leaves. Use it for routes that must swap with no motion.

Pages and layouts must render a single root element. A fragment root cannot be animated; Nuxt warns in development and the transition does not run. A layout's root cannot be its `<slot />`.

## GSAP owns the hooks

Set `css: false` and implement the JavaScript hooks. With `css: false`, Vue adds no `*-enter-*` or `*-leave-*` classes and does not wait for `transitionend`; the transition ends when you call `done`. Without it, a leftover `.page-enter-active` rule runs a CSS transition on the element GSAP is tweening.

Declare the `done` parameter. Vue calls a hook declared with only `el` synchronously and finishes the transition at once.

The hooks and the phases they own:

- `onBeforeEnter(el)`. The incoming root exists with its children but is not in the document: selectors work, measurement does not. Write initial values that need no layout, such as `autoAlpha` and transforms.
- `onEnter(el, done)`. The root is in the document, in the same task as insertion and before paint. Measure, finish initial state, then advance the phase to `intro` and build the intro from a microtask, not in the same task as the `initial` write, or `initial` is never observable. Call `done` on completion.
- `onAfterEnter(el)`. Settled. Clear temporary styles with `clearProps`, refresh ScrollTrigger, move focus. Do not revert the enter context here: a revert restores the inline values from before the tween, which are the `autoAlpha: 0` and transform written in `onBeforeEnter`, and the settled page vanishes.
- `onEnterCancelled(el)`. A new navigation arrived mid-intro. Kill the intro; the element is about to leave.
- `onBeforeLeave(el)` and `onLeave(el, done)`. The outgoing root is still in the document with its layout. Build the outro from current values, call `done` on completion.
- `onAfterLeave(el)`. `el` has been removed. End state and cleanup of anything the outro owned.
- `onLeaveCancelled` fires only for `v-show`. Page roots never get it.

Hooks receive `el` and nothing else. By `onLeave` the page component is gone, so there are no template refs, no component state, and `useRoute()` already means the new page. Mark targets with data attributes and query them inside `el`, or run the builder inside `gsap.context(fn, el)`.

`done` is a contract:

- Call it once per hook call. Extra calls are ignored.
- Call it from the timeline's `onComplete` and from `onInterrupt`, since a killed timeline never completes. Put that in one helper every builder uses.
- Call it synchronously under reduced motion after writing end values.
- An enter that never calls `done` never fires `onAfterEnter`, and the next leave cancels it.
- A leave that never calls `done` keeps the old root in the DOM forever, never fires `page:transition:finish`, holds Nuxt's scroll, and under `out-in` never inserts the new page. If something outside the hook can kill the timeline, keep the `done` call outside the timeline too.

Race the leave's `done` against a short timeout. GSAP's ticker and `requestAnimationFrame` stop in a hidden tab, and a navigation started from a background tab must still finish.

## The component dies when the leave starts

When Vue removes a page whose root has a leave transition, it unmounts the component first and keeps only the root element: `onBeforeUnmount` runs synchronously, the component's effect scope stops, the element is handed to `onLeave`, and `onUnmounted` runs in the same flush. All of that happens before the outro plays a frame. Under keepalive, `onDeactivated` fires at that moment instead.

What this means:

- A `gsap.context` the page reverts on unmount kills the page's tweens and triggers, and restores their inline styles, as the outro begins. Let it. It must leave the DOM readable, because that is the picture the outro starts from.
- Build the outro in `onLeave` inside a context the transition module owns, scoped to `el`. Revert that context in `onAfterLeave`.
- The outgoing page loses its reactivity, watchers, and listeners at leave start. Nothing in it updates during the outro. Do not plan on it responding.
- A ScrollTrigger reverted at leave start removes its pin spacer and restores the pinned element, so a page leaving mid-pin changes height as the outro begins. Hold the stable wrapper's height through the outro, or design the outro so the collapse is covered.
- Template refs are null in `onLeave`. `el` is the only handle.

## Modes and who is on screen

`mode` decides overlap. Nuxt's examples use `out-in`; Vue's default is simultaneous.

- **`out-in`.** The outro plays alone. When `done` is called, Vue removes the old root, inserts the new one, and runs `onBeforeEnter` and `onEnter`. One page owns the geometry at a time.
- **No `mode`.** The old root starts leaving and the new root is inserted in the same tick. Both are in the document through the outro. Give the container the geometry: reserve its size, or overlap the children so only the wrapper takes space in flow.
- **`in-out`** behaves like no `mode` under `<NuxtPage>`. Do not use it.

In both modes the outro cannot start before the incoming page is ready. `<NuxtPage>` renders the incoming page under `<Suspense>`: its setup, top-level `await`, `useAsyncData`, and `useFetch` run off-screen while the outgoing page stays visible and interactive. The leave begins when that resolves. So the outro never overlaps loading, the user never sees a half-loaded page, and a slow page shows only the old page and the loading indicator until it is ready. If the design wants the outro to cover the wait, see [Outro before navigation](navigation.md#outro-before-navigation).

Under `out-in` the incoming page's `onMounted` runs after the old root is gone and the new one is inserted; under no `mode` it runs at leave start. The order between that `onMounted` and `onEnter` differs between modes. Do not depend on it. Page-level phases belong to the hooks; component-level setup belongs to `onMounted`.

## First load and `appear`

Do not use `appear` on a server-rendered page. Vue's SSR compiler wraps the child of `<Transition appear>` in `<template>`, so the server HTML ships the page inert and invisible until hydration replaces it. No JavaScript, no page. On hydration, `appear` also runs the enter hooks after the server HTML has painted, so it cannot hide the settled state either.

The first load is its own lifecycle:

- Mount is hydration. The page's `onMounted` runs after hydration, which is after first paint.
- Initial state must be written before first paint by an inline head script plus a CSS rule, not by GSAP. See [SSR and first paint](navigation.md#ssr-and-first-paint).
- The intro starts in the page's `onMounted` (or on `app:suspense:resolve` for a shell-level intro) and releases the pre-paint rule as its first act.
- Without `appear`, the hooks do not run on first load, so first load and navigation are two entry points to the same intro builder.

With `ssr: false` nothing paints before Vue renders, so `onMounted` is early enough, no pre-paint rule is needed, and `appear` is safe.

## Layouts

`layoutTransition` wraps the layout's root the same way. When a navigation changes layouts, the page transition does not run; the layout transition does, and the layout's chrome leaves and enters with the page. Give layout changes their own hooks or disable one of the two. Do not make `<NuxtLayout>` the root element of a page.

Chrome that must never move on navigation lives in `app.vue` outside `<NuxtLayout>`, or in one layout every route shares.

## Direction and dynamic transitions

Route middleware runs before the transition starts and may rewrite `to.meta.pageTransition`; check it is not `false` first. Nuxt documents changing `name` this way. The hooks can read the same object through `useRouter().currentRoute.value.meta.pageTransition`, because the route has already changed when `onLeave` fires. Keep `name` in sync even with `css: false`; it lets a CSS fallback share the vocabulary.

Alternatives: a `useState` the middleware writes and the hooks read, or a computed `:transition` on `<NuxtPage>`.

Direction from the route pair is the honest signal. History direction is a separate problem; see [Back and forward](navigation.md#back-and-forward).

## Interruptions

Nuxt remounts the `<Suspense>` when a navigation starts while another is still pending, and Vue cancels a running enter when its element must leave. Handle:

- `onEnterCancelled`: kill the intro. The same element then gets `onBeforeLeave` and `onLeave`; start the outro from current values.
- A leave still running when a third route arrives: Vue removes the element through the pending `done` guard, so your `done` may run late or twice. Both are harmless. Kill the timeline in `onAfterLeave`.
- A killed timeline never resolves its promise. Use the `done` helper for every `await`.
- Two clicks before the first navigation is confirmed: Vue Router cancels the first as a navigation failure and Nuxt fires `page:loading:end` for it. No hooks run for the cancelled one.

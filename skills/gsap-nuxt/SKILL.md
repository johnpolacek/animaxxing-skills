---
name: gsap-nuxt
description: "Build or review GSAP animation in Nuxt 3 and Nuxt 4 projects: page and layout transitions through the pageTransition and layoutTransition JavaScript hooks, enter and exit motion, animated show and hide of conditional content, and scroll-driven effects across NuxtPage and NuxtLink navigation. Use whenever a Nuxt project needs any of these, even if GSAP is not named, and whenever definePageMeta, Vue Transition, onEnter, onLeave, page transitions, route transitions, keepalive, back and forward, layout jank, interrupted animations, or cleanup on navigation matter. Also use to choose between GSAP, Vue Transition CSS, and Nuxt's experimental View Transitions for a navigation effect. Not for plain Vue without Nuxt, which gsap-frameworks covers, and not for isolated GSAP API questions."
license: MIT
metadata:
  short-description: GSAP page and component lifecycles in Nuxt
---

# GSAP Nuxt

Every animated page or component runs through the same lifecycle:

**mount → initial state → intro → settled → outro → end state → unmount**

Mount and unmount belong to Vue. The five phases between them belong to your animation code and happen while the node exists. Nuxt adds a twist: `<NuxtPage>` wraps every page in Vue's `<Transition>` and `<Suspense>`, so the page component is torn down the moment its outro starts and only the root element lives on until `done` is called. This skill covers getting the five phases right under that model: hydration, navigation timing, page keys, interruptions, and cleanup. The user's request and the existing design decide how things look.

## Start with the project

1. Read repository instructions and the current code.
2. Confirm Nuxt with a `pages/` directory. If the project is plain Vue with Vue Router and no Nuxt, say this skill does not cover it and use `gsap-frameworks`.
3. Read the installed Nuxt, Vue, and Vue Router versions from `node_modules`. Prefer the installed types and their JSDoc (`node_modules/@nuxt/schema`, `node_modules/nuxt/dist`, `node_modules/@vue/runtime-core/dist`, `node_modules/vue-router/dist`) and that version's docs over memory. Version gates: `onPrehydrate` (3.12), `useRuntimeHook` (3.14), the `app/` source directory (4), view transition types (4.4), `prefetch` in the `<NuxtLink custom>` slot (4.5).
4. Read `nuxt.config`: `ssr`, `srcDir`, `app.pageTransition`, `app.layoutTransition`, `app.keepalive`, `experimental.viewTransition`, `future.compatibilityVersion`. Nuxt 4 puts `pages/`, `layouts/`, `middleware/`, `plugins/`, `composables/`, `app.vue`, and `router.options.ts` under `app/`; Nuxt 3 keeps them at the root. `~/` resolves to the source directory in both.
5. Look at `app.vue`, layouts, `<NuxtPage>` props, route middleware, global CSS, accessibility conventions, tests, and any animation library already in use.
6. Keep the project's package manager, language, file layout, styling, and component conventions.

Add GSAP or a plugin only when the requested motion needs it. Do not replace an animation library the project already chose unless asked. If the project already has the `useGSAP` composable from `gsap-frameworks`, register and lazy-load plugins through it.

## Pick GSAP, Vue Transition CSS, or View Transitions per effect

Three engines can move a Nuxt route change. Pick one per element per transition.

Use Vue Transition CSS (`pageTransition: { name, mode }` plus `.name-enter-*` and `.name-leave-*` rules) for a plain fade or slide of the whole page with no sequencing. It needs no lifecycle code.

Use `experimental.viewTransition` for:

- A shared element that morphs between two routes.
- A whole-page slide or crossfade keyed by view transition types.

It falls back to an instant swap in unsupported browsers and skips itself under reduced motion unless set to `'always'`.

Use GSAP through the `pageTransition` JavaScript hooks when the effect needs:

- Sequenced timing across many targets, split text, or scroll-linked progress.
- Interruption, reversal, or scrubbing mid-transition. A view transition is a fixed pair of snapshots.
- An outro on the live page with a completion callback that gates removal, focus, or scroll.
- Both pages on screen at once under your control.

Mixing is fine across elements: the browser morphs one image while GSAP animates the rest. Never give one element to both in the same transition, and never run the Vue hooks and a view transition on the same navigation. See [View Transitions](references/navigation.md#view-transitions).

## Follow the requested motion

The user's request decides effects, direction, timing, easing, and intensity. Map it onto the five phases without changing the look. For anything unspecified, keep the project's existing convention or pick a quiet default.

## Read only what you need

- The hooks, `done`, modes, what dies when the leave starts, first load, layouts, direction, interruptions: [Page transitions](references/page-transitions.md).
- Page keys, keepalive, Nuxt app hooks, scroll and focus, outro before navigation, back and forward, View Transitions, SSR and first paint: [Navigation](references/navigation.md).
- The five phases, GSAP setup, Vue lifecycle, show and hide, layout stability, scroll, text, plugins: [Lifecycle implementation](references/motion-system.md).
- Before calling work done: [Verification](references/verification.md).

The official GSAP skills (`gsap-core`, `gsap-frameworks`, `gsap-timeline`, `gsap-scrolltrigger`, `gsap-plugins`, `gsap-utils`, `gsap-performance`) cover the GSAP API and the Vue component basics: `onMounted`, `gsap.context`, revert on unmount, and the Nuxt `useGSAP` composable. This skill covers how GSAP fits Nuxt routing and page lifetime.

## Pieces to add, only as needed

- One client-only plugin or the `useGSAP` composable that registers GSAP and plugins once.
- A page transition module exporting one hook set (`onBeforeEnter`, `onEnter`, `onAfterEnter`, `onEnterCancelled`, `onBeforeLeave`, `onLeave`, `onAfterLeave`) with `css: false`, applied through `<NuxtPage :transition>` app-wide or `definePageMeta({ pageTransition })` per page.
- An inline head script and matching CSS rule that hide intro targets before first paint on server-rendered pages.
- Data attributes marking the elements a page animates. The hooks receive only `el`; template refs are gone by then.
- A controller per page or component that owns its five phases.
- Intro and outro timeline builders that also call `done`.
- A route middleware that sets `to.meta.pageTransition.name` when direction depends on the route pair.
- A `<Transition :css="false">` with the same hooks around conditional content that must stay mounted through its outro.

Persistent header, nav, and footer live in `app.vue` or a shared layout, outside `<NuxtPage>`. A component owns its own lifecycle; the transition hooks own page lifecycles.

## Rules

- GSAP runs only on the client. Guard with `import.meta.client`, `onMounted`, or `<ClientOnly>`. Scope selectors. Clean up every tween, trigger, split, and listener.
- Lay out the final page with normal CSS first. One stable wrapper owns the geometry through every phase. Pages and layouts need a single root element or the transition does not run.
- Mount, then set initial values, then paint. `onBeforeEnter` runs before the incoming root is inserted and `onEnter` right after, before the browser paints. Users never see the settled state before the intro.
- Animate to one settled state and clear temporary styles there.
- Always call `done`: from `onComplete`, from `onInterrupt`, and synchronously under reduced motion. A leave that never calls `done` leaves the old page in the DOM forever.
- The page component is unmounted, or deactivated under keepalive, when the leave starts, not when it ends. Its context revert and `onUnmounted` run while the outro plays. Build the outro in `onLeave` against `el`, in a context the hooks own.
- Keep outgoing pages and components in the DOM through outro and end state. Vue does this as long as `done` waits.
- The outro cannot start before the incoming page has resolved. Design the wait: the old page stays on screen and interactive.
- Under keepalive, a page lifecycle runs again on reactivation against DOM that already holds settled values. Never assume a fresh node.
- Back and forward run the same hooks as a click. Detect history navigation yourself and give it a quieter path. Never fake an outro that did not happen.
- When outgoing and incoming content overlap (no `mode`), only the stable wrapper takes up space in the layout.
- Never use `appear` on a server-rendered page: Vue's SSR wraps the child of `<Transition appear>` in `<template>`, so the page is blank until hydration and without JavaScript.
- Keep native link behavior, focus, scroll, and no-JavaScript readability.
- Prepare incoming targets before revealing the swap. Never flash settled or stale content.
- Reduced motion reaches the same settled state and still calls `done` and every completion callback.
- Prefer transforms and `autoAlpha`. Set `will-change` only while animating, then clear it.
- Use timelines for sequences. Decide up front what happens on rapid clicks and interrupted animations.
- Verify in a real browser when practical. Use a production build for route, config, dependency, or release changes.

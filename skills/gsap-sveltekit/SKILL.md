---
name: gsap-sveltekit
description: "Build or review GSAP animation in SvelteKit projects on Svelte 5: page transitions, enter and exit motion across client-side navigation, animated show and hide of conditional content, and scroll-driven effects. Use whenever a SvelteKit project needs any of these, even if GSAP is not named, and whenever a page intro fails to replay, an outro is cut off by navigation, layout jank, interrupted animations, or cleanup matter. Covers beforeNavigate, afterNavigate, onNavigate, goto, +page.svelte and +layout.svelte lifetimes, runes and $effect cleanup, and choosing between GSAP, Svelte transition:, in: and out: directives, {#key} blocks, and View Transitions for a navigation effect. Not for Svelte components outside SvelteKit routing, which gsap-frameworks covers, or isolated GSAP API questions."
license: MIT
metadata:
  short-description: GSAP page and component lifecycles in SvelteKit
---

# GSAP SvelteKit

Every animated page or component runs through the same lifecycle:

**mount → initial state → intro → settled → outro → end state → unmount**

Mount and unmount belong to Svelte. The five phases between them belong to your animation code and happen while the node exists. This skill covers getting those phases right when SvelteKit's router decides when pages mount, update in place, and unmount: navigation timing, page reuse, interruptions, and cleanup. The user's request and the existing design decide how things look.

SvelteKit reuses components across navigation. A `+page.svelte` that stays on the same route with new params updates in place, and layouts persist through every child navigation. Treat a param change as a new page lifecycle even though nothing mounts. See [Page lifetime](references/page-lifetime.md).

## Start with the project

1. Read repository instructions and the current code.
2. Confirm SvelteKit with Svelte 5 in runes mode. Plain Svelte without SvelteKit routing belongs to `gsap-frameworks`. For Svelte 4 or legacy mode, say so and map `$effect` advice onto `onMount` and `onDestroy`.
3. Read the installed `@sveltejs/kit` and `svelte` versions. Prefer their bundled types over memory: `node_modules/@sveltejs/kit/types/index.d.ts` documents every navigation object, and `node_modules/svelte/types/index.d.ts` the runes and lifecycle exports. Version gates: `onNavigate` (1.24), `$app/state` (2.12; use `$app/stores` before), `to.scroll` on navigation targets (2.51), `prefersReducedMotion` in `svelte/motion` (5.7), `{@attach}` (5.29).
4. Check `svelte.config.js`, page options (`ssr`, `csr`, `prerender`), `data-sveltekit-preload-data` on `body` in `src/app.html`, and links marked `data-sveltekit-reload`. A page with `csr = false` has no client router and no navigation hooks; a reload link is a full document load. Treat both as plain documents.
5. Look at layouts, navigation components, global CSS, accessibility conventions, tests, and any motion already in use: Svelte `transition:` directives, `svelte/animate`, a View Transitions setup, or GSAP.
6. Keep the project's package manager, language, file layout, styling, and component conventions.

Add GSAP or a plugin only when the requested motion needs it. Do not replace an animation library the project already chose unless asked.

## Pick GSAP, Svelte transitions, or View Transitions per effect

Three engines can animate a navigation. Choose per effect, one engine per element. Use Svelte `transition:`, `in:`, and `out:` for:

- A block that appears and disappears with a fade, fly, or slide and gates nothing on completion.
- A page swap inside `{#key}` where holding the old page until its `out:` finishes is the whole effect.

They keep the outgoing block mounted until every outro ends, reverse cleanly, and need no lifecycle code.

Use View Transitions, started from `onNavigate`, for a shared element that morphs between two routes or a whole-page crossfade or slide keyed by a class on `html`. They need no lifecycle code beyond the hook and fall back to an instant swap in unsupported browsers.

Use GSAP when the effect needs:

- An outro that finishes on the live outgoing page while the router waits.
- Interruption, reversal, or scrubbing mid-transition. A view transition is a fixed pair of snapshots; a directive reverses only itself.
- Sequenced timing across many targets, split text, or scroll-linked progress.
- A completion callback that gates navigation, focus, or removal.

Mixing across elements is fine: the browser morphs one image while GSAP animates the rest, or an `out:` holds a block while GSAP works inside it. Never give one element to two engines in the same transition. See [Combining engines](references/page-lifetime.md#combining-engines).

## Follow the requested motion

The user's request decides effects, direction, timing, easing, and intensity. Map it onto the five phases without changing the look. For anything unspecified, keep the project's existing convention or pick a quiet default.

## Read only what you need

- Navigation hooks and their order, outro before navigation, the lock, back and forward, scroll, focus, links, preloading, View Transitions: [SvelteKit navigation](references/sveltekit-navigation.md).
- Page reuse versus remount, layouts, `{#key}` versus `afterNavigate`, the Svelte 5 lifecycle, Svelte transitions beside GSAP, shallow-routed modals, SSR: [Page lifetime](references/page-lifetime.md).
- The five phases, GSAP setup, contexts, show and hide, layout stability, scroll, text, plugins: [Lifecycle implementation](references/motion-system.md).
- Before calling work done: [Verification](references/verification.md).

The official GSAP skills (`gsap-core`, `gsap-frameworks`, `gsap-timeline`, `gsap-scrolltrigger`, `gsap-plugins`, `gsap-utils`, `gsap-performance`) cover the GSAP API and the `onMount`, `gsap.context`, and cleanup pattern inside one Svelte component. This skill covers how GSAP fits SvelteKit's router.

## Pieces to add, only as needed

- One browser-only module that registers GSAP and plugins, guarded by `browser` from `$app/environment`.
- A route transition controller in the root `+layout.svelte`, the one component that outlives every navigation, with one stable route container around `{@render children()}`.
- `beforeNavigate` with `cancel()` and a guarded `goto` as the hold, when the outro must finish with the URL unchanged, or `onNavigate` returning the outro's promise when a URL that leads the animation is acceptable.
- `afterNavigate` in pages or the controller to start intros, compared on pathname so param and search changes do not replay them.
- `bind:this` refs or data attributes marking the elements a page animates.
- A controller per page or component that owns its five phases.
- Intro and outro timeline builders.
- A presence controller when conditional content must stay mounted through a GSAP outro, or an `out:` directive on the block when that is the whole effect.

Persistent header, nav, and footer live in the layout outside the route container. A component owns its own lifecycle; the layout controller owns page lifecycles.

## Rules

- GSAP runs only in the browser. `onMount` and `$effect` never run on the server; module-level code needs a `browser` guard. Scope selectors with `gsap.context` to a `bind:this` root. Clean up every tween, trigger, split, and listener in the effect teardown or the `onMount` return.
- Lay out the final page with normal CSS first. One stable wrapper owns the geometry through every phase.
- Mount, then set initial values, then paint. Users never see the settled state before the intro. Server HTML paints before hydration, so hide intro targets only under a root attribute set by an inline script, only during the initial phase, with a no-JavaScript path.
- Animate to one settled state and clear temporary styles there.
- Keep outgoing pages mounted and visible through outro and end state. Hold the navigation with `beforeNavigate` and re-issue it from the end callback, or return the outro's promise from `onNavigate`. The URL changes before `onNavigate` runs, so only the first keeps it unchanged during the outro.
- A navigation to the same route with new params updates the page in place. Run the lifecycle again from `afterNavigate` against DOM that already holds settled values, or remount with `{#key}`.
- Back and forward arrive as `popstate` through the same hooks. Never run an outro for them. Give them an intro-only path after scroll restoration.
- Do not read `page`, `data`, or `navigating` inside the effect that builds GSAP setup unless it should rebuild on every navigation.
- One engine per element. An `out:` directive on a node GSAP also animates fights it, and the block stays in the DOM until the directive finishes.
- Keep native link behavior, `data-sveltekit-*` options, focus, scroll, and no-JavaScript readability.
- Prepare incoming targets before revealing the swap. Never flash settled or stale content.
- Reduced motion reaches the same settled state and still fires every completion callback. Svelte transitions ignore CSS reduced-motion rules; zero them from `prefersReducedMotion`.
- Prefer transforms and `autoAlpha`. Set `will-change` only while animating, then clear it.
- Use timelines for sequences. Decide up front what happens on rapid clicks and interrupted animations.
- Verify in a real browser when practical. Use a production build for route, config, dependency, or release changes.

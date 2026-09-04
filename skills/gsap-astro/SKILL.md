---
name: gsap-astro
description: "Build or review GSAP animation in Astro projects: page transitions under the ClientRouter (formerly ViewTransitions), an outro that finishes before the swap through astro:before-preparation, cleanup in astro:before-swap, initial state on the incoming document, setup that rehooks on astro:page-load, transition:persist and persisted islands, choosing between transition:animate and GSAP per element, back and forward, prefetch, scroll and focus, animated show and hide, and scroll-driven effects. Use whenever an Astro project needs any of these, even if GSAP is not named, and whenever animations vanish, duplicate, or leak after client-side navigation. Also use to recognize an Astro site without ClientRouter as a plain multi-page site and hand it to gsap-vanilla. Not for React, Vue, or Svelte apps outside Astro, which have their own skills, or isolated GSAP API questions."
license: MIT
metadata:
  short-description: GSAP page and component lifecycles in Astro
---

# GSAP Astro

Every animated page or component runs through the same lifecycle:

**mount → initial state → intro → settled → outro → end state → unmount**

Astro renders pages to HTML on the server. Without `<ClientRouter />` the browser owns mount and unmount and the site is a plain multi-page site: everything in `gsap-vanilla` applies unchanged, including first paint, `pageswap` and `pagereveal`, the bfcache, and prerendering. With `<ClientRouter />` the document persists and the router swaps `<head>` and `<body>` in place: mount is the swap, unmount is the next swap, and module scripts, listeners, and timelines survive both. The five phases between belong to your animation code. This skill covers what Astro changes: where the outro runs, what survives a swap, what runs again, and what must be cleaned up. The user's request and the existing design decide how things look.

## Start with the project

1. Read repository instructions and the current code.
2. Read the installed Astro version. Read `node_modules/astro/dist/transitions/router.js`, `swap-functions.js`, and `node_modules/astro/components/ClientRouter.astro` before trusting memory; the package ships no changelog, so check the release notes for that version. Version gates: `<ClientRouter />` (5.0; `<ViewTransitions />` in 4.x, removed in 6.0), lifecycle events with `loader` and `newDocument` (3.6), form navigation (4.0), `transition:persist-props` and `data-astro-rerun` (4.5), `swapFunctions` (4.15).
3. Find where `<ClientRouter />` is: the shared head, some pages, or nowhere, and its `fallback` prop. Nowhere means `gsap-vanilla`, including CSS `@view-transition`.
4. Find which framework integrations render islands and which `client:*` directives are in use.
5. Check `astro.config` for `prefetch` and `experimental.clientPrerender`.
6. Look at layouts, navigation markup, global CSS, accessibility conventions, tests, and any animation already in use.
7. Keep the project's package manager, language, file layout, styling, and component conventions.

Add GSAP or a plugin only when the requested motion needs it. Do not replace an animation library the project already chose unless asked.

## Pick Astro's transition or GSAP per effect

Under `<ClientRouter />` every navigation runs a view transition, and elements marked with `transition:*` directives animate as snapshots.

Use `transition:name` and `transition:animate` for:

- A shared element that morphs between two pages.
- A whole-page `fade` or `slide` that reverses on back, with a simulated fallback in browsers without View Transitions.
- Holding persistent chrome still while content changes.

Use GSAP when the effect needs:

- An outro that finishes on the live page before the swap.
- Interruption, reversal, or scrubbing. A view transition is a fixed pair of snapshots.
- Sequenced timing across many targets, split text, or scroll-linked progress.
- A completion callback that gates navigation, focus, or removal.

Mixing is fine: the browser morphs one image while GSAP animates the rest. Never give one element to both in the same navigation. See [Combining with Astro's animations](references/client-router-navigation.md#combining-with-astros-animations).

## Follow the requested motion

The user's request decides effects, direction, timing, easing, and intensity. Map it onto the five phases without changing the look. For anything unspecified, keep the project's existing convention or pick a quiet default.

## Read only what you need

- The router's event sequence, outro before the swap, cleanup, initial state on the incoming page, direction, back and forward, scroll, focus, prefetch, fallback browsers: [ClientRouter navigation](references/client-router-navigation.md).
- Which scripts run again, listeners that outlive pages, custom elements, islands and `client:*` directives, `transition:persist`: [Scripts and islands](references/scripts-and-islands.md).
- The five phases, GSAP setup, contexts, show and hide, layout stability, scroll, text, plugins: [Lifecycle implementation](references/motion-system.md).
- Before calling work done: [Verification](references/verification.md).

`gsap-vanilla` covers the site without the router. `gsap-react` and `gsap-frameworks` cover GSAP inside an island. The official GSAP skills (`gsap-core`, `gsap-timeline`, `gsap-scrolltrigger`, `gsap-plugins`, `gsap-utils`, `gsap-performance`) cover the GSAP API. This skill covers how GSAP fits a page Astro swaps.

## Pieces to add, only as needed

- One module that imports GSAP and the plugins the project uses, registers them once, and exports them. Other scripts import from it.
- An `is:inline` script at the top of `head` that marks the root as JavaScript-active before first paint, paired with a CSS rule that hides intro targets only under that mark and only during the initial phase. Under the router the same mark is written onto `event.newDocument` in `astro:before-swap`.
- One layout-level module that registers the router listeners once and owns the transition: outro in `astro:before-preparation`, cleanup in `astro:before-swap`, initial state in `astro:after-swap`, intro in `astro:page-load`.
- A page controller per `data-page` value that owns the five phases for the current body, built by the layout module for whichever page is present.
- Intro and outro timeline builders.
- A presence controller for conditional content that must stay in the DOM through its outro.
- For a self-contained component, a custom element whose `connectedCallback` and `disconnectedCallback` own its context.
- Inside an island, that framework's GSAP setup, torn down with the island.

## Rules

- GSAP runs after the DOM it targets exists. Scope selectors with `gsap.context` to the page or component root. Clean up every tween, trigger, split, and listener before the swap that removes its owner.
- A module script runs once per visit, not once per page. Setup runs from `astro:page-load` and is correct when it runs again on a new body or twice on the same one.
- Listeners on `document` and `window` outlive the page. Register router listeners once, in one place, and have each handler find the current page before acting.
- Lay out the final page with normal CSS first. One stable wrapper owns the geometry through every phase.
- Set initial values before paint, then reveal. On first load that is the inline head script; after a swap it is `astro:before-swap` and `astro:after-swap`. Users never see the settled state before the intro, and never a blank page without JavaScript.
- Animate to one settled state and clear temporary styles there.
- The outro plays on live DOM inside `event.loader` in `astro:before-preparation`, and the router waits for it. Never animate in `astro:before-swap`: the user is looking at a snapshot.
- Back and forward get an intro-only path. A traverse fires every event, so skip the outro on `navigationType === "traverse"` on purpose.
- Keep `transition:persist` elements out of page-level cleanup and page-level intros. They cross the swap alive, timelines included.
- Keep native link behavior, the router's history, scroll restoration, and route announcement. Do not add a click interceptor beside the router for motion; the only click listener is the capture-phase guard that holds the lock while a navigation is in flight.
- Cleanup before the swap kills the page context; it does not revert it. A revert writes the intro's start values back onto a body that is still attached.
- Reduced motion reaches the same settled state and still fires every completion callback. The router already disables its own animations under `prefers-reduced-motion`.
- Prefer transforms and `autoAlpha`. Set `will-change` only while animating, then clear it.
- Use timelines for sequences. Decide up front what happens on rapid clicks and interrupted animations: the router lets a second click abort the first navigation while its outro is running, so first-click-wins needs the lock guard.
- Verify in a real browser when practical, including a page visited twice, back, forward, and a click during an outro.

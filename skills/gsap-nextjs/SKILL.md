---
name: gsap-nextjs
description: "Build or review GSAP animation in Next.js App Router projects: page transitions, enter and exit motion, animated show and hide of conditional content, and scroll-driven effects. Use whenever a Next.js App Router project needs any of these, even if GSAP is not named, and whenever layout jank, interrupted animations, or cleanup matter. Also use to choose between GSAP and React View Transitions for a navigation effect. Not for Pages Router, non-Next.js sites, or isolated GSAP API questions."
license: MIT
metadata:
  short-description: GSAP page and component lifecycles in Next.js
---

# GSAP Next.js

Every animated page or component runs through the same lifecycle:

**mount → initial state → intro → settled → outro → end state → unmount**

Mount and unmount belong to React. The five phases between them belong to your animation code and happen while the node exists. This skill covers getting those phases right: stable layout, navigation timing, interruptions, and cleanup. The user's request and the existing design decide how things look.

If the Next config has `cacheComponents` on, the router hides old routes instead of unmounting them. Treat hide as unmount and re-show as mount. See [Route lifetime under cacheComponents](references/app-router-navigation.md#route-lifetime-under-cachecomponents).

## Start with the project

1. Read repository instructions and the current code.
2. Confirm the App Router. If the project uses the Pages Router, say this skill does not cover it and stop.
3. Read the installed Next.js version. Prefer its bundled docs in `node_modules/next/dist/docs/` over memory. Version gates: `onNavigate` and `useLinkStatus` (15.3), `<ViewTransition>` and `transitionTypes` (16.2), `<Activity>` route preservation when `cacheComponents` is enabled (16.0, opt-in).
4. Check the Next config for `cacheComponents`. It changes how long routes live.
5. Look at layouts, navigation components, global CSS, accessibility conventions, tests, and any animation library already in use.
6. Keep the project's package manager, language, file layout, styling, and component conventions.

Add GSAP, `@gsap/react`, or a plugin only when the requested motion needs it. Do not replace an animation library the project already chose unless asked.

## Pick GSAP or View Transitions per effect

Next.js 16.2+ activates React `<ViewTransition>` on every route navigation with no setup.

Use `<ViewTransition>` for:

- A shared element that morphs between two routes.
- A whole-page slide or crossfade keyed by `transitionTypes`.
- A Suspense fallback giving way to loaded content.

These need no lifecycle code and fall back to an instant swap in unsupported browsers.

Use GSAP when the effect needs:

- An outro that finishes on the live outgoing page before navigation.
- Interruption, reversal, or scrubbing mid-transition. A view transition is a fixed pair of snapshots.
- Sequenced timing across many targets, split text, or scroll-linked progress.
- A completion callback that gates navigation, focus, or unmount.

Mixing is fine: the browser morphs one image while GSAP animates the rest. Never give one element to both in the same transition. See [Combining with View Transitions](references/app-router-navigation.md#combining-with-view-transitions).

## Follow the requested motion

The user's request decides effects, direction, timing, easing, and intensity. Map it onto the five phases without changing the look. For anything unspecified, keep the project's existing convention or pick a quiet default.

## Read only what you need

- Page intros and outros, transition-aware links, back and forward, focus, route swaps: [App Router navigation](references/app-router-navigation.md).
- The five phases, GSAP setup, React lifecycle, show and hide, layout stability, scroll, text, plugins: [Lifecycle implementation](references/motion-system.md).
- Before calling work done: [Verification](references/verification.md).

The official GSAP skills (`gsap-core`, `gsap-react`, `gsap-timeline`, `gsap-scrolltrigger`, `gsap-plugins`, `gsap-utils`, `gsap-performance`, `gsap-frameworks`) cover the GSAP API. This skill covers how GSAP fits React and Next.js.

## Pieces to add, only as needed

- One client-only module that registers GSAP and plugins.
- A route transition boundary around page content.
- A transition-aware Link and a navigate helper, when the outro must finish before navigation.
- Refs or data attributes marking the elements a page animates.
- A controller per page or component that owns its five phases.
- Intro and outro timeline builders.
- A presence controller when conditional content must stay mounted through its outro.

Persistent header, nav, and footer live outside the route boundary. A component owns its own lifecycle; the route boundary owns page lifecycles.

## Rules

- GSAP runs only on the client. Scope selectors. Clean up every tween, trigger, split, and listener.
- Lay out the final page with normal CSS first. One stable wrapper owns the geometry through every phase.
- Mount, then set initial values, then paint. Users never see the settled state before the intro.
- Animate to one settled state and clear temporary styles there.
- Keep outgoing pages and components mounted and visible through outro and end state. Unmount, or let the router hide, only after the end callback.
- Under `cacheComponents`, a page lifecycle runs again on re-show against DOM that already holds settled values. Never assume a fresh node.
- Back and forward never run an outro. Give them an intro-only path.
- When outgoing and incoming content overlap, only the stable wrapper takes up space in the layout.
- Keep native link behavior, focus, scroll, and no-JavaScript readability.
- Prepare incoming targets before revealing the swap. Never flash settled or stale content.
- Reduced motion reaches the same settled state and still fires every completion callback.
- Prefer transforms and `autoAlpha`. Set `will-change` only while animating, then clear it.
- Use timelines for sequences. Decide up front what happens on rapid clicks and interrupted animations.
- Verify in a real browser when practical. Use a production build for route, config, dependency, or release changes.

---
name: gsap-react-router
description: "Build or review GSAP animation in React Router v7 and v8 projects in framework mode (SSR on or off), data mode, or declarative mode: page transitions, enter and exit motion across client-side navigation, animated show and hide of conditional content, and scroll-driven effects. Use whenever a React Router or Remix-style project needs any of these, even if GSAP is not named, and whenever an intro fails to replay on a param change, an outro is cut off by navigation, layout jank, interrupted animations, or cleanup matter. Covers useBlocker as the only hold on navigation, useNavigation and pending UI, loaders, Outlet and route reuse, Link viewTransition and useViewTransitionState, back and forward, ScrollRestoration, and choosing GSAP or View Transitions per effect. Not for Next.js (gsap-nextjs), TanStack Router (gsap-tanstack-router), React without a router (gsap-react), or isolated GSAP API questions."
license: MIT
metadata:
  short-description: GSAP page and component lifecycles in React Router
---

# GSAP React Router

Every animated page or component runs through the same lifecycle:

**mount → initial state → intro → settled → outro → end state → unmount**

Mount and unmount belong to React. The five phases between them belong to your animation code and happen while the node exists. This skill covers getting those phases right when React Router decides when routes load, commit, reuse, and unmount: navigation timing, holding a navigation, route reuse, interruptions, and cleanup. The user's request and the existing design decide how things look.

React Router has no leave hook. A link click starts loading at once, and the outgoing route unmounts when the incoming one commits. `useBlocker` is the only way to hold a navigation, and a route matched again with new params keeps its element mounted. See [Route lifetime](references/route-lifetime.md).

## Start with the project

1. Read repository instructions and the current code.
2. Confirm React Router 7 or later and its mode. Framework mode has `react-router.config.ts`, `routes.ts`, `root.tsx`, and `HydratedRouter` in `entry.client.tsx`. Data mode has `createBrowserRouter` and `RouterProvider`. Declarative mode has `BrowserRouter` and no loaders, no `useNavigation`, and no blocker. A Remix 2 app uses the same hooks from `@remix-run/react`; say so and map the names.
3. Read the installed version from `node_modules/react-router/package.json`. The package ships its `docs/`, `CHANGELOG.md`, and `.d.ts` files in `dist/`; prefer them over memory. Version gates: `useBlocker` (6.19), `viewTransition` and `useViewTransitionState` (6.27), `Link mask` and `useTransitions` (7.15), middleware (7.9 behind `future.v8_middleware`, always on in 8). Version 8 is ESM-only, needs React 19.2, and drops `react-router-dom`: `RouterProvider` and `HydratedRouter` come from `react-router/dom`.
4. In framework mode check `ssr` and `prerender` in `react-router.config.ts`. Server-rendered and prerendered pages paint HTML before hydration. `ssr: false` ships an `index.html` holding only the root route and its `HydrateFallback`, so route content renders after hydration and needs no pre-paint rule. Data and declarative mode without server rendering are the same.
5. Look at `root.tsx` or the root element, layouts with `<Outlet>`, navigation components, `<ScrollRestoration>`, global CSS, accessibility conventions, tests, and any animation library already in use.
6. Keep the project's package manager, language, file layout, styling, and component conventions.

Add GSAP, `@gsap/react`, or a plugin only when the requested motion needs it. Do not replace an animation library the project already chose unless asked.

## Pick GSAP or View Transitions per effect

React Router wraps a navigation in `document.startViewTransition` when the Link, Form, or `navigate` call sets `viewTransition`. Use that for:

- A shared element that morphs between two routes, named through `useViewTransitionState` or the NavLink `isTransitioning` render prop.
- A whole-page crossfade or slide keyed by a class on the root while the transition runs.
- A swap that should not be a hard cut, including back and forward, which replay a recorded transition.

These need no lifecycle code and fall back to a plain update where the API is missing.

Use GSAP when the effect needs:

- An outro that finishes on the live outgoing page before the router loads and commits the next route.
- Interruption, reversal, or scrubbing mid-transition. A view transition is a fixed pair of snapshots.
- Sequenced timing across many targets, split text, or scroll-linked progress.
- A completion callback that gates navigation, focus, or unmount.

Mixing is fine: the browser morphs one image while GSAP animates the rest. Never give one element to both in the same transition. See [Combining with View Transitions](references/react-router-navigation.md#combining-with-view-transitions).

## Follow the requested motion

The user's request decides effects, direction, timing, easing, and intensity. Map it onto the five phases without changing the look. For anything unspecified, keep the project's existing convention or pick a quiet default.

## Read only what you need

- The blocker outro, transition-aware links, the lock, pending state, back and forward, the swap gap, scroll, focus, View Transitions: [React Router navigation](references/react-router-navigation.md).
- Modes and their hooks, route reuse versus remount, layouts and `<Outlet>`, SSR and SPA mode first paint, streaming, fetchers, modal routes: [Route lifetime](references/route-lifetime.md).
- The five phases, GSAP setup, React lifecycle, show and hide, layout stability, scroll, text, plugins: [Lifecycle implementation](references/motion-system.md).
- Before calling work done: [Verification](references/verification.md).

The official GSAP skills (`gsap-core`, `gsap-react`, `gsap-timeline`, `gsap-scrolltrigger`, `gsap-plugins`, `gsap-utils`, `gsap-performance`) cover the GSAP API, and `gsap-react` covers `useGSAP`, `scope`, `contextSafe`, and cleanup on unmount. This skill covers how GSAP fits React Router.

## Pieces to add, only as needed

- One client-only module that registers GSAP and plugins. In framework mode name it `*.client.ts` so the server bundle never evaluates it, and import it for its side effect only, from the root route. Components import `gsap` and `useGSAP` from the packages: a `.client` module's exports are `undefined` during server rendering, and a route component that calls `useGSAP` through it throws on the server.
- A route transition boundary in the root route, or in the layout that wraps the changing region, with one stable route container around `<Outlet>`.
- `useBlocker` in that boundary as the hold, when the outro must finish before navigation. One blocker per router.
- A transition-aware Link that wraps `<Link>`, plus a navigate helper, when there is no blocker (declarative mode) or the project prefers it.
- A key on the outlet, or a `pathname` dependency, so a reused route runs its lifecycle again.
- Refs or data attributes marking the elements a page animates.
- A controller per page or component that owns its five phases.
- Intro and outro timeline builders.
- A presence controller when conditional content must stay mounted through its outro.

Persistent header, nav, and footer live in the root route outside the container. A component owns its own lifecycle; the boundary owns page lifecycles.

## Rules

- GSAP runs only in the browser. Framework mode evaluates route modules on the server, so keep GSAP calls inside `useGSAP` or effects and registration in a `.client` module. Scope selectors. Clean up every tween, trigger, split, and listener.
- Lay out the final page with normal CSS first. One stable wrapper owns the geometry through every phase.
- Mount, then set initial values, then paint. Server HTML paints before hydration: hide intro targets only under a root attribute set by an inline script in the root `Layout`, only during the initial phase, with a no-JavaScript path.
- Animate to one settled state and clear temporary styles there.
- Keep outgoing routes mounted and visible through outro and end state. The router unmounts the old route when the new one commits, so hold the commit: `useBlocker` and `proceed()` from the end callback, or prevent the Link default and `navigate` after the outro.
- Never block or outro a `POP`. Back and forward get initial state and intro only, after scroll restoration.
- A navigation to the same route with new params reuses the element. Key the outlet on `location.pathname`, or run the lifecycle again from a `pathname` dependency against DOM that already holds settled values.
- Loaders run after `proceed()`, so the end state waits for data. Prefetch on intent and cover the route container until the incoming targets are prepared.
- A fetcher is not a navigation. Do not treat `fetcher.state` as a page transition.
- One engine per element. A named view transition and a GSAP tween on the same node fight.
- Keep native link behavior: modified clicks, `target`, `reloadDocument`, external URLs, `prefetch`, `NavLink` state, focus, scroll, and no-JavaScript readability.
- Prepare incoming targets before revealing the swap. Never flash settled or stale content.
- Reduced motion reaches the same settled state and still fires every completion callback, including the one that calls `proceed()`.
- Prefer transforms and `autoAlpha`. Set `will-change` only while animating, then clear it.
- Use timelines for sequences. Decide up front what happens on rapid clicks and interrupted animations.
- Verify in a real browser when practical. Use a production build for route, config, dependency, or release changes.

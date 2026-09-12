---
name: gsap-react-router
description: "Build or review React Router v7/v8 animation in framework, data, or declarative mode: GSAP page transitions, component enter/exit, scroll effects, useBlocker, route reuse, and cleanup. Use even when GSAP is unnamed, including choosing viewTransition. Also covers hidden-content recovery and first-load performance. Not for Next.js, TanStack Router, React without routing, or isolated GSAP API questions."
license: MIT
metadata:
  short-description: GSAP page and component lifecycles in React Router
---

# GSAP React Router

**mount → initial state → intro → settled → outro → end state → unmount**

Mount and unmount belong to React; animation owns the five phases between them. React Router has no leave hook: hold navigation with a blocker or intercept it before it starts. Parameter changes can reuse the route element.

Keep the requested look and existing project conventions. Add GSAP/plugins only as needed; do not replace the chosen animation library unless asked.

## Start with the project

Read repository instructions, existing animation, layouts, navigation, CSS, accessibility conventions, and checks. Then:

1. Confirm React Router 7 or later and its mode. Framework mode has `react-router.config.ts`, `routes.ts`, `root.tsx`, and `HydratedRouter` in `entry.client.tsx`. Data mode has `createBrowserRouter` and `RouterProvider`. Declarative mode has `BrowserRouter` and no loaders, no `useNavigation`, and no blocker. A Remix 2 app uses the same hooks from `@remix-run/react`; say so and map the names.
2. Read the installed version from `node_modules/react-router/package.json`. The package ships its `docs/`, `CHANGELOG.md`, and `.d.ts` files in `dist/`; prefer them over memory. Version gates: `useBlocker` (6.19), `viewTransition` and `useViewTransitionState` (6.27), `Link mask` and `useTransitions` (7.15), middleware (7.9 behind `future.v8_middleware`, always on in 8). Version 8 is ESM-only, needs React 19.2, and drops `react-router-dom`: `RouterProvider` and `HydratedRouter` come from `react-router/dom`.
3. In framework mode check `ssr` and `prerender` in `react-router.config.ts`. Server-rendered and prerendered pages paint HTML before hydration. `ssr: false` ships an `index.html` holding only the root route and its `HydrateFallback`, so route content renders after hydration and needs no pre-paint rule. Data and declarative mode without server rendering are the same.

## Choose the engine

In data/framework mode, use Link, Form, or `navigate` with `viewTransition` for snapshot morphs or page crossfades. Use GSAP for live-DOM outros that gate navigation, interruptible sequences, split text, or scroll-linked motion. One engine per element; see [combining engines](references/react-router-navigation.md#combining-with-view-transitions).

## Read only what you need

- Invisible entrances, failed initialization, indexing, and first-load performance: [Initialization and recovery](references/initialization.md), plus the [framework integration](references/motion-system.md#initialization-and-recovery).
- The blocker outro, transition-aware links, the lock, pending state, back and forward, the swap gap, scroll, focus, View Transitions: [React Router navigation](references/react-router-navigation.md).
- Modes and their hooks, route reuse versus remount, layouts and `<Outlet>`, SSR and SPA mode first paint, streaming, fetchers, modal routes: [Route lifetime](references/route-lifetime.md).
- The five phases, GSAP setup, React lifecycle, show and hide, layout stability, scroll, text, plugins: [Lifecycle implementation](references/motion-system.md).
- Before calling work done: [Verification](references/verification.md).

Install the [official GSAP skills](https://github.com/greensock/gsap-skills) alongside this repository. Load `gsap-core` for API details and `gsap-react` for component setup only as needed.

## Rules

- Preserve invisible intros on successful setup; recover the current incoming owner on failure. Follow the initialization contract before adding hiding rules.
- GSAP runs only in the browser. Framework mode evaluates route modules on the server, so keep GSAP calls inside `useGSAP` or effects and registration in a `.client` side-effect module. Import `gsap` and `useGSAP` from their packages: `.client` exports are undefined during SSR. Scope selectors. Clean up every tween, trigger, split, and listener.
- Reserve final geometry with normal CSS and a stable wrapper; overlap outgoing/incoming content without doubling layout space.
- Mount, then set initial values, then paint. Server HTML paints before hydration: hide intro targets only under a root attribute set by an inline script in the root `Layout`, only during the initial phase, with a no-JavaScript path.
- Animate to one settled state and clear temporary styles there.
- Keep outgoing routes mounted and visible through outro and end state. The router unmounts the old route when the new one commits, so hold the commit: `useBlocker` and `proceed()` from the end callback, or prevent the Link default and `navigate` after the outro.
- Never block or outro a `POP`. Back and forward get initial state and intro only, after scroll restoration.
- A navigation to the same route with new params reuses the element. Key the outlet on `location.pathname`, or run the lifecycle again from a `pathname` dependency against DOM that already holds settled values.
- Loaders run after `proceed()`, so the end state waits for data. Prefetch on intent and cover the route container until the incoming targets are prepared.
- A fetcher is not a navigation. Do not treat `fetcher.state` as a page transition.
- One engine per element. A named view transition and a GSAP tween on the same node fight.
- Keep native link behavior: modified clicks, `target`, `reloadDocument`, external URLs, `prefetch`, `NavLink` state, focus, scroll, and no-JavaScript readability.
- Reduced motion reaches the same settled state and still fires every completion callback, including the one that calls `proceed()`.
- Define interruption and rapid-click behavior; completion must release navigation waits exactly once.
- Verify in a real browser when practical. Use a production build for route, config, dependency, or release changes.

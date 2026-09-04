---
name: gsap-tanstack-router
description: "Build or review GSAP animation in TanStack Router projects for React, including TanStack Start: page transitions, enter and exit motion across client-side navigation, animated show and hide of conditional content, and scroll-driven effects. Use whenever a project on @tanstack/react-router or @tanstack/react-start needs any of these, even if GSAP is not named, and whenever an outro is cut off by navigation, an intro fails to replay on a param change, layout jank, interrupted animations, or cleanup matter. Covers useBlocker as the outro-before-navigation hook, Link interception, pendingComponent and pendingMs, useRouterState, router.subscribe events, Outlet and layout persistence, remountDeps, createFileRoute lifetimes, Link preload, viewTransition and defaultViewTransition, scrollRestoration, back and forward, and SSR with HeadContent, Scripts, and ScriptOnce. Not for Next.js (gsap-nextjs), React Router (gsap-react-router), React without a router (gsap-react), or isolated GSAP API questions."
license: MIT
metadata:
  short-description: GSAP page and component lifecycles in TanStack Router
---

# GSAP TanStack Router

Every animated page or component runs through the same lifecycle:

**mount → initial state → intro → settled → outro → end state → unmount**

Mount and unmount belong to React. The five phases between them belong to your animation code and happen while the node exists. This skill covers getting those phases right when TanStack Router decides when route components mount, update in place, and unmount: navigation timing, blockers, pending UI, route reuse, interruptions, and cleanup. The user's request and the existing design decide how things look.

TanStack Router waits for the destination's loaders before it swaps the tree, keeps a route component mounted when only its params or search change, and never unmounts a layout its child navigations share. Treat a param change as a new page lifecycle even though nothing mounts. See [Route lifetime](references/route-lifetime.md).

## Start with the project

1. Read repository instructions and the current code.
2. Confirm `@tanstack/react-router`. Next.js belongs to `gsap-nextjs`, React Router to `gsap-react-router`, React without a router to `gsap-react`. Solid Router is out of scope.
3. Read the installed `@tanstack/react-router` version and, when present, `@tanstack/react-start`. Prefer their bundled types over memory: `node_modules/@tanstack/router-core/dist/esm/router.d.ts` for `RouterOptions`, `RouterState`, and `RouterEvents`, `node_modules/@tanstack/react-router/dist/esm/useBlocker.d.ts` for the blocker, `node_modules/@tanstack/history/dist/esm/index.d.ts` for history actions. The TanStack/router repository's `docs/router/` and `docs/start/` are the source of truth. The loading architecture changed during the 1.16x and 1.17x releases; `RouterState.isTransitioning` is gone from router-core 1.171.2x, and `useBlocker` is still marked experimental.
4. Tell file-based routes (`createFileRoute`, `routeTree.gen.ts`, `__root.tsx`) from code-based routes (`createRoute`, `createRootRoute`). The lifecycle is the same; only where route options live differs.
5. Tell TanStack Start (SSR, a root document shell with `HeadContent` and `Scripts`) from a client-only Vite app (`RouterProvider` rendered into a div). Client-only apps paint nothing before React, so they need no pre-paint rule. Check `ssr` per route, `defaultSsr`, `spa.enabled`, and prerendering.
6. Read the router options: `defaultPreload`, `defaultPendingComponent`, `defaultPendingMs`, `defaultPendingMinMs`, `defaultViewTransition`, `scrollRestoration`, `defaultStaleTime`, `defaultRemountDeps`. Each changes when pages mount and what the user sees while they load.
7. Look at the root route, layouts, navigation components, global CSS, accessibility conventions, tests, and any motion already in use: `viewTransition`, Framer Motion, or GSAP.
8. Keep the project's package manager, language, file layout, styling, and component conventions.

Add GSAP, `@gsap/react`, or a plugin only when the requested motion needs it. Do not replace an animation library the project already chose unless asked.

## Pick GSAP or View Transitions per effect

TanStack Router can wrap a navigation's DOM update in `document.startViewTransition`, from `defaultViewTransition` on the router or `viewTransition` on a Link or `navigate` call, with `types` for direction.

Use View Transitions for:

- A shared element that morphs between two routes.
- A whole-page slide or crossfade keyed by view transition types.
- A pending fallback giving way to loaded content.

They need no lifecycle code and fall back to an instant swap in unsupported browsers.

Use GSAP when the effect needs:

- An outro that finishes on the live outgoing page before the router loads and swaps.
- Interruption, reversal, or scrubbing mid-transition. A view transition is a fixed pair of snapshots.
- Sequenced timing across many targets, split text, or scroll-linked progress.
- A completion callback that gates navigation, focus, or unmount.

Mixing is fine: the browser morphs one image while GSAP animates the rest. Never give one element to both in the same transition. See [Combining with View Transitions](references/tanstack-navigation.md#combining-with-view-transitions).

## Follow the requested motion

The user's request decides effects, direction, timing, easing, and intensity. Map it onto the five phases without changing the look. For anything unspecified, keep the project's existing convention or pick a quiet default.

## Read only what you need

- Router APIs and the order of one navigation, outro before navigation with `useBlocker` or an intercepted Link, the lock, back and forward, pending UI, the swap gap, scroll, focus, View Transitions: [TanStack navigation](references/tanstack-navigation.md).
- Route reuse versus `remountDeps`, layouts and `Outlet`, the React lifecycle for GSAP, conditional content, TanStack Start SSR and hydration, deferred data: [Route lifetime](references/route-lifetime.md).
- The five phases, GSAP setup, show and hide, layout stability, scroll, text, plugins: [Lifecycle implementation](references/motion-system.md).
- Before calling work done: [Verification](references/verification.md).

The official GSAP skills (`gsap-core`, `gsap-react`, `gsap-timeline`, `gsap-scrolltrigger`, `gsap-plugins`, `gsap-utils`, `gsap-performance`, `gsap-frameworks`) cover the GSAP API, `useGSAP`, `contextSafe`, and cleanup inside one component. This skill covers how GSAP fits TanStack Router.

## Pieces to add, only as needed

- One client-only module that registers GSAP and plugins.
- A route transition controller in the root route component, the one component that outlives every navigation, with one stable route container around `<Outlet />`.
- `useBlocker` in the controller as the wait, when the outro must finish before the router loads the next route.
- A `router.history.subscribe` listener that records the last history action so back and forward take the intro-only path.
- Refs or data attributes marking the elements a page animates.
- A controller per page or component that owns its five phases, keyed on the route's params when the component is reused.
- Intro and outro timeline builders.
- A presence controller when conditional content must stay mounted through its outro.

Persistent header, nav, and footer live in the root or a layout route outside the route container. A component owns its own lifecycle; the root controller owns page lifecycles.

## Rules

- GSAP runs only on the client. `useGSAP` never runs on the server; keep GSAP calls out of module scope in files Start renders on the server. Scope selectors. Clean up every tween, trigger, split, and listener.
- Lay out the final page with normal CSS first. One stable wrapper owns the geometry through every phase.
- Mount, then set initial values, then paint. Users never see the settled state before the intro. Under Start, server HTML paints before hydration, so hide intro targets only under a root attribute set by a `ScriptOnce` inline script, only during the initial phase, with a no-JavaScript path.
- Animate to one settled state and clear temporary styles there.
- Keep outgoing pages mounted and visible through outro and end state. The router swaps only after every blocker allows the navigation and the loaders finish; resolve the blocker from the end callback.
- No router event fires before the URL changes. `onBeforeNavigate` runs after the history commit; only a blocker runs before it.
- A navigation to the same route with new params reuses the component. Run the lifecycle again against DOM that already holds settled values, keyed on the params, or set `remountDeps`.
- Back and forward arrive with `action` `BACK`, `FORWARD`, or `GO`. Never run an outro for them; the URL has already moved when the blocker runs. Give them an intro-only path after scroll restoration.
- `useLocation` moves to the destination when loading starts, before the new page mounts. Do not key route content on it; key on the presented matches or on `resolvedLocation`.
- Keep native link behavior, preloading, `activeProps`, focus, scroll, and no-JavaScript readability.
- Prepare incoming targets before revealing the swap. Never flash settled or stale content.
- Reduced motion reaches the same settled state and still fires every completion callback, including the one that lets the blocked navigation proceed.
- Prefer transforms and `autoAlpha`. Set `will-change` only while animating, then clear it.
- Use timelines for sequences. Decide up front what happens on rapid clicks and interrupted animations.
- Verify in a real browser when practical. Use a production build for route, config, dependency, or release changes.

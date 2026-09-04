# Route lifetime

Read this to know which router you have, when a route mounts, updates in place, or unmounts, and how server rendering changes the first paint.

## Modes

Three top-level APIs, each adding features to the last. Check which one the project uses before reaching for a hook.

- **Declarative**: `<BrowserRouter>` with `<Routes>` and `<Route>`. `Link`, `NavLink`, `useNavigate` (returns nothing), `useLocation`, `useNavigationType`, `useLinkClickHandler`, `useBeforeUnload`. No loaders, no `useNavigation`, no `useBlocker`, no `viewTransition`, no `<ScrollRestoration>`. The transition-aware Link is the only way to run an outro before navigation, and the browser's own scroll restoration applies.
- **Data**: `createBrowserRouter` with `<RouterProvider>` from `react-router/dom`. Adds `loader`, `action`, `useNavigation`, `useBlocker`, `useFetcher`, `<Await>`, `<ScrollRestoration>`, `viewTransition`, `preventScrollReset`. No server rendering unless the project built its own.
- **Framework**: the Vite plugin, `routes.ts`, route modules with `loader`, `clientLoader`, `HydrateFallback`, `Layout`, `links`, `meta`, and `<HydratedRouter>` in `entry.client.tsx`. Adds `<Link prefetch discover>`, `<Links>`, `<Scripts>`, `middleware`, SSR by default, `prerender`, and SPA mode through `ssr: false`.

A Remix 2 app is framework mode with `@remix-run/react` names. A React Router 6.4+ data router is data mode with `unstable_` prefixes on older versions.

## Reuse versus remount

The router renders matched routes as nested elements through `<Outlet>`. React reconciles by type and position, so a navigation swaps only the levels whose route changed.

- Same route, new params or search params: the route element stays mounted. `params` and `loaderData` change; `useGSAP` with no dependencies does not run again. Neither does a mount intro.
- Different route under the same layouts: the leaf unmounts and the new one mounts. Shared layouts stay, with their state, timelines, and listeners.
- The root route persists for the life of the document. Under `Layout`, switching between the app, `HydrateFallback`, and `ErrorBoundary` keeps the document shell mounted.
- A revalidation reruns loaders and updates props. Nothing remounts.

So a page intro tied to mount plays once per mount, not once per visit. Two fixes:

- **A `pathname` dependency in the page, the default for GSAP.** Give `useGSAP` `dependencies: [pathname]` and `revertOnUpdate: true`, or run the lifecycle from an effect keyed on `useLocation().pathname`. The page keeps its state, scroll, and form values, and the DOM already holds settled values, so kill the previous timeline first and write initial state with `set` or `fromTo`, never a `from` tween that trusts a fresh node. Compare pathnames, adding params only when they mean a different screen, and skip search-only changes.
- **`<Outlet key={location.pathname} />` in the layout.** Every pathname change destroys and recreates the subtree, so mount intros replay and page state is discarded. Key on `location.key` to remount on every navigation including the same URL. Use it when the page must be re-instantiated anyway. It also discards inner scroll positions and pending fetchers in the subtree.

Do not key the root route or a layout that holds chrome on `location`. That remounts the shell and its chrome on every navigation.

## Layouts, Outlet, and the boundary

The root route mounts once per document and outlives every client-side navigation. That makes it the home of the route transition boundary: one stable route container around `<Outlet>`, the blocker, the phase, and the cover. When only part of the screen transitions, put the boundary in the layout route that wraps that part; its `<Outlet>` is the changing region and everything above it persists.

Pages register intro and outro builders with the boundary through context and unregister in their teardown. The boundary calls the outgoing page's outro when the blocker blocks or the wrapper intercepts, and the incoming page's intro when the new `location.key` commits and its targets are ready. A page that registers nothing gets the container-level default.

The outro belongs to the leaving leaf, not the layout. A layout that stays mounted has nothing to leave; a layout that also unmounts, because the navigation crosses out of it, leaves with its leaf and should register its own outro if it has one.

## React lifecycle for GSAP

`gsap-react` covers `useGSAP`, `scope`, `contextSafe`, and cleanup. Points that matter under a router:

- Effects run after commit. `useGSAP` uses a layout effect on the client, so initial `set` calls inside it land before paint on a client-rendered tree. On a server-rendered tree the HTML has already painted; see [SSR and first paint](#ssr-and-first-paint).
- React development runs setup, cleanup, and setup again on the same node. Write setup that is correct twice: explicit initial writes, cleanup that leaves the node readable, and a ref guard for work that should happen once per visit.
- Reading `useLocation()`, `useNavigation()`, or `loaderData` inside a `useGSAP` with those as dependencies rebuilds the context on every change, including search-param and pending-state changes. Depend on `pathname` alone, or read the rest through refs.
- Store the phase in state or a ref and render it as a data attribute. Do not infer it from opacity or DOM presence.
- Never call another component's `contextSafe` function synchronously from inside a `useGSAP` callback; the inner context becomes a child of the outer one and dies with its next revert. Hand off through a microtask, an effect, or an event.

## SSR and first paint

- Framework mode with `ssr: true`, the default, and any `prerender` path send full HTML. The page paints before hydration and before any effect. Hiding intro targets is only sanctioned through the root-attribute rule in [The swap gap and initial state](react-router-navigation.md#the-swap-gap-and-initial-state): an inline script first in `body` in the root `Layout`, `suppressHydrationWarning` on `html`, a no-JavaScript path, and a reduced-motion skip.
- Route modules are evaluated on the server. Importing GSAP is harmless; calling it is not. Keep registration in a `*.client.ts` module imported for its side effect from the root route, and every GSAP call inside `useGSAP`, an effect, or an event handler. Do not re-export `gsap` or `useGSAP` from the `.client` module: its exports are `undefined` on the server, so a component that imports the hook from there throws during server rendering. Import both from the packages.
- `ssr: false` prerenders only the root route and its `HydrateFallback` into `index.html`. Route content renders after hydration, so it can wait for mount and needs no pre-paint rule. The root shell still paints early; keep chrome motion out of it or treat the shell like a server-rendered page.
- `HydrateFallback` shows only on the initial document load while a `clientLoader` with `hydrate` runs or a route has no server loader. It never appears on client navigation. Give it the settled geometry so hydration moves nothing.
- Data and declarative mode without a server render paint nothing until React commits, so mount, `set`, then paint holds without any rule.
- `<Scripts>` omitted is the no-JavaScript build. Everything must read there.

## Conditional content and modals

React removes conditional content synchronously. For GSAP-driven show and hide, keep the node mounted with a presence controller: render while `visible || leaving`, play the outro, and clear `leaving` from the end callback. See [Conditional show and hide](motion-system.md#conditional-show-and-hide).

A modal opened by a route is a presence controller with the router as its unmount. Common shapes:

- A nested route rendered into the parent's `<Outlet>`, so the parent stays mounted underneath. Close by playing the outro, then `navigate(-1)` or `navigate` to the parent path. The parent's own intro must not replay: the parent is reused, and the boundary should recognize the modal path as an overlay navigation with no outro, no cover, and no lock.
- A `Link mask` (7.15) that shows one URL while routing to another, for a gallery that opens a detail in place. The underlying route stays; the modal is conditional content keyed on the real location.

Undo scroll locks, key listeners, and focus in the modal's effect teardown, which also covers a `POP` you did not initiate. A blocker in the modal is deleted when it unmounts; do not put the page blocker there.

## Fetchers, revalidation, and middleware

- `useFetcher` loads or submits without a navigation. `navigation.state` stays `idle`, `useBlocker` never fires, and a `Form` submission through a fetcher does not leave the page. Content a fetcher replaces is a component lifecycle, not a page one.
- A navigation `Form` POST is a navigation with `state === "submitting"`, then `loading` while loaders revalidate, then a commit that may be a redirect. The outgoing page is still mounted through all of it. Block it like a link if the design wants an outro; the blocker sees `nextLocation` and the submission.
- Revalidation after an action reruns every active loader and updates props in place. Nothing remounts and no outro runs. Regions whose content changes are components; give them explicit initial state on new data and keep their block size.
- `middleware` and `clientMiddleware` (7.9 behind `future.v8_middleware`, always on in 8) run around loaders and actions inside the data phase of a navigation. They can redirect or set context; they cannot hold the DOM or wait for an animation. They are not a transition hook.

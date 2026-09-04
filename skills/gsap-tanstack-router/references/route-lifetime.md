# Route lifetime

Read this to know when a route component mounts, updates in place, or unmounts, how the React lifecycle fits GSAP under this router, and what TanStack Start's server rendering changes.

## Reuse versus remount

The router renders matches as a chain: root, layouts, page, each in its own memoized `Match`. A navigation swaps only the levels whose route changed.

- Same route, new params or search: the component is reused. Its loader reruns when `loaderDeps` or `staleTime` say so; `useParams`, `useSearch`, and `useLoaderData` update in the commit. No mount, no unmount, no `useGSAP` with an empty dependency list.
- Different route under the same layouts: the page unmounts and the new one mounts. The layouts stay, with their state, timelines, and listeners.
- Layout routes (`route.tsx`, `_pathless` layouts, the root) persist for their subtree and unmount only when the tree leaves them.
- `router.invalidate` reruns loaders and updates props. Nothing remounts.
- `remountDeps({ routeId, params, search, loaderDeps })` on a route, or `defaultRemountDeps` on the router, forces a remount whenever its JSON-serializable return value changes. `({ params }) => params` is the documented way to remount per param.

So a page intro tied to a mount plays once per mount, not once per visit. Two fixes:

- **Rerun the lifecycle on the reused node, the default for GSAP.** Give `useGSAP` the params, or the loader data, as dependencies with `revertOnUpdate`. The DOM already holds settled values and the previous timeline may still be running, so kill it first and write initial state with `set` or `fromTo`, never a `from` tween that trusts a fresh node. Skip when only search params changed unless they mean a different screen.
- **`remountDeps`.** Every param change destroys and recreates the component, so the mount path replays. It discards component state and inner scroll positions, which is what the docs offer for that case.

Do not wrap `<Outlet />` in an element keyed on `useLocation().pathname`. That location moves when loading starts, before the new matches commit, so the wrapper remounts the old page once while it waits and again when the new page arrives. If a keyed wrapper is unavoidable, key it on the leaf of the presented matches, and expect it to remount every nested layout inside it.

## Layouts and the controller

The root route's component mounts once per document and outlives every client-side navigation. That makes it the home of the route transition controller: one ref'd route container around `<Outlet />`, the blocker, the history subscription, the phase, and the cover. Nested layout routes persist for their subtree and are the place for section-level chrome motion.

`Wrap` and `InnerWrap` on the router are for providers only; the docs forbid DOM-rendering components there. Keep the container in the root component.

Pages register intro and outro builders with the controller through context and unregister in their effect cleanup. The controller runs the outgoing page's outro from `shouldBlockFn` and the incoming page's intro when it reports ready. Ready is a call the page makes through the same context right after its initial writes in `useGSAP`, and it is what drops the cover and releases the lock; a timeout in the controller drops the cover anyway if no page reports. A page that registers nothing gets the container-level default.

A `useBlocker` in a page sees only navigations away from that page and unregisters when it unmounts. One blocker in the root is simpler than one per page.

## React lifecycle for GSAP

- `useGSAP` runs in a layout effect after the tree commits, before `onRendered` and before scroll restoration. `gsap-react` covers `scope`, `contextSafe`, `revertOnUpdate`, and cleanup. Use it unchanged.
- Route components render on the client inside `React.startTransition`. A component that suspends keeps the old tree on screen; the new tree mounts as a whole when it can. Layout effects, and so `useGSAP`, run in that single commit.
- Never call another component's `contextSafe` function from inside a `useGSAP` callback. GSAP nests contexts: a context whose function runs while another context's callback is executing becomes a child of that outer context, and the outer context's next revert kills it. A page's setup must not synchronously trigger the root controller's builders. Hand off through a microtask, an effect, or an event.
- Write setup so it is correct when it runs more than once on the same node. React development checks do this, and a reused route runs its keyed effect again on settled DOM. Async work started by the first run can still be in flight when the second starts, so anything a setup triggers outside its own context, such as the cover, must be safe to request twice. Use a ref guard only for work that should happen once per visit.
- Store the phase in a ref and mirror it as a data attribute. Do not infer it from opacity, DOM presence, or timeline progress.
- `onEnter`, `onStay`, and `onLeave` on a route run with the match during the load commit, before React renders it. They are for data and analytics, not for DOM work.

## Conditional content

React unmounts conditional content before an outro can play. Keep the node mounted with a presence controller: render while `visible || leaving`, play the outro, and clear `leaving` from the end callback. See [Conditional show and hide](motion-system.md#conditional-show-and-hide).

A modal that is a child route unmounts when the URL leaves it. Close it by playing its outro and then navigating, with `router.history.back()` when it was pushed or `navigate` to the parent otherwise, and tell the root controller that navigation is an overlay close so it runs no page outro and no cover. Undo scroll locks, key listeners, and focus in the effect teardown, which also covers a back navigation you did not initiate. Route masking (`mask`) changes only the URL shown; the component lifetime follows the real route.

## SSR and hydration with TanStack Start

- The root route renders the document. Its `component`, or its `shellComponent` when the root itself has `ssr: false`, returns `html`, `head` with `<HeadContent />`, and `body` with the children and `<Scripts />` last. `HeadContent` belongs in `head`; `Scripts` belongs at the end of `body`. The client entry, optional, is `hydrateRoot(document, <StartClient />)`.
- Server HTML paints before hydration, before any effect. If initial state must hide before first paint, render `<ScriptOnce>` from `@tanstack/react-router` as the first child of `body` with an inline script that marks `documentElement` as JavaScript-active, and a CSS rule that hides intro targets only under that mark and only while the root is in its initial phase. `ScriptOnce` renders the script on the server with a trailing `document.currentScript.remove()`, so it runs once during parsing and is gone before hydration, and it returns `null` on the client. Skip the mark under `prefers-reduced-motion` so the page paints settled. Add `suppressHydrationWarning` to `html`, since the server markup does not carry the attribute. Have the controller change the phase as its first act after hydration, before anything that can throw. Keep content readable without JavaScript and keep the swap cover separate from the first-paint rule.
- Add a failsafe to the same inline script: if no controller has claimed the document within about a second, remove the mark, so a bundle that never arrives leaves a readable page instead of hidden content. A controller that does arrive claims the document before anything else. A page whose mark is already gone when its controller runs, because the failsafe fired or because reduced motion skipped it, takes the instant path: the content is on screen, and hiding it again to play an intro would be worse than arriving settled.
- Hydration is the first mount. `useGSAP` runs once React attaches, and `onRendered` fires once with nothing changed. No `onBeforeNavigate` or `onBeforeLoad` precedes it.
- Do not write inline styles or move DOM before hydration. The pre-paint rule is CSS keyed on the root attribute, which is why it does not break hydration.
- `ssr: false` or `ssr: 'data-only'` on a route skips server rendering of its component: the server renders the route's `pendingComponent` as a fallback and the client shows it for at least `pendingMinMs` before the real component mounts. That mount is the first lifecycle for the route; nothing settled was painted, so it needs no pre-paint rule. The setting inherits downward and can only become more restrictive. `defaultSsr` in `createStart` sets the default.
- SPA mode (`spa.enabled`) prerenders only the root and the pending fallback; every route is a client mount. Prerendered routes hydrate like SSR routes.
- `<ClientOnly fallback>` and `useHydrated` render browser-only content after hydration. Use them for content whose server markup would differ, not as a way to hide intro targets.
- Deferred hydration (`<Hydrate when>`, experimental) keeps a boundary's server HTML on screen and hydrates it later. GSAP inside it starts only then. Treat it as a component that mounts late with its server HTML as the initial paint, and keep its targets out of the page's pre-paint rule.
- `useGSAP` never runs on the server. Importing GSAP in a route file is harmless; calling it at module scope is not. Register plugins in one client-only module that route files import lazily or inside effects.

## Deferred data and streaming

- A loader returns unawaited promises alongside awaited data; the route renders when the awaited data resolves and the rest streams, on the server through the HTML stream and on the client after mount. `<Await promise fallback>` or React 19 `use()` suspends the nearest boundary until each resolves.
- Treat each streamed region as a component with its own controller: explicit initial state on arrival, a short intro, settled, cleanup. It never reports page ready. Reserve its block size in the fallback so arrival moves nothing.
- The page outro owns everything present at leave time. Query outro targets when the outro is built, not at setup, so content that streamed in after setup leaves with the page. Intros stay separate: the page intro reveals what mounted with it, the region intro reveals what arrived later.
- Preloaded loader data lives in the router cache for `preloadStaleTime`; a navigation reuses it or joins the loader still in flight. Do not assume it survives a long outro plus an invalidation.
- With an external cache such as TanStack Query the loader only primes the cache; the same region rules apply to whatever suspends in the component.

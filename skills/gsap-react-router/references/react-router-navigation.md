# React Router navigation

Read this when changing route-level motion or navigation.

## Router APIs

Check the installed types before using these. Minimum versions in parentheses; modes in brackets where an API is not in all three.

- `<Link to replace state preventScrollReset viewTransition reloadDocument mask onClick>`: a real `<a>`. Its `onClick` runs before the router's handler, and `event.preventDefault()` there cancels that one navigation while the `href`, prefetch handlers, and `discover` stay intact. `prefetch` and `discover` exist only in framework mode; `preventScrollReset` and `viewTransition` only in framework and data mode.
- `<NavLink>`: `Link` plus `isActive`, `isPending` [framework, data], and `isTransitioning` (only when the link sets `viewTransition`) as render props, and `active`, `pending`, `transitioning` classes.
- `useNavigate()`: `navigate(to, { replace, state, relative, preventScrollReset, viewTransition, flushSync, mask })` or `navigate(delta)`. In framework and data mode it returns a promise that resolves when the navigation completes; in declarative mode it returns nothing.
- `useBlocker(shouldBlock)` (6.19) [framework, data]: the only hold on a navigation. See below.
- `useNavigation()` [framework, data]: `state` is `idle`, `loading`, or `submitting`; `location` is the destination while pending; `formMethod`, `formAction`, and `formData` describe a submission. It does not expose `historyAction`.
- `useLocation()`: `pathname`, `search`, `hash`, `state`, `key`. `key` changes on every navigation, including one to the same URL, and is `default` on the first document load.
- `useNavigationType()`: `POP`, `PUSH`, or `REPLACE` for how the current location was reached.
- `useViewTransitionState(to)` (6.27) [framework, data]: true while a view transition runs and `to` matches either side of it by pathname.
- `<ScrollRestoration getKey>` [framework, data]: render once, before `<Scripts>`.
- `useBeforeUnload(cb)`: the document unload. It cannot be delayed.
- `<Form>` GET submissions, `<Navigate>`, and `redirect` from a loader or action are navigations. `useFetcher` is not: `navigation.state` stays `idle` and the fetcher carries its own `state`.

Keep `<Link>` for every internal link so `href`, prefetching, and `NavLink` state keep working. Wrap it in a project-local transition-aware Link only when the outro must start on click without a blocker.

## Page lifecycle

**mount → initial state → intro → settled → outro → end state → unmount**

1. **Initial state.** The incoming route has committed or been reused in place, its final size is reserved, measurements are taken, and start values are set before anything is shown.
2. **Intro.** Reveal the route and play one timeline to the final layout.
3. **Settled.** Clear temporary styles. CSS owns the page. Everything is interactive.
4. **Outro.** The outgoing route stays mounted while the router waits on the blocker, or before the navigation is issued. Stop competing component animations and play one outro timeline.
5. **End state.** Finalize outgoing targets and run completion once while still mounted. Call `proceed()` or `navigate`. The outgoing tree goes away when the incoming one commits.

A controller may track internal states like `waiting` or `preparing`, but they serve these five phases.

Store the phase in React state or a ref owned by the boundary and render it as a data attribute on the route container, so CSS and tests can read it.

## Outro before navigation: the blocker

There is no leave hook. `useBlocker` takes a boolean or `({ currentLocation, nextLocation, historyAction }) => boolean` and returns a blocker with `state` (`unblocked`, `blocked`, `proceeding`), `location`, `proceed()`, and `reset()`.

- The router checks the blocker before it touches history or runs a loader. While blocked the URL is unchanged, nothing has been fetched, and the old route is live and interactive. This is where the outro runs.
- `proceed()` moves the blocker to `proceeding` and re-issues the same navigation with the same options: `replace`, `state`, `preventScrollReset`, `viewTransition`, `mask`. The router skips the blocker function while `proceeding`, so no app-side guard is needed. Every blocker returns to `unblocked` when the navigation completes. From 8.2 a revalidation no longer clears a blocked state.
- The pattern: return true for every non-`POP` navigation whose destination is a different screen; an effect on `blocker.state === "blocked"` starts the outro toward `blocker.location`; the end callback calls `proceed()`. Call `reset()` for a destination the design rejects, such as the current pathname.
- A router supports one blocker. Registering a second logs a warning and the last one wins, and a blocker inside a route component is deleted when that route unmounts. Register it once in the boundary that outlives every navigation.
- Not covered: the initial document load, hard reloads, cross-origin URLs, `reloadDocument` links, and document unload. Those are `gsap-vanilla` territory or cannot be delayed at all. A redirect returned by a loader or action happens inside a navigation that already passed the blocker; treat its destination as unrequested.
- `POP` is blockable but costly. The router restores the URL at once with a reverse `history.go`, which flashes the destination in the address bar, and `proceed()` repeats the pop after that restore. A pop onto history the router did not create cannot be blocked at all. Return false for `historyAction === "POP"` and give back and forward the intro-only path.
- Two rapid clicks: the second navigation runs the blocker function again. If it blocks, the blocker retargets: `blocker.location` and `proceed` now belong to the second destination and the hook returns a new object, so the effect runs again. Decide which wins. Last click wins by letting the outro keep running and calling the current blocker's `proceed` at end state. First click wins by capturing `proceed` when the outro starts and calling that one. That capture is safe because each `proceed` closes over its own destination and options and re-issues that navigation whatever `blocker.location` says by then. Never start a second outro.
- Do not gate the blocker function on your own lock. Returning `false` while an outro runs looks like "one navigation at a time" but does the opposite: the router runs the function for the second click, `false` lets that navigation proceed under the running outro, and the second destination wins. Keep returning `true` for every requested navigation and enforce the lock by choosing which `proceed` to call.
- Type the function as `BlockerFunction` when wrapping it in `useCallback`, or its destructured parameters lose their contextual type and fail strict type checks.
- The cost of the blocker path: loaders run only after `proceed()`, so the end state sits on screen until the destination loads. Set `prefetch="intent"` on links in framework mode so data and modules are already cached, and cover the route container from end state until the incoming route is prepared. `useNavigation().state` is `loading` across the gap and `location.key` changes at commit.

A killed timeline never resolves its promise. Wrap `await` in a helper that also resolves on `onInterrupt` and returns whether the timeline completed, so an interrupted outro still reaches `proceed()` or `reset()`. A blocked navigation whose outro never finishes leaves the app stuck on the old page with the link apparently dead.

GSAP's ticker stops in a hidden tab. Race the outro against a timeout so a click from a background tab still navigates.

## Outro before navigation: the transition-aware Link

This works in every mode and is the only option in declarative mode. Wrap `<Link>` or `<NavLink>`, forward unrelated props, and pass an `onClick` that:

- Calls the caller's `onClick` first and stops if it prevented default.
- Leaves native the clicks the router itself leaves native: non-primary buttons, modifier keys, a `target` other than `_self`, external URLs, `reloadDocument`, and hash-only or same-location links.
- Calls `event.preventDefault()`, runs the outro on the live page, then calls `navigate(to, { replace, state, preventScrollReset, viewTransition, mask, relative })` with the Link's own props.

The `href`, prefetch handlers, `discover`, and `NavLink` state survive because the anchor is still React Router's. What is lost: the automatic `replace` when the URL is unchanged (compute it), `useTransitions` wrapping (call `navigate` inside `startTransition` and return its promise), and coverage: `<Form>`, `<Navigate>`, redirects, and `navigate` calls elsewhere bypass the wrapper. Add a navigate helper for buttons. If a blocker also exists, the re-issued `navigate` is a fresh navigation the blocker will see; gate the blocker function with a ref the helper sets before navigating and clears after.

A custom `<a>` built on `useLinkClickHandler` also works but drops prefetch, `discover`, and `NavLink` state. Use a document-level click listener only when replacing existing links is impractical; it is a retrofit, not the default.

The link path starts the outro on click and holds the URL like the blocker does, and has the same swap gap, since loaders run after the outro.

## One navigation at a time

- Hold a lock from the first accepted destination through outro, cover, and commit. With a blocker the router retargets on a second click; without one the wrapper must ignore or record later clicks itself.
- Release the lock when the incoming intro starts, not when it ends: a click during the intro must kill the intro and start the outro from current values, and holding the lock through the intro leaves every link dead until it finishes.
- A `POP` during an outro is not blocked. Kill the outro so its promise settles, drop the pending destination, and let the history navigation take the intro-only path.
- Repeated clicks must not create competing navigations or timelines.

## Two kinds of navigation

- **Requested** (a link the boundary intercepted, the navigate helper, a blocked `Link`, `Form`, or `navigate`): the full lifecycle. The outgoing page plays its outro on live DOM, the router loads, the incoming page prepares behind the cover and plays its intro.
- **Unrequested** (`POP`, redirects, `<Navigate>` and `navigate` calls that bypass the helper, a fetcher revalidation that replaces content): the tree changes without an outro. Run initial state and intro only, without travel. Keep the shell stable. Optionally give these a `viewTransition` crossfade so the swap is not a hard cut.

Do not keep a copy of the old React tree to fake an outro for unrequested navigation. Support fewer outro paths instead.

## Back and forward

- `useNavigationType()` reports `POP` after commit. A blocker function sees `historyAction === "POP"` before it. Neither runs an outro.
- `<ScrollRestoration>` restores the saved position in a layout effect at commit. A page's `useGSAP` layout effect runs in the same commit, so write initial state there but defer the step from `initial` to `intro` by a microtask; the intro then starts after restoration. Refresh ScrollTrigger at the same point, and reveal-on-scroll targets above the restored position must not stay hidden.
- If the pair of pathnames was navigated with `viewTransition`, the router remembers it in session storage and replays the transition on the pop with the roles reversed. Design the intro-only path to look right under that crossfade or morph.
- A route reached by back that was reused rather than remounted still holds settled values. Write initial state explicitly.
- A bfcache restore runs no router code except re-enabling manual scroll restoration. Leave the page readable whenever it can be unloaded.

## Overlapping the old and new page

The router renders one route tree. An effect that needs both on screen at once has two honest options:

- **The browser.** A `viewTransition` navigation snapshots both trees. `useViewTransitionState` or a class on the root gives the CSS the direction and the names.
- **A DOM snapshot.** After the outgoing page reaches end state and before `proceed()`, deep-clone the route container into a fixed layer: strip ids and every data attribute your lifecycle selects on, set `inert` and `aria-hidden`, position it at the container's document offset shifted by the scroll. Proceed with no cover. The incoming intro reveals the new page over the clone and removes it at settle, on a ready timeout, on `POP`, and at the start of any new navigation.

The clone is a static picture, not a React tree: nothing in it updates, nothing in it is reachable, and it is gone before the page is interactive.

## The swap gap and initial state

Between end state and the incoming intro, the old page sits at end state while loaders run and then unmounts as the new one commits. Cover the route container during that gap, inside the element that wraps route content and never fixed to the viewport, or the header and footer flash on every click. Uncover only after every incoming target has its size and start styles.

The initial state must occupy the same layout as the settled state. Prefer `autoAlpha` and transforms. Size images, media, masks, and async regions before the intro. If the effect changes geometry, reserve the settled size with a wrapper or measure both states before writing either.

The route container owns geometry during the swap: hold a stable height while trees exchange, or animate it between measured sizes on purpose; reserve scrollbar space if route height changes would shift it.

Server-rendered and prerendered HTML paints before hydration. Do not hide it unconditionally. If initial state must hide before first paint:

- Put an inline script first in `body` in the root route's `Layout` export, which wraps the app, `HydrateFallback`, and `ErrorBoundary` alike, that marks `html` as JavaScript-active. Add `suppressHydrationWarning` to `html`, since the server HTML does not carry the attribute.
- Add a CSS rule that hides intro targets only under that mark and only while the root is in its initial phase.
- Skip the mark under `prefers-reduced-motion` so the page paints settled.
- Give the same script a failsafe: if no controller has claimed the document within about a second, remove the mark, so a bundle that never arrives leaves a readable page. A controller that does arrive claims the document first. A page whose mark is already gone when its controller runs, from the failsafe or the reduced-motion skip, takes the instant path rather than hiding content that is already on screen.
- Have the boundary change the phase as its first act after hydration, before anything that can throw.
- Keep content readable without JavaScript. Omitting `<Scripts>` is React Router's no-JavaScript mode, and the page must still read there.
- Keep the swap cover separate from the first-paint rule.

`ssr: false`, data mode, and declarative mode without server rendering paint nothing before React. `useGSAP` runs in a layout effect on the client, so explicit `set` calls there land before the first paint and no pre-paint rule is needed. A `HydrateFallback` is a skeleton that appears only on the initial load; give it the settled geometry and let the route enter through the unrequested path when its data lands.

Do not rely only on inline styles: a context revert clears them during a swap. The cover must survive cleanup until the new tree is ready.

## Pending state, loaders, and streaming

- The router awaits loaders before rendering the next route, so during `loading` the outgoing page is mounted and interactive. Pending UI belongs there: a global indicator from `useNavigation().location`, or `isPending` on the `NavLink` that was clicked. Do not start the outro from `navigation.state`; by then the navigation is already committed to happen.
- A promise returned un-awaited from a loader streams. `<Await>` inside `<Suspense>`, or React 19 `use`, renders it when it lands, and after `streamTimeout` it rejects. Treat each streamed region as a component with its own controller: explicit initial state on arrival, a short intro, settled, cleanup. Reserve its block size so arrival moves nothing. Query outro targets when the outro is built, not at setup, so content that streamed in after setup leaves with the page.
- `clientLoader` runs in the browser on navigation and, with `hydrate`, on the initial load behind `HydrateFallback`. Neither changes the lifecycle; the route still commits once its data is ready.

## Settled state, focus, and scroll

On intro completion, mark settled once, clear temporary transforms, visibility, and `will-change`, and do not keep the page inside an active timeline to hold values.

- React Router moves no focus and announces nothing on a route change. If navigation left focus on `body`, move it to the route container or main heading after the intro, with `tabIndex={-1}` and a visible focus style. Do not steal focus from an active control. Add a live region if the product needs announcements.
- `<ScrollRestoration>` runs in a layout effect at commit: a saved position on `POP`, the hash target when there is one, nothing when `preventScrollReset` was set, otherwise the top. Submissions and revalidations leave scroll alone. It keys on `location.key` by default; `getKey` with `pathname` restores across repeat visits to the same path.
- Keep that behavior. Do not add a second scroll reset unless the product needs it. Refresh ScrollTrigger after restoration, and after the intro if anything above a trigger changed height.
- Pass `preventScrollReset` through the transition-aware Link and helper; `proceed()` already carries it.

## Combining with View Transitions

Set `viewTransition` on the Link, Form, or `navigate` call. `HydratedRouter` supports it; in data mode `RouterProvider` must come from `react-router/dom`, which wires `flushSync`, or `useViewTransitionState` throws. The router calls `document.startViewTransition` around the state update at commit and records the pathname pair so a later pop replays it. GSAP runs before it, outro on live DOM before `proceed()`, and after it, intro on the new tree once the transition finishes. Keep their jobs separate:

- One engine per element per transition. A named morph and a GSAP tween on the same node fight, and a GSAP end state becomes the old snapshot. Leave a shared element lit at end state or skip the view transition for that navigation.
- Name only elements that morph. `useViewTransitionState(to)` and the `NavLink` `isTransitioning` render prop are true only while that pair transitions, so use them to set `viewTransitionName` and clear it after.
- The router does not expose the `ViewTransition` object. `useViewTransitionState` returns to false when the transition finishes; start GSAP on elements the browser touched from an effect on that flip, or keep them out of the intro.
- A new navigation during a transition skips the active one and starts another. The GSAP lock must survive that.
- `proceed()` keeps `viewTransition`, so the blocker path and the browser path compose: GSAP outro, then proceed, then the browser morphs at commit.
- Add `::view-transition { pointer-events: none }` so a running transition does not swallow clicks.
- Where `startViewTransition` is missing the router updates plainly. Every GSAP path must run without it.
- Reduced motion covers both: zero view transition durations in CSS and take the GSAP reduced path.

## Cases to design for

- Navigation requested mid-intro.
- Two destinations clicked quickly, with the blocker retargeting.
- Back or forward with no outro, including mid-outro.
- A route reused with new params, and a search-param-only change.
- A `Form` GET, `<Navigate>`, or `navigate` call that bypasses the wrapper.
- A hash-only link, which is same-page.
- A redirect from a loader or action.
- An external link, a `reloadDocument` link, and a document unload.
- Split text or scroll plugins that changed the DOM before cleanup.
- Streamed data arriving after the intro.
- React development double-mounting the boundary.

Each case must end on one visible, interactive route with stable layout and no stale inline styles.

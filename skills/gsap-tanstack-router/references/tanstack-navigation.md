# TanStack navigation

Read this when changing route-level motion or navigation.

## Router APIs

Check the installed types before using these. Everything below comes from `@tanstack/react-router` unless noted, and describes the current 1.17x releases.

- `useBlocker({ shouldBlockFn, withResolver, disabled, enableBeforeUnload })`, marked experimental in the docs. `shouldBlockFn({ current, next, action })` returns `boolean | Promise<boolean>`; `true` blocks. `current` and `next` carry `routeId`, `fullPath`, `pathname`, `params`, and `search`. `action` is `PUSH`, `REPLACE`, `BACK`, `FORWARD`, or `GO`. With `withResolver: true` the hook returns `status` (`blocked` or `idle`), `current`, `next`, `action`, `proceed`, and `reset`; without it, the function's own return value decides. `disabled` removes the blocker. `enableBeforeUnload` defaults to `true` and also raises the browser's unload dialog on reload and tab close; set it `false` for a motion-only blocker. The older `blockerFn` and `condition` forms are deprecated. The hook re-registers whenever `shouldBlockFn` changes identity, so keep it stable and read live state through a ref.
- Blockers live in the history layer, one list for the whole router, run in order and awaited one at a time. For `PUSH` and `REPLACE` they run before the URL changes and before any loader starts. For back and forward the browser has already moved: the blocker runs from `popstate` with the new entry in the address bar, a block reverses the move with `history.go`, and an allow keeps it. `ignoreBlocker` on a Link or `navigate` skips every blocker.
- `Link` props: `to`, `params`, `search`, `hash`, `state`, `replace`, `resetScroll`, `hashScrollIntoView`, `viewTransition`, `startTransition`, `ignoreBlocker`, `reloadDocument`, `preload` (`false`, `'intent'`, `'viewport'`, `'render'`), `preloadDelay` (50 ms default), `activeProps`, `inactiveProps`, `activeOptions`, `disabled`, `target`. An active link renders `data-status="active"` and `aria-current="page"`. The router's click handler runs after your `onClick` and skips navigation when the event is `defaultPrevented`, carries a modifier key, is not the primary button, targets anything but `_self`, or the link is `disabled`. An external `href` renders a plain anchor with no router handling. `createLink` builds a typed Link around your own component.
- `useNavigate({ from })` returns `navigate(options)` taking `NavigateOptions`: `to`, `params`, `search`, `hash`, `state`, `replace`, `resetScroll`, `hashScrollIntoView`, `viewTransition`, `ignoreBlocker`, `reloadDocument`, `href`. It resolves after the destination has rendered, and never if a blocker cancels it, so do not await it for a navigation that may be blocked. `router.navigate` is the same outside components; `Route.useNavigate` presets `from`. `href` to another origin or `reloadDocument` performs a document navigation; blockers still run for it, with `next` equal to `current`.
- `useRouterState({ select })`: `status` (`pending` or `idle`), `isLoading` (true while pending), `location`, `resolvedLocation`, `matches`. `isTransitioning` existed through router-core 1.171.1x and is gone from current releases; check the installed `RouterState`. Always select a slice.
- `useLocation({ select })` follows `state.location`, which moves to the destination when loading starts while the old page is still on screen. `resolvedLocation` moves after the new page has rendered.
- `useMatches`, `useMatch({ from, select })`, `useParams`, `useSearch`, `Route.useLoaderData`: the presented matches, updated in the commit that mounts the new page. `useMatchRoute()({ to, pending: true })` and `<MatchRoute pending>` say whether a destination is the one currently loading.
- `router.subscribe(event, fn)` returns an unsubscribe. Events: `onBeforeNavigate`, `onBeforeLoad`, `onLoad`, `onBeforeRouteMount`, `onResolved`, `onRendered`, each with `fromLocation` (undefined on the first load), `toLocation`, `pathChanged`, `hrefChanged`, and `hashChanged`.
- `router.history.subscribe(({ location, action }) => ...)` fires on every history change with `action.type` `PUSH`, `REPLACE`, `BACK`, `FORWARD`, or `GO`. `useCanGoBack()` reads the history index; `router.history.back()` goes back.
- `location.state.__TSR_index` is the history index and `__TSR_key` the entry key; the router's own view-transition example derives direction from the index. Both are internal fields on a public type; prefer the history action.
- Route options that shape timing: `pendingComponent`, `pendingMs` (default 1000), `pendingMinMs` (default 500), `staleTime` (default 0), `preloadStaleTime` (30 s), `loaderDeps`, `shouldReload`, `remountDeps`, `ssr`. Router-level defaults carry the `default` prefix. `onEnter`, `onStay`, and `onLeave` receive the match during commit; they are data callbacks, not DOM hooks.

## Order of one navigation

Read from the client runtime. Confirm against the installed version when timing matters.

1. A Link click or `navigate` builds the location. Blockers run, each awaited. A `true` stops here; nothing has changed. A preload that started on hover keeps running.
2. History push or replace. The URL changes. `history.subscribe` listeners run with the action; the router's own subscription calls `load`.
3. `onBeforeNavigate`, then `onBeforeLoad`. The outgoing page's scroll positions are snapshotted here.
4. `status` becomes `pending` and `location` moves to the destination. The old matches are still presented; the old page stays mounted and interactive.
5. `beforeLoad` and loaders run, reusing a fresh preload or joining one in flight. Past `pendingMs`, the pending component is presented in place of the pending route inside a React transition and held at least `pendingMinMs`.
6. If a view transition applies, `document.startViewTransition` wraps the next two steps.
7. Inside `React.startTransition`: the matches commit, `onLoad`, then `onBeforeRouteMount`. React renders the new tree. Reused components receive new params and loader data; new ones mount and run their layout effects, including `useGSAP`.
8. After the new tree has committed: `resolvedLocation` is set, `status` returns to `idle`, `onResolved`, then `onRendered`. Scroll restoration, the top reset, and hash scrolling run in `onRendered`. The `navigate` promise resolves.

A newer navigation abandons an older one at every await, and the abandoned one emits nothing further. Nothing in this list precedes the URL change except the blocker, which is why the outro lives there.

`onRendered` runs from a microtask after the root layout effect, so it sees the committed DOM, normally before paint. A page's `useGSAP` runs before it, and before scroll restoration.

First load differs: a client-only app runs a full load, so every event fires with `fromLocation` undefined; after TanStack Start hydration the router acknowledges the server-rendered matches and emits only `onRendered`, with nothing changed. In both cases the page's first `useGSAP` is the mount.

## Page lifecycle

**mount → initial state → intro → settled → outro → end state → unmount**

1. **Initial state.** The incoming page has mounted or updated in place, its final size is reserved, measurements are taken, and start values are set before anything is shown.
2. **Intro.** Reveal the route and play one timeline to the final layout.
3. **Settled.** Clear temporary styles. CSS owns the page. Everything is interactive.
4. **Outro.** The outgoing page stays mounted while the blocker holds the navigation. Stop competing component animations and play one outro timeline.
5. **End state.** Finalize outgoing targets and run completion once while still mounted. Let the navigation proceed. The outgoing tree goes away when the router commits the loaded destination.

A controller may track internal states like `waiting` or `preparing`, but they serve these five phases.

Store the phase in a ref owned by the root controller and mirror it as a data attribute on the route container, so CSS and tests can read it.

## Outro before navigation: two paths

Both run on the old page. Pick one per project and use it everywhere.

**`useBlocker`, the default.** Mount it once in the root controller. `shouldBlockFn` returns `false` for `BACK`, `FORWARD`, and `GO`, for hash-only and same-location changes, and for anything the design does not transition. Otherwise it returns a promise that the outro's end callback resolves with `false`, which allows the navigation. Never return `false` because an outro or swap is already in progress: that lets the second push commit at once, the outgoing page unmounts mid-outro, its context revert kills the timeline, `onComplete` never fires, and the first promise hangs forever. A navigation that arrives during an outro is blocked too, and the lock decides which promise resolves with `true`. See [One navigation at a time](#one-navigation-at-a-time). Nothing is cancelled or re-issued: the original push continues, so `replace`, `resetScroll`, `viewTransition`, and the Link's intent survive, no blocker re-enters, and `navigate` calls and redirects get the same outro as links. The costs: the URL waits, and so do the loaders, so the end state sits on screen until the destination loads unless `preload="intent"` or `defaultPreload: 'intent'` already started the fetch on hover. Turn intent preloading on when using this path; the navigation reuses the preload or joins the loader still in flight. Set `enableBeforeUnload: false` unless the app also wants the unload dialog.

`withResolver: true` is the docs' form for rendering a prompt. In a controller it has a trap: one resolver is shared by every navigation, and resolving any of them resets `status` to `idle`, so a second click during an outro replaces `proceed` and strands the first navigation. If you use it, capture `proceed` and `reset` in a ref the moment `status` turns `blocked` and keep them past the state change. The promise-returning `shouldBlockFn` gives each navigation its own promise and needs no React state; prefer it.

**An intercepted Link, the alternative.** Wrap `Link` with an `onClick` that applies the router's own exclusions (modifier keys, non-primary button, `target`, `disabled`, external href), calls `preventDefault`, plays the outro, then calls `navigate` with the same `to`, `params`, `search`, `hash`, `state`, `replace`, `resetScroll`, `hashScrollIntoView`, and `viewTransition`. Because the `Link` still renders, `href`, `preload`, `activeProps`, and `data-status` survive. The costs: buttons, `navigate` calls, redirects, and forms bypass it; every option must be forwarded by hand; and if a `useBlocker` also exists, the re-issued push hits it, so pass `ignoreBlocker: true` or set a guard first. Use it only when a blocker cannot be mounted where the outro is decided.

Neither path delays a document unload. `reloadDocument`, external hrefs, and the close button get at most the browser's unload dialog. A hash-only change goes through the same push; return `false` when `next.pathname` equals `current.pathname`.

## One navigation at a time

- Keep the pending navigation's resolver in a ref. When a second navigation is blocked during outro or preparing, decide once: resolve the earlier promise with `true` to cancel it and adopt the new destination, or resolve the new one with `true` and keep the first. Never leave a promise pending; a pending blocker holds its navigation forever.
- Release the lock when the incoming intro starts, not when it ends: a click during the intro must kill the intro and start the outro from current values, and holding the lock through the intro leaves every link dead until it finishes.
- Back or forward during an outro: return `false` at once, kill the outro, resolve its pending promise with `true` so the requested push never commits over the history move, and take the intro-only path.
- A killed timeline never resolves its promise. Wrap `await` in a helper that also resolves on `onInterrupt` and returns whether the timeline completed, so an interrupted outro never leaves a blocker pending.
- GSAP's ticker stops in a hidden tab. Race the outro against a timeout so a click from a background tab still navigates.
- React development runs the controller's effects twice, so the blocker registers, unregisters, and registers again. Keep the phase and resolver in refs so the second run sees the first's state.

## Two kinds of navigation

- **Requested** (`PUSH` and `REPLACE` from a Link, `navigate`, or a submit handler): the full lifecycle. The blocker holds, the outgoing page plays its outro on live DOM, the router loads and commits, the incoming page prepares and plays its intro.
- **Unrequested** (`BACK`, `FORWARD`, `GO`, a redirect thrown from `beforeLoad` or a loader, `router.invalidate`, `reloadDocument`, external links): the tree changes without an outro, or the document reloads. Run initial state and intro only, without travel. Keep the shell stable. Optionally give these a `viewTransition` crossfade so the swap is not a hard cut.

A redirect during a requested navigation pushes again and reaches the blocker; the in-progress guard above returns `false` for it. Do not keep a copy of the old React tree to fake an outro for unrequested navigation. The outgoing route unmounts on commit, so a copy is stale immediately. Support fewer outro paths instead.

## Back and forward

- Detect them from `action` in `shouldBlockFn` and from `router.history.subscribe`, which fires before any router event because the history change is what starts the load. Record the action in a ref there and read it when the incoming page reports ready.
- Never run an outro. The URL has already changed when the blocker runs; blocking reverses history and the user sees a bounce.
- Scroll restoration runs in `onRendered`, after the page's `useGSAP`. Start history intros from `onRendered` or later, then refresh ScrollTrigger. Reveal-on-scroll targets above the restored position must not stay hidden.
- A page reached by back that stayed matched with different params is reused, not remounted, and holds settled values. Write initial state explicitly.
- Leaving the site and coming back may restore the document from the bfcache. No router event runs; `pagehide` only saves scroll. Leave the page readable whenever the document may unload.

## Pending UI and the loading gap

The router waits for loaders before it swaps, so the old page stays presented and `status` is `pending`. After `pendingMs` it presents `pendingComponent` in place of the pending route, parent layouts included, for at least `pendingMinMs`. Without a pending component the old page stays until the data arrives.

- With the blocker path the outro has already finished, so the end state, or the cover, is what the user sees during the wait. Intent preloading shortens it.
- A pending component mounts inside the route container. Give it the same geometry, treat it as unrequested content with no intro handoff, and let the boundary's ready timeout release the cover. The real page then mounts through the normal path.
- For a pending hint in chrome, select `status` from `useRouterState` or use `useMatchRoute` with `pending: true` on the link's destination. There is no per-link status hook.
- Data returned from a loader as an unawaited promise streams: `<Await promise fallback>` or React 19 `use()` suspends the nearest boundary. Treat each such region as a component with its own controller. See [Deferred data](route-lifetime.md#deferred-data-and-streaming).

## Overlapping the old and new page

The router shows one route tree. An effect that needs both pages on screen at once has two honest options:

- **The browser.** `viewTransition` snapshots both trees itself. Types give the CSS the direction and the clip.
- **A DOM snapshot.** After the outgoing page reaches end state and before resolving the blocker, deep-clone the route container into a fixed layer: strip ids and every data attribute your lifecycle selects on, set `inert` and `aria-hidden`, position it at the container's document offset shifted by the scroll. Let the navigation proceed with no cover. The incoming intro reveals the new page over the clone and removes it at settle, on a ready timeout, on back or forward mid-transition, and at the start of any new navigation.

The clone is a static picture, not a React tree: nothing in it updates, and it is gone before the page is interactive. Skip the outgoing outro for this archetype; a faded end state gives the reveal nothing to sit on.

## The swap gap and initial state

With the blocker path the old page sits at end state while the loaders run and React commits. Cover the route container during that gap, inside the element that wraps route content and never fixed to the viewport, or the header and footer flash on every click. Uncover only after every incoming target has its size and start styles.

The initial state must occupy the same layout as the settled state. Prefer `autoAlpha` and transforms. Size images, media, masks, and async regions before the intro. If the effect changes geometry, reserve the settled size with a wrapper or measure both states before writing either.

The route container owns geometry during the swap: hold a stable height while trees exchange, or animate it between measured sizes on purpose; if old and new are both mounted, overlap them so only one takes up space; reserve scrollbar space if route height changes would shift it.

Under TanStack Start, server HTML paints before hydration. Do not hide it unconditionally; the pre-paint rule in [SSR and hydration](route-lifetime.md#ssr-and-hydration-with-tanstack-start) is the only sanctioned way to hide before the first intro. A client-only app paints nothing before React and needs no such rule.

Do not rely only on inline styles: a context revert clears them during a swap. The cover must survive cleanup until the new tree is ready.

## Settled state, focus, and scroll

On intro completion, mark settled once, clear temporary transforms, visibility, and `will-change`, and do not keep the page inside an active timeline to hold values.

- TanStack Router moves no focus. After a client navigation focus stays wherever it was, usually on a link that has unmounted, which drops it to `body`. Move focus to the route container or main heading from the intro's completion when the design needs it, with `tabIndex={-1}` and a visible focus style. Do not steal focus from an active control.
- Keep the router's scroll behavior. `scrollRestoration: true` restores per history entry and resets new entries to the top, both in `onRendered` before paint; the `<ScrollRestoration />` component is deprecated. `resetScroll: false` on a Link or `navigate` keeps the current position. `scrollToTopSelectors` adds nested scrollers; `scrollRestorationBehavior: 'instant'` stops a smooth scroll from running under an intro; `getScrollRestorationKey` keys by pathname instead of history entry. Without `scrollRestoration` the router still scrolls to the top and to the hash.
- Refresh ScrollTrigger after `onRendered`, and after the intro if anything above a trigger changed height.
- The router announces nothing. `head()` updates the title through `HeadContent`; add your own live region if the product needs navigation announced.

## Combining with View Transitions

`defaultViewTransition: true` or `{ types }` on the router, or `viewTransition` on a Link or `navigate`, wraps the match commit and React render in `document.startViewTransition`. `types` is an array or a function of the location change info that returns an array or `false` to skip; typed transitions need `:active-view-transition-type` support and otherwise run untyped. GSAP runs before it, outro on live DOM held by the blocker, and after it, intro on the new tree. Keep their jobs separate:

- The router awaits `updateCallbackDone`, not `finished`. `onResolved`, `onRendered`, and the `navigate` promise fire while the browser animation may still be running.
- The router does not expose the `ViewTransition` object. Either keep GSAP off the elements the transition animates so the intro can start at mount, or install a thin wrapper around `document.startViewTransition` in the client entry that remembers the active transition, and await its `finished` before the intro.
- One engine per element per transition. A named morph and a GSAP tween on the same node fight, and a GSAP end state becomes the old snapshot. If the outro fades content the browser will morph, leave the shared element lit at end state or skip the view transition for that navigation.
- Name only elements that morph, per page, and clear names after each transition. Name chrome to hold it still.
- Compute direction once, from the recorded history action or from `fromLocation.state.__TSR_index` against `toLocation.state.__TSR_index` as the router's example does, return it as a type, and read the same decision in the GSAP builders.
- Add `::view-transition { pointer-events: none }` so a running transition does not swallow clicks.
- Feature-detect `document.startViewTransition`. Every GSAP path must run when it is missing.
- Reduced motion covers both: zero view transition durations in CSS, return `false` from `types` under the media query, and take the GSAP reduced path.

## Cases to design for

- Navigation requested mid-intro.
- Two destinations clicked quickly.
- Back or forward with no outro, including mid-outro.
- A page reused with new params, and a search-param-only change.
- A `navigate` call or redirect that bypasses any Link wrapper.
- A hash-only link.
- A slow loader that shows the pending component.
- An external link and a `reloadDocument` link, which unload the document.
- Split text or scroll plugins that changed the DOM before cleanup.
- Streamed data arriving after the intro.
- React development double-running the controller's effects.

Each case must end on one visible, interactive page with stable layout and no stale inline styles.

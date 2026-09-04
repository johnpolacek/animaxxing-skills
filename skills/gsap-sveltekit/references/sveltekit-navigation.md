# SvelteKit navigation

Read this when changing route-level motion or navigation.

## Router APIs

Check the installed SvelteKit types before using these. Everything below comes from `$app/navigation` unless noted. The hooks must be called during component initialization and stay active while that component is mounted.

- `beforeNavigate(cb)`: fires before every navigation the router sees: link clicks, `goto`, GET forms, back and forward, and leaving the document. Receives `type`, `from`, `to`, `willUnload`, `delta` (popstate only), `complete`, and `cancel()`. Not called for a redirect issued while a navigation is already in flight.
- `onNavigate(cb)`: fires immediately before the new page renders, only for client-side navigation. Return a promise and SvelteKit waits for it before updating the DOM. Return a function, or a promise resolving to one, and it runs once after the DOM has updated.
- `afterNavigate(cb)`: fires after every navigation while the calling component stays mounted, and once with `type: 'enter'` after hydration. That first call is dispatched from the router's initialization one microtask after the root mounts, so whether a page component has registered by then is a race; the intro path must also work when the page mounts after the `enter` call has passed. `to.scroll` is the position actually applied.
- `goto(url, { replaceState, noScroll, keepFocus, invalidateAll, invalidate, state })`: programmatic navigation. Resolves when the navigation completes and rejects when it is cancelled or aborted. Not for external URLs; assign `location` instead.
- `preloadData(href)`: imports the destination's code and runs its `load` now. If the next navigation goes there, the result is reused.
- `disableScrollHandling()`: skips the router's scroll for the navigation in progress. Legal only while the page is updating.
- `pushState` and `replaceState`: history entries without navigation, for shallow routing.
- `navigating` from `$app/state`: `from`, `to`, `type`, and `delta` while a navigation is in flight, `null` otherwise. `page` from `$app/state`: current `url`, `route`, `params`, and `state`. Both are reactive only in runes mode.
- Link attributes: `data-sveltekit-preload-data`, `data-sveltekit-preload-code`, `data-sveltekit-noscroll`, `data-sveltekit-replacestate`, `data-sveltekit-keepfocus`, `data-sveltekit-reload`. They apply to an `a` or any ancestor, and to GET forms.

`type` values: `link`, `goto` (also redirects), `form` (GET forms), `popstate` (back and forward), `enter` (hydration, `afterNavigate` only), `leave` (document unload, `beforeNavigate` only).

The navigation object carries an undocumented `event`. Do not build on it.

## Order of one navigation

Read from the client runtime. Confirm against the installed version when timing matters.

1. `beforeNavigate` callbacks. Any `cancel()` stops here. Cancelling a `popstate` also moves history back by `delta`.
2. `navigating` is set. `load` functions run, reusing a matching preload.
3. The outgoing page's snapshot is captured. History is pushed or replaced, so the URL bar already shows the destination.
4. `onNavigate` callbacks, awaited together. The old page is still mounted and live, and `page` still reports the old URL.
5. Focus is blurred, the component tree updates, and Svelte flushes. Reused components receive new props; new ones mount and run `onMount` and `$effect`.
6. Scroll: restored for `popstate`, kept for `noScroll`, moved to a hash target, otherwise top. Skipped after `disableScrollHandling()`.
7. Focus is reset to `body`, or an `autofocus` element, unless `keepFocus` was set or something already moved it.
8. `complete` resolves, `afterNavigate` callbacks and the functions returned from `onNavigate` run, the snapshot is restored for `popstate`, and `navigating` returns to `null`.

The router checks for a newer navigation after step 2 and after step 5 and abandons the older one there, rejecting its `complete`. It does not check between steps 4 and 5, so an older `onNavigate` that resolves late still updates the DOM once before it is abandoned. The lock below exists for this.

## Page lifecycle

**mount → initial state → intro → settled → outro → end state → unmount**

1. **Initial state.** The incoming page has mounted or updated in place, its final size is reserved, measurements are taken, and start values are set before anything is shown.
2. **Intro.** Reveal the route and play one timeline to the final layout.
3. **Settled.** Clear temporary styles. CSS owns the page. Everything is interactive.
4. **Outro.** The outgoing page stays mounted while the router waits. Stop competing component animations and play one outro timeline.
5. **End state.** Finalize outgoing targets and run completion once while still mounted. Resolve the router's wait. The outgoing tree goes away as the incoming one renders.

A controller may track internal states like `waiting` or `preparing`, but they serve these five phases.

Store the phase in `$state` owned by the layout controller and render it as a data attribute on the route container, so CSS and tests can read it. Svelte batches state, so two phase writes in one tick reach the DOM as one attribute change and an observer sees only the last; `await tick()` between them, or write the attribute on the container directly when consecutive phases must each be visible.

## Outro before navigation: two hooks

Both run on the old page. Pick one per project and use it everywhere. The choice turns on one fact: `history.pushState` runs before the router awaits `onNavigate`, so on that path the address bar already shows the destination while the old page animates. If the outro must play with the URL unchanged, which is what "outro before navigation" usually means, only `beforeNavigate` does it.

**`beforeNavigate`, the default.** Call `cancel()`, play the outro on the untouched page, then `goto(to.url)` from the end callback. The outro starts on click and the URL waits. The costs: the re-issued navigation re-enters `beforeNavigate`, so set a guard before `goto` and consume it inside the callback that sees the re-issued navigation, not on the `goto` promise, which resolves too late and leaves a window where the next real click passes unblocked; the re-issued navigation is `type: 'goto'` and drops the link's `replaceState`, `noScroll`, and `keepFocus` intent unless the controller reads those attributes from the link itself; a GET form cannot be re-issued cleanly; and `load` runs after the outro, so the end state sits on screen until the new page arrives and needs a cover or a presentable look. Call `preloadData(to.url.href)` when the outro starts so the fetch overlaps it. Never cancel `popstate`.

**`onNavigate`, the alternative.** Return the outro's promise; SvelteKit renders the new page when it resolves. Nothing is cancelled or re-issued, so `data-sveltekit-*` options, `goto` options, GET forms, and `type` survive, `afterNavigate` reports what really happened, and there is no swap gap: `load` has already finished, so the new page renders the moment the outro ends and no cover is needed. The costs: the URL changes before the outro, and the outro starts after `load`, not on click, so a slow route shows a still page first. Mitigate the second with `data-sveltekit-preload-data="hover"`, the template default, and a pending style from `navigating`. Return nothing for `popstate`. Use it when a URL that leads the animation is acceptable.

Neither hook delays a `willUnload` navigation. `type: 'leave'` cannot be delayed; `cancel()` there only raises the browser's unload dialog. An external link, where `to.route.id` is `null`, can be cancelled in `beforeNavigate`, outroed, and followed with `location.assign`, which is the `gsap-vanilla` path.

## One navigation at a time

The lock depends on the path.

- On the `beforeNavigate` path the first click cancelled its navigation, so the router is idle during the outro and `beforeNavigate` fires again for a second click. While the phase is `outro` or the incoming page is preparing, `cancel()` `link`, `goto`, and `form` navigations, or record the destination and `goto` it from the end callback if the design retargets.
- On the `onNavigate` path there is no lock to hold. The router runs `beforeNavigate` callbacks only while it is idle, and it is busy from the moment it accepted the first click until just before `afterNavigate`, so a second click never reaches them. It starts a newer navigation that supersedes the first; the router abandons the old one at its next check. Kill the outro so its promise settles and let the newer navigation own the page.
- Do not cancel `popstate`. Kill the running outro so its promise resolves at once and the pending navigation commits before the history navigation renders.
- Release the lock when the incoming intro starts, not when it ends: a click during the intro must kill the intro and start the outro from current values, and holding the lock through the intro leaves every link dead until it finishes.

A killed timeline never resolves its promise. Wrap `await` in a helper that also resolves on `onInterrupt` and returns whether the timeline completed, so an interrupted outro never leaves `onNavigate` pending.

GSAP's ticker stops in a hidden tab. Race the outro against a timeout so a click from a background tab still navigates.

## Two kinds of navigation

- **Requested** (`link`, `goto`, `form`): the full lifecycle. The outgoing page plays its outro on live DOM, the router waits, the incoming page prepares and plays its intro.
- **Unrequested** (`popstate`, redirects from `load`, `invalidateAll` re-renders, links marked `data-sveltekit-reload`): the tree changes without an outro, or the document reloads. Run initial state and intro only, without travel. Keep the shell stable. Optionally wrap the swap in `document.startViewTransition` from `onNavigate` so it is not a hard cut.

Do not keep a copy of the old page to fake an outro for unrequested navigation. Support fewer outro paths instead.

## Back and forward

`popstate` goes through `beforeNavigate`, `onNavigate`, and `afterNavigate` like any navigation, with `delta` and, before the DOM updates, `to.scroll` holding the position that will be restored.

- Never run an outro. Return nothing from `onNavigate`.
- The router restores scroll before `afterNavigate`. Start the intro from `afterNavigate`, then refresh ScrollTrigger. Reveal-on-scroll targets above the restored position must not stay hidden.
- Snapshots are restored after `afterNavigate`. Do not put the phase in a snapshot.
- A page reached by back that was reused rather than remounted still holds settled values. Write initial state explicitly.
- Leaving the site and coming back may restore the document from the bfcache. SvelteKit only clears `navigating` on `pageshow`; no hook runs. Leave the page readable whenever `willUnload` is true.

## Overlapping the old and new page

The router shows one page tree. An effect that needs both on screen at once has three honest options.

- **The browser.** `document.startViewTransition` in `onNavigate` snapshots both. A class on `html` gives the CSS the direction.
- **A Svelte `out:` directive** on the page root, or on a `{#key}` wrapper in the layout. Svelte inserts the new page at once and keeps the old one until its outro ends, both in normal flow, so stack them with a grid or position the outgoing one absolutely inside the route container, and keep GSAP off the node that carries the directive. See [Combining engines](page-lifetime.md#combining-engines).
- **A DOM snapshot.** After the outgoing page reaches end state and before resolving `onNavigate`, deep-clone the route container into a fixed layer: strip ids and every data attribute your lifecycle selects on, set `inert` and `aria-hidden`, position it at the container's document offset shifted by the scroll. The incoming intro reveals the new page over the clone and removes it at settle, on a ready timeout, on `popstate`, and at the start of any new navigation.

The clone is a static picture, not a component: nothing in it updates, and it is gone before the page is interactive.

## The swap gap and initial state

With `onNavigate` there is no gap: the new page renders as soon as the promise resolves. With `beforeNavigate` the old page sits at end state while `load` runs. Cover the route container during that gap, inside the element that wraps route content and never fixed to the viewport, or the header and footer flash on every click. Uncover only after every incoming target has its size and start styles.

The initial state must occupy the same layout as the settled state. Prefer `autoAlpha` and transforms. Size images, media, masks, and async regions before the intro. If the effect changes geometry, reserve the settled size with a wrapper or measure both states before writing either.

The route container owns geometry during the swap: hold a stable height while trees exchange, or animate it between measured sizes on purpose; if old and new are both mounted, overlap them so only one takes up space; reserve scrollbar space if route height changes would shift it.

Server-rendered HTML paints before hydration. Do not hide it unconditionally. If initial state must hide before first paint:

- Put an inline script first in `body` in `src/app.html` that marks `html` as JavaScript-active, and a CSS rule that hides intro targets only under that mark and only while the root is in its initial phase.
- Skip the mark under `prefers-reduced-motion` so the page paints settled.
- Give the same script a failsafe: if no controller has claimed the document within about a second, remove the mark, so a bundle that never arrives leaves a readable page. A controller that does arrive claims the document first. A page whose mark is already gone when its controller runs, from the failsafe or the reduced-motion skip, takes the instant path rather than hiding content that is already on screen.
- Have the controller change the phase as its first act after hydration, before anything that can throw.
- Keep content readable without JavaScript and keep the swap cover separate from the first-paint rule.

Do not rely only on inline styles: a context revert clears them during a swap. The cover must survive cleanup until the new tree is ready.

## Preloading and streaming

- Hover and tap preloading run `load` before the click. With `onNavigate` this is what lets the outro start promptly. With `beforeNavigate`, `preloadData` at outro start does the same.
- Preloaded data is dropped by invalidation or by a navigation elsewhere. Do not assume it survives a long outro.
- Promises streamed from `load` resolve after the page renders. Treat each streamed region as a component with its own controller: explicit initial state on arrival, a short intro, settled, cleanup. Reserve its block size so arrival moves nothing. Query outro targets when the outro is built, not at setup, so content that streamed in after setup leaves with the page.

## Settled state, focus, and scroll

On intro completion, mark settled once, clear temporary transforms, visibility, and `will-change`, and do not keep the page inside an active timeline to hold values.

- SvelteKit focuses `body`, or an `autofocus` element, before `afterNavigate`. Move focus to the main heading from `afterNavigate` only when the design needs it, with `tabindex="-1"` and a visible focus style. Do not steal focus from an active control.
- Keep the router's scroll behavior. Call `disableScrollHandling()` only while the page is updating, from the incoming page's `onMount` or an effect, then own the scroll yourself. In the current runtime `afterNavigate` runs after the scroll has been applied; check the installed version before calling it there.
- Refresh ScrollTrigger after scroll restoration, and after the intro if anything above a trigger changed height.
- SvelteKit's live region announces the new `title`. Give every page a title in `svelte:head` so an animated navigation is still announced.

## Combining with View Transitions

The documented recipe wraps the update: `onNavigate` returns a promise that `document.startViewTransition`'s callback resolves, and the callback then awaits `navigation.complete`, so the old snapshot is taken before the DOM updates and the new one after. GSAP runs before it, outro on live DOM awaited before the transition starts, and after it, intro on the new tree after `finished` for elements the transition touched. Keep their jobs separate:

- One engine per element per transition. A named morph and a GSAP tween on the same node fight, and a GSAP end state becomes the old snapshot.
- If the outro fades content the browser will morph, leave the shared element lit at end state or skip the view transition for that navigation.
- Name only elements that morph, per page, and clear names after each transition. Name chrome to hold it still.
- Set a direction class on `html` before starting the transition and remove it in `finished`. Read the same decision in the GSAP builders.
- Add `::view-transition { pointer-events: none }` so a running transition does not swallow clicks.
- Feature-detect `document.startViewTransition`. Every GSAP path must run when it is missing.
- Reduced motion covers both: zero view transition durations in CSS and take the GSAP reduced path.

## Cases to design for

- Navigation requested mid-intro.
- Two destinations clicked quickly.
- Back or forward with no outro, including mid-outro.
- A page reused with new params, and a search-param-only change.
- Programmatic `goto` and a GET form that bypass any link wrapper.
- A hash-only link, which the router leaves to the browser.
- A redirect from `load`, which skips `beforeNavigate`.
- An external link and a `data-sveltekit-reload` link, which unload the document.
- Split text or scroll plugins that changed the DOM before cleanup.
- Streamed data arriving after the intro.

Each case must end on one visible, interactive page with stable layout and no stale inline styles.

# App Router navigation

Read this when changing route-level motion or navigation.

## Router APIs

Check the installed Next.js docs before using these. Versions in parentheses.

- `<Link onNavigate={(e) => ...}>` (15.3). Fires only for same-origin client navigation, not for modified clicks, external URLs, `download`, or new tabs. `e.preventDefault()` cancels it. This is where an outro-before-navigation starts.
- `useLinkStatus()` (15.3), inside a Link. `pending` is true from click until the URL updates. Useful for a hint while a non-prefetched route loads.
- `router.push(href, { scroll, transitionTypes })` and `router.replace(...)` from `next/navigation`. Pass the Link's `replace` and `scroll` intent through after the outro.
- `<Link transitionTypes>` (16.2) and React `<ViewTransition>`, active on every navigation. See [Combining with View Transitions](#combining-with-view-transitions).
- `router.bfcacheId` (16, with `cacheComponents`). New on push or replace, same on back and forward. Use it as a key to reset a subtree on new navigation but keep it on history navigation.

Keep `next/link` for all links so prefetching still works. Wrap it in a project-local transition-aware Link that uses `onNavigate` to run the outro, cancel that one navigation, and push after the end state. Add a helper for buttons and other programmatic navigation. This works as expected on 16.3 with `cacheComponents` on: the outro plays on the live page, the push commits, the old route is hidden, and the new page mounts.

Raise the cover, wait one frame so it paints, then push. Do not wait on `requestAnimationFrame` alone: it never fires in a hidden tab, and neither does GSAP's ticker, so race the frame against a short timeout and expect timelines to stall until the tab is visible.

Use a document-level click listener only when replacing existing links is impractical. It is a retrofit, not the default.

## Page lifecycle

**mount → initial state → intro → settled → outro → end state → unmount**

1. **Initial state.** The incoming route mounts, its final size is reserved, measurements are taken, and start values are set before anything is shown.
2. **Intro.** Reveal the route and play one timeline to the final layout.
3. **Settled.** Clear temporary styles. CSS owns the page. Everything is interactive.
4. **Outro.** The outgoing route stays mounted. Stop competing component animations and play one outro timeline.
5. **End state.** Finalize outgoing targets and run completion once while still mounted. Commit the navigation if it was intercepted. The outgoing tree goes away only once the incoming tree is ready behind the cover.

A controller may track internal states like `waiting` or `preparing`, but they serve these five phases.

One navigation at a time. The first accepted destination wins through outro, cover, and push. Release the lock when the incoming intro starts, not when it ends: a click during the intro must kill it and start the outro from current values, and holding the lock through the intro leaves every link dead until it finishes. Repeated clicks must not create competing pushes or timelines.

A killed timeline never resolves its promise. Wrap `await` in a helper that also resolves on `onInterrupt`, returning whether the timeline completed, so an interrupted navigation does not strand its async frame.

## Two kinds of navigation

Not every route change can run an outro.

- **Requested** (transition-aware Link, navigate helper): the full lifecycle. `onNavigate` cancels the navigation, the outgoing page plays its outro on live DOM, the controller pushes, and the incoming page prepares behind the cover.
- **Unrequested** (browser back and forward, links that bypass the helper, `router.refresh`, redirects): the tree has already changed when the app hears about it. Run initial state and intro only. Keep the shell stable. Optionally wrap route content in a `<ViewTransition>` crossfade so the swap is not a hard cut.

Do not keep a copy of the old React tree to fake an outro for unrequested navigation. With `cacheComponents` the router already keeps the old tree hidden, so a copy renders twice. Without it, a copy goes stale during streaming and refreshes. Support fewer outro paths instead.

## Overlapping the old and new page

The router shows one route tree. An effect that needs both pages on screen at once, such as a mask reveal of the new page over the old one, has two honest options:

- **The browser.** A `<ViewTransition>` snapshots both trees itself. Keyed `enter` and `exit` classes give the clip-path and the scale-down in CSS. React joins the classes of every matching type, so when a navigation carries several types the CSS order decides.
- **A DOM snapshot.** After the outgoing page reaches its end state and before the push, deep-clone its route container into a fixed layer: strip ids and every data attribute your lifecycle or plugins select on, set `inert` and `aria-hidden`, position it at the route's document offset with the clone shifted by the scroll so it lines up with what was on screen. Push with no cover. The incoming intro lifts the route container above the layer, reveals it, and tweens the clone from the page's own context. The boundary removes the clone at settle, on the ready timeout, on back or forward mid-transition, and at the start of any new navigation.

The clone is a static picture, not a React tree, which is what keeps it honest: nothing in it updates, nothing in it is reachable, and it is gone before the page is interactive. Skip the outgoing outro for this archetype; a faded end state gives the reveal nothing to sit on.

## Route lifetime under cacheComponents

With `cacheComponents` on, Next.js does not unmount the outgoing route. It hides it inside React `<Activity>`: the DOM stays with `display: none`, React state survives, and effect cleanups run as if unmounting. On back or forward the route shows again and effects run again. A few recent routes stay hidden; older ones are removed.

What this means:

- **Hide is unmount.** `useGSAP` cleanup runs and reverts inline values on DOM that will be shown again. Cleanup must leave the page readable, not half-reverted or stuck at its outro end. A `useLayoutEffect` cleanup runs before the hide and is the right place to reset inline transforms and opacity.
- **Hidden routes still match selectors.** `.column` or `#page-content` can hit a hidden copy from a cached route. Scope every selector through `useGSAP` `scope` or refs. Never query `document`.
- **Re-show is mount.** Setup runs again on a node that already holds settled values. Write initial state explicitly with `set` or `fromTo`. A `from` tween that trusts a fresh node is wrong.
- **Hidden measures zero.** Create ScrollTrigger, Flip, and split instances only when visible. Refresh surviving triggers on re-show.
- **Hidden pages leak.** Scope page-level CSS variables, `overflow` locks, and `will-change` to the route container, or undo them in cleanup.
- **Effects fire on every re-show.** Anything that should run once per visit needs a ref guard.
- **Tests see hidden DOM.** Use visibility-aware selectors.

Without `cacheComponents`, the outgoing route unmounts on commit. Design for the hidden case anyway; it costs nothing when unmount happens.

## Route keys

Use pathname as the transition key.

- Include search params only when they mean a different screen. Do not animate filter or sort changes as page changes.
- Hash-only links are same-page. Leave them native.
- Do not transition to the current pathname and search.
- Sanitize destinations before passing them to the router.

## Transition-aware Link

Keep the Link interface and forward unrelated props. Intercept only what `onNavigate` reports as client navigation. `onClick` fires for every click, so do not use it to decide.

Leave native: modified clicks, non-primary buttons, external origins, `target` or `download`, hash-only and same-location links, open-in-new-tab.

Carry `replace`, `scroll`, query strings, and hashes through to the router call.

For a document-level click retrofit, resolve the closest `a[href]`, apply the same exclusions, and remove the listener on cleanup. Do not stop unrelated handlers unless the transition is accepted.

## The swap gap and initial state

When the outro finishes before navigation, there is a gap: the old page has reached its end state and the new page may not have mounted yet. Cover the route container during the gap. Uncover only after every incoming target has its size and start styles.

The cover spans the route area and nothing else. Position it inside the element that wraps the changing route content, never fixed to the viewport: a full-viewport cover hides the persistent header and footer for the length of every route fetch, which the user sees as the chrome flashing on each click. Only an archetype whose effect is a full-screen wipe, such as a curtain, may cover the chrome, and then on purpose.

The initial state must occupy the same layout as the settled state. Prefer `autoAlpha` and transforms, which keep elements in flow. Size images, media, masks, and async regions before the intro. If the effect changes geometry, reserve the settled size with a wrapper or measure both states before writing either.

The route container owns geometry during the swap:

- Know both routes' bounds before exposing the swap.
- Hold a stable height while trees exchange, or animate the container between measured sizes on purpose.
- If both trees are mounted, overlap them so only one takes up space.
- Keep the shell stable. Reserve scrollbar space if route height changes would shift it.
- Keep a size reservation until the incoming route settles or the container animation ends.

Do not hide server-rendered content unconditionally. If initial state must hide before first paint:

- Scope the hiding rule to a root attribute that means JavaScript motion is active, and to the page's initial phase, so it releases the moment the lifecycle takes over.
- Set that attribute from an inline script placed first in `body`. It runs before content paints. Add `suppressHydrationWarning` to `html`, since the server HTML does not carry the attribute.
- Give the same script a failsafe: if no controller has claimed the document within about a second, remove the attribute, so a bundle that never arrives leaves a readable page. A controller that does arrive claims the document first. A page whose attribute is already gone when its controller runs, from the failsafe or from a reduced-motion skip, takes the instant path rather than hiding content that is already on screen.
- Keep content readable without JavaScript.
- Keep the swap cover separate from the first-paint rule.

Do not rely only on inline styles, since a GSAP context reverts them during a swap. The cover must survive cleanup until the new tree is ready.

## Streaming and Suspense

Under `cacheComponents` a route is a static shell plus streamed holes. The lifecycle splits the same way:

- **The shell is the page.** Keep the hero, headings, and navigation in the prerendered shell so the page reports ready on mount and a shared element has its target at once. An uncached `await` inside `<Suspense>` is enough to make a region stream; do not reach for `connection()`, which blocks prefetching.
- **A streamed region is a component.** Give it its own controller: explicit initial state on mount, a short intro, settled, cleanup. It never reports page ready. Reserve its block size in the fallback so arrival moves nothing, row for row if the content is a list.
- **The page outro owns everything present at leave time.** Query outro targets when the outro is built, not at setup, so content that streamed in after setup leaves with the page. Intros stay separate: the page intro reveals what mounted with it, the region intro reveals what arrived later.
- **`loading.tsx` is a skeleton, not a page.** It only appears when the whole shell is missing. Give it the same geometry and let the boundary's ready timeout release the cover; the real page then enters through the unrequested path.

## Shared elements with Flip

A GSAP morph across routes works on the App Router, including under `cacheComponents`:

- The outgoing outro captures `Flip.getState` on the element inside the clicked link, then fades everything else and leaves that element lit. Use no cover for this navigation; the end state is what the user should see until the swap.
- Pass the state to the incoming page through a small handoff object owned by the boundary. Reads must not consume it: React StrictMode runs the page setup twice and the first run's intro can read before the second run's does. Clear the handoff when the navigation finishes.
- The incoming intro calls `Flip.from(state, { targets: newElement, absolute: true })`. `targets` is required: the old element is still in the DOM, hidden by Activity, and without it Flip animates that hidden copy. Matching by `data-flip-id` works even when the original is hidden or gone.
- Keep the incoming shared element visible at setup and out of the stagger set. Position it before first paint by building the intro in the ready microtask, not a frame later.
- The reverse direction is the same two builders with the roles swapped, so one pair serves grid, detail, and home.

## Targets and order

Pages mark the elements they animate with refs or data attributes. Set all initial states before any intro tween. Animate in the order the user asked for. Build the outro explicitly; reversing the intro rarely gives the requested end state. If nothing is marked, animate the route container.

Keep header, nav, and footer outside the route boundary unless the request says they transition every time. Their one-time intro is its own lifecycle.

## Settled state, focus, and scroll

On intro completion:

- Mark the route settled exactly once.
- Clear temporary transforms, visibility, transition overrides, and `will-change` so CSS takes over.
- Do not keep a page inside an active timeline just to hold final values.
- Move focus to the route container or main heading only if navigation left focus on `body`. Do not steal focus from an active control.
- Give a focused container `tabIndex={-1}` and a visible focus style that fits the design.
- Keep the router's scroll behavior. Do not add a second scroll reset unless the product needs it.

## Outro, end state, and interruption

- Keep the outgoing route mounted with its size reserved until the outro completes.
- If navigation is requested mid-intro, kill the intro and build the outro from current values. Reverse only when intro and outro are exact inverses.
- At end state, make outgoing targets non-interactive and run completion once while still mounted and visible. Unmount, or let the router hide, only as the incoming route takes over.
- Wrap delayed callbacks and event handlers that create GSAP work in the GSAP context. Remove native listeners on cleanup.
- Reduced motion goes through the same five phases with instant changes. Never skip a callback that commits navigation or unmounts content.
- A different page arriving while the last one is still entering means the router moved without you, usually back or forward mid-intro. The hidden page's revert killed its intro, so nothing will finish that navigation. Before the new page's intro, drop everything the abandoned one left: its types, its handoff, its snapshot, its destination. Tell it apart from a development double setup of the same page by comparing root nodes, not handles, since a page registers itself before it reports ready.

## Combining with View Transitions

`<ViewTransition>` runs during the router's navigation. It snapshots old and new pixels and lets CSS animate between them. GSAP runs before navigation (outro on live DOM) and after it (intro on the new tree). Keep their jobs separate:

- One engine per element per transition. A named morph and a GSAP tween on the same node fight.
- Mount `<ViewTransition>` boundaries only while the browser engine is in use. React starts a document view transition on any navigation that mounts or unmounts a boundary, even one whose every class resolves to none, and `share` fires whenever a named pair exists regardless of `default`. Rendering the boundaries conditionally is the only way to keep GSAP navigations free of the snapshot pass.
- The price of that conditional wrapper: switching it changes the element type around the route container, so React remounts the whole route and its setup runs again with a replayed intro. Keep the switch in persistent chrome, never inside the route it wraps, and treat a switch as a reload of the page's lifecycle.
- Name only elements that morph, once per page. Set `default="none"` on named boundaries so they do not crossfade on unrelated transitions.
- When GSAP owns the route intro and outro, keep route content out of `<ViewTransition>` or set `default="none"`, so the browser does not crossfade content GSAP already prepared.
- A morph pairs only when the destination renders in the same commit (prefetched or cached). If it suspends first, the element plays its enter animation instead. Make the GSAP intro look right either way.
- Add `::view-transition { pointer-events: none }` so a running transition does not swallow clicks.
- Put the `<ViewTransition>` in each page, not the layout. Layouts persist, so enter and exit never fire there.
- Reduced motion covers both: zero view-transition durations in CSS and take the GSAP reduced path.

Pass `transitionTypes` on the Link and router call so both engines know the direction. The controller can read the same value to build a matching outro.

## Cases to design for

- Navigation requested mid-intro.
- Two destinations clicked quickly.
- Back or forward with no outro.
- A hidden route shown again with settled DOM.
- Programmatic navigation that bypasses the helper.
- A change of only search params or hash.
- An incoming route that streams or suspends.
- Split text or scroll plugins that changed the DOM before cleanup.
- React development double-mounting the client boundary.

Each case must end on one visible, interactive route with stable layout and no stale inline styles.

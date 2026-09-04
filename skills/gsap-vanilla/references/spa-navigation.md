# Same-document navigation

Read this only when the site fetches pages and swaps content without reloading the document.

## Decide whether to own a router

A same-document router must intercept links, fetch and parse HTML, swap content, update the title and URL, handle back and forward, restore scroll, move focus, re-run page scripts, cancel stale requests, and announce route changes. Swup, Barba, and Taxi do all of that and expose hooks where GSAP fits. Prefer one unless the project already owns a router or the user asks for one.

With a library, everything below still applies. Map its leave and enter hooks to outro and intro, return the timeline's promise so the library waits, and keep the lock, the cover, and cleanup as described.

## Page lifecycle

**mount → initial state → intro → settled → outro → end state → unmount**

1. **Outro.** The link is intercepted and the outgoing content plays its outro on live DOM while the next page is fetched.
2. **End state.** Outgoing targets finalize and completion runs once. Raise the cover over the route container.
3. **Unmount and mount.** The router replaces the container's children with the parsed content, updates the title, and pushes the URL.
4. **Initial state.** The new content is in the DOM, sized, and measured. Start values are written behind the cover.
5. **Intro.** Lower the cover and play one timeline to settled.
6. **Settled.** Clear temporary styles. CSS owns the page.

One navigation at a time. The first accepted destination wins through outro, fetch, swap, and cover. Release the lock when the intro starts, not when it ends, so a click mid-intro kills the intro and starts the outro from current values. Abort the in-flight fetch with an `AbortController` when a new destination is accepted.

A killed timeline never resolves its promise. Wrap `await` in a helper that also resolves on `onInterrupt` and returns whether the timeline completed.

## Intercepting links

Listen on the document for clicks and resolve the closest `a[href]`. Leave native: modified clicks, non-primary buttons, other origins, `target`, `download`, `mailto` and `tel`, hash-only and same-location links, and links marked to opt out. Use `pushState` for accepted links and `replaceState` for links marked replace.

Where the Navigation API exists, one `navigate` listener with `event.intercept({ handler })` covers link clicks, form submissions, and programmatic navigation, and reports `navigationType`. Keep the click path as the fallback for browsers without it.

## Fetching and swapping

- Fetch with an `Accept: text/html` header and parse with `DOMParser`. Take the route container's content, the `title`, and any `body` attributes such as `data-page` that pages differ on.
- Scripts inside fetched HTML do not execute when inserted. Register page setups in one module keyed by `data-page` and call the matching one after the swap. Do not rely on inline page scripts.
- Stylesheets some pages add must be loaded before those pages are revealed. Append the `link` and wait for its `load` event.
- Keep one route container. Persistent chrome lives outside it and never reloads. Its state, timelines, and listeners survive navigation, which is the reason to go same-document at all.
- Overlap old and new only inside a reserved wrapper so one box owns the geometry. Hold the container's height during the swap, or animate it between measured sizes on purpose.
- Keep the cover inside the route container, not fixed to the viewport, unless the effect is a full-screen wipe on purpose.

## History, scroll, and focus

- Set `history.scrollRestoration` to `manual` and own it. On push, scroll to top or to the hash target after the swap. Save the scroll position in the history state before leaving so `popstate` can restore it after the swap, then refresh ScrollTrigger.
- Back and forward never run an outro. On `popstate` the URL has already changed. Fetch, swap, and run initial state and intro only, or wrap the swap in `document.startViewTransition` so it is not a hard cut.
- After the swap, move focus to the route container or its main heading if focus was on removed content or on `body`. Give the target `tabindex="-1"` and a focus style that fits the design.
- Update `document.title` and announce the new page through a live region.
- Do not transition to the current URL. Treat search-param changes as page changes only when they mean a different screen.

## Cleanup on unmount

Before replacing the container's children:

- Revert the page's GSAP context, which kills its tweens, triggers, and splits and clears their inline styles.
- Remove listeners, observers, timers, and plugin instances the page created.
- Undo anything the page changed outside its container: scroll locks, root attributes, theme, body classes.
- Do not kill triggers globally. Chrome and the next page own theirs.

## Combining with same-document View Transitions

`document.startViewTransition(() => swap())` snapshots the old content, runs the swap, and animates to the new snapshot. Use it for history navigation and plain crossfades. The rules are the same as cross-document: one engine per element, GSAP intros after `finished` for touched elements, and `::view-transition { pointer-events: none }`.

## Cases to design for

- Navigation requested mid-intro.
- Two destinations clicked quickly.
- A fetch that fails or returns something that is not HTML. Fall back to `location.assign`.
- A slow fetch. The cover stays up; show a hint after a delay.
- Back or forward with no outro.
- A page that changes body classes, theme, or scroll lock.
- A page setup that should run on every visit versus once per session.

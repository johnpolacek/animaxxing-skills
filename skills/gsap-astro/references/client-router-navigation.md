# ClientRouter navigation

Read this when changing page-level motion or navigation on a site that uses `<ClientRouter />`.

## Is the router running

`<ClientRouter />` from `astro:transitions` goes in `<head>`, usually through a shared layout, and only pages that include it navigate in place. `transitionEnabledOnThisPage()` from `astro:transitions/client` reports the current page; `supportsViewTransitions` reports the browser. A link to a page without the router is fetched, found wanting, and followed as a full load, so an outro still plays but nothing survives into the next page.

The `fallback` prop decides what browsers without View Transitions get. `animate` (default) simulates the transition by setting `data-astro-transition-fallback` to `old` and then `new` on `<html>` and waiting for the CSS animations those attributes start. `swap` replaces the page at once. `none` gives those browsers a full-page navigation and no router at all: no `astro:` event fires there, not even `astro:page-load` on first load. With `none`, keep `gsap-vanilla`'s load path as the baseline.

Do not add a click interceptor beside the router to run motion. It listens on `document`, respects `defaultPrevented`, and leaves native: modified clicks, non-primary buttons, other origins, `target` other than `_self`, `download`, and anything marked `data-astro-reload`. `astro:before-preparation` is the hook. The one legitimate use of a click listener is the lock below: a capture-phase listener that calls `preventDefault()` on internal links only while a navigation is in flight, so the router never sees the second click.

## The navigation sequence

Verified against the router source. Read the installed version's `dist/transitions/router.js` if any step below carries the design.

1. A link click, form submit, `navigate()`, or `popstate` starts a navigation. The previous navigation, if still running, is aborted.
2. `astro:before-preparation` fires on `document` with the old page live and visible. Cancelable; `preventDefault()` hands the navigation to the browser as a full load.
3. `event.loader()` runs: fetch, parse into `event.newDocument`, preload new stylesheets. Wrapping it delays everything after it.
4. `astro:after-preparation` fires. The scroll position is saved to the history entry unless this is a traverse.
5. `data-astro-transition` is set on `<html>` to the direction and `document.startViewTransition()` snapshots the old page. From here until the new page is revealed the user sees pixels, not DOM.
6. `astro:before-swap` fires inside the transition callback with `event.newDocument`, `event.viewTransition`, and a replaceable `event.swap`. Not cancelable.
7. The swap: scripts already run are deselected, `<html>` attributes are replaced with the new document's, `<head>` is diffed, focus is saved, `<body>` is replaced, `transition:persist` elements are moved into the new body, focus is restored if it was inside a persisted element.
8. History is pushed or replaced, never on traverse. Scroll goes to the top or the hash, or is restored on traverse. This runs a microtask after the swap, so for a moment the incoming body is in the document under the outgoing URL. Anything that attributes DOM state to `location`, such as a phase log or analytics, sees the new page's initial state filed under the old path. Read the destination from `event.to`, not from `location`, until `astro:after-swap`.
9. `astro:after-swap` fires. The new DOM is in place, history and scroll are updated, nothing has painted.
10. The transition's update callback resolves. New scripts run in document order, then `astro:page-load` fires, then the route announcer reads the new title.
11. The view transition animates and `finished` resolves; `data-astro-transition` is removed.

On first load `astro:page-load` fires at window `load`, after images, and the router's module and the page's modules have already run by then.

## Page lifecycle

**mount → initial state → intro → settled → outro → end state → unmount**

1. **Outro.** `astro:before-preparation`, inside the wrapped loader, on live DOM.
2. **End state.** The outro's completion. Outgoing targets are finalized once; the loader promise resolves and the router proceeds.
3. **Unmount and mount.** `astro:before-swap` is the last moment the old body exists; the swap replaces it.
4. **Initial state.** `astro:before-swap` writes the pre-paint mark onto `event.newDocument`; `astro:after-swap` writes start values on the new body before paint.
5. **Intro.** `astro:page-load`, after the new page's scripts ran.
6. **Settled.** Clear temporary styles. CSS owns the page.

Store the phase on the page root. A controller may track `waiting` or `preparing`, but they serve these five phases.

## Event attributes

`astro:before-preparation` and `astro:before-swap` share `from`, `to` (writable; its final value becomes the history entry), `direction`, `navigationType` (`push`, `replace`, `traverse`), `sourceElement` (the link, the form or submitter, or the element passed to `navigate()`), `info` from `navigate()`, `newDocument`, and `signal`, an `AbortSignal` that trips when a newer navigation starts (present in the router source, not in the docs; check the installed types). Before preparation adds `formData` and a writable `loader`, and its `direction` is writable and accepts any string. Before swap adds `viewTransition` (a same-shaped stand-in in fallback mode) and `swap`, and its `direction` is read-only. `astro:after-preparation`, `astro:after-swap`, and `astro:page-load` carry nothing.

`navigate(href, { history, formData, info, state, sourceElement })` from `astro:transitions/client` starts a navigation from a script or an island. It does not sanitize `href`. Use `history.back()` and `history.forward()` for programmatic history moves; they reach the router through `popstate`. `data-astro-history="replace"` on a link does what `history: "replace"` does.

## Outro before the swap

Wrap the loader: capture `event.loader`, replace it with a function that starts the outro and the original loader together and resolves when both are done. The router waits, so the swap cannot show the end state early, and the outro's length is the only budget the fetch gets. Starting them together rather than in sequence keeps a slow route from adding its latency to the outro.

- Skip the outro when `event.navigationType === "traverse"`, when `event.formData` is set, and when `event.to` is the current URL.
- Same-page hash links fire no events; the router only scrolls.
- One navigation at a time. The router itself offers no lock: a second click unconditionally aborts the first navigation and fires a new `astro:before-preparation` while the first outro may still be running, so "first destination wins" cannot be built from the events alone. Build it from the router's respect for `defaultPrevented`: a capture-phase click listener on `document`, active only from an accepted `astro:before-preparation` until the incoming intro starts, that applies the router's own exclusions and calls `preventDefault()` on any further internal link. If the design wants the last click to win instead, drop the guard, keep one outro by killing the running one and building the next from current values, and let the first wrapped loader resolve as soon as its `signal` aborts so nothing awaits a dead navigation.
- A click during a running view transition skips that transition and starts over. The intro that was playing is killed by the new outro, not by the router.
- Race the outro against a timeout. GSAP's ticker stops in a hidden tab, and a loader that never resolves leaves the user on a page that no longer answers clicks.
- A killed timeline never resolves its promise. Await through a helper that also resolves on `onInterrupt`.
- Under reduced motion, resolve at once.
- A navigation the loader gives up on (fetch failed, next page has no router, cross-origin redirect) becomes a full load after the outro. The end state stays on screen until the new document paints; keep it presentable.
- The loader rewrites `event.to` on a redirect, so a destination read at the start of preparation can differ from the page that arrives. Decide the intro from `event.to` in `astro:before-swap`.

## Cleanup before the swap

`astro:before-swap` is the last event with the old body in the DOM, and the user is watching a snapshot, so nothing done here is visible. Kill the page's GSAP context, kill its ScrollTriggers, revert splits, remove listeners and observers, and undo scroll locks and `<body>` classes. Kill, not revert: `revert()` restores the inline values recorded when the context was created, which for a settled page means writing the intro's start transform and opacity back onto nodes that are still attached, and that is what the fallback path or a late snapshot shows. The old body is about to be discarded, so its inline styles do not matter; the persisted subtrees and any split markup are the parts that do, and those get `revert()`. Skip `[data-astro-transition-persist]` subtrees; they leave with the new body. Killing after the swap leaves triggers listening to scroll on behalf of nodes that no longer exist.

Do not animate here, and do not measure `event.newDocument`: it is an inert parsed document, so every box is zero.

## Initial state on the incoming page

The inline head script that marks `<html>` before first paint runs once per visit, and its attributes do not survive the swap because `<html>` attributes are replaced by the new document's. So:

- In `astro:before-swap`, set the mark and the initial phase on `event.newDocument.documentElement`. The pre-paint CSS rule then hides intro targets in the new body from the first frame it exists.
- In `astro:after-swap`, write every target's start values with `set` or `fromTo` on the live new body. Nothing has painted yet, on either the native or the fallback path.
- In `astro:page-load`, build the page controller for the current body and start the intro. The new page's scripts have run by then.

Reserve final sizes with CSS, not with inline styles a context revert would clear. The root animation you chose plays over this: with `none` on the root the new body appears at the swap holding its initial state; with `fade` it fades in holding it, and the intro starts after `viewTransition.finished` or is designed to look right under a crossfade.

Setup must be correct when it runs twice on the same body: the layout module runs it on first execution because `astro:page-load` waits for window `load`, and the event then runs it again. Key the guard on the body node, not a boolean.

## Direction

`event.direction` is `"forward"` or `"back"`, or any string a before-preparation listener writes there to name a custom pair. Astro puts it on `<html>` as `data-astro-transition` for the length of the transition, which is what `transition:animate` keys its backwards animations on. Carry the value from `astro:before-swap` into the controller for the intro; in fallback modes the attribute can be gone by `astro:page-load`.

## Back and forward

History navigation goes through the same events with `navigationType === "traverse"`, and the old body is still live during preparation, so unlike a plain MPA an outro is possible. Do not use it. The URL has already changed, the user expects the page they left, and after a swipe gesture the browser has already animated: the router then drops its own animation and swaps at once. Give traverse an intro-only path with no travel. If the intro should also be skipped after a gesture, read `hasUAVisualTransition` from your own `popstate` listener; the router does not pass it on.

A history entry the router did not create, or a return to a page loaded without the router, is a full reload; the first-load path handles it.

The router keeps the document alive, so the bfcache is not involved while it handles navigation. A full load from `data-astro-reload`, a page without the router, or an external site still ends the document, and pressing back can restore it from the bfcache. Keep `gsap-vanilla`'s `pagehide` rule: finish any outro instantly and leave the page readable.

## Scroll

The router sets `history.scrollRestoration` to `manual` and owns it: push and replace scroll to the top or the hash; traverse restores the position saved on the last `scrollend`. Both happen before `astro:after-swap`, which is where the docs put a scroll override. Do not add a second reset.

Create ScrollTriggers in `astro:page-load` and refresh after fonts and the new page's images, since window `load` does not fire again. On traverse the page is already scrolled when triggers are created; reveal targets above the restored position must not stay hidden. Refresh once more at settle if the intro changed heights above a trigger.

## Focus and announcement

After the swap, focus is restored only if it was inside a `transition:persist` element. Otherwise it is on `body`. On intro completion, move focus to the page container or main heading if it is still on `body`, with `tabindex="-1"` and a focus style that fits the design. Never take focus from a control inside a persisted region.

The router appends an `aria-live="assertive"` announcer and reads the `<title>`, first `<h1>`, or pathname shortly after `astro:page-load`. Keep a `<title>` on every page and do not add a second live region.

## Prefetch

With the router present, prefetch is on for every internal link with the `hover` strategy unless `astro.config` says otherwise: `prefetch: false` turns it off, `prefetchAll: false` limits it to links with `data-astro-prefetch`, and `data-astro-prefetch="tap"`, `"viewport"`, or `"load"` changes one link. Data saver and slow connections fall back to `tap`.

Hover prefetch means the fetch inside the wrapped loader usually hits cache and the outro is the whole wait. Where it cannot (tap, a link far from the viewport, Safari without cache headers), the fetch runs during the outro anyway because loader and outro start together. Importing `prefetch()` from `astro:prefetch` for programmatic warming needs the `prefetch` config even though the router turned prefetching on. `experimental.clientPrerender` turns prefetch into Speculation Rules (its `eagerness` option is 5.6+); `gsap-vanilla`'s prerender rules then apply to full loads only, since the router still fetches HTML for its own swaps.

## Combining with Astro's animations

Every element with a `transition:*` directive gets a `view-transition-name` and, by default, `transition:animate="fade"`. An element with a directive but no `transition:name` is named from its component and position, so the same component in the same place on both pages pairs up automatically. Everything else rides the browser's root crossfade. The browser animates snapshots between the swap and `finished`; GSAP animates live DOM before the snapshot and after the swap. Keep their jobs separate:

- One engine per element per navigation. A named element under a GSAP tween during the transition fights its own snapshot, and the outro's end state becomes the old snapshot.
- When GSAP owns the page transition, put `transition:name="root"` and `transition:animate="none"` on `<html>`. `none` compiles to no animation on old, new, and group, so the new body appears at the swap in its initial state and the outro's end state is the last thing seen before it. Then name only the elements the browser should morph, once per page. The `<html>` tag must be the first thing in the layout template after the frontmatter: a leading JSX-style comment or any other node makes the compiler emit a fragment with no `html`, `head`, or `body`, and the directive is dropped without a warning. An HTML comment is fine.
- For a named element, start its GSAP intro after `event.viewTransition.finished` captured in `astro:before-swap`; until then the live element sits under its pseudo-element. Elements outside the transition start at `astro:page-load`.
- `fade({ duration })` and `slide({ duration })` from `astro:transitions` adjust the presets. A custom animation is an object with `forwards` and `backwards`, each holding `old` and `new` keyframe animations, declared in component frontmatter with the keyframes in global CSS. Keep GSAP out of those.
- `initial` hands the element to the browser's default and is not simulated in fallback mode.
- Add `::view-transition { pointer-events: none }` so a running transition does not swallow clicks.
- The router disables all of its animations, fallback included, under `prefers-reduced-motion`. GSAP takes its own reduced path.

## Cases to design for

- A click during the outro, and a click during the intro.
- Back and forward, including a swipe gesture.
- A link to a page without the router, or marked `data-astro-reload`.
- A form submission.
- A hash link on the same page and a hash link to another page.
- A `transition:persist` element or island crossing the swap mid-animation.
- A page visited a second time, whose module script does not run again.
- A destination that redirects.
- A browser without View Transitions, on the `fallback` value the site ships.
- A click from a background tab on a prefetched link.

Each case must end on one visible, interactive page with stable layout and no stale inline styles.

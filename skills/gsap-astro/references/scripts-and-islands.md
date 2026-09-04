# Scripts and islands

Read this when a script must run per page, when a listener or timeline leaks across navigations, or when GSAP lives inside a framework island.

## How scripts run under the router

Astro turns a plain `<script>` in a component into a bundled module script: TypeScript, imports, `type="module"`, one copy per page however many times the component appears, inlined when small. `<script is:inline>`, or any script with another attribute, ships as written.

Under `<ClientRouter />` the document is never reloaded, so:

- A module script runs once per visit, keyed on its `src` URL or its inline text. It runs the first time a page that carries it is reached and never again, even after navigating away and back. A page-specific script therefore runs once per session, not once per view.
- After each swap the router runs, in document order, only the scripts the visit has not seen, plus `is:inline` scripts marked `data-astro-rerun` (4.5+). Then `astro:page-load` fires.
- An `is:inline` script without `data-astro-rerun` never re-runs after a swap: the router records every script's text at initialization and skips any match on later pages. Do not put lifecycle code in one. Use it for the pre-paint mark only, and guard any global it sets, because `window` persists.
- `DOMContentLoaded` fires once per visit. Replace it with `astro:page-load`.
- Window `load` fires once as well. Anything that waited on it, such as a ScrollTrigger refresh after images, needs an equivalent after each swap: wait on the new page's images explicitly.

So the shape is: one layout-level module registers the router listeners the first time it runs, and each page-specific module registers a controller factory under its `data-page` name in module scope. The `astro:page-load` handler reads `data-page` from the current body and builds the matching controller. Both survive because module scope survives.

## Listeners outlive pages

`document` and `window` are the same objects across every swap. A listener added on them lives until removed, and a listener added per page is added again on every visit:

- Register router listeners (`astro:before-preparation`, `astro:before-swap`, `astro:after-swap`, `astro:page-load`) once, from a module's top level, never from inside a page-load handler.
- Every handler locates the current page root before doing anything. The page that registered it may be gone.
- Element listeners on nodes inside `<body>` die with the body, but the closures that hold GSAP objects do not. Store them next to the page's context and remove them in `astro:before-swap`.
- `ResizeObserver`, `IntersectionObserver`, `matchMedia` listeners, timers, and `requestAnimationFrame` loops all survive. Same cleanup.
- ScrollTrigger and Observer hold document-level scroll and resize listeners. Kill the page's instances before the swap, never with a global kill that also takes chrome and persisted triggers.

## Custom elements as component owners

A custom element defined in a component script gets `connectedCallback` for every instance on every page, including instances that arrive by swap, and `disconnectedCallback` when the old body is replaced. Both run inside the swap, before paint, so they are the per-instance mount and unmount under the router, with `this.querySelector` as the scope. Give a self-contained component its `gsap.context` in `connectedCallback` and revert it in `disconnectedCallback`; it needs no `astro:page-load` hook. On first load the definition runs after parse, so the pre-paint rule still owns the frame before it.

The page controller stays with `astro:page-load`. It owns cross-component sequencing and the transition, which a single element cannot see.

## Islands

A `client:*` directive turns a framework component into an island: server-rendered HTML wrapped in `<astro-island>`, hydrated on the client by that framework. Hydration is asynchronous and per island: `client:load` as soon as its code arrives, `client:idle` on `requestIdleCallback` with an optional `timeout` (4.15+), `client:visible` on intersection with an optional `rootMargin` (4.1+), `client:media` when a query matches, `client:only` with no server HTML at all. None of them is guaranteed to have hydrated by `astro:page-load`.

What the page lifecycle can do with an island:

- Animate the island's box. Its server-rendered HTML is in the new body from the swap, laid out and measurable, so it can be a page intro target like any element. `client:only` renders only its `slot="fallback"` until it mounts; reserve its size and give it its own intro.
- Not reach inside. Page-level selectors stop at `astro-island`. The framework owns that subtree and re-renders it, so split wrappers and inline styles written from outside are overwritten or break reconciliation.
- Not rely on it for the outro. The page outro treats the island as one box; an island's own exit runs on its own terms.

GSAP inside the island follows the framework's rules, `gsap-react` for React and `gsap-frameworks` for Vue, Svelte, Solid, and Preact, with the island's root as scope. Its mount is hydration, and its unmount is the swap: the island element fires `astro:unmount` on `astro:after-swap` once it is no longer connected, and the React client entry unmounts its root on that event so effect cleanups run. Check the installed integration's client entry for other frameworks. Two consequences: island cleanup happens after the page's `astro:before-swap` cleanup, and a global `ScrollTrigger.killAll()` in the page cleanup takes the island's triggers before the island can revert them itself.

An island that calls `navigate()` from `astro:transitions/client` gets the same lifecycle as a link, and can pass itself as `sourceElement`.

In development, a `client:only` island on the next page makes the router load that page in a hidden iframe during preparation to collect its styles. Do not measure outro timing against a dev server.

## transition:persist

`transition:persist` (2.10+) keeps an element or island across the swap: it is lifted out of the old body and moved into the new one at its counterpart's position, with its DOM identity, listeners, running timelines, media playback, and framework state intact. Match by position, or by a name: `transition:persist="player"`, or `transition:name` plus `transition:persist`. Head elements can persist too. A persisted island re-renders with the new page's props unless `transition:persist-props` (4.5+) keeps the old ones. CSS animations restart and iframes reload regardless.

For GSAP:

- A persisted subtree belongs to its own owner, never to the page controller. Page cleanup in `astro:before-swap` skips `[data-astro-transition-persist]`, and the page intro does not target anything inside one.
- A GSAP context inside a persisted island is not reverted by the swap; its framework component keeps running. Do not revert it from page code, or the island arrives on the next page torn down.
- The element moves in the DOM, its neighbors change, and the page scrolls. Refresh any ScrollTrigger inside it in `astro:page-load`, and expect a pin inside a persisted region to need re-creating.
- The counterpart on the new page must exist or the element is discarded with the old body. Design the outro so a persisted element with no home on the next page is not mid-flight when that happens.
- Focus inside a persisted element survives the swap. Focus anywhere else lands on `body`.

## Chrome

Header, nav, and footer are part of `<body>`, so without `transition:persist` they are replaced on every swap, and an intro on them replays. Persist them when their state or a running animation should survive, or give them a once-per-session intro gated in module scope, plus `sessionStorage` for full loads. Name them with `transition:name` so the browser holds them still while content crossfades, or leave them unnamed under a root `none`.

# Page lifetime

Read this to know when a page mounts, updates in place, or unmounts, how the Svelte 5 lifecycle fits GSAP, and how Svelte's own transitions coexist with it.

## Reuse versus remount

SvelteKit renders a route as a pyramid: root layout, nested layouts, page. A navigation swaps only the levels whose component changed.

- Same route, new params or search params: the `+page.svelte` is reused. Its `data` and `page` update; `onMount`, `onDestroy`, and effects without a changed dependency do not run.
- Different route under the same layouts: the page unmounts and the new one mounts. The shared layouts stay, with their state, timelines, and listeners.
- A route that breaks out of a layout with `+page@` or a group: the layouts below the break remount too.
- `invalidate` and `invalidateAll` re-run `load` and update props. Nothing remounts.
- Shallow routing with `pushState` changes `page.state` only.

So a page intro tied to `onMount` plays once per mount, not once per visit. Two fixes:

- **`afterNavigate` in the page, the default for GSAP.** It fires on mount and after every navigation while the page stays mounted, with `type`, `from`, and `to`. Compare `from?.url.pathname` with `to?.url.pathname`, adding params when they mean a different screen, and skip when only search params changed. The page keeps its state and the DOM already holds settled values, so kill the previous timeline first and write initial state with `set` or `fromTo`, never a `from` tween that trusts a fresh node.
- **`{#key page.url.pathname}` around `{@render children()}` in the layout.** Every pathname change destroys and recreates the page, so `onMount` intros replay and `in:` and `out:` directives on the wrapper play. Use it when the page must be re-instantiated anyway or the effect is a Svelte transition. It discards page state and inner scroll positions, and it remounts on param changes, which is what the docs offer for that case.

Do not key the whole layout on `page.url`. That remounts the shell and its chrome on every navigation.

## Layouts and the controller

The root `+layout.svelte` mounts once per document and outlives every client-side navigation. That makes it the home of the route transition controller: one `bind:this` route container around `{@render children()}`, the navigation hooks, the phase in `$state`, and the cover. Nested layouts persist for their subtree and are the place for section-level chrome motion.

Pages register intro and outro builders with the controller through context or a shared module and unregister in their teardown. The controller calls the outgoing page's outro from `onNavigate` and the incoming page's intro from `afterNavigate`. A page that registers nothing gets the container-level default.

Hooks registered in a page are removed when it unmounts. A `beforeNavigate` in a page sees the navigation away from that page. An `afterNavigate` in a page sees its own arrival and every navigation while it stays mounted.

## Svelte 5 lifecycle for GSAP

- `onMount` with a synchronous callback returning cleanup, or `$effect` returning teardown, both run only in the browser after the DOM exists. `gsap-frameworks` covers the `gsap.context` and `revert` pattern. Use it unchanged.
- `$effect` re-runs when state it read synchronously changes, running its teardown first. An effect that reads `page.url`, `data`, or `navigating` re-runs on navigation, reverting and rebuilding the context, including on search-param changes. Read those values inside `afterNavigate` or through `untrack`, not in the effect body, unless the rebuild is intended.
- `bind:this` values are `undefined` during initialization. Read them in an effect or `onMount`.
- `$effect.pre` runs before the DOM update it is scheduled with. `tick()` resolves after pending changes are applied. Use them to measure before and after an update. `beforeUpdate` and `afterUpdate` do not exist in runes mode.
- `{@attach}` runs a function in an effect when its element mounts, again when state it reads changes, with an optional teardown. It suits per-element GSAP setup that must follow an element through `{#each}` blocks.
- Store the phase in `$state` and render a data attribute from it. Do not infer the phase from opacity or DOM presence.
- `onDestroy` runs during server rendering. Keep GSAP out of it, or guard with `browser`.

## Combining engines

Svelte transitions, GSAP, and View Transitions can share a page but not a node.

- A `transition:`, `in:`, or `out:` directive drives its node through the Web Animations API or a `tick` function. A GSAP tween on the same node writes the same properties and one of them loses. Put the directive on a wrapper and GSAP inside it, or use one engine.
- When a block with an `out:` directive is removed, every element in the block stays in the DOM until every outro in it finishes, and the new content is inserted at once, so old and new are in flow together. Use that when the effect is a crossfade in a stacked container. Avoid it when GSAP owns the outro: the block lingers past the GSAP end state after the router has moved on.
- Directives are local by default: one plays when its own block is created or destroyed, including when the router swaps a page whose root carries it, but not when an outer `{#if}` in the same component toggles. Add `|global` only when that outer toggle should play it.
- Svelte transitions ignore `@media (prefers-reduced-motion)` rules that zero CSS durations. Zero their `duration` from `prefersReducedMotion.current` in `svelte/motion` and take the GSAP reduced path in the same condition.
- `svelte/animate` on `{#each}` items and GSAP Flip solve the same problem. Pick one per list.
- View Transitions snapshot whatever the DOM shows, including a half-finished directive or a GSAP end state. Start them only after both have reached the state you want photographed.

## Conditional content

`{#if}` removes a block synchronously unless a directive inside it is outroing. For GSAP-driven show and hide, keep the node mounted with a presence controller: render while `visible || leaving`, play the outro, and clear `leaving` from the end callback. For a plain fade, `out:fade` on the block is the presence controller and needs no GSAP.

A shallow-routed modal is a presence controller with history as its close. Open with `pushState`, close by playing the outro and then calling `history.back()`, and treat the resulting `popstate` as the removal, not as a page navigation. Undo scroll locks, key listeners, and focus in the modal's teardown, which also covers a back navigation you did not initiate.

## SSR and hydration

- `$effect` and `onMount` do not run on the server. Keep GSAP out of module scope, or guard with `browser` from `$app/environment`. Importing GSAP on the server is harmless; running it is not.
- Register plugins once in a browser-guarded module that other modules import.
- Hydration paints server HTML first. The first-paint rule in [The swap gap and initial state](sveltekit-navigation.md#the-swap-gap-and-initial-state) is the only sanctioned way to hide before the first intro.
- `csr = false` on a page removes the client router; navigation hooks never fire there. `ssr = false` gives an empty shell until the client renders, so the first intro can wait for mount without a pre-paint rule.
- `afterNavigate` with `type: 'enter'` is the first-load intro. A prerendered page gets it on hydration like any other. A bfcache restore runs no hook at all.

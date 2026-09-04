# Verification

Check in proportion to what changed. Do not turn a focused animation task into a full audit.

## Always

- Run the repo's `svelte-check`, lint, format, and test commands where they exist.
- Confirm settled content is visible, interactive, and free of leftover GSAP inline styles.
- Confirm timelines, triggers, listeners, and plugin DOM changes are cleaned up on unmount and on a reused page's re-run.
- Confirm the page is readable with JavaScript disabled and with the pre-paint mark set but hydration blocked.
- Test reduced motion when the change has a reduced-motion branch, for GSAP and for any Svelte directive.

## Runtime changes

Check the changed lifecycle in a real browser when practical:

- Initial state is applied before reveal. Throttle the network and reload; no settled server HTML flashes before hydration.
- Intro ends in one settled state.
- Outro keeps the node mounted until completion runs, and only then does the held navigation re-issue or the `onNavigate` promise resolve. On the `beforeNavigate` path the URL is unchanged for the whole outro.
- Rapid or interrupted input ends in one coherent state.
- Layout boxes do not jump.

For route navigation, test the paths the change affects: an ordinary internal link, back and forward, a rapid double navigation, a same-route param change, a search-param-only change, a `goto`, and a reload. Confirm URL, visible page, focus, history, and scroll agree, and that `navigating` returns to `null`.

For a reused page, the returning lifecycle must run initial state and intro on its preserved DOM with no doubled tweens, and scroll triggers must measure correctly after new data renders.

When Svelte directives or View Transitions are involved, confirm no element is animated by two engines, outroing blocks are gone once their outro ends, and clicks land during a running transition.

For conditional components, test show, hide, and one interruption. Confirm removal happens after the outro.

## Builds and wider checks

Run a production build for changes to routes, `svelte.config.js`, page options, dependencies, `src/app.html`, or anything release-facing; the dev server hydrates differently from the built output. Serve the build the way the adapter does: under `adapter-node` that is `node build`, since `vite preview` serves no server-rendered routes there. Run wider browser, accessibility, responsive, streaming, and performance checks only when the change touches them or the user asks for a full audit.

Report which checks ran and which could not. Do not claim runtime behavior was verified when only static review was possible.

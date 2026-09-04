# Verification

Check in proportion to what changed. Do not turn a focused animation task into a full audit.

## Always

- Run the repo's type, lint, format, and test commands where they exist. Regenerate `routeTree.gen.ts` if file-based routes changed.
- Confirm settled content is visible, interactive, and free of leftover GSAP inline styles.
- Confirm timelines, triggers, listeners, plugin DOM changes, the blocker, and the history subscription are cleaned up on unmount and on a reused route's rerun.
- Under TanStack Start, confirm the page is readable with JavaScript disabled and with the pre-paint mark set but hydration blocked.
- Test reduced motion when the change has a reduced-motion branch, for GSAP and for any `viewTransition` types.

## Runtime changes

Check the changed lifecycle in a real browser when practical:

- Initial state is applied before reveal. Under Start, throttle the network and reload; no settled server HTML flashes before hydration.
- Intro ends in one settled state.
- Outro keeps the node mounted until completion runs, and the blocked navigation proceeds only then.
- Rapid or interrupted input ends in one coherent state, with no blocker promise left pending.
- Layout boxes do not jump.

For route navigation, test the paths the change affects: an ordinary internal link, back and forward, a rapid double navigation, a same-route param change, a search-param-only change, a `navigate` call, a slow loader that shows the pending component, and a reload. Confirm URL, visible route, focus, history, and scroll agree, and that `status` returns to `idle`.

For a reused route, the returning lifecycle must run initial state and intro on its preserved DOM with no doubled tweens, and scroll triggers must measure correctly after the new data renders.

When both `viewTransition` and GSAP are involved, confirm no element is animated by both and that clicks land during a running transition.

For conditional components, test show, hide, and one interruption. Confirm unmount happens after the outro.

## Builds and wider checks

Run a production build, and `vite preview` or the Start server, for changes to routes, the router options, the Vite or Start config, dependencies, the root document shell, or anything release-facing; the dev server hydrates differently from the built output and React development runs effects twice. Run wider browser, accessibility, responsive, streaming, and performance checks only when the change touches them or the user asks for a full audit.

Report which checks ran and which could not. Do not claim runtime behavior was verified when only static review was possible.

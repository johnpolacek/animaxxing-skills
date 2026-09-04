# Verification

Check in proportion to what changed. Do not turn a focused animation task into a full audit.

## Always

- Run the repo's type, lint, format, and test commands where they exist. In framework mode run `react-router typegen` before `tsc` if the project's typecheck script does not already, so route types are current.
- Confirm settled content is visible, interactive, and free of leftover GSAP inline styles.
- Confirm timelines, triggers, listeners, and plugin DOM changes are cleaned up.
- Test reduced motion when the change has a reduced-motion branch, including that `proceed()` still runs.

## Runtime changes

Check the changed lifecycle in a real browser when practical:

- Initial state is applied before reveal, including on a server-rendered or prerendered first load.
- Intro ends in one settled state.
- Outro keeps the route mounted until completion runs, and the URL does not change until then.
- Rapid or interrupted input ends in one coherent state.
- Layout boxes do not jump.

For route navigation, test the paths the change affects: an ordinary internal link, a link to the same route with new params, back and forward, and a rapid double navigation. Confirm URL, visible route, focus, history, and scroll agree. Confirm that no blocker is left in a `blocked` state with the page apparently dead, and that a `Form`, `<Navigate>`, or `navigate` call that bypasses the wrapper still lands on a readable page.

When both `viewTransition` and GSAP are involved, confirm no element is animated by both, that a pop replaying a recorded transition still looks right, and that clicks land during a running transition.

For streamed regions, throttle the network so `<Await>` resolves after the page intro and confirm the region enters on its own and leaves with the page.

For conditional components and modal routes, test show, hide, one interruption, and a `POP` close. Confirm unmount happens after the outro.

Use visibility-aware selectors in browser tests, such as role queries or an explicit visible filter, since a covered or `inert` route is still in the DOM.

## Builds and wider checks

Run a production build for changes to routes, `react-router.config.ts`, dependencies, server and client boundaries, `.client` modules, or anything release-facing. In framework mode the server build evaluates route modules; a GSAP call outside an effect fails there, not in dev. Run wider browser, accessibility, responsive, streaming, and performance checks only when the change touches them or the user asks for a full audit.

Report which checks ran and which could not. Do not claim runtime behavior was verified when only static review was possible.

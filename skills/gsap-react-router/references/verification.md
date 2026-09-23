# Verification

Check in proportion to what changed. Do not turn a focused animation task into a full audit.

## Always

- Run the repo's type, lint, format, and test commands where they exist. In framework mode run `react-router typegen` before `tsc` if the project's typecheck script does not already, so route types are current.
- Confirm settled content is visible, interactive, and free of leftover GSAP inline styles.
- Confirm timelines, triggers, listeners, and plugin DOM changes are cleaned up.
- Test reduced motion: the same settled state, every completion callback fired, including `proceed()`.
- At phone width: readable text, stable boxes, no horizontal overflow.
- Touch-treated controls release after taps. For device changes, run the [device checks](devices.md#verify).

## Initially hidden content

Run the [failure verification matrix](initialization.md#failure-verification) when adding or changing hiding, preparation, or recovery. It covers disabled JavaScript, a blocked bundle after the marker, throws before/after styles and splits, stalled fonts/media, late initialization, no-flash success, reduced motion, and interruption/repeated setup. Assert text and native links, not opacity alone. Include shell/footer and intentionally hidden content.

Use this framework's [integration rules](motion-system.md#initialization-and-recovery) for rendering and navigation expectations. Measure document-load LCP separately from transitions when first-load behavior changes; report measured results and untested paths.

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

## Smooth scrolling and transition archetypes

Run the checks in [Smooth scrolling](smooth-scroll.md#verify) and [Transition archetypes](transition-archetypes.md#verify) when the change touches them. Under React Router also confirm:

- After `proceed()` the page starts where `<ScrollRestoration>` put it: the top, the hash target, or unchanged with `preventScrollReset`. After a `POP`, the saved position, keyed by `getKey` when one is set, with no eased travel from the old page and no jump when `start()` runs. In declarative mode, the top after a push and the browser's position after a pop.
- Fast Refresh on the root module and StrictMode leave one scroller and one ticker callback.
- No blocker stays `blocked` under a closed curtain; a `POP` during a covered swap ends uncovered and unblocked.
- A navigation that morphs a shared element sets no `viewTransition`, and the pop back replays nothing.

## Builds and wider checks

Run a production build for changes to routes, `react-router.config.ts`, dependencies, server and client boundaries, `.client` modules, or anything release-facing. In framework mode the server build evaluates route modules; a GSAP call outside an effect fails there, not in dev. Run wider browser, accessibility, responsive, streaming, and performance checks only when the change touches them or the user asks for a full audit.

Report which checks ran and which could not. Do not claim runtime behavior was verified when only static review was possible.

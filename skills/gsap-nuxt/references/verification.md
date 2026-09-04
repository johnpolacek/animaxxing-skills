# Verification

Check in proportion to what changed. Do not turn a focused animation task into a full audit.

## Always

- Run the repo's type, lint, format, and test commands where they exist, including `nuxt typecheck` when the project uses it.
- Confirm settled content is visible, interactive, and free of leftover GSAP inline styles.
- Confirm timelines, triggers, listeners, and plugin DOM changes are cleaned up, on unmount and on deactivate.
- Confirm every transition hook calls `done` on completion, on interruption, and under reduced motion.
- On server-rendered projects, confirm the page is readable with JavaScript disabled and with the pre-paint mark set but the client bundle blocked.
- Test reduced motion when the change has a reduced-motion branch.

## Runtime changes

Check the changed lifecycle in a real browser when practical:

- Initial state is applied before reveal. For the first load, throttle the network and reload; no settled content flashes.
- Intro ends in one settled state.
- Outro keeps the node in the DOM until `done`, and the node is gone right after.
- Rapid or interrupted input ends in one coherent state.
- Layout boxes do not jump, including at leave start when the page's context reverts.

For route navigation, test the paths the change affects: an ordinary `<NuxtLink>`, back and forward, a second click before the first navigation resolves, a query-only change (no transition should run), a route with `pageTransition: false`, and a layout change. Confirm URL, visible page, focus, history, and scroll agree, and that exactly one page root remains in the DOM after each transition.

With keepalive, also navigate away and back. The returning page must re-run initial state and intro on its preserved DOM with no doubled tweens, and scroll triggers must measure correctly after reactivation.

With `experimental.viewTransition`, confirm the Vue transition is disabled on those navigations, no element is animated by both engines, names are cleared afterward, and clicks land during a running transition.

For conditional components, test show, hide, and one interruption. Confirm removal happens after the outro, and that a `v-show` re-show during an outro reverses or restarts as intended.

## Builds and wider checks

Run `nuxt build` and check the output with `nuxt preview` for changes to pages, layouts, `nuxt.config`, router options, middleware, dependencies, or client and server boundaries. Run wider browser, accessibility, responsive, and performance checks only when the change touches them or the user asks for a full audit.

Report which checks ran and which could not. Do not claim runtime behavior was verified when only static review was possible.

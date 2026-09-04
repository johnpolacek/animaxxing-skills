# Verification

Check in proportion to what changed. Do not turn a focused animation task into a full audit.

## Always

- Run the repo's type, lint, format, and test commands where they exist.
- Confirm settled content is visible, interactive, and free of leftover GSAP inline styles.
- Confirm timelines, triggers, listeners, and plugin DOM changes are cleaned up.
- Test reduced motion when the change has a reduced-motion branch.

## Runtime changes

Check the changed lifecycle in a real browser when practical:

- Initial state is applied before reveal.
- Intro ends in one settled state.
- Outro keeps the node mounted until completion runs.
- Rapid or interrupted input ends in one coherent state.
- Layout boxes do not jump.

For route navigation, test the paths the change affects: an ordinary internal link, back and forward, and a rapid double navigation. Confirm URL, visible route, focus, history, and scroll agree.

With `cacheComponents` on, also navigate away and back. The returning route must re-run initial state and intro on its preserved DOM with no doubled tweens, and scroll triggers must measure correctly after re-show. Use visibility-aware selectors in browser tests, such as role queries or an explicit visible filter, since hidden routes stay in the DOM.

When both `<ViewTransition>` and GSAP are involved, confirm no element is animated by both and that clicks land during a running transition.

For conditional components, test show, hide, and one interruption. Confirm unmount happens after the outro.

## Builds and wider checks

Run a production build for changes to routes, Next config, dependencies, server and client boundaries, or anything release-facing. Run wider browser, accessibility, responsive, streaming, and performance checks only when the change touches them or the user asks for a full audit.

Report which checks ran and which could not. Do not claim runtime behavior was verified when only static review was possible.

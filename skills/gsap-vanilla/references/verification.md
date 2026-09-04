# Verification

Check in proportion to what changed. Do not turn a focused animation task into a full audit.

## Always

- Run the repo's type, lint, format, and test commands where they exist.
- Confirm settled content is visible, interactive, and free of leftover GSAP inline styles.
- Confirm timelines, triggers, listeners, and plugin DOM changes are cleaned up.
- Confirm the page is readable with JavaScript disabled and with the pre-paint mark set but the main script blocked.
- Test reduced motion when the change has a reduced-motion branch.

## Runtime changes

Check the changed lifecycle in a real browser when practical:

- Initial state is applied before first paint. Throttle the network and reload; no settled content flashes.
- Intro ends in one settled state.
- Outro keeps the node in the DOM until completion runs.
- Rapid or interrupted input ends in one coherent state.
- Layout boxes do not jump.

For full-document navigation, test an ordinary internal link, a reload, back and forward, a link clicked twice quickly, and a click from a background tab. Confirm URL, visible page, focus, history, and scroll agree. Press back after an outro and confirm the restored page is readable, whether it came from the bfcache or a fresh load.

With cross-document View Transitions, confirm no element is animated by both engines, names are cleared after each transition, clicks land during a running transition, and the site still works with the transition unsupported.

For same-document navigation, also test a failed fetch, a slow fetch, and a page that changed body classes or scroll lock.

For conditional components, test show, hide, and one interruption. Confirm removal happens after the outro.

## Builds and wider checks

Run a production build for changes to the build setup, dependencies, or anything release-facing. Run wider browser, accessibility, responsive, and performance checks only when the change touches them or the user asks for a full audit.

Report which checks ran and which could not. Do not claim runtime behavior was verified when only static review was possible.

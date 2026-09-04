# Verification

Check in proportion to what changed. Do not turn a focused animation task into a full audit.

## Always

- Run the repo's type, lint, format, and test commands where they exist, including `astro check` when the project uses it.
- Confirm settled content is visible, interactive, and free of leftover GSAP inline styles.
- Confirm timelines, triggers, listeners, and plugin DOM changes are cleaned up. After three navigations, `ScrollTrigger.getAll()` lists only the current page's, chrome's, and persisted regions' triggers.
- Confirm the page is readable with JavaScript disabled and with the pre-paint mark set but the main script blocked.
- Test reduced motion when the change has a reduced-motion branch.

## Runtime changes

Check the changed lifecycle in a real browser when practical:

- Initial state is applied before first paint on a full load. Throttle the network and reload; no settled content flashes.
- Initial state is applied before the new body paints after a swap. Watch a navigation frame by frame if the design depends on it.
- Intro ends in one settled state.
- Outro keeps the old body in the DOM until completion runs, and the swap waits for it.
- Rapid or interrupted input ends in one coherent state.
- Layout boxes do not jump.

Under `<ClientRouter />`, test an ordinary internal link, a link to a page already visited so its script does not run again, back and forward, a reload mid-site, a link clicked twice quickly, a click during the intro, a form, a hash link, a link marked `data-astro-reload`, and a click from a background tab. Confirm URL, visible page, focus, history, scroll, and route announcement agree. Press back after an outro and confirm the returning page is readable and got an intro, not an outro.

When Astro's `transition:animate` and GSAP are both involved, confirm no element is animated by both, clicks land during a running transition, and the site still works with View Transitions unsupported on the `fallback` value it ships.

For islands, test the island hydrating after the page intro started, a `transition:persist` island crossing a swap mid-animation, and the island's cleanup running at `astro:after-swap` without doubled tweens on the next page.

Without the router, follow `gsap-vanilla`'s checks for full-document navigation, the bfcache, and cross-document View Transitions.

For conditional components, test show, hide, and one interruption. Confirm removal happens after the outro.

## Builds and wider checks

Run `astro build` and check with `astro preview` for changes to layouts, `astro.config`, integrations, dependencies, or anything release-facing. Development differs from production: `client:only` preparation loads a hidden iframe and Vite injects styles differently, so timing and flashes seen only in dev are not proof either way. Run wider browser, accessibility, responsive, and performance checks only when the change touches them or the user asks for a full audit.

Report which checks ran and which could not. Do not claim runtime behavior was verified when only static review was possible.

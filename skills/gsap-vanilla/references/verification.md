# Verification

Check in proportion to what changed. Do not turn a focused animation task into a full audit.

## Always

- Run the repo's type, lint, format, and test commands where they exist.
- Confirm settled content is visible, interactive, and free of leftover GSAP inline styles.
- Confirm timelines, triggers, listeners, and plugin DOM changes are cleaned up.
- Confirm the page is readable with JavaScript disabled and with the pre-paint mark set but the main script blocked.
- Test reduced motion: the same settled state, every completion callback fired.
- At phone width: readable text, stable boxes, no horizontal overflow.
- Touch-treated controls release after taps. For device changes, run the [device checks](devices.md#verify).

## Initially hidden content

Run the [failure verification matrix](initialization.md#failure-verification) when adding or changing hiding, preparation, or recovery. It covers disabled JavaScript, a blocked bundle after the marker, throws before/after styles and splits, stalled fonts/media, late initialization, no-flash success, reduced motion, and interruption/repeated setup. Assert text and native links, not opacity alone. Include shell/footer and intentionally hidden content.

Use this framework's [integration rules](motion-system.md#initialization-and-recovery) for rendering and navigation expectations. Measure document-load LCP separately from transitions when first-load behavior changes; report measured results and untested paths.

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

With a smooth scroller, run the [scroll checks](smooth-scroll.md#verify) on a fresh load, a `back_forward` load, and a bfcache return; a page left mid-outro must not come back clipped, and a same-page hash link eases once rather than jumping and then easing. With a curtain, preloader, or shared element, run the [archetype checks](transition-archetypes.md#verify); on a full-document site also confirm a covered first frame follows only an outro, never a reload or history load, and that a shared element morphs through the browser's view transition, not Flip.

For conditional components, test show, hide, and one interruption. Confirm removal happens after the outro.

## Builds and wider checks

Run a production build for changes to the build setup, dependencies, or anything release-facing. Run wider browser, accessibility, responsive, and performance checks only when the change touches them or the user asks for a full audit.

Report which checks ran and which could not. Do not claim runtime behavior was verified when only static review was possible.

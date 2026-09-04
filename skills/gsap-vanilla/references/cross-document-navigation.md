# Cross-document navigation

Read this when a full-document site uses View Transitions, or when GSAP must hand off to the browser at a page boundary.

## Opting in

Both documents need `@view-transition { navigation: auto }` in their CSS. Then every same-origin navigation the user starts from page content, plus back and forward, snapshots the old page, loads the new one, and crossfades the root. Address-bar navigations, cross-origin pages, and pages without the rule get an instant swap.

Feature-detect with `CSS.supports("view-transition-name: a")` for the CSS side and `"onpagereveal" in window` for the events. Browsers without support skip the transition and lose nothing else. Every GSAP path must work with the transition absent.

## Events

- `pageswap` fires on the old document just before it is replaced. `event.viewTransition` is the outbound transition or null. `event.activation` carries the navigation type and the from and to history entries. This is where the old page assigns `view-transition-name` to the element the user clicked, chosen from the destination URL, and where `skipTransition()` cancels a transition that should not run.
- `pagereveal` fires on the new document at its first render opportunity, before first paint. `event.viewTransition` is the inbound transition or null. Read `navigation.activation.from` for where the user came from. Assign names to the matching elements here, then await `viewTransition.ready` and clear them.
- `pagereveal` also fires on a bfcache restore and on prerender activation. Check `navigation.activation` before assuming a fresh load.

Clear every `view-transition-name` you set once snapshots are taken. A name left on an element travels into the bfcache, and on return two elements can share it, which skips the transition.

## Types and direction

`@view-transition { types: slide-forward }` sets types statically. Set them in `pageswap` and `pagereveal` through `event.viewTransition.types` when the direction depends on the route pair, and key CSS on `html:active-view-transition-type(slide-forward)`. The GSAP controller can read the same decision to build a matching intro.

## Stabilizing the new page

The inbound transition starts at first render opportunity, which can be before the page has its fonts, its critical script, or its full above-the-fold markup. Then the new snapshot is wrong and the transition lands on a page that is still changing.

- Stylesheets in `head` already block render.
- Put `blocking="render"` on the module script that sets initial state, so the snapshot shows the initial state, not the settled one.
- Add `<link rel="expect" href="#main" blocking="render">` so the browser parses the main element before revealing.
- Keep those blocks small. Everything under them delays first paint on every load.

## Combining with GSAP

GSAP runs on the live page before the browser leaves it and on the new page after it arrives. The view transition runs between them, on snapshots. Keep their jobs separate.

- One engine per element per transition. A named morph and a GSAP tween on the same node fight, and the GSAP end state becomes the old snapshot.
- If a GSAP outro fades or moves content, that is what the browser snapshots. Either skip the transition for that navigation with `skipTransition()` in `pageswap`, or leave the shared element lit at end state so the morph has something to start from.
- On the new page, start the GSAP intro after `viewTransition.finished` for elements the transition touched. Elements outside the transition can start at `pagereveal`. Both paths must also run when `viewTransition` is null.
- Name only elements that morph. Name chrome to hold it still; the root crossfade covers the rest.
- Reduced motion covers both: zero view transition durations in CSS under `prefers-reduced-motion` and take the GSAP reduced path.
- Add `::view-transition { pointer-events: none }` so a running transition does not swallow clicks.

## Back and forward

A history navigation gets a view transition too, reversed if the CSS keys on type. GSAP never gets an outro on the way back. On the new page, a `traverse` activation selects the intro-only path.

## Cases to design for

- A link clicked while the outro is running.
- A slow destination. The old page's end state sits on screen until the new document arrives; keep it presentable.
- Back to a page in the bfcache: `pageshow` reports `persisted`, `pagereveal` reports a `traverse` activation, and timelines are still alive.
- Back to a page not in the bfcache: full reload, `back_forward` navigation type, intro-only.
- A prerendered destination, where `pagereveal` fires on activation.
- Browsers without view transition support, which must still get the GSAP outro and intro.

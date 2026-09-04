# Page load and unload

Read this for anything that happens when a document loads, is restored, or is left.

## Load lifecycle

**mount → initial state → intro → settled → outro → end state → unmount**

On a full-document site:

1. **Mount** is parsing. The DOM exists in pieces until parsing ends, and the browser may paint the top of a long page before it does.
2. **Initial state** is applied before the browser paints. Otherwise the user sees the settled page flash and then vanish into the intro.
3. **Intro** starts once targets exist and have their sizes: `DOMContentLoaded` for layout, `document.fonts.ready` for text, a specific image's `load` for a layout that depends on it.
4. **Settled** clears temporary styles and hands the page to CSS.
5. **Outro** runs on the live page after a link is clicked and before the browser follows it.
6. **End state** commits the navigation from the completion callback.
7. **Unmount** is the next document replacing this one. Nothing survives it.

Store the current phase as a data attribute on the page root. CSS and tests read it; nothing infers it from opacity or DOM presence.

## When scripts run

- An inline script in `head` runs before any content is parsed or painted. It is the only place that can set state before first paint in every browser.
- `defer` and `type="module"` scripts run after parsing and before `DOMContentLoaded`. The DOM is complete, but the browser may already have painted part of it. A deferred script cannot prevent that paint on its own.
- `async` scripts run whenever they arrive. Do not use them for lifecycle code.
- `blocking="render"` on a `head` script holds first paint until the script runs. Use it as a guarantee where supported, but keep the inline-script path as the baseline so other browsers do not flash.
- A module script can run after `DOMContentLoaded` already fired. Check `document.readyState` before waiting on the event.

## Initial state before first paint

Never hide content unconditionally in CSS. A user without JavaScript, a crawler, or a script that failed to load must still see the page.

- The inline `head` script sets a mark on `html` such as `data-motion="js"`. It can also skip the mark entirely under `prefers-reduced-motion`, so the page paints settled and no intro runs. Do not put a `data-phase` on `html`: the page root owns that attribute, and a second one on the document root reads to CSS, tests, and observers as another page changing phase.
- The page root ships with `data-phase="initial"` in the HTML, and one CSS rule hides intro targets only under the mark and only in that phase, for example `html[data-motion="js"] [data-page][data-phase="initial"] [data-intro] { visibility: hidden }`. It releases the moment the controller changes the phase.
- The controller writes every target's start values with `gsap.set` or `fromTo` before it changes the phase, so the release never shows the settled state.
- Use `visibility`, not `display`, so layout is measured with the elements in place.

If the script fails after the mark is set, the page stays hidden. Keep the marking script tiny and inline so it cannot fail separately from the CSS, and have the controller change the phase as its first act, before anything that can throw.

## Waiting for the DOM, fonts, and media

- Build the controller on `DOMContentLoaded`, or immediately if the document is already interactive.
- Wait for `document.fonts.ready` before splitting or measuring text, or let SplitText's auto-split handle fonts.
- Give images and media `width` and `height` or an aspect ratio so the intro does not wait for them. If a layout depends on an image without dimensions, wait for that image, not the whole `load` event.
- Refresh ScrollTrigger on `load` and after fonts, since both change document height.

## Navigation type

`performance.getEntriesByType("navigation")[0].type` reports how this document was reached: `navigate`, `reload`, `back_forward`, or `prerender`. Where the Navigation API exists, `navigation.activation.navigationType` reports `push`, `replace`, `reload`, or `traverse`.

- A new navigation gets the full intro.
- A reload gets the full intro or a shorter one. The user did not arrive anywhere.
- A history navigation to a fresh document gets an intro-only path with no travel. The user is returning. Never run an outro on the way back; the old page is gone before script hears about it.
- A prerendered document is handled below.

## Prerendered pages

With Speculation Rules the browser may load and run the next page before the user clicks. `document.prerendering` is true while that happens, and `prerenderingchange` fires once on activation.

Set initial state during prerendering. Start the intro, timers, and anything the user must see only after activation. A timeline started while prerendering finishes invisibly, and the user gets a settled page with no intro.

`pagereveal` also fires on activation, so a listener there sees prerendered pages and bfcache restores as well as fresh loads.

## The bfcache

When the user leaves, the browser may freeze the document in the back-forward cache instead of destroying it. Coming back restores it as it was, timelines and all, and fires `pageshow` with `persisted` set to true.

- On `pagehide`, finish any outro instantly and leave the page in its readable settled state. That is what the user sees on return.
- On `pageshow` with `persisted`, do not replay the intro. Refresh ScrollTrigger, resync anything time-based, and resume what was paused.
- An outro end state that leaves the page faded or covered is a bug the user sees only when pressing back. Clear it in `pagehide`.
- Never add `unload` listeners. A `beforeunload` listener blocks the bfcache in some browsers unless removed after use. Use `pagehide`, which fires in both cases and reports `persisted`.

## Leaving a page with an outro

There is no router to intercept. Intercept the click.

- Listen on the document for clicks and resolve the closest `a[href]`. Leave native: modified clicks, non-primary buttons, other origins, `target`, `download`, `mailto` and `tel`, hash-only and same-location links, and links marked to opt out.
- Prevent default, run the outro, then follow the link with `location.assign(href)` from the end-state callback. A navigation started from a click handler still counts as user-initiated for View Transitions.
- Lock to one navigation. A second click during the outro is ignored, or retargets the destination if the design wants that.
- Race the outro against a timeout so a stalled timeline never traps the user on the page. GSAP's ticker stops in a hidden tab, so a click from a background tab must still navigate.
- Form submissions get no outro.
- Under reduced motion, run the end-state callback immediately.

Prefetch the destination during the outro with `<link rel="prefetch">` or Speculation Rules so the new document is ready when the outro ends. The outro's length is the only budget the network gets.

## Shell chrome

Header, navigation, and footer are rebuilt on every full load. An intro on them plays on every click.

- Play a chrome intro once per session, gated by `sessionStorage`, or not at all.
- Give chrome a `view-transition-name` so cross-document View Transitions hold it still while the content changes.
- Keep chrome out of the page outro unless the design wants it to leave.

## Hidden tabs

`requestAnimationFrame` and GSAP's ticker stop in a hidden tab. Anything that awaits a frame or a timeline can wait forever. Race frame waits against a short timeout, and expect timelines to finish when the tab becomes visible.

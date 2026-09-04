---
name: gsap-vanilla
description: "Build or review GSAP animation on plain HTML, CSS, and JavaScript sites with no component framework: page load intros without a flash of settled content, exit animation before a link is followed, cross-document View Transitions with pageswap and pagereveal, back and forward with the bfcache, prerendered pages, animated show and hide, scroll-driven effects, and fetch plus pushState navigation by hand or with Swup, Barba, or Taxi. Use whenever a static site, a multi-page site, or a Vite or bundler project without React, Vue, Svelte, or Astro needs any of these, even if GSAP is not named, and whenever flashes, interrupted animations, or cleanup matter. Not for component frameworks, which have their own skills, or isolated GSAP API questions."
license: MIT
metadata:
  short-description: GSAP page and component lifecycles on plain HTML sites
---

# GSAP Vanilla

Every animated page or component runs through the same lifecycle:

**mount → initial state → intro → settled → outro → end state → unmount**

On a plain site the browser owns mount and unmount. A page mounts when its document parses and unmounts when the next document replaces it, and nothing survives that swap: not a timeline, not a variable, not a listener. The five phases between belong to your animation code. This skill covers getting them right without a framework: first paint, navigation timing, history, interruptions, and cleanup. The user's request and the existing design decide how things look.

## Start with the project

1. Read repository instructions and the current code.
2. Find out how pages are produced: hand-written HTML, a static generator with no client framework, a bundler such as Vite with no UI framework, or a transition library such as Swup, Barba, or Taxi. If a component framework renders the pages, say this skill does not cover it and use that framework's skill.
3. Find out how GSAP loads: npm import, import map, or script tag. Keep it.
4. Find out how scripts run: inline, `defer`, or `type="module"`. This decides when the DOM exists and whether the page can paint before the script runs.
5. Check the target browsers. Cross-document View Transitions, `pageswap` and `pagereveal`, the Navigation API, and `blocking="render"` are not everywhere. Feature-detect each one instead of trusting memory, and make sure the site works with all of them missing.
6. Look at the shared layout, navigation markup, global CSS, accessibility conventions, tests, and any animation already in use.

Add GSAP or a plugin only when the requested motion needs it. Do not replace an animation or transition library the project already chose unless asked.

## Pick a navigation model

A plain site navigates in one of three ways. Decide which before writing lifecycle code, and do not mix them on one site.

- **Full document loads.** Every link replaces the document. The outro plays before the link is followed; the intro plays when the new page loads. This is the default and needs no router.
- **Full document loads with cross-document View Transitions.** The browser snapshots the old page and animates to the new one. GSAP fills in what a snapshot pair cannot do.
- **Same-document navigation.** Script fetches the next page and swaps content in place, so chrome, state, and timelines survive. Use a maintained library unless the project already owns a router or has a reason to. See [Same-document navigation](references/spa-navigation.md).

## Pick GSAP or View Transitions per effect

Use cross-document View Transitions for:

- A shared element that morphs between two pages.
- A whole-page slide or crossfade keyed by transition types.
- Holding persistent chrome still while the content around it changes.

They need no lifecycle code and fall back to an instant swap in unsupported browsers.

Use GSAP when the effect needs:

- An outro that plays on the live page before the browser leaves it.
- Interruption, reversal, or scrubbing. A view transition is a fixed pair of snapshots.
- Sequenced timing across many targets, split text, or scroll-linked progress.
- A completion callback that gates navigation, focus, or removal.

Mixing is fine: the browser morphs one image while GSAP animates the rest. Never give one element to both in the same transition. See [Combining with GSAP](references/cross-document-navigation.md#combining-with-gsap).

## Follow the requested motion

The user's request decides effects, direction, timing, easing, and intensity. Map it onto the five phases without changing the look. For anything unspecified, keep the project's existing convention or pick a quiet default.

## Read only what you need

- First paint, script timing, fonts, navigation type, prerendering, the bfcache, hidden tabs, and leaving a page with an outro: [Page load and unload](references/page-load.md).
- `@view-transition`, `pageswap`, `pagereveal`, types, render blocking, and handing off between the browser and GSAP: [Cross-document navigation](references/cross-document-navigation.md).
- Fetch and swap routers, link interception, history, scroll, focus, script re-execution, and when to use a library: [Same-document navigation](references/spa-navigation.md).
- The five phases, GSAP setup, contexts, show and hide, layout stability, scroll, text, plugins: [Lifecycle implementation](references/motion-system.md).
- Before calling work done: [Verification](references/verification.md).

The official GSAP skills (`gsap-core`, `gsap-timeline`, `gsap-scrolltrigger`, `gsap-plugins`, `gsap-utils`, `gsap-performance`) cover the GSAP API. This skill covers how GSAP fits a page the browser owns.

## Pieces to add, only as needed

- One module that imports GSAP and the plugins the project uses and registers them once. Other modules import from it.
- An inline script at the top of `head` that marks the root as JavaScript-active before first paint, paired with a CSS rule that hides intro targets only under that mark and only during the initial phase.
- A page controller that owns the five phases for the current document, chosen by a `data-page` attribute on `body` or `main`.
- A transition-aware link handler that runs the outro, then follows the link.
- Intro and outro timeline builders.
- A presence controller for conditional content that must stay in the DOM through its outro.
- For same-document navigation only: a router or a library adapter, one route container, and a cover.

Persistent header, nav, and footer are rebuilt on every full load. Give them a once-per-session intro or none. See [Shell chrome](references/page-load.md#shell-chrome).

## Rules

- GSAP runs after the DOM it targets exists. Scope selectors with `gsap.context` to the page or component root. Clean up every tween, trigger, split, and listener when its owner goes away.
- Lay out the final page with normal CSS first. One stable wrapper owns the geometry through every phase.
- Set initial values before first paint, then reveal. Users never see the settled state before the intro, and never a blank page without JavaScript.
- Animate to one settled state and clear temporary styles there.
- Keep outgoing content in the DOM and visible through outro and end state. Follow the link, remove the node, or swap only from the end callback.
- Back and forward never run an outro. A fresh document reached by history gets an intro-only path, and a bfcache restore gets no intro at all.
- A prerendered page sets initial state at once and waits for activation before it animates.
- Keep native link behavior, focus, scroll restoration, and no-JavaScript readability.
- Never add `unload` or `beforeunload` listeners for animation. They disable the bfcache. Use `pagehide`.
- Reduced motion reaches the same settled state and still fires every completion callback.
- Prefer transforms and `autoAlpha`. Set `will-change` only while animating, then clear it.
- Use timelines for sequences. Decide up front what happens on rapid clicks and interrupted animations.
- Verify in a real browser when practical, including reload, back, forward, and a click from a background tab.

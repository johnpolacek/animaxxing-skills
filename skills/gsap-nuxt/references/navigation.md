# Navigation

Read this when changing how pages live and die: keys, keepalive, Nuxt app hooks, scroll, focus, links, history, View Transitions, and SSR.

## Page lifecycle

**mount → initial state → intro → settled → outro → end state → unmount**

On a Nuxt route change with GSAP in the transition hooks:

1. **Navigation.** A `<NuxtLink>` click or `navigateTo`. `page:loading:start`, route middleware, guards, the page chunk (usually prefetched), `beforeResolve`, commit. The old page is untouched.
2. **Incoming setup.** `<NuxtPage>` renders the new page under Suspense: `page:start`, then its setup and data run off-screen. The old page stays visible and interactive.
3. **Outro.** Suspense resolves: `page:finish`, then `page:loading:end`. Vue unmounts the old page component and hands its root to `onBeforeLeave` and `onLeave`. Under `out-in` the new root waits; without `mode` it is inserted now.
4. **End state.** The outro's `done`. Vue removes the old root; `onAfterLeave` and `page:transition:finish` fire; Nuxt scrolls one frame later.
5. **Initial state and intro.** `onBeforeEnter` before insertion, `onEnter` after, the page's `onMounted` in the same flush. Write start values, then play.
6. **Settled.** The intro's `done`, then `onAfterEnter`. Clear temporary styles. CSS owns the page.

One navigation at a time is Vue Router's job: a new navigation cancels a pending one, and Nuxt remounts the Suspense. Your job is that every hook call ends in `done` and every timeline can be killed.

## When a page is reused versus remounted

`<NuxtPage>` keys the page on the `pageKey` prop, else `definePageMeta({ key })`, else the matched route path with params filled in. So:

- `/posts/1` to `/posts/2` changes the key: remount, full transition, `page:start` and `page:finish`.
- Query or hash changes keep the key: the component is reused, no transition, no `page:start`. `page:loading:start` and `page:loading:end` still fire. Animate in place from `onBeforeRouteUpdate` or a `watch` on the route.
- `key: route => route.fullPath` remounts on query changes too. Use it only when a query means a different screen.
- `key: 'static'` or `<NuxtPage page-key="static">` never remounts across params. Param changes become in-page updates and the hooks never run.
- Hash-only links are same-page. Leave them native; Nuxt scrolls to the target with the router's `scrollBehaviorType`.

Nuxt's own test for "this navigation changes the page" is the same: the key differs or the matched components differ. View transitions and scroll use it.

## Route lifetime under keepalive

`definePageMeta({ keepalive: true })`, `<NuxtPage keepalive>`, or `app.keepalive` wraps pages in `<KeepAlive>`. A page is then deactivated instead of unmounted and reactivated instead of remounted. DOM and state survive; the lifecycle does not.

- **Deactivate is unmount.** `onDeactivated` fires when the leave starts. Revert the page's context there. The root still plays `onLeave`, then moves to KeepAlive's off-document storage.
- **Stored pages measure zero.** Do not create or refresh ScrollTrigger, Flip, or split instances while deactivated.
- **Activate is mount.** `onActivated` fires after the root is inserted, and also once after `onMounted` on first mount. Setup runs again on DOM that holds settled or half-reverted values. Write initial state explicitly with `set` or `fromTo`; a `from` tween that trusts a fresh node is wrong. `onMounted` does not run again.
- **The hooks run the same.** `onBeforeEnter` and `onEnter` fire on reactivation with the stored root as `el`; `onLeave` fires on deactivation.
- **Cached pages leak.** Scope page-level CSS variables, `overflow` locks, and `will-change` to the page root, or undo them in `onDeactivated`.
- `include` and `exclude` match component names. Under `future.compatibilityVersion: 5` page component names are normalized to route names.

Without keepalive the page unmounts at leave start. Design for the keepalive case anyway; it costs nothing when unmount happens.

## Nuxt app hooks

Register with `useNuxtApp().hook(name, fn)` in a plugin, or `useRuntimeHook` (3.14+) in a component so it unregisters with the scope. In navigation order:

- `page:loading:start`: in `router.beforeEach`, before middleware. Also when the `pageKey` prop changes. Fires for query-only changes and for navigations that later fail.
- `page:start`: the incoming page's Suspense went pending. Its setup and data are running; the old page is on screen.
- `page:finish`: that Suspense resolved. This is when the leave starts, not the end of the transition.
- `page:loading:end`: after `page:finish`, or on navigation failure or router error. Pair with `page:loading:start` for a global navigating state, lock, or cover.
- `page:transition:finish`: the outgoing page's `onAfterLeave`. Under `out-in` the new root has just been inserted and its `onEnter` has not run yet.
- `page:view-transition:start`: only with `experimental.viewTransition`; passes the `ViewTransition`.
- `app:suspense:resolve`: the root Suspense resolved on the client, the first-load counterpart of `page:finish`. `app:mounted` fires earlier, when `mount()` returns.
- `link:prefetch`: a `<NuxtLink>` is about to prefetch.

Use these for app-level state: cover, lock, loading indicator, analytics, announcing. Use the transition hooks for anything that touches the page's elements. For work after the intro, `onAfterEnter` is the only hook that fires then.

## Scroll and focus

Nuxt's default `scrollBehavior` (override it in `app/router.options.ts`) waits for `page:loading:end`, then for the outgoing leave to finish, then one animation frame, then scrolls: `savedPosition` on back and forward, the hash target if any, otherwise top. `definePageMeta({ scrollToTop: false })`, or a function of `to` and `from`, disables it per route. Same-path hash changes scroll at once.

So the window moves after the outro and around the first frame of the intro. Keep initial state independent of scroll position (transforms, `autoAlpha`), create ScrollTrigger instances after that scroll (`onAfterEnter`, or `page:transition:finish` plus a frame), and refresh in `onAfterEnter`. Do not add a second scroll reset.

Override `scrollBehavior` only to change the position logic. Keep the wait: returning a promise that resolves after `page:transition:finish` is Vue Router's documented way to delay scroll for a transition.

Focus: in `onAfterEnter`, move focus to the page root or its heading only if focus is on `body`. Give the target `tabindex="-1"` and a visible focus style. `autoAlpha: 0` is `visibility: hidden` and refuses focus, so focus at settled, not at insert. Keep `<NuxtRouteAnnouncer>` for the announcement.

## Outro before navigation

Vue keeps the old page through `onLeave`, so an outro that merely plays before the old page disappears needs no interception. But Vue Router commits the URL before `onLeave` runs: by the time the hooks see the old root, the address bar already shows the destination and the incoming page has loaded. If the outro must play with the URL unchanged, which is what "outro before navigation" usually means, the hooks cannot do it; the outro has to run in a global route middleware that awaits it, and `onLeave` then only hands `done` over for an element that is already at its end state. Do not port a Next.js transition-aware link that prevents default, animates, then pushes; here it doubles the outro or races the hooks.

The ways to move the outro earlier:

- **The outro must cover the load.** By default the leave waits for the incoming page. To start the outro at click time, use `<NuxtLink custom v-slot="{ href, navigate }">`, start the outro and call `navigate()` together, and let `onLeave` call `done` at once when the outro has already reached end state, or attach `done` to the running timeline. Make the page non-interactive from the click. Leave modified clicks, external URLs, `target`, and `download` to the native anchor.
- **Nothing may load and the URL must wait until the outro ends.** A global route middleware `await`s the outro on the client (`import.meta.client && !useNuxtApp().isHydrating`) and then returns. Route middleware runs after `page:loading:start` and before guards, chunk loading, the URL commit, and the incoming setup. Never await it on history navigation. The lock cannot live in this middleware: returning `false` for a second click while the first is awaiting makes Vue Router cancel the first as well, since the pending navigation is now the second, and both are lost. Put the lock in front of the router, in the link component, so the second click never becomes a navigation.
- **A leave must be refused.** `onBeforeRouteLeave` returning `false` cancels the navigation before anything moves. Use it for unsaved work, not for animation locks; returning `false` on back or forward also rewrites the URL back.

Shared elements need no interception. `Flip.getState` in `onBeforeLeave` (the old page is laid out and the new page is not yet inserted in either mode), hand the state through the transition module, `Flip.from(state, { targets })` in `onEnter`. Under no `mode` the old element is still in the DOM, so pass `targets` explicitly.

## Back and forward

History navigation runs the same middleware, hooks, and transition as a click, and Vue Router does not tell a guard how a navigation started. What works:

- `useRouter().options.history.listen((to, from, info) => ...)` fires for `popstate` navigations only, before the router runs, with `info.direction` of `back`, `forward`, or empty. Record the destination it reports and let the hooks compare it with the route they are entering; do not clear a boolean on `page:loading:end`, which fires before `onLeave` and `onEnter` and so wipes the flag before the hooks read it. Vue Router marks this API alpha; check `node_modules/vue-router` after upgrades.
- A `popstate` listener on `window` fires in the same dispatch, before any guard. `event.hasUAVisualTransition` means the browser already animated a swipe gesture; skip the intro then, as Nuxt's own view-transition plugin does.
- `scrollBehavior` receives `savedPosition` only on history navigation, but that is after commit and after the leave.

Give history navigation a quieter path: a short outro or an immediate `done`, then intro-only with no travel, since the user is returning. The hooks still fire; do not skip `done`.

The bfcache does not apply to same-document navigation. A full reload of a Nuxt page is a fresh hydration and takes the first-load path.

## View Transitions

`experimental.viewTransition: true` (or `'always'`, or `{ enabled, types }`) calls `document.startViewTransition` in `router.beforeResolve` for navigations that change the page, runs the route swap and Suspense inside its update callback, and finishes it on `page:finish`. `true` skips it under `prefers-reduced-motion`; `'always'` does not. Per page: `definePageMeta({ viewTransition })` with `enabled`, `types`, `toTypes`, and `fromTypes` (4.4+; functions of `to` and `from` work here, not in `nuxt.config`). Style with `::view-transition-*` and `html:active-view-transition-type(...)`. `page:view-transition:start` hands you the `ViewTransition` to read or add types. A `popstate` with `hasUAVisualTransition` skips it.

Vue's `<Transition>` has no View Transitions mode of its own; this plugin is the integration.

Rules for mixing:

- Never run the `pageTransition` hooks and a view transition on the same navigation. The DOM is frozen while the browser captures, and Suspense resolves while the old page is still leaving, so the new snapshot is wrong or blank. Follow Nuxt's recipe: a global middleware sets `to.meta.pageTransition = false` and `to.meta.layoutTransition = false` when `document.startViewTransition` exists, and your GSAP path lives in the page's `onMounted`.
- One engine per element per transition. Name only elements that morph, set the name only for that navigation, and clear it.
- GSAP intros for elements the transition touched start after `transition.finished`; take the `ViewTransition` from `page:view-transition:start`. Elements outside it can start at `onMounted`.
- Data fetched in page setup runs inside the frozen update; Nuxt's docs list this as a known issue. Prefer prefetched or cached data on routes that use it.
- Add `::view-transition { pointer-events: none }`.
- Reduced motion covers both: `true` already skips the browser side; take the GSAP reduced path.

Use view transitions for a shared-element morph or a whole-page slide keyed by types. Use the GSAP hooks for everything sequenced, interruptible, or scroll-linked. Pick per route, not per element.

## SSR and first paint

GSAP runs only in the browser.

- Register GSAP and plugins in a `.client.ts` plugin or the `useGSAP` composable from `gsap-frameworks`; guard module-level side effects with `import.meta.client`.
- `onMounted`, `onActivated`, and the transition hooks never run on the server. `<script setup>` top level and `watchEffect` do.
- `<ClientOnly>` renders its slot only after mount and its `fallback` on the server; the slot is not in the server HTML at all. Use it for a canvas or a plugin-driven widget that cannot render as HTML, not to hide a page.
- With `ssr: false` the client renders everything and first-paint hiding is unnecessary.

Hydration happens after the server HTML has painted, so a first-load intro needs initial state before first paint, applied by CSS under a mark that only JavaScript sets:

- Add an inline script through `app.head.script` in `nuxt.config` with `innerHTML` and `tagPosition: 'head'`. It runs before the body parses. It sets a root mark such as `data-motion="js"` on `<html>`, and skips the mark under `prefers-reduced-motion` so that path paints settled. Do not put a `data-phase` on `<html>`: the page root owns that attribute, and a second one on the document root reads to CSS, tests, and observers as another page changing phase.
- Vue hydrates `#__nuxt`, not `<html>`, so attributes set there cause no hydration mismatch.
- One CSS rule hides intro targets only under the mark and only while the page root is in its initial phase, such as `html[data-motion="js"] [data-page][data-phase="initial"] [data-intro] { visibility: hidden }`. The server renders the page root with `data-phase="initial"`, so the rule applies from first paint and releases when the controller advances the phase. Use `visibility`, not `display`, so layout is measured with the elements in place.
- The first `onMounted` writes start values with `gsap.set`, flips the phase, then plays. If the bundle fails after the mark is set the page stays hidden, so keep the inline script tiny and flip the phase before anything that can throw.
- Give the same script a failsafe: if no controller has claimed the document within about a second, remove the mark, so a bundle that never arrives leaves a readable page. A controller that does arrive claims the document first. A page whose mark is already gone when its controller runs, from the failsafe or the reduced-motion skip, takes the instant path rather than hiding content that is already on screen.
- Content stays readable without JavaScript: no mark, no rule.
- `onPrehydrate` inlines a callback before `</body>`, after the content has parsed and possibly painted. It is for DOM fixes right before hydration, not for the pre-paint mark.

Route navigations do not go through this: `onBeforeEnter` runs before the incoming root is inserted.

## Cases to design for

- Navigation requested mid-intro.
- Two destinations clicked before the first resolves.
- Back or forward, including a swipe the browser already animated.
- A keepalive page shown again with settled DOM.
- A change of only query or hash.
- A slow incoming page: the old page stays on screen. Decide what the user sees for two seconds.
- A layout change, where the page transition does not run.
- A leave that reverts a pinned ScrollTrigger.
- Reload on a slow network: no settled flash, then a clean intro.
- Development hot reload, which re-runs setup on a live page.

Each case must end on one visible, interactive page with stable layout, no stale inline styles, and every `done` called.

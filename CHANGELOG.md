# Changelog

All notable changes to Animaxxing Skills are documented here. Releases follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- `animaxxing-webgl`, a new motion skill for GSAP-driven WebGL image effects on one shared OGL renderer and canvas per document. Image planes track each `<img>` through scroll and resize; a hover lens, a scroll-velocity wave, and a reveal or exit wipe are GSAP tweens on shader uniforms. The `<img>` stays the accessible content and the fallback without WebGL, on context loss, without CORS, and under reduced motion. The stage caps pixel ratio, sleeps off screen and in hidden tabs, rebuilds after a context restore, and every revert frees its GL resources. OGL was chosen over three.js at 14.5 KB against 133 KB gzipped for the classes used.
- Endless drag recipe in `animaxxing`: `dragLoop`, a horizontal row that wraps seamlessly under drag, throw, and sideways wheel, lands on items, and can drift with a pause control; and `dragGrid`, a canvas of tiles that wraps on both axes. Clones are `aria-hidden` and `inert` without ids, keyboard focus brings items into view, vertical swipes keep scrolling the page, and revert mid-throw restores the markup exactly.
- Signature curves in `animaxxing`'s motion vocabulary: register a CustomEase once and pass its name to any recipe `ease` option. `style-animaxxing` names its own curve. Recipe defaults are unchanged.
- Framework skills' `transition-archetypes.md` gains **Persistent WebGL canvas**: the shell holds the stage so one canvas and context survive client-side routes.

## [0.7.0] - 2026-09-23

### Added

- Section pager recipe in `animaxxing`: full-screen sections that change one at a time on a wheel flick, swipe, or key, built on GSAP Observer. Trackpad inertia never skips a section, fields and composite widgets keep their keys, and focus shows a parked section at once.
- Sound cues recipe in `animaxxing`: opt-in Web Audio sounds for interactions and timelines, plus ambient beds. Silent until the visitor turns sound on, suspended while the tab is hidden, with a per-cue gap and voice cap.

## [0.6.1] - 2026-09-23

### Changed

- `animaxxing` is shorter and says each rule once. Every recipe opens with one lifecycle line. Rules shared by all recipes live only in SKILL.md: plugin versions, reduced-motion rebuilds, one owner per target, parent-timeline kills, and loop pauses. Reduced-motion notes that repeated the contract tables now sit in those tables. The layout Flip wiring is framework-neutral. No recipe code changed.

## [0.6.0] - 2026-09-23

### Added

- Media effects recipe in `animaxxing`: clip-path image reveals, a mouse-only hover preview, scroll-scrubbed video, and a canvas frame sequence with bounded loading.
- Component motion recipe in `animaxxing`: a full-screen menu overlay, native `<dialog>` enter and exit with Escape, an accordion `disclosure` (the one sanctioned height tween), and a sliding tab indicator.
- Hover effects recipe in `animaxxing`: label rolls, underline sweeps, and image zoom, shared between mouse hover and keyboard focus, never stuck after a tap.

### Fixed

- `gsap-nuxt`: a shared-element morph moves the scroller to the router's destination before playing, since Nuxt's own scroll lands mid-morph from a scrolled page.

## [0.5.0] - 2026-09-23

### Added

- Smooth scroll recipe in `animaxxing`: Lenis and ScrollSmoother behind one set of controls, stepped with ScrollTrigger, with native controls under reduced motion.
- Page covers recipe in `animaxxing`: a curtain that covers a route swap and turns back when interrupted, and a first-visit preloader that follows real readiness.
- Layout Flip recipe in `animaxxing`: filter, reorder, and expand animations, and shared-element morphs across pages.
- Shared framework references `smooth-scroll.md` and `transition-archetypes.md`, packaged into every framework skill, with framework-specific integration for scrollers, curtains, preloaders, shared elements, and Flip in each render cycle. Reference apps in all seven frameworks now implement the scroller, a curtain, and a shared-element morph against a common spec in animaxxing-skills-test, and the guidance was corrected wherever they found it wrong or missing.
- Pause controls for every ambient loop (WCAG 2.2.2): the wave's stop function carries `pause()` and `resume()`, and particle controls add `pause()` and `play()`. Follower and wave guidance covers off-screen and user pausing.
- `revertText(element)` in split entrances restores a runner's target when the controller kills a parent timeline, which never reaches a nested runner's interrupt callback.

### Fixed

- A recipe setup that throws no longer leaves its GSAP context current. Previously every later tween, trigger, and split in the app was recorded by the failed context.
- `scrambleIn` and `scrambleOut` register ScrambleTextPlugin; they only logged a missing-plugin warning and never scrambled.
- A new split runner on an element stops the previous run first, so the old run can no longer complete late, revert the new split, or fire its completion.
- Particle `blast()` or `exit()` during an entrance releases the particles it was steering, and `idle()` after that blast lands the target at its entered state. `destroy()` is final, even for delayed callbacks, and restores the target's inline styles.
- Particle colors follow theme changes without clearing the canvas, including `prefers-color-scheme`.
- `revealOnScroll` hides waiting items with opacity only, so they stay in the accessibility tree and the tab order; focusing one reveals it.
- `horizontalRun` scrolls the page for keyboard focus only, not mouse clicks.
- `pinnedScene` teardown restores only the elements its tweens animated, leaving other effects' inline values alone.
- `dragTrack` lands on the nearest item under reduced motion.
- `countUp` reads the locale's decimal mark, so `99.999%` and `0.125` count correctly. Counting digits are hidden from assistive technology beside a visually hidden final value, and an existing `aria-label` is left alone.
- A wave stopped with `keepSplit` hands its letters over at rest. Blast-off's shake picks new offsets on each repeat.

## [0.4.0] - 2026-09-23

### Added

- SVG effects recipe in `animaxxing`: stroke drawing in and out, icon morph toggles, and a path follower.
- Counters and marquees recipe in `animaxxing`: count-up figures that keep their formatting and reserved width, and a seamless marquee with accessible clones and pause controls.
- Pointer effects recipe in `animaxxing`: magnetic pull, tilt with pointer position variables, a cursor follower, and a drag-and-throw track, mouse-only where decorative and keyboard- and touch-safe for the track.
- Scroll effects recipe in `animaxxing`: reveals, scrubbed statements, parallax, pinned scenes, horizontal runs, a progress rule, and velocity skew, with rollback, reduced-motion fallbacks, and keyboard support for horizontal runs.

### Fixed

- Text and particle recipes roll back their own setup when construction throws: split entrances, route letters, speak-in, wave, blast-off, and particle attachment. Killing a split entrance or scramble mid-run restores the text.
- `dragTrack` stops InertiaPlugin's velocity tracker on revert, which otherwise wrote inline transform properties after restore.
- `particle-effects` compiles as one module: `ignite` declared a second `EMBER_RATE`, now `RULE_EMBER_RATE`.

### Changed

- Motion verification points at the `motion/` suite in animaxxing-skills-test, which now type-checks and runs every recipe.
- Framework scroll guidance warns that reverting scrubbed triggers can leave inline start values, notably with `invalidateOnRefresh`, and shows how to restore them.

## [0.3.4] - 2026-09-15

### Added

- Shared device guidance in every framework skill: capability tiers, touch, viewport changes, performance budgets, and verification.
- Editable particle density for coarse pointers; outlines and owned particles are preserved.

### Changed

- Particle input tracks hover, touch presses, and keyboard focus without sticky tap states or repeated bursts.
- Framework and motion checks cover phone widths, touch, and reduced motion.
- Framework rules limit `will-change` to active animation and select tiers by capability.
- `scripts/sync_initialization.py` packages all shared Markdown references.

## [0.3.3] - 2026-09-14

### Changed

- Clarified data readiness separately from motion initialization across all framework skills, including authentication, dependent queries, loading geometry, and connection notices.
- Added Next.js integration and verification for staggered data arrival, stable page chrome, and entrances that do not replay on ordinary updates.
- Routed the core `animaxxing` skill's loading-flash guidance to the framework owner.

## [0.3.2] - 2026-09-12

### Changed

- All seven framework skills preserve invisible intros while requiring bounded initialization, partial-setup rollback, per-visit recovery, and stale-work cancellation.
- Added framework-specific recovery integration and failure checks, plus sourced guidance on rendering, indexing limits, and first-load LCP.
- Motion recipes now require effect restoration when adapted; styles delegate recovery to the framework.
- Packaged one maintained initialization reference inside every framework skill. Repository validation checks synchronization.

## [0.3.1] - 2026-09-12

### Changed

- Renamed `motion-animaxxing` to `animaxxing` so the core animation skill appears first in the installer.
- Renamed `aesthetic-animaxxing` to `style-animaxxing` for visual design and motion art direction. Framework, motion, and style responsibilities remain unchanged.
- Updated skill metadata, composition references, contributor guidance, and the README/index to use the new names and lead with the core animation skill.

### Migration

- Replace installed `motion-animaxxing` and `aesthetic-animaxxing` entries with `animaxxing` and `style-animaxxing`, respectively. Existing copied application modules and recipe APIs are unchanged.

## [0.3.0] - 2026-09-12

### Added

- `motion-animaxxing`: independently installable vanilla TypeScript and GSAP text and particle recipes, with effect selection, font and SplitText requirements, and technical verification. Effects preserve the consuming project's fonts, palette, and layout.

### Changed

- Split responsibilities into three families: framework skills own lifecycle, motion skills own reusable effect implementations, and aesthetic skills own visual design and motion art direction.
- `aesthetic-animaxxing` keeps its tokens, typography, layout, pacing, and surface choices, and composes `motion-animaxxing` for the full treatment. Static and minimal-motion restyles have explicit scope guidance.
- Moved the seven recipe files and generic SplitText stability/verification guidance from the aesthetic into the motion skill. Recipe builder signatures and TypeScript implementations are unchanged; particle markup now inherits the consuming app's color instead of requiring an aesthetic token.
- Documented adaptation of weight ranges to existing variable fonts and alternatives for static fonts.
- Updated discovery metadata, installation/composition and migration guidance, contributor instructions, and plugin manifests for all three families. Repository link validation now covers nested skill references.

### Migration

- Install `motion-animaxxing` alongside `aesthetic-animaxxing` and the matching framework skill to retain the full animated treatment. Recipe reference paths now belong to the motion skill; existing copied application modules do not need migration.

## [0.2.2] - 2026-09-08

### Fixed

- Character-animation guidance now keeps scoped kerning settings consistent across SplitText setup and revert to prevent horizontal snaps.
- Split entrance recipes accept an optional scoped character-mask class for confirmed glyph clipping, preserving animation timing, accessibility, and cleanup.

### Changed

- Typography diagnosis distinguishes kerning shifts from clipped glyph ink, late fonts, ligatures, wrapping, and other geometry changes.
- Verification compares glyph appearance and character positions across cleanup, checks both reveal directions, and covers desktop, mobile, reduced motion, and interruptions.

## [0.2.1] - 2026-09-04

### Added

- `aesthetic-animaxxing`: the resize policy. A settled width change remounts the page and replays its entrance; height-only changes are ignored; the wave stops the moment a headline reflows.

## [0.2.0] - 2026-09-04

### Added

- An aesthetic skill family. Each `aesthetic-<name>` skill carries one complete look as design tokens, typography and layout grammar, a motion vocabulary, and portable vanilla TypeScript plus GSAP effect recipes, and hands its motion to a framework skill's lifecycle.
- `aesthetic-animaxxing`: the Animaxxing look. Monochrome tokens in plain CSS and Tailwind v4 with light and dark schemes, Rethink Sans and JetBrains Mono type roles, the twelve-column editorial layout grammar, and recipes for split-text entrances, the scattering-letters route intro and outro, speak-in paragraphs, the letter wave, the blast-off outro, the particle field, and the marquee, reactor, resolve, slipstream, and ignite particle treatments.

### Changed

- Contributor guidance distinguishes framework skills (portable, design-free) from aesthetic skills (one design, framework-free, never owning lifecycle).
- Plugin manifests describe both families.

## [0.1.0] - 2026-09-04

### Added

- Framework-specific GSAP lifecycle skills for vanilla sites, Astro, SvelteKit, Nuxt, React Router, TanStack Router, and Next.js App Router.
- Claude Code and Cursor plugin manifests.
- Codex display metadata for every skill.
- Automated validation for skill structure, manifests, links, and CLI discovery.

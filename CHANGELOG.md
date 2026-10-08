# Changelog

All notable changes to Animaxxing Skills are documented here. Releases follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.38.0] - 2026-10-08

### Fixed

- `writeOn` parked each stroke at the end of its line, where the stroke's round cap still uncovered the line's last letters. Paused before writing, as when it waits to be scrolled to, a note showed the ends of its lines. Strokes now park past the cap's reach.
- `pinnedScene` keeps its lint note on the `let` a closure reads before it is assigned.

### Changed

- Print effects advise building a scroll-triggered effect at setup, paused, and playing it on view, so the finished content never shows first.

## [0.37.0] - 2026-10-08

### Fixed

- `scrubStatement` clamps its range to the scroll. A statement near the page's end, whose bottom can never rise to 45% of the viewport, used to stop partway, its last words still faded. It now finishes at the bottom of the scroll.

## [0.36.0] - 2026-10-08

### Added

- `topple`: a row of dominoes. A push runs down the row, each falling onto the next, until the last lies flat and the rest lean along the row. Only the falling one is stepped; every domino behind it is placed to lean exactly against its neighbor, so the row never passes through itself.
- `pageTurn`: a book you leaf through. Drag a page across the spine, or use the arrow keys, and the leaf turns about the spine in 3D, its shading deepening as it stands on edge. Released short of the spine, it falls back.

## [0.35.0] - 2026-10-08

### Added

- `pile` takes fixed `pegs` that pieces bounce off, and upright `walls` standing on the floor, `wallHeight` tall, for a Plinko board. A piece that crosses a wall in one step is sent back to the side it came from.
- `swing`: a sign hanging from a hook swings when dragged, flicked, tapped, or pushed from the keyboard, each swing smaller until it hangs still. It sleeps once at rest.
- `swipeDismiss` takes `look`. `slide` is the old motion. `tilt` leans with the drag, shows a label for the side it's going, and flings off turning. `fold` folds away from its top edge.

## [0.34.0] - 2026-10-08

### Added

- `slingshot`: pull a handle back and let go to fling the pile's next piece the opposite way, harder the farther it was pulled. Dots preview the arc while aiming. Arrow keys aim and Enter fires. The handle springs back and never leaves the box.
- `pile` takes `ceiling`, so thrown pieces bounce off the box's top, and gains `launch(x, y, vx, vy)` and a readable `gravity`.

## [0.33.0] - 2026-10-08

### Added

- `tabIndicator` takes `stretch`: the leading edge reaches the new tab first and the trailing edge catches up.
- `panelSwap`: tab panels slide with the direction of travel, the old one out and the new one in from the side the indicator moved toward. The new panel waits until the old one has mostly gone, so the two never overlap to read.
- `stateButton` celebrates and refuses more clearly. On success the button pops as the check draws and sparks burst from its edge (`sparks`, 0 for none). On error the spinner snaps into a cross that draws stroke by stroke, and the shake tilts.

## [0.32.0] - 2026-10-08

### Fixed

- `headerSection`'s label CSS anchors both names to the label's fixed edge. While two names cross, they share a cell as wide as the wider one, so on a label at the header's right, the old start alignment made the outgoing name jump sideways whenever the new one was longer or shorter.

## [0.31.0] - 2026-10-07

### Added

- A pulse and ambient recipe.
  - Pulses beat a few times, then rest: `ping` spreads rings from a dot, `heartbeat` thumps twice, `bump` pops a badge as its count changes.
  - Ambient loops start paused and end each cycle where they began: `float`, `drift`, `breathe`, and `orbit`.
  - `watch` plays loops only while their section is on screen and the visitor has not paused them, drives the pause button, and keeps them still under reduced motion.

## [0.30.0] - 2026-10-07

### Added

- A rule: text keeps its line breaks from first paint to rest. Wait for the faces before measuring or splitting, never tween letter-spacing, width, or weight on wrapping text, and animate a paragraph as one block unless its split lines match the resting breaks. Verification already had the check; the rule now applies before anything is built.

## [0.29.0] - 2026-10-07

### Added

- `melt`'s `form` takes `from: "top"`: drops swell on the element's top edge, let go, and fall into the shape, for a name that drips in from the top of its frame.
- Verification checks that line breaks never move while text animates, with the three usual causes: a face that loads after layout, a line split that wraps differently from the resting text, and letter-spacing, width, or weight tweened on wrapping text.
- Verification notes that a reveal triggered by its section plays before it is seen when the element sits well below the section's top.

### Changed

- Print effects advise inking a paragraph as one target rather than split into lines.

## [0.28.0] - 2026-10-07

### Added

- A doorways recipe: three moves built on one arch shape.
  - `archReveal`: a point at an arch's foot draws the arch open, then the picture grows out of it to fill the frame. With `out`, it closes back down to the point.
  - `doorwayPassage`: as a track scrolls, a doorway in a picture lights up, and a mask shaped like it grows over the stage, showing the next picture inside. Scroll drives it, so stopping holds the frame and scrolling back retraces it.
  - `shapeFlight`: a picture flies from one frame to another and turns from a rectangle into an arch, or back. The rectangle is the arch's own polygon with each point pressed onto the nearest edge, so one shape tweens into the other. Only the clip and transforms move: neither frame changes size, and the picture is never stretched.
  - `archPolygon` shapes an arch frame in CSS that a flight can land in.

## [0.27.0] - 2026-10-07

### Added

- Framed views take `clip`, an element the drawing never paints outside. The canvas is fixed to the viewport, so a view inside a box that scrolls on its own drew past the box's edges as it scrolled out. Flight, morph, liquid image, and melt pass it through.
- `pourStream` takes `scroller`, for a column inside a box that scrolls on its own. The head follows that box's view rather than the window's, and the drawing stays inside the box.

## [0.26.0] - 2026-10-07

### Added

- `sortable` takes `grab: "item"`, so the pointer can drag a row from anywhere on it, for short rows where a handle is a small target. The handle keeps the keyboard either way.

## [0.25.0] - 2026-10-07

### Added

- Three more line reveals in split entrances: `linesSlideIn` and `Out` (sideways from behind the masks, alternating sides), `linesWipeIn` and `Out` (a straight edge across each line), and `linesIrisIn` and `Out` (a circle opening from each line's middle).

### Changed

- `linesEllipseIn` and `Out` read as their own move now. The arch was so wide and quick on a short line that it looked like `linesMaskIn`. It now opens from a point into a tall arch, slower, with the line lifting only a little, so the curve stays in view.

### Fixed

- Shaped line reveals centered on each line's mask, which spans the block's full width, so a short line opened beside its words. They now center on the line's own text, measured from its text nodes.
- A clip-path written with `toFixed` can read "533.0px", and GSAP then leaves it uninterpolated: the shape sits still and jumps at the end. Values are rounded instead.

## [0.24.0] - 2026-10-07

### Added

- Liquid hovers in hover effects, each moving only by transforms and knowing where the pointer crossed:
  - `beadUnderline`: a bead of ink lands where the pointer enters, stretches into the underline, and pulls back into a bead at the exit.
  - `pourFill`: a round control fills like liquid poured from the side the pointer came from, wobbles, and drains out the side it leaves by.
  - `jelly`: a button squashes and springs like jelly, with a highlight that follows the pointer.
- `pourReveal` in media effects: content pours into its frame through a wobbling blob that spreads from a point, and drains back with `out`. Only `clip-path` and the inner scale move.
- Metaballs, a new `animaxxing-webgl` recipe: liquid-metal drops that merge as they touch, shaded as polished metal in the element's own color.
  - `melt`: one bead swells, drops run out to their places on a shape, and the shape fills in under them; `drip` lets it fall apart. `drawText` makes a word the shape.
  - `pourStream`: a stream pours down a column beside a list as the page scrolls, its head following the reader, and a drop settles beside each row it reaches; it pools at the bottom.

### Changed

- A framed view's poster may be any element, such as the live text a melt draws.

## [0.23.0] - 2026-10-07

### Added

- Print effects gain two more:
  - `writeOn`: live text is written on by a brush, one rounded, slightly wavy stroke per line, through an SVG mask that is removed at rest.
  - `pullCorner` and `dragPull`: a sheet's corner lifts and folds back along a diagonal, showing the paper's back, and peels off under a pointer or finger, or on Enter. The sheet's content never changes; only its clip does.

## [0.22.0] - 2026-10-07

### Added

- Print effects, a new recipe borrowed from printmaking:
  - `paintReveal`: a cover in the paper's color wears away with a dry-brush edge, optionally led by a roller such as a brayer. Each pixel gets a fixed threshold once; GSAP tweens one number, through a setter, so scrubbing and seeking paint too.
  - `inkText`: live text inks in through a grainy SVG mask. The HTML is untouched, and the masks are removed at rest.
  - `registrationSlip`: an `aria-hidden` second impression lands out of register behind a heading and snaps true.
- `charsSlideIn` and `charsSlideOut`: letters zip together from above and below, alternating.
- `zoomThrough` `push` and `pull` modes: the camera flies into one tile of a grid until it fills the section, or opens on that tile and pulls back to the whole grid.

### Fixed

- `pathLoop` on a `<textPath>` without `startOffset` logged an invalid empty length; it now sets `0%` first and removes it on revert.

## [0.21.0] - 2026-10-06

### Added

- `morphSequence` in SVG effects: a path flows through several shapes in order, resting on each, and with `loop` ends back on its own shape so it repeats seamlessly. It returns a paused timeline for the controller to play, repeat, or scrub; reduced motion keeps the authored shape. `morphToggle` still covers two-state icons.

## [0.20.1] - 2026-10-06

### Fixed

- Scene flight ended past its last image, so the end of a scroll range showed an empty view. `uTravel` 1 now stops in front of the last image, where the first sat at 0.

## [0.20.0] - 2026-10-06

### Added

- `animaxxing-webgl` grows past images. Framed views draw a WebGL drawing in an element's box on the shared stage, rendered offscreen with its own camera and depth, with a **poster** `<img>` as the accessible content and fallback, just as an image plane keeps its `<img>`.
  - Scene flight: a camera flies through a 3D spiral of images with perspective and fog, on one `uTravel` uniform that a timeline or `scrollFlight` drives; `pointerLean` tilts it toward the mouse.
  - Particle morph: thousands of GPU points move between shapes made from text, an image's ink, a sphere, or scatter, each leaving on its own delay. Each shape fits the element by its own width and height, so a wide word and a round sphere both fill it. `uScatter`, `uSpin`, and `pointerPush` round it out.
  - Liquid image: the pointer drags trails through an image that bend it and split its color slightly, and fade back to rest. `pour()` sweeps one stroke for an intro. Its flow map uses 8-bit targets that every device supports, and rounds down half a step each frame so trails settle fully at any frame rate.
- Test suite: `webgl-views.spec.ts` covers posters, fallbacks, context loss, sleeping off screen, balanced GL resources including framebuffers and renderbuffers, and sampled pixels for each recipe.

### Changed

- `textureSource` in image planes is exported, so other recipes load image textures the same way.
- The skill's description no longer rules out 3D scenes and particle systems; it still rules out glTF models and physics.

## [0.19.2] - 2026-10-06

### Changed

- A broad request whose feel the project's cues already settle gets a plan in a line or two, then the build, without a question. The skill asks once only when the cues don't settle the feel or the scope. Before, the main skill said to ask whenever the scope was unclear, while Finding the vibe said to ask only when the cues were thin; a live test showed agents following the guide.

## [0.19.1] - 2026-10-06

### Fixed

- Finding the vibe was unreachable in a live test. A mood request ("make the landing page feel more premium") loaded only the framework skill, and a loaded `animaxxing` built without reading the guide. Now:
  - The `animaxxing` description names finding a feel, and narrows its exclusion from "branding, redesign" to "visual redesign", so a request about feel is not read as branding.
  - "Choose the scope" sends a request for a feel, or one that names no effect, to the guide before any effect is chosen, and folds an open feel into the one scope question.
  - Each framework skill points to `animaxxing` for what moves and how it feels, when it is installed.

## [0.19.0] - 2026-10-06

### Added

- Finding the vibe: a short reference for when the feel of the motion isn't settled, a full treatment, a new project, or a user describing a mood. Read the feel from the project and find out what the user wants animation to do, then let that shape the choices. Considerations, not presets. At most one question, folded into the scope question when both are open. Skipped for named effects and for the `style-animaxxing` look.

### Fixed

- The routing table's hover effects row had lost its link, which had landed on the shake row, so label rolls and underline sweeps routed nowhere. The repository check now fails on any table row whose column count differs from its header.

## [0.18.1] - 2026-10-05

### Fixed

- With `touch`, a finger's enter arrives just before its press, so it was ignored. `magnetic` now measures its center at the press, so a finger leans it a little instead of from a stale center. `tilt` measures its card there too, and `hoverPreview` shows the pressed row at once, without waiting for a move.

## [0.18.0] - 2026-10-05

### Added

- Touch for hover and cursor effects. A `touch` option on `magnetic`, `tilt`, `spotlight`, `momentumHover`, `proximity`, `imageTrail`, `hoverPreview`, and the WebGL `hoverDistortion`, and a `touch` area on `cursorFollower`: a finger or pen held down moves like the mouse, and lifting it is leaving. The element claims its touch gestures, so use it on contained surfaces, not content people scroll past.
- `textRoll`, `underlineSweep`, and `imageZoom` take `touch`: a finger held on the control shows the hover until it lifts or a scroll cancels the press. Nothing sticks after a tap.
- `pile` in physics effects: pieces fall into a box, bounce off its floor, walls, and each other, and come to rest in a heap. Sleeping pieces stop the heap from buzzing.

### Changed

- `pressFeedback` turns off the browser's tap highlight on its control, since its squash and ripple are the touch response.

## [0.17.1] - 2026-10-05

### Fixed

- Scroll effects explain ScrollTrigger's scroll memory across client route changes: its refresh can put back the previous page's position, clamped to the new page's height. Keep positions yourself, restore once the page is drawn, and reapply after each refresh until the visitor scrolls.
- The Next.js navigation guide no longer limits the wrong scroll restore to `cacheComponents`: with ScrollTrigger on the page it happens without it too.

## [0.17.0] - 2026-10-05

### Added

- `headerShrink`: a tall header condenses into a slim bar over the first stretch of scroll. Its backdrop shortens, the wordmark scales and can condense, the nav rises. Transforms and font axes only, scrubbed, so nothing below reflows.
- `headerSection`: the header's label rolls to the name of the section beneath it, up going down and down going up.

## [0.16.0] - 2026-10-05

### Added

- `dialogMotion` takes `from`: the dialog opens as a circle growing out of that element, usually the button that opened it, and closes back into it. A clip, so the text inside never stretches; it clears at rest.

## [0.15.3] - 2026-10-04

### Added

- Scroll effects explain nested scrollers: a pin inside an element that scrolls on its own hops a frame behind native scrolling. Drive the element with `lenisScroll({ wrapper, content })`.
- Smooth scroll shows `lenisScroll` on one element instead of the window.

## [0.15.2] - 2026-10-04

### Added

- `revealOnScroll` takes `repeat`: scrolling back up past an item sends it out again, quick and straight, and it rises again on the way down. The default still reveals once.

## [0.15.1] - 2026-10-04

### Changed

- The ripple's ring is wider and stronger, so it reads at a glance on a full image; it still rests flat.

## [0.15.0] - 2026-10-04

### Added

- `dissolve`, `pixelate`, and `ripple` in `animaxxing-webgl` uniform effects, on new `uDissolve`, `uPixelate`, and `uRipple` uniforms: an image appears grain by grain, resolves from coarse blocks in clear steps, or rides one ring out from the center. Each is flat at rest.

## [0.14.1] - 2026-10-04

### Changed

- The recipe contract says to park start positions with `gsap.set` or `fromTo`, never with a CSS transform the tween also moves, and verification traces covers' computed transforms. A CSS `translateY(100%)` start makes GSAP stop every panel a full height short.

## [0.14.0] - 2026-10-04

### Added

- `charsImplodeIn` and `charsExplodeOut` in split entrances: characters rush in from straight out of the line's center and slam together, or blow apart the same way.

## [0.13.1] - 2026-10-04

### Changed

- Scramble keeps each character's kind: capitals cycle through capitals, lowercase through lowercase, digits through digits, and punctuation stays blank until it appears. Frames come from the timeline's time, so scrubbing and replays repeat. It no longer needs `ScrambleTextPlugin`.

## [0.13.0] - 2026-10-04

### Added

- `fontAxisHover` in hover effects: a word in a line of words gains weight or widens on hover or focus while its box holds its exact resting width, so no neighbor moves and no line rewraps.
- Text stability covers weight and width moves in running text: make words `inline-block` at rest, hold exact widths since GSAP rounds pixel widths, and keep separators with the word before them. Verification adds running text checks.

## [0.12.1] - 2026-10-04

### Fixed

- `swipeDismiss` measures a flick only from the last ~100ms before release, so a fast drag that stops short springs back instead of dismissing.

## [0.12.0] - 2026-10-04

### Added

- Sortable recipe: a vertical list reordered by dragging a handle or from the keyboard, with neighbors sliding aside, a live region, and `onReorder`.
- `swipeDismiss` in pointer effects: an item thrown away sideways past a distance or with a flick, the gap closing behind it, with button and Delete key paths.
- `stateButton` in component motion: a button's label lifts away for a spinner, a success finishes the turn and draws a check, a failure shakes, and a status announces each result, without the button changing size.
- Press feedback recipe: `pressFeedback` squashes a control under a press and springs it back, with an ink ripple from the press point, for mouse, touch, pen, and Enter and Space.
- `shake` in the motion vocabulary's new Accents section: a damped side-to-side swing for errors, paired with the error text.
- `spotlight` in pointer effects: a circle reveals a second layer under the mouse, a held touch, or keyboard focus.
- `directionalFill` in hover effects: a fill enters from the edge the mouse crossed and leaves by the exit edge, with focus and tap paths.
- `stackCards` and `zoomThrough` in scroll effects: cards pin into a shrinking deck as they scroll, and a word or frame grows from a focus point (or opens from a clip window) until the reader passes into the next scene.
- `pathScrub` and `pathLoop` in SVG effects: text on a `textPath` slides along a curve with scroll, or turns around a two-lap closed path with pause controls.
- Typewriter recipe: `typeIn` and `typeOut` type and delete an element's text behind a caret at a human rhythm without moving the layout, and `retype` cycles one word through a list, stopping on the last.
- `glitchIn` and `glitchOut` in split entrances, with six types: `slice`, `blocks`, `skew`, `ghost`, `weight`, and `scanline`. Jumps are stepped at twelve a second and never blink; the original text stays readable under `aria-hidden` copies.
- `glitch` in `animaxxing-webgl` uniform effects: bands and blocks of an image jump sideways on a new `uGlitch` uniform, with `enter`, `exit`, and `burst`.
- `odometer` in counters and marquees: digit columns roll to each new value, forward through 9 to 0 when rising and back when falling, continuing from mid-roll when interrupted, with the latest value read once by assistive technology.

### Changed

- Recipes that restore a `style` attribute exactly read it before removing it, since Chrome can write a just-cleared inline style back as `style=""`.
- The `animaxxing` description groups its effects by input (text, scroll, pointer, drag) and stays under the 1,024 limit with the new effects at 955 characters. `skills/llms.txt` keeps the full trigger list.
- `scripts/validate_repository.py` checks that each skill's `name` matches its directory and its `description` is 1 to 1,024 characters.

## [0.11.0] - 2026-10-03

### Added

- Plain-CSS equivalents in `style-animaxxing`: `plain-css.md` replaces the Tailwind class strings in typography and layout, and `tokens.md` declares the font, spacing, radius, and border variables for apps without Tailwind.
- Browser verification CI runs the seven framework suites and the motion suite in a matrix. Manual runs accept a `companion_ref` branch or commit for coordinated changes across both repositories, and failed jobs keep browser traces.

### Changed

- `animaxxing` has a full treatment. When the user says "we're animaxxing", every element enters from a blank first paint, rests static or ambient, and leaves on every requested navigation, keeping the brand. A named effect still adds only that effect, and an unclear request gets one question.

### Fixed

- Inline-style snapshots keep each declaration's priority, so authored `!important` values survive teardown in every recipe that records and restores styles.
- `blastOff.revert()` preserves authored transforms, filters, and CSS priorities after an interruption, a full run, or reduced motion, including repeated teardown.
- A throwing particle factory or observer attachment rolls back target styles, canvas attributes, tweens, and listeners. A throwing treatment cleanup no longer skips the remaining restores, and later controls and queued resizes stay inert.
- `dragLoop` brings the real item into view for keyboard focus, even after a clone set wraps or while a wheel snap or throw is pending.
- The `scrollDirection` example header stays on screen while it holds focus.
- `animaxxing-webgl` image planes follow computed `visibility`, including a hidden wrapper. A hidden image still resolves readiness, so revealing its wrapper draws the plane without a flash of the DOM image.
- The `animaxxing-webgl` hover lens uses an increasing `smoothstep` edge, as GLSL requires. The reversed edge it replaced has undefined results in GLSL.

## [0.10.0] - 2026-09-24

### Added

- `enterExit` in component motion: one timeline holds an entrance and a different exit, split by `addPause()`. Closing mid-entrance reverses it at `reverseSpeed`, and reopening mid-exit returns to the open rest. An `easeReverse` option (GSAP 3.15+) gives reversals their own ease, and the closed state paints at build even before GSAP's first tick.
- Interruption guidance in the motion vocabulary: when to rebuild a timeline and when to reverse one, `easeReverse` pairings for overshoot eases, and the 3.15 version gate.
- `proximity` in pointer effects: items scale, and optionally lift, by the mouse's distance, shaped by a `falloff` ease. With `axis: "x"` and a bottom origin it makes a dock; hit areas stay still while `[data-proximity-target]` children scale. Mouse only.
- `scrollWaypoints` in scroll effects: one element `Flip.fit`s onto a `[data-waypoint]` marker in each later section, landing as that marker reaches the viewport's middle. Legs last the scroll between stops, and every ScrollTrigger refresh re-measures from rest.
- `curveCover` in page covers: one SVG shape sweeps across with its edge bowed ahead and flattens as it covers, then carries its trailing edge out the far side. Same `cover` and `reveal` as the curtain, from any edge, turning back when interrupted.
- `linesEllipseIn` / `Out` and `linesHighlightIn` / `Out` in split entrances: lines swell open from an elliptical sliver while rising, and a highlighter bar in `--line-highlight` sweeps each line's words in and retracts.
- `morphScrub` in SVG effects: a path morphs toward an alternate shape as the page scrolls, such as a curved section edge that flattens as its section arrives.
- `runDrift` in scroll effects: `[data-run-drift]` items slide within their frames as they cross a horizontal run, through its `containerAnimation`.
- Curtain `wipe` and `drift` options: panels open and close by `clip-path` polygon instead of sliding, and the content wrapper travels with the sweep so the outgoing page is pushed away and the incoming page trails in.
- Masked frames for `imageReveal`: a CSS `mask` in a brand shape combines with the wipe.

## [0.9.0] - 2026-09-24

### Added

- Momentum hover in `animaxxing`'s pointer effects: a fast mouse sweep knocks items along its path with InertiaPlugin and spins them by where they were struck, then they settle. Each item is a still hit area with a moving target, so a target never slides out from under the pointer and gets struck again. Mouse only.
- Image trail in pointer effects: images spill along the mouse path, drift with its motion, and shrink away, capped at a set number alive. Copies are `aria-hidden` with empty `alt`.
- Cursor follower `label` option: over `[data-cursor-text]`, the dot gives way to a pill scrolling that text, looping two copies by one copy's width like the marquee.
- Flick cards in the endless drag recipe: a fanned card stack that wraps; a drag past a threshold or a quick flick deals the next card to the front. Only the front card is reachable by Tab; arrow keys, `next`, `prev`, and `toIndex` take the shortest way round, and a click on a leaning card brings it forward.
- Physics effects recipe: `burst` and `burstFrom` fire confetti from a point, and `rain` drops emoji or icons over a layer, all with Physics2DPlugin. Pieces live in one `aria-hidden` shell layer, share a 120-piece budget (60 on coarse pointers), and remove themselves. Reduced motion spawns nothing.
- `navTheme` and `scrollDirection` in scroll effects, one ScrollTrigger each: the header mirrors the `[data-nav-theme]` section beneath its middle, and the root carries `data-scroll-direction` and `data-scroll-started` for a header that hides going down. Both run under reduced motion; CSS drops the transition.
- `logoCycle` in counters and marquees: grid cells swap one at a time with a hidden pool of logos, moving real elements, with pause and play.
- Curtain `tilt` and `title` options: panels lean in and tip out the other way, and `cover(title)` shows the incoming page's name while covered.
- `revealOnScroll` gains `scale`, `rotation`, and `ease` for pop-in stickers; `parallax` gains `start` and `end` for a footer revealed from under the page. Defaults are unchanged.

## [0.8.0] - 2026-09-23

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

# Effect restoration

Apply this when adapting any recipe. Every recipe rolls back its own setup when construction throws (`guarded` or `own` in each module) and reverts on interruption where its return shape allows; keep that when copying. The recipes do not own the complete failure boundary. The installed `gsap-<framework>` skill owns initialization deadlines, visit tokens, navigation, and recovery timing. Its controller needs rollback registered before effect setup, not just a handle returned afterward.

## Builder guarantees

- Capture original values only for properties and DOM the effect changes. Preserve existing inline styles, accessible text, nested links, and controls.
- Acquire resources inside a guarded setup block. Register each disposer immediately after acquisition, before the next operation can throw. A split created before a later tween fails still needs reverting.
- On a construction exception, stop acquired work, undo partial changes, then rethrow for the framework to settle its owner. Attempt every disposer even if one fails. Do not wait for an `onComplete` that will never run.
- Return an idempotent teardown or register one with the controller. Existing timeline-only builders need context ownership plus explicit teardown for non-GSAP resources; `timeline.kill()` alone is not DOM restoration.
- Stop writers before restoring values: timelines, delayed calls, tickers, resize/font observers, and pointer/focus listeners. The controller invalidates async work before invoking teardown.
- Revert nested splits inside out. Use plugin revert handles on isolated text leaves. SplitText revert reconstructs descendants from saved HTML; it does not preserve their node identity or attached listeners. Keep framework-bound children and controls outside the split target, or animate a separate visual copy while preserving accessible controls. Never restore a framework subtree with your own saved `innerHTML`. Restore ARIA changes and avoid duplicate accessible text.
- Undo effect-owned masks, clipping, child opacity, transforms, weight, pinned widths, and suspended CSS transitions. Preserve normal hidden states and unrelated application styles. Avoid blanket `clearProps: "all"` in shared targets.
- A disposer does not navigate, release route locks, focus another page, replay ambient effects, or decide which page becomes visible. It restores its changes; the controller applies the correct settled or end state afterward.

## Recipe-specific resources

| Recipe | Teardown must cover |
|---|---|
| Split entrances / route letters | Timelines, every split, masks, original item styles, and any suspended CSS transition. |
| Speak-in | Nested word/character splits, persistent tilt/weight finishes, widths, and timeline callbacks. |
| Wave | Scheduled next cycles, active tweens, splits, pinned glyph widths, and inline weight. |
| Scroll effects | Triggers, pin spacers, splits, scrubbed and reveal tweens, the settle tween, focus listeners, the run's `overflow`, and inline motion values a pinned revert leaves behind. Inner `containerAnimation` triggers first. |
| Pointer effects | Listeners, `quickTo` values left inline, `--pointer-*` properties, the `Draggable` and any throw in flight, its inline touch and selection styles, observers, and the viewport's `overflow`. |
| SVG effects | Draw timelines, stroke dash styles, the original `d` of a morphed path, the follower's transform and origin, and any morph in flight. |
| Counters and marquees | The count tween, original text, reserved width, the counting and visually hidden spans, the marquee strip and clones, observers, listeners, and the hover ease. |
| Blast-off | Tweens and splits across the composition, including container transforms and button changes. |
| Particle field/effects | Ticker callbacks, emitters, particles/tweens, delayed calls, observers, event listeners, effect-owned canvas/wrapper styles, and the target's inline opacity, visibility, transform, and clip. |

Reduced motion preserves normal completion without creating unnecessary split or particle resources. Recovery teardown must also be safe when setup returned early or completed already. The controller decides whether essential completion still needs to run once.

# Demo-agent handoff: invisible intro recovery

Implement in the Animaxxing demo separately. Its reported CSS hiding and missing general entrance recovery are static findings, not verified production indexing or performance failures. No demo implementation changed here.

Read installed `gsap-nextjs` references `initialization.md` and `motion-system.md`, plus `animaxxing` reference `effect-restoration.md`.

- Keep the intended invisible-to-visible intros on successful startup.
- Replace unconditional hiding with early JavaScript-gated CSS and readable server HTML.
- The early script arms recovery without relying on the bundle or GSAP.
- Keep recovery armed through fonts/media, initial writes, splits, and timeline construction.
- Registration is not readiness. Cancel the initialization timer only when the intro can run.
- Register partial rollback before setup. Invalidate stale work, stop writers, revert effect changes, then settle once.
- Guard every late promise, callback, split, and controller entry before writes.
- Track recovery per visit outside disposable React effects. Keep page and shell owners independent.
- Never reveal outgoing, cached hidden, closed, or intentionally hidden content during recovery.
- Preserve reduced-motion completion, focus, navigation locks, native anchors, and direct route access.
- Reveal primary headings and hero media without unrelated preparation. Measure first-load LCP separately from transitions.
- Run the failure matrix in `initialization.md`. Inspect rendered output without promising indexing or rankings.

## Framework audit

| Skill | Existing safeguard | Gap addressed |
|---|---|---|
| Vanilla | Early marker, bounded claim wait, late-controller fallback, preparation-failure wording | Partial rollback, continued preparation deadline, owner isolation, stale callbacks |
| Next.js | Readable no-JS rule; navigation reference had a claim-only timer | Setup failure, effect replay, streaming and cached hidden routes |
| Astro | Full-load marker and incoming-document marking | Swap-scoped deadline, failed setup, duplicate hooks, persisted owners |
| Nuxt | Early marker, claim-only timer, `done` and keepalive guidance | Premature phase release, partial setup, hook cancellation and deactivation |
| SvelteKit | Early marker, claim-only timer, navigation interruption | Premature phase release, deferred preparation, reused pages and stale snapshots |
| React Router | SSR marker, claim-only timer, client-only distinctions | Premature phase release, effect replay, loader and blocker ownership |
| TanStack Router | Start `ScriptOnce`, claim-only timer, pending/SSR distinctions | Premature phase release, late ready reports, reused matches and subscriptions |

The shared contract is maintained once and packaged locally into every framework skill. Independent installation needs no sibling skill path. Motion restores effects; styles do not acquire lifecycle logic.

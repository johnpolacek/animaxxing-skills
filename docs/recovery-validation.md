# Recovery guidance validation

Date: 2026-09-12. Skills version: 0.3.2.

## Skills repository

- Audited all seven framework skills, including their navigation and verification references.
- Validated all nine skills with `skills-ref==0.1.1` and the skill-creator validator.
- `npx --yes skills@1.5.23 add . --list` discovered all nine skills.
- `python3 scripts/validate_repository.py` passed manifest versions, relative links, index coverage, and packaged-reference synchronization.
- `git diff --check` passed. `git pull --ff-only` reported up to date.

## Test repository

Repository: `../animaxxing-skills-test`. Regression commit: `342a844`.

`VANILLA_TEST_PORT=4183 pnpm test` passed all 125 Chromium checks against production builds:

| Framework | Passed |
|---|---:|
| Vanilla | 29 |
| Next.js | 16 |
| Astro | 16 |
| SvelteKit | 16 |
| Nuxt | 16 |
| React Router | 16 |
| TanStack Start | 16 |

The new shared checks cover disabled JavaScript, native links, direct route URLs, and bundle failure after observing the early marker. Current references all emit route HTML. No client-only variant was treated as SSR.

`VANILLA_TEST_PORT=4183 pnpm test:vanilla recovery.spec.ts` then passed all 13 strengthened recovery cases, including an active entrance callback failure and cancellation of delayed writes. This rerun covers the final fixture changes after the full suite.

TypeScript passed for the root test suite and the vanilla app, including the recovery fixture. The suite initially lacked its Chromium binary and reused an unrelated app on port 4173. Installed Chromium and reran on port 4183. A direct-route assertion was corrected to use each app's actual anchor URL, including trailing slashes.

## Limits

- The isolated failure fixture validates recovery ordering with real GSAP/SplitText. Font/media preparation uses controlled promise stalls and rejections.
- Injected failures are not yet wired into each framework's actual controller. Framework-specific hydration replay, streaming, cached routes, hook cancellation, and persisted islands still need those tests.
- The fixture does not verify every motion recipe or automatically harden copied recipe modules.
- No production indexing, field LCP, crawler rendering, suspended-tab, or bfcache result is claimed.
- Demo implementation is unchanged. Use the [demo-agent handoff](demo-recovery-handoff.md).

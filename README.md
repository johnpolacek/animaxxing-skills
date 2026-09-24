# Animaxxing Skills

<img src="assets/logo.svg" alt="Animaxxing Skills logo" width="120">

AI agent skills for ambitious, production-ready animation with [GSAP](https://gsap.com), in three composable families. **Framework skills** own routing, rendering, animation timing, initialization recovery, interruption, and cleanup. **Motion skills** supply reusable effects that preserve the project's design. **Style skills** carry a complete art direction: tokens, typography, layout, and a curated selection of motion treatments.

These skills sit above the [official GSAP skills](https://github.com/greensock/gsap-skills), which cover the GSAP API itself. Install both.

[Agent Skills](https://agentskills.io) format. Works with the [skills CLI](https://github.com/vercel-labs/skills), Claude Code, Cursor, Codex, Copilot, and 40+ agents.

## Installing

### npx skills (recommended)

```bash
npx skills add https://github.com/greensock/gsap-skills
npx skills add https://github.com/johnpolacek/animaxxing-skills
```

The CLI auto-detects the installed agent. To target one explicitly, pass `--agent`:

```bash
npx skills add https://github.com/johnpolacek/animaxxing-skills --agent cursor
```

### Claude Code

```text
/plugin marketplace add johnpolacek/animaxxing-skills
```

See the [Agent Skills docs](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/overview).

### Cursor

**Settings → Rules → Add Rule → Remote Rule (GitHub)** and use `johnpolacek/animaxxing-skills`. Or install via `npx skills add` above.

### Clone / copy

Copy the folders under `skills/` into your agent's skill directory:

| Agent | Skill Directory |
|-------|-----------------|
| Claude Code | `~/.claude/skills/` |
| Cursor | `~/.cursor/skills/` |
| OpenAI Codex | `~/.codex/skills/` |
| OpenCode | `~/.config/opencode/skills/` |
| Google Antigravity | `~/.gemini/antigravity/skills/` |

## Skills

### Motion skills

| Skill | Description |
|-------|-------------|
| **animaxxing** | Reusable vanilla TypeScript and GSAP recipes: split-text entrances, scattering headlines, speak-in copy, letter waves, scroll reveals, scrubbed statements, parallax, pinned scenes, horizontal runs, smooth scrolling with Lenis or ScrollSmoother, curtain and preloader covers, Flip layout and shared-element morphs, image reveals, hover previews, scroll-scrubbed video and frame sequences, menu, dialog, accordion, and tab motion, label rolls and underline sweeps, magnetic buttons, tilt cards, cursor followers, drag tracks, endless drag loops and wrapping 2D grids, signature CustomEase curves, full-screen section paging, sound cues, SVG drawing and morphs, count-up figures, marquees, particle buttons/cards/links/fields, and blast-off exits. Includes text stability and effect verification. Preserves existing fonts, colors, and layout; the framework skill owns lifecycle timing |
| **animaxxing-webgl** | GSAP-driven WebGL image effects on one shared [OGL](https://github.com/oframe/ogl) renderer and canvas per document: planes that track each `<img>` through scroll and resize, a hover distortion lens, a scroll-velocity wave, and a reveal or exit wipe, all tweened on shader uniforms. The real `<img>` stays the accessible content and the fallback without WebGL, on context loss, without CORS, and under reduced motion. Caps pixel ratio, pauses off screen and in hidden tabs, and disposes every GL resource on revert. Kept separate so `animaxxing` never depends on a renderer |

### Framework skills

Every framework packages four shared references: initialization and recovery for reliable reveals; device guidance for touch, viewport changes, and performance budgets; smooth scrolling across navigation; and transition archetypes for curtains, first-visit preloaders, shared-element morphs, and a WebGL canvas that persists across routes.

| Skill | Description |
|-------|-------------|
| **gsap-vanilla** | Plain HTML, CSS, and JavaScript sites: initial state before first paint, outro before a link is followed, cross-document View Transitions with `pageswap` and `pagereveal`, the bfcache, prerendering, fetch and swap routers, and Swup, Barba, or Taxi hooks |
| **gsap-astro** | Astro: page transitions under `<ClientRouter />`, outro before the swap through `astro:before-preparation`, cleanup in `astro:before-swap`, initial state on the incoming document, rehooking on `astro:page-load`, `transition:persist` and islands, `transition:animate` versus GSAP, back and forward, prefetch |
| **gsap-sveltekit** | SvelteKit on Svelte 5: page transitions, enter and exit motion across client-side navigation, show and hide of conditional content, scroll-driven effects, GSAP versus Svelte `transition:` directives versus View Transitions, `beforeNavigate` and `onNavigate` outros, page reuse and `{#key}`, back and forward, runes cleanup |
| **gsap-nuxt** | Nuxt 3 and 4: page and layout transitions through the `pageTransition` JavaScript hooks and `done`, what dies when the leave starts, `out-in` versus overlap, page keys and `keepalive`, Nuxt app hooks, scroll and focus, outro before navigation, back and forward, `experimental.viewTransition`, SSR first paint |
| **gsap-react-router** | React Router v7 and v8 (framework, data, declarative modes): page transitions, enter and exit motion, show and hide of conditional content, scroll-driven effects, GSAP versus `viewTransition`, `useBlocker` or intercepted links for navigation holds, transition-aware links, route reuse and `<Outlet>` keys, `useNavigation` pending UI, back and forward, `ScrollRestoration`, SSR and SPA mode first paint |
| **gsap-tanstack-router** | TanStack Router for React and TanStack Start: page transitions, outro before navigation with `useBlocker`, pending components and `pendingMs`, route reuse and `remountDeps`, `router.subscribe` events, back and forward, `viewTransition`, scroll restoration, SSR first paint with `ScriptOnce` |
| **gsap-nextjs** | Next.js App Router: page transitions, enter and exit motion, show and hide of conditional content, scroll-driven effects, GSAP versus React View Transitions, route lifetime under `cacheComponents`, transition-aware links, back and forward, cleanup |

### Style skills

| Skill | Description |
|-------|-------------|
| **style-animaxxing** | The Animaxxing art direction: monochrome editorial design in Rethink Sans and JetBrains Mono, poster-scale type, hairline rules, light and dark schemes, and a curated motion treatment. Tokens in plain CSS and Tailwind v4, type and layout grammar, and surface choices that configure `animaxxing` |

## Composing the skills

| Request | Skills to use |
|---|---|
| Animate an existing brand with these effects | Matching `gsap-<framework>` + `animaxxing` |
| Add WebGL image effects | Matching `gsap-<framework>` + `animaxxing-webgl` |
| Apply the Animaxxing design without animation | `style-animaxxing` |
| Apply the design with minimal motion | `style-animaxxing` + matching framework skill; add `animaxxing` when using its effects |
| Give it the full Animaxxing treatment | All three: framework + motion + style |

Each skill is independently installable; install and load the skills needed for the requested combination. The framework skill owns the lifecycle below, navigation timing, interruption, and cleanup. Motion recipes return timelines or `enter`/`exit`/`blast`/`idle` instances for its controller to call. A style selects and configures those effects alongside its visual design. Load only the references needed for the current task.

Ask the agent to "animaxx it" for the full treatment, or specify "keep our branding" to use the effects alone. Asking for a static restyle does not require GSAP or a motion skill.

### Updating existing installations

In 0.3.1, `motion-animaxxing` is renamed to `animaxxing` and `aesthetic-animaxxing` to `style-animaxxing`. Replace the old installed entries with the new names to avoid duplicate discovery. `animaxxing` appears first in the installer; the optional `style-animaxxing` carries the visual design.

From 0.2.x, the implementations previously inside `aesthetic-animaxxing/references/recipes/` now live in `animaxxing/references/recipes/`. Install `animaxxing` alongside `style-animaxxing` and the matching framework skill for the full treatment. Generic SplitText guidance lives in `animaxxing/references/text-stability.md`, with effect checks in its verification reference. Existing copied application modules are unaffected; recipe builder signatures are unchanged.

## The lifecycle

Every framework skill uses the same model; motion recipes map onto it, and styles select their visual treatment. An animated page or component runs through:

**mount → initial state → intro → settled → outro → end state → unmount**

Mount and unmount belong to the framework. The five phases between them belong to the animation code and happen while the node exists. Each skill explains how its framework decides when those phases run, what can interrupt them, and what must be cleaned up.

## Structure

```text
animaxxing-skills/
  README.md
  CHANGELOG.md
  AGENTS.md              # Guidance for agents editing this repo (CLAUDE.md and GEMINI.md are copies)
  LICENSE
  assets/
    logo.svg             # Marketplace and repository mark
  .claude-plugin/        # Claude Code plugin config (plugin.json, marketplace.json)
  .cursor-plugin/        # Cursor plugin config (plugin.json, marketplace.json)
  .github/
    copilot-instructions.md
    workflows/validate.yml
  shared/
    initialization.md    # Canonical recovery and first-load guidance
    devices.md           # Canonical device tiers, touch, viewport, and budgets
    smooth-scroll.md     # Canonical scroller lifecycle through navigation
    transition-archetypes.md # Canonical curtain, preloader, shared-element, and persistent canvas rules
  scripts/
    sync_initialization.py # Packages every shared reference; validation checks drift
  skills/
    llms.txt             # Skill index for agents (names, summaries, trigger terms)
    animaxxing/
      SKILL.md
      agents/openai.yaml
      references/
        effect-restoration.md # Partial setup rollback and effect teardown
        motion-vocabulary.md # Effect catalog and controller contract
        text-stability.md
        verification.md      # Effect and portability checks
        recipes/
          split-entrances.md
          route-letters.md
          speak-in.md
          wave.md
          blast-off.md
          scroll-effects.md
          pointer-effects.md
          svg-effects.md
          counters-and-marquees.md
          smooth-scroll.md
          page-covers.md
          layout-flip.md
          media-effects.md
          component-motion.md
          hover-effects.md
          section-pager.md
          sound-cues.md
          endless-drag.md
          particle-field.md
          particle-effects.md
    animaxxing-webgl/
      SKILL.md             # Renderer choice (OGL) and the fallback contract
      agents/openai.yaml
      references/
        verification.md    # Fallback, context loss, pausing, and disposal checks
        recipes/
          webgl-stage.md     # One shared renderer and canvas per document
          image-planes.md    # Planes that track each <img>
          uniform-effects.md # Hover lens, scroll wave, wipe
    gsap-vanilla/
      SKILL.md
      agents/openai.yaml
      references/
        page-load.md
        cross-document-navigation.md
        spa-navigation.md
        motion-system.md
        initialization.md # Packaged recovery and first-load contract
        devices.md        # Packaged device and input tiers
        smooth-scroll.md  # Packaged scroller lifecycle
        transition-archetypes.md # Packaged curtains, preloaders, shared elements
        verification.md
    gsap-astro/
      SKILL.md
      agents/openai.yaml
      references/
        client-router-navigation.md
        scripts-and-islands.md
        motion-system.md
        initialization.md # Packaged recovery and first-load contract
        devices.md        # Packaged device and input tiers
        smooth-scroll.md  # Packaged scroller lifecycle
        transition-archetypes.md # Packaged curtains, preloaders, shared elements
        verification.md
    gsap-sveltekit/
      SKILL.md
      agents/openai.yaml
      references/
        sveltekit-navigation.md
        page-lifetime.md
        motion-system.md
        initialization.md # Packaged recovery and first-load contract
        devices.md        # Packaged device and input tiers
        smooth-scroll.md  # Packaged scroller lifecycle
        transition-archetypes.md # Packaged curtains, preloaders, shared elements
        verification.md
    gsap-nuxt/
      SKILL.md
      agents/openai.yaml
      references/
        page-transitions.md
        navigation.md
        motion-system.md
        initialization.md # Packaged recovery and first-load contract
        devices.md        # Packaged device and input tiers
        smooth-scroll.md  # Packaged scroller lifecycle
        transition-archetypes.md # Packaged curtains, preloaders, shared elements
        verification.md
    gsap-react-router/
      SKILL.md
      agents/openai.yaml
      references/
        react-router-navigation.md
        route-lifetime.md
        motion-system.md
        initialization.md # Packaged recovery and first-load contract
        devices.md        # Packaged device and input tiers
        smooth-scroll.md  # Packaged scroller lifecycle
        transition-archetypes.md # Packaged curtains, preloaders, shared elements
        verification.md
    gsap-tanstack-router/
      SKILL.md
      agents/openai.yaml
      references/
        tanstack-navigation.md
        route-lifetime.md
        motion-system.md
        initialization.md # Packaged recovery and first-load contract
        devices.md        # Packaged device and input tiers
        smooth-scroll.md  # Packaged scroller lifecycle
        transition-archetypes.md # Packaged curtains, preloaders, shared elements
        verification.md
    gsap-nextjs/
      SKILL.md
      agents/openai.yaml # Codex display metadata
      references/
        app-router-navigation.md
        motion-system.md
        initialization.md # Packaged recovery and first-load contract
        devices.md        # Packaged device and input tiers
        smooth-scroll.md  # Packaged scroller lifecycle
        transition-archetypes.md # Packaged curtains, preloaders, shared elements
        verification.md
    style-animaxxing/
      SKILL.md
      agents/openai.yaml
      references/
        tokens.md
        typography-and-layout.md
        motion-vocabulary.md # Art direction and surface choices
        verification.md      # Design checks
```

## Verification

[animaxxing-skills-test](https://github.com/johnpolacek/animaxxing-skills-test) holds, for each framework, a starter site, the task prompt an agent is given, a reference implementation built by following the skill, and Playwright specs that assert the lifecycle behavior the skill promises: no flash before the intro, a clean settled state, an outro that finishes before navigation, intro-only history, one navigation at a time, interruptible intros, reduced motion through every phase, and cleanup. Its eval script rebuilds a framework's app from the starter with Claude Code and runs the specs against the result.

The test repository also checks disabled-JavaScript routes and bundle failure after the early marker across all seven HTML-rendering references. An isolated GSAP/SplitText fixture tests partial setup, stalled preparation, late work, and owner isolation. It does not certify recovery inside every framework controller.

The [Animaxxing](https://github.com/johnpolacek/animaxxing) demo is the reference for `style-animaxxing` and `animaxxing`. Each has its own `references/verification.md`: the style checks design and effect selection; the motion skill checks effect behavior, text stability, and reuse with the consuming app's fonts and colors. The test repository's `motion/` suite type-checks and runs every motion recipe in Chromium, including the `animaxxing-webgl` recipes through SwiftShader; a style suite is planned.

## Demo

See the [demo-agent recovery handoff](docs/demo-recovery-handoff.md) for the implementation contract and framework audit, and the [validation report](docs/recovery-validation.md) for executed checks and remaining gaps.

The [Animaxxing](https://github.com/johnpolacek/animaxxing) repository holds a Next.js showcase that consumes these skills as a real project and validates their guidance against navigation, interruption, accessibility, responsive layout, and cleanup requirements. Its look is carried by `style-animaxxing` and its effects by `animaxxing`, and its install page at `/animaxx` walks through installing the skills.

## Contributing

Read [AGENTS.md](AGENTS.md) before adding or editing a skill. New skills must follow the shared lifecycle and gate advice on framework versions. Framework skills stay free of project-specific design. Motion skills own reusable recipes and technical requirements without prescribing a brand. Style skills select and configure motion alongside their design. Both motion and style skills stay free of framework lifecycle ownership.

After editing any file in `shared/`, run `python3 scripts/sync_initialization.py` to update the standalone skill copies. Framework-specific integration stays in each `motion-system.md`.

Run the same checks as CI before opening a pull request:

```bash
for skill in skills/*/; do uvx --from skills-ref==0.1.1 agentskills validate "$skill"; done
npx --yes skills@1.5.23 add . --list
python3 scripts/validate_repository.py
```

## Releasing

This repository uses semantic versions for its Claude and Cursor plugin manifests. To publish a release:

1. Add the user-visible changes to `CHANGELOG.md`.
2. Set the same version in every version field in `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`, and `.cursor-plugin/marketplace.json`.
3. Run the validation workflow locally or wait for CI to pass on `main`.
4. Tag the commit as `v<version>` and create the matching GitHub release.

## License

MIT

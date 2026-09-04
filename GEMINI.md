# Guidance for AI Agents Working in This Repo

This repository contains **Animaxxing skills** in two families. **Framework skills** (`gsap-<framework>`) cover page transition and component lifecycle guidance for GSAP in specific frameworks; each sits above the official [GSAP skills](https://github.com/greensock/gsap-skills), which cover the GSAP API itself. **Aesthetic skills** (`aesthetic-<name>`) carry one specific look: design tokens, typography and layout grammar, a motion vocabulary, and portable effect recipes in vanilla TypeScript and GSAP. A framework skill owns the lifecycle; an aesthetic skill owns how each phase looks. When editing or adding skills, follow these rules.

## Repo structure

- **skills/** — Each subdirectory is one skill. The CLI and agents discover skills by scanning `skills/` for directories that contain `SKILL.md`.
- **skills/llms.txt** — Index of skills with summaries and trigger terms. Update it whenever a skill is added or its scope changes.
- **Skill directory name** must exactly match the `name` in that skill's frontmatter (e.g. `skills/gsap-nextjs/` ↔ `name: gsap-nextjs`).
- Do not vendor the official `gsap-*` skills here. Reference them by name and tell users to install both repos.

## SKILL.md requirements

- **Frontmatter (YAML):**
  - `name` (required): lowercase, hyphens only, max 64 chars, must match parent directory name.
  - `description` (required): what the skill does, when to use it, and when not to. Include trigger terms so agents know when to apply it. Max 1024 chars.
  - `license` (required here): `MIT`.
  - `metadata` (optional): string-to-string map. Use `short-description` for a one-line summary shown by agent UIs.
- **Body:** Markdown instructions. Keep under ~500 lines; put long reference material in `references/` and link from SKILL.md so agents load only what they need.
- **agents/openai.yaml** (optional): Codex display name, short description, and default prompt.

## Conventions

- Every framework skill uses the same lifecycle: **mount → initial state → intro → settled → outro → end state → unmount**. Reuse the wording from `gsap-nextjs`. Aesthetic skills name that lifecycle as the framework skill's and map their recipes onto its phases.
- Write descriptions in **third person** (e.g. "Use when…" not "You can use when…").
- Be concise; do not restate the GSAP API or the framework's docs. Focus on how the framework's routing, rendering, and cleanup change what GSAP code must do.
- Gate advice on framework versions. Tell the agent to read the installed version and bundled docs before trusting memory.
- Keep framework skills portable: no project-specific design, naming, or file layout.
- Aesthetic skills are the deliberate exception, on design only. They exist to carry one look, so tokens, type, and effect recipes are specific by design. They must still be framework-free (vanilla TypeScript and GSAP; no React, Next.js, Vue, or Svelte constructs; Tailwind class strings only alongside a plain-CSS equivalent), must never own lifecycle (no routing, mounting, cleanup timing, or navigation rules; recipes expose `enter`/`exit`-style builders for a framework skill's controller to call), and must name the framework skill family as the owner of the lifecycle.
- Aesthetic skill layout: `skills/aesthetic-<name>/SKILL.md`, `agents/openai.yaml`, `references/tokens.md`, `typography-and-layout.md`, `motion-vocabulary.md`, `verification.md`, and `references/recipes/*.md`, one self-contained module per recipe with its lifecycle contract stated at the top.
- When adding a new skill: create `skills/<skill-name>/SKILL.md`, then update `skills/llms.txt` and the README "Skills" and "Structure" sections. For a framework skill, add a matching framework directory to the animaxxing-skills-test repository (starter, TASK.md, reference app, specs) so the skill can be verified. For an aesthetic skill, record how it is verified in its `references/verification.md` and point at the demo that wears it, until the test repository grows an aesthetic suite.

## References

- [Agent Skills specification](https://agentskills.io/specification.md)
- [skills CLI (discovery, install)](https://github.com/vercel-labs/skills)
- [Official GSAP skills](https://github.com/greensock/gsap-skills)

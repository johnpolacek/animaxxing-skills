# Guidance for AI Agents Working in This Repo

This repository contains **Animaxxing skills** in three families. **Framework skills** (`gsap-<framework>`) cover page transition and component lifecycle guidance for GSAP in specific frameworks; each sits above the official [GSAP skills](https://github.com/greensock/gsap-skills), which cover the GSAP API itself. **Motion skills** (the core `animaxxing` skill) supply reusable vanilla TypeScript and GSAP effects, technical requirements, and effect checks without prescribing a brand. **Style skills** (`style-<name>`) carry one art direction: design tokens, typography and layout grammar, and a curated selection and configuration of motion recipes. The framework owns when effects run; motion owns their implementation; the style owns the look and selects the treatment. When editing or adding skills, follow these rules.

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

- Every framework skill uses the same lifecycle: **mount → initial state → intro → settled → outro → end state → unmount**. Reuse the wording from `gsap-nextjs`. Motion skills name that lifecycle as the framework skill's and map their builders onto its phases. Styles select the treatment for those phases without owning execution timing.
- Write descriptions in **third person** (e.g. "Use when…" not "You can use when…").
- Be concise; do not restate the GSAP API or the framework's docs. Focus on how the framework's routing, rendering, and cleanup change what GSAP code must do.
- Gate advice on framework versions. Tell the agent to read the installed version and bundled docs before trusting memory.
- Keep framework skills portable: no project-specific design, naming, or file layout.
- Motion skills must be framework-free (vanilla TypeScript and GSAP; no React, Next.js, Vue, or Svelte constructs). They preserve existing fonts, colors, and layout. Express requirements as capabilities, such as a variable weight axis, and expose or document how to adapt example values. Do not require a style skill to use an effect.
- Style skills are the deliberate exception on design: their tokens, typography, layout, and motion selection are specific by design. Keep reusable effect code and technical text-stability guidance in motion skills. A static restyle must remain usable without a motion skill or GSAP; the full treatment composes the matching framework and motion skills.
- Neither motion nor style skills own lifecycle: no routing, mounting, cleanup timing, or navigation rules. Motion recipes expose builders and cleanup handles for the framework controller to call; styles select and configure them. Name the framework skill family as the lifecycle owner. Tailwind class strings need a plain-CSS equivalent.
- Cross-skill composition names the required installed skill and its references; do not assume independently installed skill folders are siblings. Keep each motion skill's recipe dependencies and technical references within that skill.
- Shared framework guidance lives in `shared/`; run `scripts/sync_initialization.py` to package it into each `gsap-*/references/`. Keep framework-specific guidance local.
- Core motion skill layout: `skills/animaxxing/SKILL.md`, `agents/openai.yaml`, `references/motion-vocabulary.md`, `text-stability.md` when relevant, `verification.md`, and `references/recipes/*.md`, one self-contained module per recipe with its lifecycle contract stated at the top.
- Style skill layout: `skills/style-<name>/SKILL.md`, `agents/openai.yaml`, `references/tokens.md`, `typography-and-layout.md`, `motion-vocabulary.md` for art direction and surface choices, and `verification.md` for design checks.
- When adding a new skill: create `skills/<skill-name>/SKILL.md`, then update `skills/llms.txt` and the README "Skills" and "Structure" sections. For a framework skill, add a matching framework directory to the animaxxing-skills-test repository (starter, TASK.md, reference app, specs) so the skill can be verified. For a motion or style skill, record how it is verified in its `references/verification.md` and point at the demo that exercises it until the test repository grows dedicated suites. Motion verification also checks reuse without the demo's branding.

## References

- [Agent Skills specification](https://agentskills.io/specification.md)
- [skills CLI (discovery, install)](https://github.com/vercel-labs/skills)
- [Official GSAP skills](https://github.com/greensock/gsap-skills)

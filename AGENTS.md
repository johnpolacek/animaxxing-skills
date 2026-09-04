# Guidance for AI Agents Working in This Repo

This repository contains **Animaxxing skills**: page transition and component lifecycle guidance for GSAP in specific frameworks. Each skill sits above the official [GSAP skills](https://github.com/greensock/gsap-skills), which cover the GSAP API itself. When editing or adding skills, follow these rules.

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

- Every framework skill uses the same lifecycle: **mount → initial state → intro → settled → outro → end state → unmount**. Reuse the wording from `gsap-nextjs`.
- Write descriptions in **third person** (e.g. "Use when…" not "You can use when…").
- Be concise; do not restate the GSAP API or the framework's docs. Focus on how the framework's routing, rendering, and cleanup change what GSAP code must do.
- Gate advice on framework versions. Tell the agent to read the installed version and bundled docs before trusting memory.
- Keep skills portable. No project-specific design, naming, or file layout.
- When adding a new skill: create `skills/<skill-name>/SKILL.md`, then update `skills/llms.txt` and the README "Skills" and "Structure" sections. Add a matching framework directory to the animaxxing-skills-test repository (starter, TASK.md, reference app, specs) so the skill can be verified.

## References

- [Agent Skills specification](https://agentskills.io/specification.md)
- [skills CLI (discovery, install)](https://github.com/vercel-labs/skills)
- [Official GSAP skills](https://github.com/greensock/gsap-skills)

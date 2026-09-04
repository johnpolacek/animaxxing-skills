# Animaxxing — Repository-wide instructions for GitHub Copilot

This repository publishes portable Agent Skills for GSAP animation in specific routing and rendering environments. Before changing a skill, read `AGENTS.md` and the target framework's `SKILL.md`.

- Keep each skill focused on how its framework changes routing, rendering, animation timing, interruption, and cleanup. Leave the GSAP API itself to the official GSAP skills.
- Use the shared lifecycle wording exactly: mount → initial state → intro → settled → outro → end state → unmount.
- Gate framework advice on installed versions and bundled source or types rather than memory.
- Preserve progressive disclosure: essential routing stays in `SKILL.md`; substantial framework mechanics belong in focused `references/` files linked from it.
- Keep names, descriptions, the README skills table, and `skills/llms.txt` synchronized.
- Run the validation workflow before committing.

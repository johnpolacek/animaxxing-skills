# Animaxxing — Repository-wide instructions for GitHub Copilot

This repository publishes Agent Skills for GSAP animation in two families: framework skills for specific routing and rendering environments, and aesthetic skills that each carry one complete look with portable effect recipes. Before changing a skill, read `AGENTS.md` and the target skill's `SKILL.md`.

- Keep each framework skill focused on how its framework changes routing, rendering, animation timing, interruption, and cleanup. Leave the GSAP API itself to the official GSAP skills.
- Aesthetic skills own look and recipes, never lifecycle: vanilla TypeScript and GSAP, no framework constructs, no routing or cleanup rules.
- Use the shared lifecycle wording exactly: mount → initial state → intro → settled → outro → end state → unmount.
- Gate framework advice on installed versions and bundled source or types rather than memory.
- Preserve progressive disclosure: essential routing stays in `SKILL.md`; substantial framework mechanics belong in focused `references/` files linked from it.
- Keep names, descriptions, the README skills table, and `skills/llms.txt` synchronized.
- Run the validation workflow before committing.

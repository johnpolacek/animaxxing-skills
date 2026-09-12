# Animaxxing — Repository-wide instructions for GitHub Copilot

This repository publishes Agent Skills in three families: framework skills for routing and rendering environments, motion skills for reusable GSAP effects, and aesthetic skills for visual design and motion art direction. Before changing a skill, read `AGENTS.md` and the target skill's `SKILL.md`.

- Framework skills own routing, rendering, animation timing, interruption, and cleanup. Leave the GSAP API itself to the official GSAP skills.
- Motion skills own reusable recipes and technical requirements, preserving the app's fonts, colors, and layout. Use vanilla TypeScript and GSAP without framework constructs.
- Aesthetic skills own tokens, typography, layout, and effect selection/configuration. Keep implementations in motion skills; a static restyle must not require animation.
- Neither motion nor aesthetic skills own lifecycle. Use the shared wording exactly: mount → initial state → intro → settled → outro → end state → unmount.
- Gate framework advice on installed versions and bundled source or types rather than memory.
- Preserve progressive disclosure: essential routing stays in `SKILL.md`; substantial details belong in focused `references/` files linked from it. Cross-skill references use installed skill names rather than assuming sibling directories.
- Keep names, descriptions, the README skills tables, and `skills/llms.txt` synchronized.
- Run the validation workflow before committing.

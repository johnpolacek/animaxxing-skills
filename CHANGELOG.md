# Changelog

All notable changes to Animaxxing Skills are documented here. Releases follow [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-09-04

### Added

- An aesthetic skill family. Each `aesthetic-<name>` skill carries one complete look as design tokens, typography and layout grammar, a motion vocabulary, and portable vanilla TypeScript plus GSAP effect recipes, and hands its motion to a framework skill's lifecycle.
- `aesthetic-animaxxing`: the Animaxxing look. Monochrome tokens in plain CSS and Tailwind v4 with light and dark schemes, Rethink Sans and JetBrains Mono type roles, the twelve-column editorial layout grammar, and recipes for split-text entrances, the scattering-letters route intro and outro, speak-in paragraphs, the letter wave, the blast-off outro, the particle field, and the marquee, reactor, resolve, slipstream, and ignite particle treatments.

### Changed

- Contributor guidance distinguishes framework skills (portable, design-free) from aesthetic skills (one design, framework-free, never owning lifecycle).
- Plugin manifests describe both families.

## [0.1.0] - 2026-09-04

### Added

- Framework-specific GSAP lifecycle skills for vanilla sites, Astro, SvelteKit, Nuxt, React Router, TanStack Router, and Next.js App Router.
- Claude Code and Cursor plugin manifests.
- Codex display metadata for every skill.
- Automated validation for skill structure, manifests, links, and CLI discovery.

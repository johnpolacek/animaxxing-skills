# Changelog

All notable changes to Animaxxing Skills are documented here. Releases follow [Semantic Versioning](https://semver.org/).

## [0.3.1] - 2026-09-12

### Changed

- Renamed `motion-animaxxing` to `animaxxing` so the core animation skill appears first in the installer.
- Renamed `aesthetic-animaxxing` to `style-animaxxing` for visual design and motion art direction. Framework, motion, and style responsibilities remain unchanged.
- Updated skill metadata, composition references, contributor guidance, and the README/index to use the new names and lead with the core animation skill.

### Migration

- Replace installed `motion-animaxxing` and `aesthetic-animaxxing` entries with `animaxxing` and `style-animaxxing`, respectively. Existing copied application modules and recipe APIs are unchanged.

## [0.3.0] - 2026-09-12

### Added

- `motion-animaxxing`: independently installable vanilla TypeScript and GSAP text and particle recipes, with effect selection, font and SplitText requirements, and technical verification. Effects preserve the consuming project's fonts, palette, and layout.

### Changed

- Split responsibilities into three families: framework skills own lifecycle, motion skills own reusable effect implementations, and aesthetic skills own visual design and motion art direction.
- `aesthetic-animaxxing` keeps its tokens, typography, layout, pacing, and surface choices, and composes `motion-animaxxing` for the full treatment. Static and minimal-motion restyles have explicit scope guidance.
- Moved the seven recipe files and generic SplitText stability/verification guidance from the aesthetic into the motion skill. Recipe builder signatures and TypeScript implementations are unchanged; particle markup now inherits the consuming app's color instead of requiring an aesthetic token.
- Documented adaptation of weight ranges to existing variable fonts and alternatives for static fonts.
- Updated discovery metadata, installation/composition and migration guidance, contributor instructions, and plugin manifests for all three families. Repository link validation now covers nested skill references.

### Migration

- Install `motion-animaxxing` alongside `aesthetic-animaxxing` and the matching framework skill to retain the full animated treatment. Recipe reference paths now belong to the motion skill; existing copied application modules do not need migration.

## [0.2.2] - 2026-09-08

### Fixed

- Character-animation guidance now keeps scoped kerning settings consistent across SplitText setup and revert to prevent horizontal snaps.
- Split entrance recipes accept an optional scoped character-mask class for confirmed glyph clipping, preserving animation timing, accessibility, and cleanup.

### Changed

- Typography diagnosis distinguishes kerning shifts from clipped glyph ink, late fonts, ligatures, wrapping, and other geometry changes.
- Verification compares glyph appearance and character positions across cleanup, checks both reveal directions, and covers desktop, mobile, reduced motion, and interruptions.

## [0.2.1] - 2026-09-04

### Added

- `aesthetic-animaxxing`: the resize policy. A settled width change remounts the page and replays its entrance; height-only changes are ignored; the wave stops the moment a headline reflows.

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

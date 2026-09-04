# Animaxxing — Repository-wide instructions for GitHub Copilot

When writing or suggesting GSAP animation in a **Next.js App Router** project:

- **Lifecycle:** Every animated page or component runs mount → initial state → intro → settled → outro → end state → unmount. Set initial values after mount and before paint, animate to one settled state, and clear temporary styles there.
- **Client only:** GSAP runs only in client components. Register GSAP and plugins once in a client-only module. Scope selectors with `useGSAP({ scope })` or `gsap.context()` and revert on cleanup.
- **Outros:** Keep the outgoing page or component mounted and visible through its outro. Navigate, unmount, or let the router hide it only from the completion callback. Use `onNavigate` on `Link` (Next.js 15.3+) to delay navigation until the outro finishes.
- **Back and forward:** Never run an outro on history navigation. Give it an intro-only path.
- **cacheComponents:** When enabled, the router hides routes instead of unmounting them. Treat re-show as mount and never assume a fresh DOM node.
- **View Transitions:** Next.js 16.2+ activates React `<ViewTransition>` on navigation. Use it for shared element morphs and whole-page crossfades. Use GSAP for outros that gate navigation, interruptible or scrubbed motion, and sequenced timelines. Never give one element to both in the same transition.
- **Layout:** Lay out the final page with normal CSS first. One stable wrapper owns the geometry through every phase so overlapping old and new content never shifts layout.
- **Accessibility:** Reduced motion reaches the same settled state and still fires every completion callback. Keep native link behavior, focus, and scroll.

**More detail:** The `skills/` directory in this repo contains full SKILL.md guidance with references for App Router navigation, lifecycle implementation, and verification. For agents that support the Agent Skills format (Cursor, Claude Code, Codex, etc.), install this repo as a skill for the complete reference, alongside the official [GSAP skills](https://github.com/greensock/gsap-skills).

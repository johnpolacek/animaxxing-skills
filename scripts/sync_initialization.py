#!/usr/bin/env python3
"""Package the shared contract inside each independently installable framework skill."""

from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parent.parent
HEADER = "<!-- Generated from shared/initialization.md; run scripts/sync_initialization.py. -->\n\n"


def sync(check: bool = False) -> None:
    expected = HEADER + (ROOT / "shared/initialization.md").read_text()
    for skill in sorted((ROOT / "skills").glob("gsap-*/SKILL.md")):
        target = skill.parent / "references/initialization.md"
        if check:
            if not target.exists() or target.read_text() != expected:
                raise SystemExit(f"Stale packaged reference: {target.relative_to(ROOT)}")
        else:
            target.write_text(expected)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    sync(parser.parse_args().check)

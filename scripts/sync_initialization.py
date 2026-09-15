#!/usr/bin/env python3
"""Package every shared reference inside each independently installable framework skill."""

from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parent.parent
SHARED = ROOT / "shared"


def header(name: str) -> str:
    return f"<!-- Generated from shared/{name}; run scripts/sync_initialization.py. -->\n\n"


def sync(check: bool = False) -> None:
    sources = sorted(SHARED.glob("*.md"))
    if not sources:
        raise SystemExit("No shared references found")
    for source in sources:
        expected = header(source.name) + source.read_text()
        for skill in sorted((ROOT / "skills").glob("gsap-*/SKILL.md")):
            target = skill.parent / "references" / source.name
            if check:
                if not target.exists() or target.read_text() != expected:
                    raise SystemExit(f"Stale packaged reference: {target.relative_to(ROOT)}")
            else:
                target.write_text(expected)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    sync(parser.parse_args().check)

#!/usr/bin/env python3
"""Validate repository-level publishing invariants using the standard library."""

from __future__ import annotations

import json
import re
from pathlib import Path

from sync_initialization import sync


ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
MANIFESTS = (
    ROOT / ".claude-plugin" / "marketplace.json",
    ROOT / ".claude-plugin" / "plugin.json",
    ROOT / ".cursor-plugin" / "marketplace.json",
    ROOT / ".cursor-plugin" / "plugin.json",
)
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)#]+)(?:#[^)]*)?\)")
FIELD_PATTERN = re.compile(r"^(name|description): (.*)$", re.MULTILINE)
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def main() -> None:
    sync(check=True)
    documents = {path: load_json(path) for path in MANIFESTS}

    claude_version = documents[ROOT / ".claude-plugin" / "plugin.json"]["version"]
    cursor_plugin = documents[ROOT / ".cursor-plugin" / "plugin.json"]
    cursor_marketplace = documents[ROOT / ".cursor-plugin" / "marketplace.json"]
    versions = {
        claude_version,
        cursor_plugin["version"],
        cursor_marketplace["metadata"]["version"],
        cursor_marketplace["plugins"][0]["version"],
    }
    if len(versions) != 1 or not SEMVER_PATTERN.fullmatch(claude_version):
        raise SystemExit(f"Plugin versions must be matching semantic versions: {sorted(versions)}")

    logo = ROOT / cursor_plugin["logo"]
    if not logo.is_file():
        raise SystemExit(f"Cursor logo does not exist: {logo.relative_to(ROOT)}")

    skill_names = sorted(path.parent.name for path in SKILLS.glob("*/SKILL.md"))
    if not skill_names:
        raise SystemExit("No skills found")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    index = (SKILLS / "llms.txt").read_text(encoding="utf-8")
    for name in skill_names:
        frontmatter = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8").split("---")[1]
        fields = dict(FIELD_PATTERN.findall(frontmatter))
        if fields.get("name") != name:
            raise SystemExit(f"skills/{name}/SKILL.md name must match its directory")
        description = fields.get("description", "")
        if description.startswith('"'):
            description = json.loads(description)
        if not 0 < len(description) <= 1024:
            raise SystemExit(f"skills/{name}/SKILL.md description is {len(description)} characters; the limit is 1024")
        if name not in readme:
            raise SystemExit(f"README.md does not mention {name}")
        if name not in index:
            raise SystemExit(f"skills/llms.txt does not mention {name}")

    for document in SKILLS.rglob("*.md"):
        for target in LINK_PATTERN.findall(document.read_text(encoding="utf-8")):
            if re.match(r"^(?:https?://|mailto:)", target):
                continue
            resolved = (document.parent / target).resolve()
            if not resolved.exists():
                raise SystemExit(f"Broken link in {document.relative_to(ROOT)}: {target}")

    print(f"Validated {len(skill_names)} skills and {len(MANIFESTS)} manifests at version {claude_version}.")


if __name__ == "__main__":
    main()

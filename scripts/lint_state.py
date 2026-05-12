#!/usr/bin/env python3
"""
lint_state.py — Verify chapter status values across the study-session skill
match the canonical SOT in references/state-schema.md.

Stdlib-only. Run from the skill root:

    python3 scripts/lint_state.py .

Exit code:
    0 — clean (no errors; warnings allowed)
    1 — errors found (deprecated status, unknown status, missing required field, etc.)
    2 — bad invocation
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

# ──────────────────────────────────────────────────────────────
# Canonical SOT — must match references/state-schema.md
# ──────────────────────────────────────────────────────────────

CANONICAL_STATUSES = {
    "in-progress",
    "phase-2-pending-conversion",
    "phase-3-pending",
    "phase-3-textbase-only",
    "phase-3-complete",
    "applied",
    "scheduled",
}

# Section-level status enum (orthogonal axis; lives in references/section-tracking.md).
# Sections inside a chapter use the same `status:` key name as chapter notes do, so
# the linter must accept these values without flagging them as unknown chapter
# statuses. `in-progress` is shared with the chapter enum above (intentional —
# same word, same meaning at its respective level).
SECTION_STATUSES = {
    "pending",
    "in-progress",
    "covered",
    "used-as-exercise",
    "skipped",
}

# `complete` is an aggregate alias allowed ONLY inside chapter_status: blocks
# in books.yml-style files (one-line per chapter). It must NOT appear as a chapter
# note frontmatter `status:` value.
AGGREGATE_ALIAS = {"complete"}

DEPRECATED_STATUSES = {
    "phase-2-complete",
    "phase-3-incomplete",
}

REQUIRED_CHAPTER_NOTE_FIELDS = (
    "title",
    "book",
    "chapter",
    "type",
    "status",
    "created",
)

# Files that DEFINE the schema or list the deprecated names — plain prose mentions
# of deprecated names in these files are allowed (the SOT itself names them).
SCHEMA_DEFINING_FILES = {
    "references/state-schema.md",
    "references/calibration.md",  # has historical chapter_status example referenced
    "references/section-tracking.md",  # defines the section status enum
}

# Glob patterns to scan
TARGET_GLOBS = (
    "SKILL.md",
    "references/*.md",
    "references/methods/*.md",
    "evals/evals.json",
    "evals/fixtures/**/*.yml",
    "evals/fixtures/**/*.md",
)


# ──────────────────────────────────────────────────────────────
# Tiny YAML-frontmatter and YAML-value parsing (stdlib only)
# ──────────────────────────────────────────────────────────────

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def extract_frontmatter(text: str) -> str | None:
    """Return the YAML frontmatter block (without --- fences) or None."""
    m = FRONTMATTER_RE.match(text)
    return m.group(1) if m else None


# Match `key: value` at any indentation, capturing key + raw value (rest of line).
KEY_VALUE_RE = re.compile(r"^(\s*)([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)$")

# A `status: <value>` line where <value> is a bare token (no list, no comment-only).
STATUS_LINE_RE = re.compile(
    r"""^\s*status\s*:\s*
        ([A-Za-z][A-Za-z0-9-]*)   # the status token
        \s*(?:\#.*)?$             # optional trailing comment
    """,
    re.VERBOSE,
)

# `chapter_status:` block — followed by indented `N: <status>` lines.
CHAPTER_STATUS_HEADER_RE = re.compile(r"^(\s*)chapter_status\s*:\s*(\{?)\s*$")
CHAPTER_STATUS_ENTRY_RE = re.compile(
    r"""^\s*[\"\']?[A-Za-z0-9_]+[\"\']?\s*:\s*
        ([A-Za-z][A-Za-z0-9-]*)
        \s*(?:\#.*)?$
    """,
    re.VERBOSE,
)


def find_status_lines(text: str):
    """Yield (lineno, value) for every `status: <token>` line that takes a single
    token (so we skip union/enum lines like `status: a | b | c` which are
    schema documentation, not assertions of a status)."""
    for i, line in enumerate(text.splitlines(), start=1):
        # Skip lines that are clearly enum documentation: contain `|` after status.
        m = STATUS_LINE_RE.match(line)
        if m:
            yield i, m.group(1), line.rstrip()


def find_chapter_status_entries(text: str):
    """Yield (lineno, value) for entries inside `chapter_status:` blocks.

    Handles both block form:
        chapter_status:
          1: complete
          4: phase-3-pending
    and inline-empty form:
        chapter_status: {}
    (which has no entries to lint).
    """
    lines = text.splitlines()
    n = len(lines)
    i = 0
    while i < n:
        line = lines[i]
        header = CHAPTER_STATUS_HEADER_RE.match(line)
        if not header:
            i += 1
            continue
        # If `{}` or `{...}` inline, skip — handled by frontmatter parser if needed.
        if header.group(2) == "{":
            # inline mapping — try to extract key:value pairs from the rest of the line / next lines
            # For our fixtures, `chapter_status: {}` is empty; skip.
            i += 1
            continue
        base_indent = len(header.group(1))
        # Walk forward while indentation > base_indent.
        j = i + 1
        while j < n:
            nxt = lines[j]
            if nxt.strip() == "":
                j += 1
                continue
            stripped_indent = len(nxt) - len(nxt.lstrip(" "))
            if stripped_indent <= base_indent:
                break
            entry = CHAPTER_STATUS_ENTRY_RE.match(nxt)
            if entry:
                yield j + 1, entry.group(1), nxt.rstrip()
            j += 1
        i = j


def find_required_fields_in_frontmatter(fm_text: str) -> set[str]:
    found = set()
    for line in fm_text.splitlines():
        m = KEY_VALUE_RE.match(line)
        if not m:
            continue
        indent = len(m.group(1))
        if indent != 0:
            # Only top-level frontmatter keys
            continue
        found.add(m.group(2))
    return found


# ──────────────────────────────────────────────────────────────
# File traversal
# ──────────────────────────────────────────────────────────────

def iter_target_files(root: Path):
    seen = set()
    for pat in TARGET_GLOBS:
        for p in root.glob(pat):
            if p.is_file():
                rp = p.resolve()
                if rp in seen:
                    continue
                seen.add(rp)
                yield p


def relpath(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(root))
    except ValueError:
        return str(p)


# ──────────────────────────────────────────────────────────────
# Lint logic
# ──────────────────────────────────────────────────────────────

def is_chapter_note_path(rel: str) -> bool:
    """Heuristic: chapter notes live under evals/fixtures/.../books/<slug>/ch-*.md
    or end with /ch-NN-*.md. Required-field checks apply to these."""
    return ("/books/" in rel and rel.endswith(".md")) or re.search(r"/ch-\d+-", rel) is not None


def lint_file(path: Path, root: Path):
    rel = relpath(path, root)
    text = path.read_text(encoding="utf-8", errors="replace")
    errors: list[str] = []
    warnings: list[str] = []

    is_schema_def = rel in SCHEMA_DEFINING_FILES

    # ── status: <single token> lines ──
    for lineno, value, raw in find_status_lines(text):
        if value in DEPRECATED_STATUSES:
            errors.append(
                f"{rel}:{lineno}: deprecated status '{value}' "
                f"(replace per references/state-schema.md) — line: {raw.strip()}"
            )
        elif value == "complete":
            # `status: complete` (bare) is NOT allowed at chapter-note frontmatter.
            errors.append(
                f"{rel}:{lineno}: bare 'complete' is not a valid chapter `status:` "
                f"— use 'phase-3-complete' (canonical) — line: {raw.strip()}"
            )
        elif value not in CANONICAL_STATUSES:
            # Allow section-level status values (orthogonal enum, same `status:` key
            # at section depth — see references/section-tracking.md).
            if value in SECTION_STATUSES:
                pass
            # Unknown — but skip if file is schema-defining (it might be talking about hypotheticals).
            elif not is_schema_def:
                errors.append(
                    f"{rel}:{lineno}: unknown status '{value}' "
                    f"(not in canonical enum) — line: {raw.strip()}"
                )

    # ── chapter_status: { N: <token> } entries ──
    for lineno, value, raw in find_chapter_status_entries(text):
        allowed = (
            value in CANONICAL_STATUSES
            or value in AGGREGATE_ALIAS
        )
        if value in DEPRECATED_STATUSES:
            errors.append(
                f"{rel}:{lineno}: deprecated chapter_status value '{value}' "
                f"— line: {raw.strip()}"
            )
        elif not allowed:
            if not is_schema_def:
                errors.append(
                    f"{rel}:{lineno}: unknown chapter_status value '{value}' "
                    f"(not in canonical enum or aggregate alias) — line: {raw.strip()}"
                )

    # ── Plain-prose mentions of deprecated names (warning only) ──
    if not is_schema_def and rel != "scripts/lint_state.py":
        for dep in DEPRECATED_STATUSES:
            # Skip if the file is the lint script itself (it lists the deprecated names).
            for i, line in enumerate(text.splitlines(), start=1):
                if dep in line:
                    # If it's inside a status: or chapter_status: line we already reported.
                    if re.search(rf"\bstatus\s*:\s*{re.escape(dep)}\b", line):
                        continue
                    if re.match(r"^\s*[\"\']?[A-Za-z0-9_]+[\"\']?\s*:\s*" + re.escape(dep) + r"\b", line):
                        continue
                    warnings.append(
                        f"{rel}:{i}: prose mention of deprecated '{dep}' "
                        f"— consider updating to canonical name"
                    )

    # ── Required frontmatter fields on chapter notes ──
    if is_chapter_note_path(rel):
        fm = extract_frontmatter(text)
        if fm is None:
            warnings.append(f"{rel}: no YAML frontmatter found (chapter notes need one)")
        else:
            present = find_required_fields_in_frontmatter(fm)
            missing = [f for f in REQUIRED_CHAPTER_NOTE_FIELDS if f not in present]
            for f in missing:
                warnings.append(f"{rel}: chapter note missing required frontmatter field '{f}'")

    return errors, warnings


def lint_evals_json(path: Path, root: Path):
    """Light JSON parse to catch broken evals.json + scan for status mentions."""
    rel = relpath(path, root)
    errors: list[str] = []
    warnings: list[str] = []
    import json
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"{rel}: invalid JSON — {e}")
        return errors, warnings
    # Walk strings looking for deprecated statuses.
    def walk(obj, trail=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                walk(v, f"{trail}.{k}" if trail else str(k))
        elif isinstance(obj, list):
            for idx, v in enumerate(obj):
                walk(v, f"{trail}[{idx}]")
        elif isinstance(obj, str):
            for dep in DEPRECATED_STATUSES:
                # Match as a whole word.
                if re.search(rf"(?<![A-Za-z0-9-]){re.escape(dep)}(?![A-Za-z0-9-])", obj):
                    warnings.append(
                        f"{rel}: deprecated status '{dep}' mentioned in {trail or '<root>'}"
                    )
    walk(data)
    return errors, warnings


def main(argv):
    if len(argv) > 2:
        print("usage: lint_state.py [skill_root]", file=sys.stderr)
        return 2
    root = Path(argv[1] if len(argv) == 2 else ".").resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2

    all_errors = []
    all_warnings = []
    files_scanned = 0

    for path in iter_target_files(root):
        files_scanned += 1
        if path.suffix == ".json":
            errs, warns = lint_evals_json(path, root)
        else:
            errs, warns = lint_file(path, root)
        all_errors.extend(errs)
        all_warnings.extend(warns)

    # Report
    for w in all_warnings:
        print(f"WARN  {w}")
    for e in all_errors:
        print(f"ERROR {e}")

    print(
        f"\nScanned {files_scanned} file(s). "
        f"{len(all_errors)} error(s), {len(all_warnings)} warning(s)."
    )

    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

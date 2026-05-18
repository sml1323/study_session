#!/usr/bin/env python3
"""
lint_state.py — Verify chapter status values across the study-session skill
match the canonical SOT in references/state-schema.md.

Stdlib-only. Run from the skill root:

    python3 scripts/lint_state.py .                          # lint skill tree
    python3 scripts/lint_state.py . --books-yml ~/study-journal/books.yml
                                                              # also lint an external
                                                              # books.yml for forbidden
                                                              # narrative-in-metadata
                                                              # patterns

Exit code:
    0 — clean (no errors; warnings allowed)
    1 — errors found (deprecated status, unknown status, missing required field,
        narrative-in-metadata leak in chapter_metrics, etc.)
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


# `status:` keys that belong to a different schema entity (not the chapter-status
# enum). When we see `<parent>:` followed by indented `status: <value>` where
# <parent> is in this set, skip the lint check — daily_floor.status, review_queue
# entry .status, self_diagnostic.status, etc. are independent enums (active /
# met / missed / etc.) defined in their own reference files.
NON_CHAPTER_STATUS_PARENTS = {
    "daily_floor",
    "review_routing",
    "external_deadline",
    "self_diagnostic",
    "review_queue",
    "ai_use_log",
    "ai_policy",
}


def find_status_lines(text: str):
    """Yield (lineno, value) for every `status: <token>` line that takes a single
    token (so we skip union/enum lines like `status: a | b | c` which are
    schema documentation, not assertions of a status).

    Skips `status:` lines that are nested under a NON_CHAPTER_STATUS_PARENTS key —
    those are independent enums (e.g., daily_floor.status: active).
    """
    lines = text.splitlines()
    # Track parent key at each indentation depth.
    indent_stack: list[tuple[int, str]] = []  # (indent, key)
    in_fence = False
    for i, line in enumerate(lines, start=1):
        # Track fenced code blocks — both ```yaml and ``` toggle. We still lint
        # inside them (fixtures use them) but parent tracking should reset on
        # entry/exit because the fenced block is a fresh context.
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            indent_stack = []
            continue

        # Skip blank / comment-only lines.
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))
        # Pop indent stack entries that are >= current indent.
        while indent_stack and indent_stack[-1][0] >= indent:
            indent_stack.pop()

        # `status: <token>` check.
        m = STATUS_LINE_RE.match(line)
        if m:
            # If we're under a non-chapter parent, skip.
            if any(parent in NON_CHAPTER_STATUS_PARENTS for _, parent in indent_stack):
                continue
            yield i, m.group(1), line.rstrip()

        # Otherwise, if it's a `key:` opener (no scalar after), push onto stack.
        kv = KEY_VALUE_RE.match(line)
        if kv:
            key = kv.group(2)
            value_part = kv.group(3).strip()
            # Treat as opener if value is empty (i.e., a block opener like `daily_floor:`).
            if value_part == "" or value_part.startswith("#"):
                indent_stack.append((indent, key))


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


# ──────────────────────────────────────────────────────────────
# books.yml chapter_metrics narrative-in-metadata lint
# ──────────────────────────────────────────────────────────────
#
# Per references/state-schema.md § "books.yml chapter_metrics — allowed and
# forbidden fields", `chapter_metrics[N]` must hold only enums / numbers /
# dates / status maps / short anchors. Narrative strings, *_note qualifiers,
# and per-session narrative key variants (e.g., `*_session_N_scoped`,
# `*_session_N_lockin`, `confidence_self_report_session_N_scoped`) are
# forbidden — they belong in the chapter note body or in the per-book
# `_archived/` snapshot.
#
# This lint runs only when --books-yml is passed (typically against the
# user's actual ~/study-journal/books.yml), not against the skill tree
# fixtures (which are intentionally minimal).

# Allowed metric field names (allowlist). Patterns ending with `_N` mean
# any digit-suffix is OK.
ALLOWED_METRIC_PREFIXES = {
    # B1 / post-split learning + calibration signals
    "learning_passed",
    "chapter_complete",
    "calibration_health",
    "calibration_gap_abs",
    "confirm_next_chapter",
    "score_prediction",
    "score_prediction_gap",
    "actual_score",
    "actual_score_weights",
    # Pre-B1 legacy still allowed during transition
    "abs_gap",
    "calibration_diagnosis",
    # Phase 3 metrics (allowed metadata)
    "textbase_recall_coverage",
    "situation_model_transfer_score",
    "situation_model_transfer_questions_count",
    "textbase_low_but_transfer_pass",
    "confidence_self_report",
    "confidence_accuracy_gap",
    # Session lifecycle / counts
    "phase_2_ended_at",
    "phase_3_attempts",
    "phase_3_downgraded_to_quiz",
    "calibrate_same_session",
    "session_count",
    # Hint/answer telemetry
    "hint_levels",
    "avg_hint_level",
    "avg_answer_length",
    # Phase 4 / spaced
    "transfer_attempt",
    "spaced_retrievals",
    "calibration_history",
    "review_queue",
    # Section tracking
    "section_progress",
    # Per-chapter overrides (allowed)
    "title",
    "genre_lean",
    "ai_policy",
    "intensity",
    # Archive pointer
    "archived",
    # Health flags object
    "session_health",
    # Bloom distribution
    "prompt_bloom_distribution",
    # Concept tracking
    "concept_candidates",
}

# Allowed `_session_N` / `_attempt_N` numeric series (state-schema explicitly
# permits these as int-valued per-session/per-attempt scores).
ALLOWED_INDEXED_PATTERNS = (
    re.compile(r"^confidence_accuracy_gap_session_\d+$"),
    re.compile(r"^closed_book_coverage_attempt_\d+$"),
    re.compile(r"^confidence_self_report_attempt_\d+$"),
    re.compile(r"^confidence_accuracy_gap_attempt_\d+$"),
)

# Allowed session_health keys (must be enum/bool only).
ALLOWED_SESSION_HEALTH_KEYS = {
    "illusion",
    "surface",
    "form_fatigue",
    "echo",
    "struggle_skip",
    "hint_abuse",
    "label_migration",
}

# Canonical calibration_health enum values (B1).
CALIBRATION_HEALTH_VALUES = {
    "well_calibrated",
    "loose",
    "over_confident",
    "under_confident",
    "unknown",
}


def _is_allowed_metric_key(key: str) -> bool:
    if key in ALLOWED_METRIC_PREFIXES:
        return True
    for pat in ALLOWED_INDEXED_PATTERNS:
        if pat.match(key):
            return True
    return False


def _yaml_load(text: str):
    """Best-effort YAML loader without external deps. Tries PyYAML first;
    falls back to None (caller drops into regex-fallback path)."""
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text)
    except ImportError:
        return None


def _regex_lint_books_yml(text: str, rel: str):
    """Stdlib-only fallback when PyYAML is unavailable. Catches the most common
    narrative-in-metadata patterns by regex. Will miss some violations a full
    YAML parser would catch — flagged as best-effort in the warning."""
    errors: list[str] = []
    warnings: list[str] = []
    lines = text.splitlines()

    # Track the parent key path by indentation (similar to find_status_lines).
    # We need to know when we're INSIDE chapter_metrics[N].* / session_health
    # to scope the checks.
    indent_stack: list[tuple[int, str]] = []

    def parent_at(depth_lo: int) -> list[str]:
        """Keys whose indent is < depth_lo (i.e., ancestors of the current line)."""
        return [k for ind, k in indent_stack if ind < depth_lo]

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        # Pop entries at same/greater indent.
        while indent_stack and indent_stack[-1][0] >= indent:
            indent_stack.pop()

        kv = KEY_VALUE_RE.match(line)
        if not kv:
            continue
        key = kv.group(2)
        value_part = kv.group(3).strip()

        # Determine if we're inside chapter_metrics[N] at this point.
        ancestors = [k for _, k in indent_stack]
        in_chapter_metrics = "chapter_metrics" in ancestors
        in_session_health = "session_health" in ancestors

        if in_chapter_metrics and not in_session_health:
            # The immediate parent could be a chapter id (e.g., "1") — that pushes
            # us "inside" the per-chapter metrics dict. Only flag if the key is at
            # the chapter-metrics field level, which we detect by checking that the
            # most recent ancestor IS chapter_metrics OR a chapter id (digit/quoted).
            # Simplification: any `key:` whose ancestor chain contains chapter_metrics
            # and whose immediate parent (top of stack) is either chapter_metrics or
            # a chapter id, gets checked.
            top_parent = indent_stack[-1][1] if indent_stack else ""
            is_field_of_chapter = (
                top_parent == "chapter_metrics"
                or (top_parent.isdigit() or (top_parent.startswith('"') and top_parent[1:-1].isdigit()))
            )
            # Heuristic: chapter ids appear as `"1":` so top_parent comes from KEY_VALUE_RE
            # capture which strips quotes off. Allow numeric strings too.
            try:
                int(top_parent)
                is_field_of_chapter = True
            except (ValueError, TypeError):
                pass
            if is_field_of_chapter and not _is_allowed_metric_key(key):
                errors.append(
                    f"{rel}:{i}: forbidden metric key '{key}' in chapter_metrics "
                    f"— not in allowlist (see references/state-schema.md § "
                    f"'books.yml chapter_metrics'). Line: {line.rstrip()}"
                )

        if in_session_health:
            if key not in ALLOWED_SESSION_HEALTH_KEYS:
                errors.append(
                    f"{rel}:{i}: forbidden session_health key '{key}' — only "
                    f"enum/bool keys allowed ({', '.join(sorted(ALLOWED_SESSION_HEALTH_KEYS))}). "
                    f"Line: {line.rstrip()}"
                )
            elif value_part and value_part not in ("true", "false", "null") and not value_part.startswith("#"):
                # Allow label_migration enum values
                if key == "label_migration":
                    if value_part not in ("pending", "renamed", "left-as-is", "null"):
                        errors.append(
                            f"{rel}:{i}: session_health.label_migration must be enum, "
                            f"got {value_part!r}. Line: {line.rstrip()}"
                        )
                else:
                    errors.append(
                        f"{rel}:{i}: session_health.{key} = {value_part!r}: forbidden "
                        f"narrative value — session_health values must be bool."
                    )

        # spaced_retrievals[].anchors detection (line-based)
        if key == "anchors" and ("spaced_retrievals" in ancestors or "spaced_retrievals" == kv.group(2)):
            # The anchors: row appears either inline `{... anchors: [...] ...}` or on its own line.
            errors.append(
                f"{rel}:{i}: spaced_retrievals[].anchors: forbidden — narrative "
                f"anchors list belongs in the chapter note body. Line: {line.rstrip()}"
            )

        # calibration_health enum check
        if key == "calibration_health" and value_part:
            v = value_part.strip().strip('"').strip("'")
            v = v.split("#", 1)[0].strip()  # strip inline comment
            if v and v not in CALIBRATION_HEALTH_VALUES:
                errors.append(
                    f"{rel}:{i}: calibration_health = {v!r}: not in canonical enum "
                    f"({', '.join(sorted(CALIBRATION_HEALTH_VALUES))})"
                )

        # Track block opener.
        if value_part == "" or value_part.startswith("#"):
            indent_stack.append((indent, key))

    # Inline anchors detection: `{ date: ..., anchors: [...] }` on a single line.
    inline_anchors_re = re.compile(r"\banchors\s*:\s*\[")
    for i, line in enumerate(lines, start=1):
        if "spaced_retrievals" in line:
            continue  # skip the header line itself
        if inline_anchors_re.search(line) and "{" in line:
            errors.append(
                f"{rel}:{i}: inline spaced_retrievals entry has narrative `anchors:` list "
                f"— forbidden in books.yml. Line: {line.rstrip()[:150]}"
            )

    warnings.append(
        f"{rel}: PyYAML not available; using regex-fallback lint (best-effort). "
        f"Install PyYAML for stricter checks."
    )
    return errors, warnings


def lint_books_yml_metrics(path: Path):
    """Lint an external books.yml for narrative-in-metadata violations.

    Returns (errors, warnings). Errors include:
      - chapter_metrics keys outside the allowlist (likely narrative variants)
      - session_health values that are strings other than the enum/bool set
      - spaced_retrievals[].anchors with narrative tokens
      - calibration_health values outside the canonical enum
    """
    errors: list[str] = []
    warnings: list[str] = []
    rel = str(path)

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        errors.append(f"{rel}: cannot read — {e}")
        return errors, warnings

    data = _yaml_load(text)
    if data is None:
        # Stdlib regex fallback — best-effort, catches most common violations.
        return _regex_lint_books_yml(text, rel)

    books = (data or {}).get("books", {})
    if not isinstance(books, dict):
        warnings.append(f"{rel}: no `books:` mapping at top level — nothing to lint")
        return errors, warnings

    for slug, book in books.items():
        if not isinstance(book, dict):
            continue
        cm = book.get("chapter_metrics") or {}
        if not isinstance(cm, dict):
            continue
        for chap_id, metrics in cm.items():
            if not isinstance(metrics, dict):
                continue
            for key, val in metrics.items():
                if not _is_allowed_metric_key(key):
                    errors.append(
                        f"{rel}: books['{slug}'].chapter_metrics['{chap_id}']: "
                        f"forbidden metric key '{key}' — not in allowlist; "
                        f"narrative variants belong in the chapter note body or "
                        f"_archived/books-yml-snapshot-*.md "
                        f"(see references/state-schema.md § 'books.yml chapter_metrics')"
                    )
                # session_health: only enum/bool keys allowed
                if key == "session_health" and isinstance(val, dict):
                    for sh_key, sh_val in val.items():
                        if sh_key not in ALLOWED_SESSION_HEALTH_KEYS:
                            errors.append(
                                f"{rel}: books['{slug}'].chapter_metrics['{chap_id}']"
                                f".session_health.{sh_key}: forbidden key — only enum/bool "
                                f"keys allowed ({', '.join(sorted(ALLOWED_SESSION_HEALTH_KEYS))}); "
                                f"narrative qualifiers go to the chapter note body."
                            )
                        elif isinstance(sh_val, str) and sh_val not in ("true", "false"):
                            errors.append(
                                f"{rel}: books['{slug}'].chapter_metrics['{chap_id}']"
                                f".session_health.{sh_key} = {sh_val!r}: forbidden "
                                f"narrative value — session_health values must be bool."
                            )
                # calibration_health must be canonical enum
                if key == "calibration_health" and isinstance(val, str):
                    if val not in CALIBRATION_HEALTH_VALUES:
                        errors.append(
                            f"{rel}: books['{slug}'].chapter_metrics['{chap_id}']"
                            f".calibration_health = {val!r}: not in canonical enum "
                            f"({', '.join(sorted(CALIBRATION_HEALTH_VALUES))})"
                        )
                # spaced_retrievals[].anchors: narrative list forbidden
                if key == "spaced_retrievals" and isinstance(val, list):
                    for idx, row in enumerate(val):
                        if isinstance(row, dict) and "anchors" in row:
                            errors.append(
                                f"{rel}: books['{slug}'].chapter_metrics['{chap_id}']"
                                f".spaced_retrievals[{idx}].anchors: forbidden — "
                                f"narrative anchors list belongs in the chapter note body."
                            )

    return errors, warnings


def main(argv):
    args = argv[1:]
    books_yml_path: Path | None = None

    # Pull off --books-yml <path> if present.
    if "--books-yml" in args:
        i = args.index("--books-yml")
        if i + 1 >= len(args):
            print("usage: lint_state.py [skill_root] [--books-yml <path>]", file=sys.stderr)
            return 2
        books_yml_path = Path(args[i + 1]).expanduser().resolve()
        args = args[:i] + args[i + 2 :]

    if len(args) > 1:
        print("usage: lint_state.py [skill_root] [--books-yml <path>]", file=sys.stderr)
        return 2
    root = Path(args[0] if len(args) == 1 else ".").resolve()
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

    if books_yml_path is not None:
        if not books_yml_path.is_file():
            print(f"--books-yml: not a file: {books_yml_path}", file=sys.stderr)
            return 2
        files_scanned += 1
        errs, warns = lint_books_yml_metrics(books_yml_path)
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

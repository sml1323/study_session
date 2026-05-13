#!/usr/bin/env python3
"""Reference reload coverage report for the study-session skill.

Reads ~/study-journal/.session-log/<date>.jsonl (PostToolUse hook output,
written by scripts/log_reference_read.sh) and reports:

  - reload counts per reference / method file (most → least)
  - cold references: in the skill but never loaded in the window
  - per-session reference breadth distribution
  - declared-vs-read drift: read_and_declared / read_not_declared /
    declared_not_read / unknown_or_context_carried (the four-way partition
    described in SKILL.md § Per-response context surfacing)

Declarations come from chapter-note frontmatter (`references_touched`,
`methods_invoked`) under ~/study-journal/books/**/ch-*.md, or from an
explicit list via --declared.

Usage:
    python3 scripts/analyze_references.py
    python3 scripts/analyze_references.py --period 7d
    python3 scripts/analyze_references.py --period all --json
    python3 scripts/analyze_references.py --declared declared.txt
    python3 scripts/analyze_references.py --no-auto-declared

Limits of the declared-vs-read check (read before trusting the numbers):
    Chapter-note frontmatter is append-only and accumulates declarations
    across many sessions, while the hook log filters by --period. So
    `declared_not_read` is a *set-level* signal — it tells you a file was
    cited at some point but never Read in the window. For periods that
    cover the chapter's full lifespan ("--period all"), this is tight; for
    short windows, treat `declared_not_read` as a soft warning unless the
    chapter is also within the window. Per-turn-exact comparison would
    require a transcript parser; not implemented here.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = Path.home() / "study-journal" / ".session-log"
JOURNAL_BOOKS_DIR = Path.home() / "study-journal" / "books"


def parse_period(period: str) -> timedelta | None:
    if period == "all":
        return None
    m = re.match(r"^(\d+)([dwm])$", period)
    if not m:
        raise SystemExit(
            f"Invalid period: {period!r} (expected like 30d, 2w, 6m, or all)"
        )
    n, unit = int(m.group(1)), m.group(2)
    if unit == "d":
        return timedelta(days=n)
    if unit == "w":
        return timedelta(weeks=n)
    return timedelta(days=n * 30)


def parse_ts(raw: str) -> datetime | None:
    """Accept both '...Z' UTC form (legacy) and '...+09:00' KST form."""
    try:
        if raw.endswith("Z"):
            return datetime.fromisoformat(raw[:-1] + "+00:00")
        return datetime.fromisoformat(raw)
    except (ValueError, AttributeError):
        return None


def load_entries(cutoff: datetime | None):
    if not LOG_DIR.exists():
        return
    for path in sorted(LOG_DIR.glob("*.jsonl")):
        try:
            for line in path.read_text().splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts = parse_ts(entry.get("t", ""))
                if ts is None:
                    continue
                if cutoff is not None and ts < cutoff:
                    continue
                yield entry, ts
        except OSError:
            continue


def list_skill_files() -> list[str]:
    files: list[str] = []
    refs_dir = SKILL_ROOT / "references"
    if refs_dir.exists():
        for p in refs_dir.rglob("*.md"):
            files.append(str(p.relative_to(SKILL_ROOT)))
    return sorted(files)


# ──────────────────────────────────────────────────────────────
# Declared-vs-read parsing
# ──────────────────────────────────────────────────────────────


def _extract_frontmatter(text: str) -> str | None:
    """Return YAML frontmatter body (between leading '---\\n' and the next '\\n---\\n')."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    return text[4:end]


def _extract_list_field(frontmatter: str, field: str) -> list[str]:
    """Stdlib-only YAML list extraction for `field:` block or inline form.

    Handles:
        field:
          - value1
          - value2
        field: [v1, v2]
        field: []

    Does NOT handle nested objects, multi-line strings, anchors. The fields we
    target (`references_touched`, `methods_invoked`) are flat string lists by
    schema, so this is sufficient.
    """
    out: list[str] = []
    in_block = False
    for raw_line in frontmatter.splitlines():
        if not in_block:
            if not raw_line.lstrip().startswith(field + ":"):
                continue
            after = raw_line.split(":", 1)[1].strip()
            if after.startswith("[") and after.endswith("]"):
                inner = after[1:-1].strip()
                if not inner:
                    return []
                return [v.strip().strip("'\"") for v in inner.split(",") if v.strip()]
            if after and not after.startswith("#"):
                # `field: value` scalar form (not what schema says, but tolerate)
                return [after.strip("'\"")]
            in_block = True
            continue
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        if raw_line.startswith(" ") and stripped.startswith("- "):
            out.append(stripped[2:].strip().strip("'\""))
            continue
        # any non-indented or non-list line ends the block
        break
    return out


def normalize_declared(decl: str, skill_files: set[str]) -> str | None:
    """Map a footer/frontmatter declaration to a hook-log-form path.

    Footer form examples:
        'arq.md§Step-4-steelman'  → 'references/methods/arq.md'
        'pdp-loop.md§TUTOR'        → 'references/pdp-loop.md'
        'hint-escalation.md'       → 'references/methods/hint-escalation.md'
        'references/methods/arq.md' → 'references/methods/arq.md'  (already-full)

    Resolution: strip any '§section' anchor, then prefer
    references/methods/<base>.md if that file exists in the skill, else
    references/<base>.md. Returns None if neither resolves — caller treats
    that as a declared_invalid (hallucinated or typo'd) entry.
    """
    if not decl:
        return None
    base = decl.split("§", 1)[0].strip().strip("'\"")
    if not base or base == "(none)":
        return None
    # Already-full path form
    if base.startswith("references/"):
        return base if base in skill_files else None
    if not base.endswith(".md"):
        return None
    method_form = f"references/methods/{base}"
    if method_form in skill_files:
        return method_form
    ref_form = f"references/{base}"
    if ref_form in skill_files:
        return ref_form
    return None


def load_explicit_declared(
    path_str: str, skill_files: set[str]
) -> tuple[set[str], list[str], list[str]]:
    """Load declared list from a file. One entry per line, footer-form or full-path.

    Lines starting with '#' or blank are skipped. Returns
    (valid_set, invalid_list, raw_lines).
    """
    src = Path(path_str)
    if not src.exists():
        raise SystemExit(f"--declared file not found: {src}")
    valid: set[str] = set()
    invalid: list[str] = []
    raws: list[str] = []
    for line in src.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        raws.append(line)
        norm = normalize_declared(line, skill_files)
        if norm is None:
            invalid.append(line)
        else:
            valid.add(norm)
    return valid, invalid, raws


def scan_chapter_note_declarations(
    skill_files: set[str],
) -> tuple[set[str], list[str], dict[str, list[str]]]:
    """Walk ~/study-journal/books/**/ch-*.md and union their declared lists.

    Returns (valid_set, invalid_list, per_file_raw_decls) where per_file is for
    debugging output. Set-level only — no per-session correlation, since the
    frontmatter is append-only and does not record session_id alongside each
    declaration. This is the documented limit (see module docstring).
    """
    valid: set[str] = set()
    invalid: list[str] = []
    per_file: dict[str, list[str]] = {}
    if not JOURNAL_BOOKS_DIR.exists():
        return valid, invalid, per_file
    for note in JOURNAL_BOOKS_DIR.glob("*/ch-*.md"):
        try:
            text = note.read_text()
        except OSError:
            continue
        fm = _extract_frontmatter(text)
        if fm is None:
            continue
        decls = _extract_list_field(fm, "references_touched") + _extract_list_field(
            fm, "methods_invoked"
        )
        if not decls:
            continue
        rel = str(note.relative_to(Path.home()))
        per_file[rel] = decls
        for d in decls:
            norm = normalize_declared(d, skill_files)
            if norm is None:
                invalid.append(f"{rel}: {d}")
            else:
                valid.add(norm)
    return valid, invalid, per_file


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--period",
        default="30d",
        help="Time window: 30d / 7d / 2w / 6m / all (default: 30d)",
    )
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    ap.add_argument(
        "--declared",
        default=None,
        help=(
            "Path to a file containing declared refs/methods (one per line, in "
            "footer form e.g. 'arq.md§Section' or full path 'references/...'). "
            "If omitted, the analyzer auto-scans ~/study-journal/books/**/ch-*.md "
            "frontmatter."
        ),
    )
    ap.add_argument(
        "--no-auto-declared",
        action="store_true",
        help="Skip the auto chapter-note scan. Only use --declared (if given).",
    )
    args = ap.parse_args()

    delta = parse_period(args.period)
    cutoff: datetime | None = None
    if delta is not None:
        cutoff = datetime.now(timezone.utc).astimezone() - delta

    reload_counts: Counter[str] = Counter()
    session_paths: dict[str, set[str]] = defaultdict(set)
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    total_reads = 0

    for entry, ts in load_entries(cutoff):
        path = entry.get("path", "")
        sid = entry.get("session_id", "")
        if not path:
            continue
        # SKILL.md is rarely Read-tool'd (it's bundled by the harness), so it
        # would always look "cold" — skip from the analysis.
        if path == "SKILL.md":
            continue
        reload_counts[path] += 1
        if sid:
            session_paths[sid].add(path)
        total_reads += 1
        first_seen = ts if first_seen is None or ts < first_seen else first_seen
        last_seen = ts if last_seen is None or ts > last_seen else last_seen

    skill_files = list_skill_files()
    skill_files_set = set(skill_files)
    loaded = set(reload_counts.keys())
    cold = [f for f in skill_files if f not in loaded]

    # ── Declared-vs-read partition ────────────────────────────
    declared_set: set[str] = set()
    declared_invalid: list[str] = []
    declared_source: str = "none"
    declared_per_file: dict[str, list[str]] = {}

    if args.declared:
        declared_set, declared_invalid, _raw = load_explicit_declared(
            args.declared, skill_files_set
        )
        declared_source = f"--declared {args.declared}"
    elif not args.no_auto_declared:
        declared_set, declared_invalid, declared_per_file = scan_chapter_note_declarations(
            skill_files_set
        )
        declared_source = f"auto-scan: {JOURNAL_BOOKS_DIR}/**/ch-*.md"

    read_and_declared = sorted(loaded & declared_set)
    read_not_declared = sorted(loaded - declared_set)
    declared_not_read = sorted(declared_set - loaded)
    unknown_or_context_carried = sorted(
        skill_files_set - loaded - declared_set
    )

    if args.json:
        out = {
            "period": args.period,
            "total_reads": total_reads,
            "first_seen": first_seen.isoformat() if first_seen else None,
            "last_seen": last_seen.isoformat() if last_seen else None,
            "session_count": len(session_paths),
            "reload_counts": dict(reload_counts.most_common()),
            "cold_references": cold,
            "per_session_breadth": {sid: len(p) for sid, p in session_paths.items()},
            "declared_source": declared_source,
            "declared_count": len(declared_set),
            "declared_invalid": declared_invalid,
            "partition": {
                "read_and_declared": read_and_declared,
                "read_not_declared": read_not_declared,
                "declared_not_read": declared_not_read,
                "unknown_or_context_carried": unknown_or_context_carried,
            },
        }
        json.dump(out, sys.stdout, indent=2, ensure_ascii=False, default=str)
        sys.stdout.write("\n")
        return 0

    print(f"=== study-session reference coverage — period: {args.period} ===")
    print(f"    log dir: {LOG_DIR}")
    if total_reads == 0:
        if not LOG_DIR.exists():
            print(
                "\n  No log dir yet — PostToolUse hook hasn't fired any qualifying Reads.\n"
                "  Verify ~/.claude/settings.json hooks section + scripts/log_reference_read.sh."
            )
        else:
            print(
                "\n  No entries in this window. Try --period all, "
                "or wait for a real study-session run to populate the log."
            )
        return 0

    print(f"    total reads: {total_reads}")
    print(f"    sessions:    {len(session_paths)}")
    print(f"    first entry: {first_seen.isoformat() if first_seen else '-'}")
    print(f"    last entry:  {last_seen.isoformat() if last_seen else '-'}")

    print("\n--- Reload counts (most → least) ---")
    for path, count in reload_counts.most_common():
        n_sessions = sum(1 for paths in session_paths.values() if path in paths)
        print(f"  {count:4d} reads / {n_sessions:3d} sessions   {path}")

    print(f"\n--- Cold references ({len(cold)} files never loaded) ---")
    if not cold:
        print("  (none — every reference has been loaded at least once)")
    else:
        print("  Interpretation hints:")
        print("    - L2 / language refs cold = no English-book session in window (likely fine)")
        print("    - Method refs cold = chapter type never invoked them (check routing)")
        print("    - Policy refs cold = SKILL.md routing table may not point there")
        print()
        for f in cold:
            print(f"    {f}")

    print("\n--- Per-session breadth (refs read in one session) ---")
    breadth_counts = Counter(len(paths) for paths in session_paths.values())
    for breadth in sorted(breadth_counts.keys()):
        n = breadth_counts[breadth]
        bar = "▇" * min(n, 40)
        print(f"  {breadth:3d} refs  {bar} ({n})")
    avg = sum(len(p) for p in session_paths.values()) / max(len(session_paths), 1)
    print(f"\n  Average: {avg:.1f} refs/session")

    # ── Declared-vs-read partition ────────────────────────────
    print("\n--- Declared-vs-read partition ---")
    print(f"  declared source: {declared_source}")
    print(f"  declared (valid):   {len(declared_set):4d}")
    print(f"  declared (invalid): {len(declared_invalid):4d}")
    print()
    print(f"  read_and_declared:          {len(read_and_declared):4d}")
    print(f"  read_not_declared:          {len(read_not_declared):4d}")
    print(f"  declared_not_read:          {len(declared_not_read):4d}   ← drift signal")
    print(f"  unknown_or_context_carried: {len(unknown_or_context_carried):4d}")

    if declared_not_read:
        print("\n  declared_not_read (cited but not Read in window — contract violations):")
        for f in declared_not_read:
            print(f"    {f}")
        print(
            "\n  Soft-warning note: chapter-note frontmatter is append-only, so a file may "
            "have been Read in an earlier period. Re-run with `--period all` to widen the "
            "window before treating as a hard violation."
        )

    if declared_invalid:
        print(
            f"\n  declared_invalid ({len(declared_invalid)} entries don't resolve to any "
            "skill file — likely hallucinated or typo'd):"
        )
        for entry in declared_invalid[:20]:
            print(f"    {entry}")
        if len(declared_invalid) > 20:
            print(f"    ... and {len(declared_invalid) - 20} more")

    if read_not_declared:
        print(
            "\n  read_not_declared (loaded into context but absent from chapter-note "
            "declarations — minor; may be a missed footer):"
        )
        for f in read_not_declared:
            print(f"    {f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

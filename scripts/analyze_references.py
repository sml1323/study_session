#!/usr/bin/env python3
"""Reference reload coverage report for the study-session skill.

Reads ~/study-journal/.session-log/<date>.jsonl (PostToolUse hook output,
written by scripts/log_reference_read.sh) and reports:

  - reload counts per reference / method file (most → least)
  - cold references: in the skill but never loaded in the window
  - per-session reference breadth distribution

Usage:
    python3 scripts/analyze_references.py
    python3 scripts/analyze_references.py --period 7d
    python3 scripts/analyze_references.py --period all --json
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
    loaded = set(reload_counts.keys())
    cold = [f for f in skill_files if f not in loaded]

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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

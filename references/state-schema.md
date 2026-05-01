# State Schema — Single Source of Truth

This file is the **canonical SOT** for chapter status values and frontmatter fields used by `books.yml` and chapter notes. Any other reference, fixture, or eval must conform to this enum. The lint script `scripts/lint_state.py` enforces it.

If a status value is not in this enum, it does not exist. Do not invent new states; if the lifecycle needs a new state, add it here first, then propagate.

## Canonical chapter status enum

A chapter is always in **exactly one** of the following states:

| Status | Meaning | Set by | Next transition |
|---|---|---|---|
| `in-progress` | Plan done; Phase 2 reading underway across one or more sessions; chapter not yet read end-to-end | tutor mode (during Phase 2) | → `phase-2-pending-conversion` (raw PIMEQ marginalia exist at end of Phase 2) **or** → `phase-3-pending` (Phase 2 ended cleanly with conversion done in-session) |
| `phase-2-pending-conversion` | Reading done; raw PIMEQ marginalia or bare highlights still need to be converted to source / concept / retrieval cards | end of tutor mode if conversion deferred | → `phase-3-pending` once the conversion pass runs |
| `phase-3-pending` | Phase 2 fully complete (including conversion); calibrate has **not** run yet | end of tutor mode (post-conversion) **or** end of conversion pass | → `phase-3-textbase-only` (Step 2b skipped) **or** → `phase-3-complete` (Step 2b ran and SM gate passed) **or** stays here on Step 2b retry/SM-fail |
| `phase-3-textbase-only` | Calibrate Step 2a (textbase recall) ran; Step 2b (situation-model transfer) was skipped (typically light intensity); `chapter_complete` is **false** | calibrate mode (light path) | → `phase-3-pending` once Step 2b is queued for next session, **or** → `phase-3-complete` when Step 2b runs and passes |
| `phase-3-complete` | Calibrate fully ran; `situation_model_transfer_score` met the book-type gate; `chapter_complete: true` | calibrate mode (full path, gate passed) | → `applied` after Phase 4 transfer attempt logged, **or** → `scheduled` if no transfer attempt and chapter enters spaced re-engagement |
| `applied` | Phase 4 transfer attempt logged (success / partial / failure / domain-mismatch); chapter has produced an external use | apply sub-step | → `scheduled` once the spaced re-engagement queue is set |
| `scheduled` | Chapter is fully done as an active learning unit and now lives only on the spaced re-engagement queue (1d / 1w / 1m) | compose mode after Phase 4 (or after Phase 3 if no Phase 4) | terminal — only spaced retrieval entries append from here |

### Removed / deprecated

The following states **must not appear** in any document or fixture:

| Deprecated | Replacement | Reason |
|---|---|---|
| `phase-2-complete` | `phase-3-pending` (post-conversion, no calibrate yet) **or** `phase-2-pending-conversion` (raw marginalia outstanding) | Redundant with `phase-3-pending`; created ambiguity about whether conversion was done |
| `phase-3-incomplete` | `phase-3-pending` | Two names for the same state; lint rejects it |
| `complete` (bare, no phase prefix) | `phase-3-complete` | Ambiguous about which phase is meant; lint rejects it for the chapter `status:` field. Note: per-chapter shorthand inside `chapter_status:` blocks of `books.yml` (e.g., `1: complete`) is an aggregate "this chapter is done end-to-end" alias and is **allowed only inside `chapter_status:`**, not as the chapter note frontmatter `status:` value. Prefer `phase-3-complete` everywhere. |

### State transitions (diagram)

```
                    plan done
                       │
                       ▼
                 in-progress ──── Phase 2 reading ───┐
                       │                             │
       conversion done │                             │ raw marginalia at session close
                       ▼                             ▼
              phase-3-pending ◀──────── phase-2-pending-conversion
                       │                             │
                       │     conversion pass runs ───┘
                       │
                  calibrate runs
                       │
            ┌──────────┴──────────┐
            │                     │
   Step 2b skipped         Step 2b ran
   (light intensity)       and SM gate passed
            │                     │
            ▼                     ▼
   phase-3-textbase-only   phase-3-complete
            │                     │
   Step 2b runs &                 │
   SM gate passed                 ▼
            └─────────────▶  applied (Phase 4 logged)
                                  │
                                  ▼
                              scheduled
```

If Phase 3 runs but the SM gate fails, status **stays at `phase-3-pending`** and a Step 2b-only retry is queued for ≥ 24 hr later. Do not invent a "phase-3-failed" state.

## Frontmatter fields — chapter note

Required at every status (some are populated as the chapter advances; "required" here means the field exists in the frontmatter, even if `null`):

| Field | Type | When populated | Notes |
|---|---|---|---|
| `title` | string | created | `<book> Ch.<N> — <chapter-title>` |
| `book` | string (slug) | created | matches a key in `books.yml` `books:` |
| `chapter` | int or string | created | int for numbered chapters; string for named parts (e.g., Polya `"I"`) |
| `type` | enum | created | one of `methodology` / `problem-driven` / `conceptual` / `argument-driven` / `reference` |
| `status` | enum | created, updated each phase transition | from the canonical enum above |
| `sessions` | int | bumped each session | |
| `created` | date | created | ISO date |
| `last_session` | date | updated each session | ISO date |
| `phase_2_ended_at` | ISO 8601 datetime or `null` | end of Phase 2 | drives calibrate gating (30-min floor for same-session opt-in; 5-day stale threshold) |
| `hint_levels` | list[int] | each help moment | one entry per moment, 0–4 |
| `avg_hint_level` | float | end of session | derived from `hint_levels` |
| `avg_answer_length` | int | end of session | mean words per response |

Phase 3 metrics — populated when calibrate runs:

| Field | Type | Notes |
|---|---|---|
| `textbase_recall_coverage` | float 0–1 or `null` | Step 2a/3 score; advisory floor by book type |
| `situation_model_transfer_score` | float 0–1 or `null` | mean of Step 2b transfer questions; **gate** for `chapter_complete` |
| `situation_model_transfer_questions_count` | int | 0 if Step 2b skipped (light intensity) |
| `chapter_complete` | bool | gated on `situation_model_transfer_score` meeting book-type threshold |
| `confidence_self_report` | int 0–100 | captured **before** recall (Step 1) |
| `confidence_accuracy_gap` | int | `confidence_self_report - situation_model_transfer_score * 100` |
| `calibrate_same_session` | bool | true if Phase 3 ran in same sitting as Phase 2 (opt-in path) |
| `phase_3_downgraded_to_quiz` | bool | true if calibrate downgraded to 3-question quiz (5+ day stale) |
| `phase_3_attempts` | int | bumped on each retry |
| `textbase_low_but_transfer_pass` | bool | rare path: textbase < advisory floor but SM ≥ gate |

Health and meta:

| Field | Type | Notes |
|---|---|---|
| `session_health` | object with 6 bools | all six tier flags; see `references/failure-modes.md` |
| `prompt_bloom_distribution` | object | 6 Bloom levels; flagged when `understand` > 70% |
| `review_queue` | list of `{due, type}` | spaced retrieval queue |
| `related_chapters` | list of `{book, chapter, relation}` | cross-refs |
| `evergreen_extracts` | list of paths | `~/study-journal/evergreen/*.md` |
| `concept_candidates` | list of strings | trigger-deferred concept tracking |

Full body section schema lives in `references/chapter-template.md`.

## Frontmatter fields — `books.yml`

Per book entry:

| Field | Type | Notes |
|---|---|---|
| `title`, `authors`, `edition`, `path`, `format` | strings | book identity |
| `type` | enum | book-level type; same enum as chapter `type:` |
| `genre_lean` | enum | `narrative-leaning` / `expository-leaning` / `mixed` |
| `total_pages`, `printed_page_offset` | int | for citation discipline |
| `current_chapter` | int or string | most recent chapter touched |
| `chapter_status` | object `{N: status}` | one entry per chapter studied so far; values from canonical enum (or aggregate `complete` shorthand inside this block only) |
| `chapter_metrics` | object | per-chapter Phase 3 metrics; mirrored from each chapter note |
| `review_queue` | list | per-book spaced retrieval queue |

Top-level `books.yml`:

| Field | Type | Notes |
|---|---|---|
| `books` | object | one entry per book slug |
| `review_queue` | list of `{book, chapter, due, type}` | global spaced retrieval queue |

## Lint contract

`scripts/lint_state.py` walks the skill tree and asserts:

1. Every `status:` value (chapter note frontmatter) is in the canonical enum and not in the deprecated list.
2. Every `chapter_status:` map entry value is in the canonical enum, the deprecated list (which fails), or the aggregate alias `complete` (only inside `chapter_status:` blocks).
3. Documents that *describe* the schema (this file, `chapter-template.md`, `calibration.md`, `pdp-loop.md`, `annotation-typology.md`, `SKILL.md`) may mention deprecated names only inside fenced code or explicit "deprecated" tables — the linter only reports plain prose mentions, with this SOT and the deprecated table whitelisted.
4. Required chapter-note frontmatter fields (`title`, `book`, `chapter`, `type`, `status`, `created`) are present in every fixture chapter note; missing fields are warnings.

The lint runs without external packages (Python standard library only). Run from skill root:

```
python3 scripts/lint_state.py .
```

Exit code 0 = clean; non-zero = violations found.

## Cross-references

- `SKILL.md` — uses these states in the spine and the "Things to avoid" rules
- `references/chapter-template.md` — full body schema; frontmatter mirrors this file
- `references/calibration.md` — Step 2a/2b mechanics, gate thresholds, status transitions in calibrate
- `references/annotation-typology.md` — defines when `phase-2-pending-conversion` applies
- `references/pdp-loop.md` — pseudocode for state transitions
- `evals/fixtures/**` — must conform to this enum

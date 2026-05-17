# State Schema — Single Source of Truth
<!-- TODO evidence-tag - see references/evidence-labels.md; this files thresholds/policies are not yet labeled -->

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
| `situation_model_transfer_score` | float 0–1 or `null` | mean of Step 2b transfer questions |
| `situation_model_transfer_questions_count` | int | 0 if Step 2b skipped (light intensity) |
| `learning_passed` | bool | `situation_model_transfer_score` meets the book-type gate. **The chapter_complete signal** (see Decision rule #4 in SKILL.md). |
| `chapter_complete` | bool | **= `learning_passed`** (B1 split, 2026-05-17). Calibration health is tracked separately and does not hard-block this. |
| `calibration_gap_abs` | int 0–100 or `null` | `\|score_prediction − actual_score\|` (Phase 3 Step 4a). `null` if either score is missing. |
| `calibration_health` | enum | `well_calibrated` (abs ≤ 10) / `loose` (10 < abs ≤ 20) / `over_confident` (abs > 20, predicted > actual) / `under_confident` (abs > 20, predicted < actual) / `unknown` (gap not computable). See § "calibration_health enum" below. |
| `confirm_next_chapter` | bool | `true` when `calibration_gap_abs > 30` — the next session's open should prompt the user for confirmation before advancing chapters. Default `false`. |
| `confidence_self_report` | int 0–100 | captured **before** recall (Step 1) |
| `confidence_accuracy_gap` | int | `confidence_self_report - situation_model_transfer_score * 100`; legacy diffuse-confidence gap, retained for trend |
| `calibrate_same_session` | bool | true if Phase 3 ran in same sitting as Phase 2 (opt-in path) |
| `phase_3_downgraded_to_quiz` | bool | true if calibrate downgraded to 3-question quiz (5+ day stale) |
| `phase_3_attempts` | int | bumped on each retry |
| `textbase_low_but_transfer_pass` | bool | rare path: textbase < advisory floor but SM ≥ gate |

### `calibration_health` enum

| Value | Meaning | Trigger |
|---|---|---|
| `well_calibrated` | abs gap ≤ 10. Metacomprehension is functioning. | `calibration_gap_abs ≤ 10` |
| `loose` | abs gap 11–20. Borderline; watch trend. | `10 < calibration_gap_abs ≤ 20` |
| `over_confident` | abs gap > 20, predicted higher than actual. Illusion-of-understanding signal. | `calibration_gap_abs > 20` AND `score_prediction > actual_score` |
| `under_confident` | abs gap > 20, predicted lower than actual. Imposter-signal candidate; surface as positive. | `calibration_gap_abs > 20` AND `score_prediction < actual_score` |
| `unknown` | `score_prediction` or `actual_score` not captured (e.g., light-intensity light path; Step 2b skipped). | either score missing |

The split between `chapter_complete` (= `learning_passed`) and `calibration_health` is the B1 reviewer-patch split: a chapter can be learning-passed and over-confident at the same time; conflating them into one gate hid the calibration signal. Down-stream: `over_confident` chapters get a 24-hr Step 2b retry on a fresh scenario *and* a `confirm_next_chapter: true` flag, but the chapter is no longer hard-blocked from `phase-3-complete`.

### Backward compatibility

Existing chapter notes (created before 2026-05-17) carry the pre-B1 single-gate `chapter_complete` definition (= SM AND abs_gap ≤ 20). They are **read-only under the new schema**: do not retroactively rewrite their frontmatter to add `learning_passed` / `calibration_health` / `confirm_next_chapter`. The lint script treats absence of B1 fields on a pre-B1 chapter note as expected, not as a violation. New chapter notes (Phase 3 runs after 2026-05-17) use the split schema.

Health and meta:

| Field | Type | Notes |
|---|---|---|
| `session_health` | object with 6 bools | all six tier flags; see `references/failure-modes.md` |
| `prompt_bloom_distribution` | object | 6 Bloom levels; flagged when `understand` > 70% |
| `review_queue` | list of `{due, type}` | spaced retrieval queue |
| `related_chapters` | list of `{book, chapter, relation}` | cross-refs |
| `evergreen_extracts` | list of paths | `~/study-journal/evergreen/*.md` |
| `concept_candidates` | list of strings | trigger-deferred concept tracking |
| `session_health.label_migration` | enum or `null` | one of `pending` / `renamed` / `left-as-is` / `null`; flagged when a chapter note's existing recall rows use `R-P / R-I / R-M / R-E / R-Q` form and migration was surfaced. See `references/annotation-typology.md § Reserved letters` |
| `references_touched` | list[string] | per-response self-declared refs, append-only with dedup; `file§section` form (e.g., `pdp-loop.md§TUTOR`); see `SKILL.md § Per-response context surfacing` |
| `methods_invoked` | list[string] | per-response self-declared method sub-routines, append-only with dedup; bare filename or `file§section` form (e.g., `arq.md§Step-4-steelman`); `methods/` prefix omitted |

Full body section schema lives in `references/chapter-template.md`.

### Recall-table label convention

Closed-book recall tables in the chapter note body (Phase 2 chunk-boundary recalls, Phase 3 calibrate textbase recall) use **numeric row labels**:

- Row keys: `R1`, `R2`, `R3`, ... — *never* `R-P`, `R-I`, `R-M`, `R-E`, `R-Q`.
- The probe category word lives as a subscript on the schema key (`R1_proposition`) and is optional as a parenthetical in surface output (`R1 (proposition): ...`).
- Single-letter `P / I / M / E / Q` is reserved for margin PIMEQ prefixes (see `references/annotation-typology.md`). Recall rows must not collide with margin prefix letters because shared first letters induce structural hallucination across sessions (the recall row's category word leaks into the next session's margin PIMEQ vocabulary).
- Per-book-type probe schemas: `references/generative-prompts.md § recall_probe_schema`.

The lint script does **not** currently enforce this convention (it's a content rule, not a status-enum rule). Detected via the chapter-note rendering pattern at session resume; surfaced under `session_health.label_migration` for affected legacy notes.

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
| `chapter_structure` | object `{N: {title, sections: [...]}}` | per-chapter section list; populated at init (full ToC) or lazily on first entry; full schema + section status enum in `references/section-tracking.md` |
| `chapter_metrics` | object | per-chapter metrics — **metadata-only** (enums/numbers/dates/status maps/short anchors). Long-form narrative is forbidden; see § "books.yml `chapter_metrics` — allowed and forbidden fields" below |
| `review_queue` | list | per-book spaced retrieval queue |

## books.yml `chapter_metrics` — allowed and forbidden fields

`books.yml` is re-cached on every `Edit` tool call. Long-form session narrative inside `chapter_metrics[N]` inflates `cache_create` on each save and historically accounted for 30–40% of session token cost (audited 2026-05-12: one 47-turn session burned $9.60 of cache_create against a 30 KB books.yml that had grown to hold per-session `progress` strings of 2–3 KB each).

The fix is structural: `chapter_metrics[N]` carries *only* machine-readable signals; narrative spills to the chapter note body or to `books/<slug>/_archived/`.

### Allowed (metadata-only)

| Field | Type | Notes |
|---|---|---|
| `phase_2_ended_at` | ISO 8601 datetime | drives calibrate gating |
| `session_count` | int | bumped per session |
| `phase_3_attempts` | int | bumped per Phase 3 retry |
| `phase_3_downgraded_to_quiz` | bool | stale-calibrate flag |
| `textbase_recall_coverage` | float 0–1 | Step 2a/3 |
| `situation_model_transfer_score` | float 0–1 | Step 2b gate |
| `situation_model_transfer_questions_count` | int | 0 if Step 2b skipped |
| `chapter_complete` | bool | gated on SM score |
| `confidence_accuracy_gap_session_N` | int | one per session, signed |
| `closed_book_coverage_attempt_N` | float | legacy attempt scores |
| `confidence_self_report_attempt_N` | int 0–100 | legacy |
| `confidence_accuracy_gap_attempt_N` | int | legacy |
| `spaced_retrievals` | list of `{date, type, q_count, score}` rows | machine-readable; `notes` field optional but cap **one short sentence** if present |
| `session_health` | object with **enum/boolean keys only** (`illusion`, `surface`, `struggle_skip`, `echo`, `form_fatigue`, `hint_abuse`, plus book-specific enum flags) | no `*_note` qualifiers |
| `section_progress` | object `{section_id: status}` | mirrors `chapter_structure[N].sections` |
| `archived` | string (path) | cross-reference to `books/<slug>/_archived/books-yml-snapshot-<date>.md` if a slim-down has run |
| `title`, `genre_lean`, `ai_policy`, `intensity` (Feynman-style per-chapter overrides) | enum/string | per-chapter metadata when it differs from book-level |

### Forbidden (move to chapter note body or `_archived/`)

| Pattern | Where it goes |
|---|---|
| `progress: "..."` (any length) | chapter note § "Session N" body |
| `session_N_progress_archive: "..."` | chapter note § "Session N" body |
| `session_N_recall_notes: "..."` | chapter note § "Phase 3 — Calibrate" body |
| `section_progress_notes: { "X.Y": "narrative" }` | chapter note § "Section progress" + per-section "Open threads" |
| `next_session_warmup_anchors: [...]` (long bullets) | chapter note § "다음 session warmup anchor" body |
| `counter_feedback_event: {claim_by_ai, counter_by_user, ...}` | chapter note § "Notable events" or "Open threads" |
| `misconceptions_active: {M1: "narrative", ...}` | chapter note § "Phase 1" misconceptions or evergreen note |
| `session_health.*_note` (any narrative qualifier on a health flag) | chapter note § "session_health" body |
| `legacy_metric_note` / `situation_model_transfer_note` / `confidence_accuracy_gap_session_N_note` | chapter note § "Phase 3" body |
| anything else > ~80 chars of prose | chapter note body |

Rule of thumb: if the value is a complete Korean/English sentence rather than a token, enum, number, or date, it belongs in the chapter note, not `books.yml`.

### Migration when a `books.yml` has already grown long-form

Do not silently delete. Snapshot first, then slim:

1. Create `books/<slug>/_archived/books-yml-snapshot-<YYYY-MM-DD>.md`
2. Dump every forbidden field verbatim as markdown sections (preserves the YAML string value as a blockquote so the user can later re-narrativize into chapter note prose)
3. Remove the forbidden fields from `books.yml`
4. Add `archived: books/<slug>/_archived/books-yml-snapshot-<date>.md` inside the relevant `chapter_metrics[N]` so future sessions can find the dump

The compose step at session end **must enforce this**: when populating `chapter_metrics[N]`, surface any narrative string as a candidate spill into the chapter note instead of writing it into `books.yml`.

## Canonical section status enum (orthogonal to chapter status)

Sections inside a chapter carry their own status, defined here as the SOT. This axis is *independent* of the chapter-level enum above — a chapter is `in-progress` while its sections are mostly `pending`. Full semantics, transitions, and the chapter-completion gate built on this enum live in `references/section-tracking.md`.

| Status | Meaning |
|---|---|
| `pending` | Default; not yet processed |
| `in-progress` | Mid-section session close; current chunk lives here |
| `covered` | Closed-book recall + PIMEQ both ran on the section's narrative |
| `used-as-exercise` | Section's prose was used as training material for some method, but the section's own narrative claims were not processed via recall + PIMEQ — **learning debt** |
| `skipped` | Explicit user bypass; reason recorded in chapter-note Section progress block |

`covered` and `used-as-exercise` are **not** interchangeable. Phase-3 advancement and any "next chapter" recommendation requires every section to be `covered` or `skipped`.

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

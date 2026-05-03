# Chapter Note Template

The chapter note is the *byproduct* of the session, auto-filled by the compose mode from session traces. The user does not face a blank form — the skill captures answers during the session and writes them out.

## File location

```
~/study-journal/books/<book-slug>/ch-NN-<title-slug>.md
```

Example: `~/study-journal/books/arq/ch-04-rival-causes.md`

For Polya by part:
- `~/study-journal/books/polya/part-1-classroom.md` (treated as one "chapter")
- `~/study-journal/books/polya/part-2-<heuristic-slug>.md` (per heuristic if studied actively)
- `~/study-journal/books/polya/part-3-ex-NN-<slug>.md` (per worked example)

For Feynman volumes:
- `~/study-journal/books/feynman-vol-1/ch-NN-<title>.md`

## Frontmatter schema (full)

```yaml
---
title: <book-name> Ch.<N> — <chapter-title>
book: <slug>
chapter: <number-or-id>
type: methodology | problem-driven | conceptual | argument-driven | reference
status: in-progress | phase-2-pending-conversion | phase-3-pending | phase-3-textbase-only | phase-3-complete | applied | scheduled   # canonical enum lives in references/state-schema.md
sessions: <count>
created: YYYY-MM-DD
last_session: YYYY-MM-DD
phase_2_ended_at: 2026-04-28T14:30:00+09:00   # ISO8601; set when Phase 2 reading concludes; drives calibrate gating
hint_levels: [0, 1, 1, 2, 0]   # one entry per help moment
avg_hint_level: 0.8
avg_answer_length: 35           # words

# Phase 3 metrics (populated after calibrate; textbase and situation model are scored separately)
textbase_recall_coverage: 0.65            # 0-1, Step 2a/3 scoring — what the chapter said (advisory)
situation_model_transfer_score: 0.75      # 0-1, mean of Step 2b transfer questions — gate for chapter_complete
situation_model_transfer_questions_count: 2  # number of Step 2b questions asked (0 if skipped)
chapter_complete: true                    # gated on situation_model_transfer_score AND abs_gap ≤ 20
confidence_self_report: 80                # 0-100, Step 1 diffuse confidence (legacy)
score_prediction: 75                      # 0-100, Step 1 behavioral exam-score forecast — captured BEFORE recall
actual_score: 70                          # composite: textbase_recall_coverage*50 + situation_model_transfer_score*50
score_prediction_gap: 5                   # Step 4a, signed (prediction − actual)
abs_gap: 5                                # |score_prediction_gap|; ≤10 well-calibrated, 11-20 borderline, >20 illusion
calibration_diagnosis: well-calibrated    # well-calibrated | borderline | illusion
confidence_accuracy_gap: 5                # confidence_self_report - SM*100 (Step 4b, legacy gap kept for trend)
categorization_re_test:                   # populated when Phase 1 ran the Mason-Singh micro-task
  phase_1_grouping: surface               # surface | mixed | principle
  phase_3_grouping: principle
  shift: surface_to_principle             # surface_to_principle | unchanged | regression
calibrate_same_session: false             # true if Phase 3 ran in the same sitting as Phase 2 (opt-in path)
phase_3_downgraded_to_quiz: false         # true if calibrate was downgraded to a 3-question quiz (5+ day stale)
phase_3_attempts: 1                       # bumped each time user retries Phase 3
textbase_low_but_transfer_pass: false     # rare path: textbase < advisory floor but SM transfer ≥ gate

# Health flags
session_health:
  hint_abuse: false
  illusion: false
  surface: false
  struggle_skip: false
  form_fatigue: false
  echo: false

# AI dialogue Bloom-level distribution (per chapter; see references/llm-tutor-design.md)
prompt_bloom_distribution:
  remember: 0
  understand: 8
  apply: 1
  analyze: 0
  evaluate: 0
  create: 0
# When `understand` > 70% of total, the chapter is flagged for prompt-diversification at session end.

# Spaced retrieval queue (set after Phase 4)
review_queue:
  - { due: 2026-04-29, type: 1d }
  - { due: 2026-05-05, type: 1w }
  - { due: 2026-05-28, type: 1m }

# Daily-floor commitment device (see references/spacing-policy.md)
daily_floor:
  target_distinct_days: 5                 # computed from book type
  retrievals_per_day_min: 2
  window_end: 2026-05-14                  # 14 days from Phase 2 close (problem-driven gets 21)
  retrievals_executed:                    # behavior-counted, not exposure-counted
    - { date: 2026-05-01, count: 2, types: [chunk_recall, transfer_attempt] }
  status: active                          # active | met | missed

# External deadline anchor (see references/spacing-policy.md § Shift 3)
external_deadline:
  type: mock-exam | semester-end | self-set | cohort-exam | other | null
  date: 2026-06-15
  description: "med school 4th-year mock 2 (KMLE prep)"
  social_anchor: "study group meets every Monday"   # optional

# FCI/BEMA-style self-diagnostic (computed at +1m or external_deadline.date, whichever first)
self_diagnostic:
  metric: normalized_gain
  pre_score: 0.35                         # Phase 1 baseline on expectations + misconceptions
  post_score: 0.78                        # +1m spaced retrieval coverage on the same items
  normalized_gain: 0.66                   # (post-pre) / (1-pre)
  expected_band: { low: 0.30, high: 0.40 }
  diagnosis: above_band                   # below_band | in_band | above_band
  computed_at: 2026-05-30

# Exam-wrapper trace (auto-appended every chapter; ritual not optional — Hodges 2020, Ratnayake 2023)
exam_wrapper_trace:
  abs_gap: 5
  hint_levels_summary: { max: 2, avg: 0.8, level_4_count: 0 }
  active_review_attempts: 4               # closed-book recall + transfer attempts during the chapter
  transfer_attempt_result: success
  composed_at: 2026-05-03

# Cross-refs
related_chapters:
  - { book: arq, chapter: 3, relation: "depends-on" }
  - { book: polya, part: I, relation: "method-shared" }

evergreen_extracts:                # if extract mode pulled atomic principles
  - ../evergreen/arq-rival-causes-checklist.md

# Learner profile (used to differentiate default schedule + flag transfer hypotheses)
# Most recommendations to Korean STEM learners are TRANSFER HYPOTHESES — direct evidence in
# Korean STEM populations is sparse. Mark explicitly when surfacing recommendations.
# Direct evidence anchor: Chung 2024 — Korean med 4th-year mock exam as dominant retrieval signal.
learner_profile:
  ui_language: ko                  # ko | en | other
  textbook_origin: translated      # original | translated | bilingual | mixed
  school_context: med-school       # med-school | engineering | hs-csat | hs-peet | grad | none | other
  exam_target: KMLE                # KMLE | PEET | CSAT | self-set | none | other
                                   # (Patch v3 names KMLE/PEET/CSAT only; other Korean STEM exams
                                   #  go under `other` with a free-text description until R11 expands the enum.)
  transfer_hypothesis_flag: true   # true if recommendations to this learner are transfer-hypothesis
                                   # rather than directly evidenced for the population
---
```

## Body sections

```markdown
# Ch.<N> — <title>

## Phase 1 — Plan
- **PKA dump**: <user's pre-reading dump>
- **Prediction**: <user's prediction>
- **Goal question**: <user's specific question>

### Expectations (skill-generated)
- ...
- ...
- ...

### Misconceptions to watch (skill-generated)
- ...
- ...

---

## Phase 2 — During reading

### Session 1 — YYYY-MM-DD (avg hint X.X, avg answer N words)

#### Section 1
- **concept_define [X]**: <user's response>
  - *Feedback*: <skill's specific feedback>
- **next_predict**: <prediction> → **actual**: <what happened> → **gap**: <miss/match>
- **monitoring_failures**: [section, reason] (if any)
- **selective_annotations**:
  - p.142 — <claim> (high-leverage)
  - p.143 — <claim>

#### Section 2
- ...

#### ARQ extract (if argument present)
- (See `references/methods/arq.md` for the format. Block embedded inline.)

```yaml
arq_extracts:
  - target: "Section 4.2 — author's argument for X"
    issue: "..."
    conclusion: "..."
    reasons_evidence: "..."
    assumptions: { facts: "...", values: "..." }
    alternative_conclusions: "..."
    judgment: "부분 동의"
    self_explanation_one_line: "..."
    optional: { fallacy: null, rival_causes: "...", ... }
    citations: [...]
```

#### Polya log (if problem present)
- (See `references/methods/polya.md` for the format.)

```yaml
polya_logs:
  - problem_ref: "..."
    understand: { restated, given, goal, conditions }
    plan: { similar_to, strategy, sub_problems }
    carry_out:
      steps: [{ do, schoenfeld: { what, why, how } }, ...]
      failed_attempts: [...]
    answer: { result, sanity_check }
    hint_level: 2
    look_back: { principle, deep_structure, shared_with, schema_category }
    optional: { newman_diagnosis, ... }
```

### Session 2 — YYYY-MM-DD (continued)

(append-only; new session here, do not edit Session 1)

---

## Phase 3 — Calibrate (opening warmup of next session, by default)

**Date**: YYYY-MM-DD (delay from Phase 2 last session: <hours>; mode: cross-session | same-session-optin | downgraded-to-quiz)

### Confidence + score prediction (both before recall)
- Diffuse confidence: 80/100 (legacy)
- **Score prediction** (final-exam forecast): 75/100 — gate input

### Step 2a — Textbase recall (what the chapter said)
<user's typed 1-page summary, captured before opening chapter>

### Step 2b — Situation-model transfer (apply to NEW examples)
- Q1: "<transfer question with new scenario>"
  - User answer: "<...>"
  - Score: 1.0 / 0.5 / 0
  - Notes: "<what was missing or wrong>"
- Q2: "<another transfer question>"
  - User answer: "<...>"
  - Score: 0.5
  - Notes: "<right framework, wrong scope>"

### Gap calibration (textbase scoring)
- Expectations covered: 4/5
- Concept_defines covered: 6/8
- Factual errors:
  - "<wrong claim>"
  - "<wrong claim>"
- `textbase_recall_coverage`: 0.75
- `situation_model_transfer_score`: 0.75 (mean of Step 2b)

### Calibration gaps
- **Score-prediction gap (gate)**: predicted 75, actual 70, abs_gap 5 → well-calibrated (≤10)
- Confidence-accuracy gap (legacy): 80 − 75 = 5
- Categorization shift (Phase 1 → Phase 3): surface → principle ✓ (schema-formation signal)
- Cross-chapter trend (last 4 chapters' abs_gap): 22 → 14 → 8 → 5 (improving)

### Feynman explanation
<user's explain-to-beginner attempt>
- *Feedback*: <jargon flagged, gap notes>

### Concept map
[link or inline mermaid/ascii]

### Self-test
- Q1: ...
  - A: ...
  - correct: yes
- Q2: ...
- Q3: ...

---

## Phase 4 — Apply

### Transfer attempt
- **Domain**: <different domain user picked>
- **Mapping**: <how chapter principle applies>
- **Where it breaks**: <limit case>
- **Result**: success | partial | failure | domain-mismatch

### Spaced re-engagement scheduled
- +1 day: 2026-04-29
- +1 week: 2026-05-05
- +1 month: 2026-05-28

---

## Open threads
- <thing still unclear>
- <topic to follow up>

## Cross-chapter notes
- Connects to Ch.3 because: ...
- Differs from Ch.5's claim about: ...

---

## Spaced retrieval log (filled at +1d, +1w, +1m)

### 2026-04-29 (+1d)
- Prompt: "Name the 3 most important things from Ch.4."
- Answer: ...
- Accuracy: 0.7

### 2026-05-05 (+1w)
- ...
```

## Append-only conventions

- Each session adds a new `### Session N — date` block under Phase 2
- Phase 3 happens once per chapter (re-runs are appended with `### Phase 3 retry — date`)
- Phase 4 transfer attempts can be multiple — each gets its own subsection
- Spaced retrieval entries append over time
- Strikethrough is allowed for explicit corrections to prior entries; do not delete
- Do not edit prior session entries; if a prior answer was wrong, the user revises in a *new* session entry that explicitly references the prior

## Compose mode auto-fill rules

When compose mode runs (end of session or end of phase):

1. Pull session traces from internal state (or transcript if running in Claude Code)
2. Map each captured response to its frontmatter or body section
3. Compute derived fields:
   - `avg_hint_level` from `hint_levels`
   - `avg_answer_length` from session response lengths
   - `actual_score` from `textbase_recall_coverage*50 + situation_model_transfer_score*50`
   - `score_prediction_gap`, `abs_gap`, `calibration_diagnosis` from Step 1 + Step 4a
   - `confidence_accuracy_gap` from `confidence_self_report` + SM transfer (legacy trend)
   - `session_health.illusion` ← true if `abs_gap > 20`
   - `session_health.*` other flags from detection rules in `references/failure-modes.md`
   - `daily_floor.status` from `retrievals_executed` (behavior-counted) vs `target_distinct_days` × `retrievals_per_day_min`
   - `exam_wrapper_trace` block (always — ritual, not optional; Hodges 2020 dose-response)
4. Update `last_session`, increment `sessions`
5. Write file (overwrite if exists for the same date — multiple sessions same day are concatenated within the existing entry block)
6. Update `~/study-journal/books.yml` `chapter_metrics` and `calibration_history`
7. If chapter is at +1m or external_deadline.date arrived (whichever first): compute and append `self_diagnostic` block (FCI/BEMA-style normalized_gain vs expected band)

## Reading the note for resume

When skill resumes a chapter (next session), read:

1. Frontmatter `status` field — determines next phase
2. Last `### Session N` block — picks up section progress
3. `Open threads` — surfaces things to address
4. `Spaced retrieval log` — checks if any retrieval is due

Do not re-read the entire body unless needed for a Phase 3 calibrate.

## Cross-references

- `references/generative-prompts.md` — content of each Phase
- `references/methods/*.md` — formats for embedded ARQ / Polya / Newman blocks
- `references/calibration.md` — Phase 3 specifics
- `references/citation-format.md` — quote_id schema for citations

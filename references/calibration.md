# Calibration — Phase 3 Mechanics

Evidence labels: see `references/evidence-labels.md`. Hard-rule citation gate is defined there — thresholds tagged `operational-heuristic` / `placeholder` below are guidelines, not hard gates, when cited from SKILL.md.

Phase 3 is the **measurement step**. Without it, learning is invisible and self-report substitutes for evidence — and self-reports of understanding are systematically miscalibrated against delayed recall. The skill should not mark a chapter complete without Phase 3. [evidence: placeholder — exact citation pending; the previously cited "Yang 2023, r=0.18" was not externally verifiable; replace with a verified metacomprehension source before next major release.]

## The delay: cross-session by default

Karpicke & Blunt 2011 (Science) compared retrieval practice vs concept mapping. Retrieval won by ~50% on a *delayed* test, but on an *immediate* test the gap was much smaller. The delay is what creates the calibration mechanism. *[evidence: rct-strong — Karpicke & Blunt 2011, Science]*

**Mechanically**: immediate post-reading recall reads from working memory, which is still primed. Delayed recall reads from durable encoding. The two answer different questions:
- Immediate recall = "did you encode the surface?"
- Delayed recall = "did you encode it durably?"

For learning, only the second matters.

**The skill's default**: calibrate runs as the *opening of the next session*, not the tail of the current one. The cross-session gap (hours at minimum, often overnight) is well above the 30-minute floor and is closer to what Karpicke & Blunt 2011 actually measured. This also doubles as `prior_chapter_recall` — the same act covers measurement of Phase 2 *and* spaced retrieval warmup for the new session.

**Same-session calibrate is opt-in only.** The skill checks `phase_2_ended_at` and refuses if `now - phase_2_ended_at < 30 minutes`. The 30-minute floor is the absolute minimum; a real cross-session break (next day) is preferable. Same-session use is opt-in because immediate Phase 3 defeats the purpose: it measures recall from the same encoding pass as Phase 2, not the durable version. Log the run with `calibrate_same_session: true` so the path's usage and outcomes can be reviewed later. *[evidence: operational-heuristic — the 30-min number is a working-memory contamination floor chosen for actionability; no RCT validates this specific cutoff. The qualitative direction (immediate ≠ delayed) is rct-strong (Karpicke & Blunt 2011).]*

**Stale calibrate (5+ days)**: if `phase_2_ended_at` is older than ~5 days, the chapter has aged out of the calibrate window. Coverage at that point measures long-term retention rather than Phase 2 encoding quality, and comparison to expectations is contaminated by general decay. Downgrade to a 3-question retrieval quiz instead of running the full Phase 3 sequence; log `phase_3_downgraded_to_quiz: true`. Quiz results feed the spaced retrieval log, not the Phase 3 metrics. The user can still request a full Phase 3 explicitly — just don't run one by default at that age. *[evidence: operational-heuristic — the 5-day boundary is a first-cut. Forgetting-curve work (Ebbinghaus 1885; modern Cepeda et al. 2008) supports that retention varies steeply with delay, but the specific 5-day cutoff between "Phase 2 encoding quality" and "long-term retention" is operational, not RCT-derived.]*

## The Phase 3 sequence

Run in this order. Do not reshuffle.

The sequence measures **two distinct representations** (Kintsch construction-integration model): a **textbase** (what the chapter said, propositional) and a **situation model** (an integrated mental model that supports inference and transfer). The two are dissociable — a strong textbase can coexist with a weak situation model, or the reverse — so they are scored separately. `chapter_complete` is gated on situation-model transfer, not textbase recall, because durable usable learning lives in the situation model. Recall coverage matters but does not by itself authorize chapter complete.

### Step 1: confidence_check + score_prediction (BOTH before recall)

Two parallel anchors, captured back-to-back **before** any recall attempt. The pair distinguishes generic confidence from a behavioral score prediction; the latter is what calibrates against actual outcome.

> "Before you recall: how confident are you that you can reproduce the chapter's main ideas right now? 0-100."

Capture as `confidence_self_report: <int>`.

> "Now a different question: if a final exam on this chapter were given right now, what score would you predict you'd get? 0-100."

Capture as `score_prediction: <int>`.

Both must come before recall — after is contaminated by the recall attempt itself. The two are not redundant: `confidence_self_report` is a diffuse self-rating (Dunning-Kruger-prone); `score_prediction` is a concrete behavioral forecast that grounds the calibration loop. The score_prediction is the one used in the **±10pt calibration gate** below.

Why score_prediction beats raw confidence (Ratnayake 2023): asking "how confident are you" elicits an affective rating; asking "what score would you get" elicits a behavioral forecast that the user must reason about against a specific imagined task. The two diverge enough that capturing both reveals miscalibration patterns the single-confidence prompt misses. *[evidence: observational — Ratnayake 2023 reports the affective-vs-behavioral distinction; the specific "±10pt gate" cutoff is operational (see Step 4a caveat below).]*

### Step 2a: textbase recall

> "Without looking at the chapter or your notes: write a 1-page summary covering the main claim, the key concepts introduced, and one example from the chapter. Take 10 minutes."

Capture as `textbase_recall: <text>`. The user must not open the chapter file — if running interactively, take their typed recall before showing any chapter content.

### Step 2b: situation-model transfer

After textbase recall is captured (still no chapter access), generate **1-2 transfer questions** that did not appear in the chapter. Each question gives a NEW scenario, example, or domain, and asks the user to apply the chapter's framework or predict its conclusion.

Templates by book type:

- **conceptual**: "Given this NEW scenario [briefly described], what would the chapter's framework predict? Why?"
- **methodology**: "Apply the chapter's method to this NEW [argument / problem / case] — describe the first 2-3 steps you'd take."
- **argument-driven**: "If the chapter's central claim is right, what would it imply about [adjacent unmentioned case]? If it's wrong, what would have to be true instead?"
- **problem-driven**: "Solve this NEW problem in the same family without consulting the chapter's worked examples."

Capture as:

```yaml
situation_model_transfer:
  - prompt: "<the question>"
    answer: "<user's answer>"
    score: 0 | 0.5 | 1   # 1 = applied correctly; 0.5 = partial mapping with one substantive error; 0 = could not apply or wrong direction
    notes: "<what was missing or wrong>"
```

If the chapter is too short, too lookup-style, or the user is genuinely out of time, run only one question and mark `situation_model_transfer_questions_count: 1`. Light-intensity sessions are allowed to skip this step entirely; in that case `chapter_complete` cannot be set to true — flag the chapter as `phase-3-textbase-only` instead.

### Step 3: gap_calibration (textbase scoring)

Open the chapter (or chapter note Phase 1 expectations). Score the textbase recall:

```
expectations_covered = (expectations satisfied in recall) / (total expectations)
concepts_covered = (concept_defines from Phase 2 in recall) / (total concept_defines)
factual_errors = list of wrong claims in recall
textbase_recall_coverage = (expectations_covered + concepts_covered) / 2  # or weighted
```

Report as:

```yaml
gap_calibration:
  expectations_covered: 4/5
  concepts_covered: 6/8
  factual_errors:
    - "Said X is necessary; chapter says X is sufficient"
    - "Confused author's position on Y with the position the author was rebutting"
  textbase_recall_coverage: 0.75
situation_model_transfer_score: 0.5   # mean of Step 2b transfer scores
```

### Step 4: calibration gaps (two computed gaps, ±10pt and confidence)

Compute **both** gaps; they answer different questions.

#### Step 4a — score_prediction_gap (the ±10pt calibration gate)

```
actual_score = (textbase_recall_coverage * w_t) + (situation_model_transfer_score * w_s)   # 0-100 composite, w_t + w_s = 100
score_prediction_gap = score_prediction - actual_score                                     # signed
abs_gap = |score_prediction_gap|
```

> ⚠ **Patch source caveat — `study-session-skill-patch-v3-2026-04-30.md` (Round 10) names the ±10pt calibration gate (Ratnayake 2023) but does NOT specify how to compute `actual_score` from textbase + SM scores.** The composite weighting below is a conservative first-cut, not RCT-validated. Per-book-type splits await R11. *[evidence: operational-heuristic — w_t/w_s table is operational; ±10pt gate name from Ratnayake 2023 is observational.]*

| Book type | `w_t` (textbase weight) | `w_s` (SM weight) | Rationale (placeholder) |
|---|---|---|---|
| methodology | 50 | 50 | balanced; methodology exams test both recall and application |
| conceptual | 50 | 50 | balanced |
| argument-driven | 50 | 50 | balanced; steelman tests both |
| problem-driven | 30 | 70 | exam dominantly tests application |
| math-proof-heavy | 30 | 70 | exam dominantly tests proof transfer |
| reference | n/a | n/a | PDP not enforced |

*All rows above: evidence: operational-heuristic. Replace per-book-type split with user override when they object; do not treat as authoritative.*

When operating: if the user objects to the split (e.g., "my actual exam is 80% recall"), accept their override on a per-chapter basis and store as `actual_score_weights: { textbase: <int>, sm: <int> }` in the chapter note frontmatter. Do not treat the table as authoritative.

| `abs_gap` | Diagnosis | Surfacing |
|---|---|---|
| ≤ 10 | **Well-calibrated.** The user can predict their own performance within ±10pt; metacomprehension is functioning. | Surface as positive: "Predicted X, actual Y, gap Z — well-calibrated." |
| 11-20 | Borderline. | Surface neutrally: "Predicted X, actual Y, gap Z — calibration is loose; watch the trend." |
| > 20 | **Illusion signal.** The user's self-model of their learning is mis-tracking the chapter. | Surface and **recommend the chapter back to retrieval re-entry**: schedule a Step 2b retry on a fresh transfer scenario in 24 hr. See B1's `calibration_health` split below — large `abs_gap` is no longer a hard block on `chapter_complete`; it sets `confirm_next_chapter: true` and surfaces an over/under-confident health label. |

*All three rows: evidence: operational-heuristic. The ≤10 / 11-20 / >20 partition is a first-cut chosen for actionability; Ratnayake 2023 names the ±10pt direction but does not publish the 11-20 vs >20 split.*

Capture:

```yaml
calibration:
  score_prediction: 75
  actual_score: 60
  score_prediction_gap: 15
  abs_gap: 15
  diagnosis: borderline
```

#### Step 4b — confidence_accuracy_gap (legacy gap, retained for trend)

```
confidence_accuracy_gap = confidence_self_report - (situation_model_transfer_score * 100)
```

Compute against situation-model transfer (the gate), not textbase. Retained because the trend over many chapters is informative (does this user systematically over-claim diffuse confidence relative to behavioral prediction?), but the **gate** is `score_prediction_gap` (Step 4a), not this one.

If `confidence_accuracy_gap > 30`: flag illusion signal in `session_health.illusion`.
If `confidence_accuracy_gap < -20` (under-confident): surface as positive — usually means user is calibrating well or has imposter signal.

*[evidence: operational-heuristic — the >30 and <-20 thresholds are first-cut; the legacy gap is retained for trend, not as a primary gate.]*

#### Step 4c — calibration accuracy trend (cross-chapter)

After every Phase 3, append the chapter's `abs_gap` to `books.yml` `calibration_history`:

```yaml
arq:
  calibration_history:
    - { chapter: 1, abs_gap: 22, diagnosis: illusion, date: 2026-04-12 }
    - { chapter: 2, abs_gap: 14, diagnosis: borderline, date: 2026-04-19 }
    - { chapter: 3, abs_gap: 8,  diagnosis: well-calibrated, date: 2026-04-26 }
    - { chapter: 4, abs_gap: 5,  diagnosis: well-calibrated, date: 2026-05-03 }
  calibration_trend: improving         # improving | flat | degrading
```

Surface the trend at chapter close (one line, only when it changed direction):

> "Calibration trend across last 4 chapters: 22 → 14 → 8 → 5. You're learning to predict yourself."

This is the metacomprehension trace the user usually cannot see; making it visible is the highest-leverage move on the calibration side after Phase 3 itself.

### Step 5: feynman_explain

> "Now: explain [chapter's main concept] as if to someone who knows nothing about [field]. No jargon. Take your time."

Capture as `feynman_explanation: <text>`.

**Read for**:
- Jargon leakage (uses chapter's technical terms without redefining)
- Hand-waving on the part that the recall already revealed as a gap
- Length — too short (< 200 words) often signals surface
- Genuine reformulation vs paraphrase of the chapter

### Step 6: concept_map_build (optional but recommended)

> "Sketch a concept map: nodes for the main ideas, edges for relationships. Include at least one link to a concept from a prior chapter."

User outputs ASCII/mermaid/text-described. Skill does not generate the map (Nesbit & Adesope: g=0.82 for *constructed*, g=0.37 for *consumed*). *[evidence: observational — Nesbit & Adesope 2006 meta-analysis effect sizes; not a single RCT but converged across studies.]*

### Step 6b: categorization_re_test (when applicable)

If Phase 1 (plan mode) ran a **categorization micro-task** — e.g., the user grouped 6-8 sample problems into categories before reading the chapter — re-run the same categorization in Phase 3 with the **same problems**. The shift from surface-feature grouping to principle-feature grouping is the schema-formation signal (Mason & Singh 2016).

Concrete protocol (problem-driven, methodology, math-proof-heavy chapters):

1. Show the same 6-8 sample problems used in Phase 1 plan.
2. Ask: "Group these problems. Each group should share something the problems have in common."
3. Capture the grouping.
4. Score: did the user group by **surface features** (the same names, the same numbers, "all the pulley problems") or by **principle features** (the same underlying mechanism, the same Polya schema, the same proof technique)?

```yaml
categorization_re_test:
  problems_shown: 6
  phase_1_grouping: surface     # surface | mixed | principle
  phase_3_grouping: principle
  shift: surface_to_principle    # the learning signal
  notes: "Phase 1 grouped by 'pulley vs spring vs incline'; Phase 3 grouped by 'energy conservation vs force balance vs combined'."
```

A surface→principle shift is strong schema-formation evidence; if `phase_3_grouping` is still surface, the chapter has not produced the schema the chapter intended, regardless of what the recall coverage looks like. Surface this in addition to the score_prediction_gap. *[evidence: observational — Mason & Singh 2016 (and the Chi 1981 surface→principle physics-problem-categorization tradition) report the surface→principle shift as a schema-formation signal; not a single RCT with this exact protocol.]*

If Phase 1 did not run categorization (e.g., on a pure argument-driven chapter where the move does not apply), skip this step. Do not retroactively invent a Phase 1 categorization at Phase 3 time.

### Step 7: self_test_generate

> "Generate 3 questions an exam on this chapter would ask. Then answer them without looking at the chapter."

Capture as:

```yaml
self_test:
  - q: "Why does X imply Y?"
    a: "Because Z..."
    correct: true
  - q: "What's the relationship between A and B?"
    a: "A causes B"
    correct: false  # actually B causes A
    note: "User reversed the causal direction"
```

The questions are queued for spaced re-engagement (Phase 4 of the next session).

---

## Coverage Rubrics (graded separately for textbase and situation model)

### Textbase recall rubric (`textbase_recall_coverage`, 0.0–1.0)

| Score | What the textbase recall demonstrates |
|---|---|
| **0.0** | almost no recall — user names the topic only, or less |
| **0.25** | remembers the topic + 1 surface fact; no structure |
| **0.5** | recalls some core concepts, but relations between them are weak or wrong |
| **0.75** | explains most core concepts and their relations, with partial examples |
| **1.0** | explains concepts, relations, and examples — full propositional summary of what the chapter said |

Round to the nearest 0.25; half-steps (0.6, 0.85) are allowed when the recall straddles bands. This is a textbase-only measure — being able to reproduce what the chapter said does not authorize `chapter_complete` on its own.

### Situation-model transfer rubric (per Step 2b transfer question)

| Score | What the answer demonstrates |
|---|---|
| **0** | could not apply, or applied in the wrong direction |
| **0.5** | partial mapping with one substantive error (right framework, wrong scope; or right direction, wrong mechanism) |
| **1** | applied correctly to the new scenario, with the chapter's framework as the explicit basis |

`situation_model_transfer_score` is the mean across the 1-2 transfer questions asked. The two failure modes to watch:

- **Verbatim recall masquerading as transfer**: the user repeats the chapter's example back instead of applying the framework to the new scenario. Score 0.
- **Surface-feature mapping**: the user picks up surface keywords from the new scenario and pattern-matches without applying the chapter's underlying mechanism. Score 0 to 0.5 depending on whether anything substantive transferred.

### Pass threshold by book type

`chapter_complete` is gated on situation-model transfer; textbase recall is an advisory cue (low textbase makes transfer measurement noisier, but a strong transfer answer with weak textbase still passes — durable usable learning lives in the situation model). Step B (diagnostic MCQ) does **not** substitute for either.

| Book type | `textbase_recall_coverage` advisory floor | `situation_model_transfer_score` gate | Additional |
|---|---|---|---|
| methodology | ≥ 0.5 | ≥ 0.7 | — |
| conceptual | ≥ 0.5 | ≥ 0.7 | — |
| argument-driven | ≥ 0.5 | ≥ 0.7 | steelman of opposing view logged (see `failure-modes.md` Failure 6) |
| problem-driven | ≥ 0.4 | ≥ 0.7 | one transfer-problem attempt logged in Phase 4 |
| reference | n/a | n/a | PDP not enforced |

*All threshold rows: evidence: operational-heuristic. The qualitative direction (textbase advisory, SM gating) is observational (Kintsch construction-integration model + dissociation literature); the specific 0.5 / 0.7 / 0.4 numbers are first-cut. User-side override is supported via per-chapter `actual_score_weights` (see Step 4a).*

If textbase is below the advisory floor but situation-model transfer passes, log `textbase_low_but_transfer_pass: true` and let `chapter_complete: true`; flag the unusual pattern in session_health notes for trend review (often it indicates the user already had the framework before reading and this chapter mostly re-keyed it).

If textbase passes but transfer fails, the chapter is not complete — this is exactly the dissociation the dual-rubric is designed to catch (the user remembers what the chapter said but cannot use it). Status stays `phase-3-pending`; schedule a 24-hour retry of Step 2b only (the textbase recall does not need to be redone).

For light-intensity sessions that skip Step 2b entirely (`situation_model_transfer_questions_count: 0`), `chapter_complete` cannot be true; mark `phase-3-textbase-only` and queue a Step 2b retry for the next session.

### What happens below threshold

- Status stays `phase-3-pending` (or moves back to `in-progress` if the user wants to re-read sections that surfaced as gaps).
- The recall and transfer attempts are still logged — the data points matter even when below threshold.
- Schedule a 24-hour retry; do not erase the original attempt. If only Step 2b (transfer) failed, the retry is Step 2b only.
- Do not soften the result to encourage the user — the rubric exists to break the illusion-of-understanding loop, not to validate it.

### What happens at situation_model_transfer_score = 1.0

- Promote 1-2 concepts to `evergreen/` extraction immediately while the signal is strong (see `references/citation-format.md` for the extraction format).
- Mark `concept_candidates` rows for the trigger evaluation in `~/study-journal/concepts/` (see SKILL.md "Concept-level tracking").

---

## Re-reading policy (default: single read + retrieval; re-read targeted only)

The skill's default after Phase 2 is **not** to re-read the chapter. Re-reading raises the user's *feeling* of understanding (calibration goes up — the chapter feels more familiar) without raising actual retention or transfer. The fluency illusion this creates is the dominant failure mode that calibration is designed to detect; defaulting to re-reading would defeat that.

The default is therefore: **one careful read + chunk-boundary retrievals** (see `references/generative-prompts.md` interim_recall) **+ Phase 3 calibrate**. Re-reading is allowed only on the conditions below.

### When re-reading is allowed

| Condition | Re-read what | Spacing |
|---|---|---|
| Phase 3 textbase coverage below floor | the specific sections that surfaced as gaps in `gap_calibration.factual_errors` and `concepts_covered` | next session (≥ 24 hr later); not same session |
| Phase 3 transfer score below gate but textbase passes | only the section(s) that contain the chapter's central mechanism / framework — not the full chapter; then attempt Step 2b again | next session |
| Argument-reading Step 5 (targeted re-reading on identified gap) | the specific passage where Step 4 dialogic surfaced an unaddressed counterclaim | within the same Phase 2 session, OK |
| Low-PK reader, chapter incoherent on first pass | the full chapter, **massed second pass within same session** (low-PK readers benefit from immediate cohesion-building; spaced re-read on a low-PK first pass leaves the model under-formed) | same session |
| Spaced re-read for retention reinforcement | the full chapter or sections | ≥ 1 week later |

### When re-reading is *not* allowed

- Same-session re-reading immediately after Phase 2 by a high-PK or normal-PK reader, when textbase coverage hasn't been measured yet. The user is reading for fluency, not learning. Push to Phase 3 first.
- Re-reading as a substitute for transfer attempt. If `situation_model_transfer_score` is below gate, re-reading the chapter does not move the SM score; only attempting transfer on a new scenario does. Schedule a Step 2b retry instead.
- Re-reading every chapter as routine "study habit". This is the default behavior the skill is engineered to displace.

If the user requests a re-read outside these conditions, surface once: "Re-reading raises familiarity but not retention. Recommended instead: [spaced retrieval / Step 2b retry on new scenario / move to next chapter and queue this one for spaced re-engagement]." If they still want to re-read, log it as `unguarded_reread: true` and let them; the trend is the data point.

## What "complete" means

A chapter is complete when:

1. Phase 1 done (PKA, prediction, goal_question, expectations, misconceptions captured)
2. Phase 2 done (chapter read; section-break prompts captured; ARQ/Polya invoked as applicable)
3. Phase 3 done — confidence + textbase recall (Step 2a) + situation-model transfer (Step 2b) + gap + Feynman + self-test — **as opening of a later session, or as same-session opt-in with `now - phase_2_ended_at >= 30 min`**
4. `situation_model_transfer_score` meets the book-type gate (see Pass threshold table above)
5. Phase 4 transfer attempt logged (success / partial / failure / domain mismatch) — for problem-driven, this is also gating; for other types, advisory

Anything less is `phase-X-pending`. Be explicit about state in `books.yml`:

```yaml
# canonical enum: references/state-schema.md
# `complete` is an aggregate alias allowed only inside chapter_status: blocks
arq:
  current_chapter: 4
  chapter_status:
    1: complete                  # aggregate: chapter end-to-end done (== phase-3-complete or beyond)
    2: complete
    3: complete
    4: phase-3-pending           # read + converted, calibrate not run yet
    5: phase-3-textbase-only     # textbase recall done, Step 2b skipped — chapter_complete is false
  last_session: 2026-04-28
```

If user says "Ch.4 끝났어" before Phase 3, do not update to complete. Status stays `phase-3-pending` until calibration runs.

## Multiple pending chapters

If more than one chapter is `phase-3-pending` (the user studied across several sessions without calibrating), surface the queue at session start: "Ch.4 (1 day pending), Ch.7 (4 days pending) are calibrate-ready. Run Ch.4 as warmup; defer Ch.7 to next session?" Default: **oldest first, one calibrate per opening**. Do not pile multiple full calibrates into a single warmup — that re-creates the form-fatigue failure mode the rest of the skill is engineered to avoid. If the older chapter is at the 5+ day stale boundary, downgrade it to a 3-question quiz (see § "The delay" stale-calibrate rule) and run a full Phase 3 on the next-oldest still in-window.

---

## Metrics that go on books.yml after each chapter

```yaml
arq:
  chapter_metrics:
    4:
      textbase_recall_coverage: 0.65          # Step 2a / 3
      situation_model_transfer_score: 0.75    # Step 2b mean (gate field)
      situation_model_transfer_questions_count: 2
      confidence_self_report: 80              # Step 1 diffuse confidence (legacy)
      score_prediction: 75                    # Step 1 behavioral forecast (gate input)
      actual_score: 70                        # composite: textbase*50 + SM*50
      score_prediction_gap: 5                 # Step 4a; |gap| ≤ 10 = well-calibrated
      abs_gap: 5
      calibration_diagnosis: well-calibrated
      confidence_accuracy_gap: 5              # confidence - SM*100 (Step 4b, legacy)
      categorization_re_test:
        phase_1_grouping: surface
        phase_3_grouping: principle
        shift: surface_to_principle
      hint_levels: [0, 1, 1, 2, 0]
      avg_hint_level: 0.8
      avg_answer_length: 35
      transfer_attempt: success
      session_count: 2
      chapter_complete: true                  # gated on situation_model_transfer_score AND abs_gap ≤ 20
      session_health:
        hint_abuse: false
        illusion: false                       # set true if abs_gap > 20
        surface: false
        struggle_skip: false
        form_fatigue: false
        echo: false
```

These are the inputs to weekly review and progress dashboard.

---

## Long-term progress signals

Across multiple chapters, watch:

| Trend | Direction | What it means |
|-------|-----------|---------------|
| `textbase_recall_coverage` | should rise | propositional learning signal — what the chapters *said* is sticking |
| `situation_model_transfer_score` | should rise | core learning signal — durable usable knowledge |
| Gap between textbase and SM | should narrow over book | model integration improving (early chapters often have textbase ≫ SM; mature reading converges) |
| **`abs_gap` (score_prediction)** | should narrow toward ≤10 | metacomprehension calibrating — user can predict own performance |
| Confidence-accuracy gap (vs SM, legacy) | should narrow toward 0 | diffuse-confidence calibration improving |
| Categorization shift rate (surface→principle) | should rise across chapters | schema formation accumulating |
| Avg hint level | should fall | dependency reducing |
| Avg answer length | should hold or rise | engagement quality |
| Transfer success rate | should rise | far transfer developing |
| Spaced retrieval (1w, 1m) | should hit > 60% | durable encoding |

Plot or list these in the weekly review (compose mode output).

If any trend reverses, surface and propose intervention:
- Coverage dropping → reduce session length, more frequent review
- Confidence gap widening → more Phase 3 emphasis; reduce AI explanation
- Hint level rising → enforce productive failure window
- Answer length dropping → push back on short answers; recalibrate effort

---

## Spaced re-engagement (Phase 4)

After a chapter is fully complete, schedule retrieval at:
- +1 day (next session)
- +1 week
- +1 month

*[evidence: observational — expanding spacing is rct-strong (Cepeda et al. 2008, "Spacing effects in learning"); the specific 1d/1w/1m schedule is operational, chosen for practical cadence rather than RCT-derived optimal intervals.]*

Implementation: `books.yml` carries a queue:

```yaml
review_queue:
  - { book: arq, chapter: 4, due: 2026-04-29 }   # +1 day
  - { book: arq, chapter: 4, due: 2026-05-05 }   # +1 week
  - { book: arq, chapter: 4, due: 2026-05-28 }   # +1 month
```

When skill starts a session, check queue. If anything due, run prior_chapter_recall before the new chapter:

> "Today's session has a Ch.4 retrieval due. Take 5 min: name the 3 most important things from Ch.4 without looking. Then we start Ch.5."

Capture results in books.yml:

```yaml
chapter_metrics:
  4:
    spaced_retrievals:
      - { date: 2026-04-29, accuracy: 0.7 }
      - { date: 2026-05-05, accuracy: 0.55 }
      # +1 month pending
```

If a spaced retrieval drops below 50%, re-add chapter to active review (not just spaced). Possibly run a mini calibrate session on it. *[evidence: operational-heuristic — the 50% cutoff is a first-cut; no RCT validates this specific re-add threshold.]*

---

## Edge cases

- **User can't recall anything in Phase 3**: don't soften. Capture `textbase_recall_coverage = 0` and skip Step 2b (transfer with empty textbase is noise). Surface signal; recommend re-reading the parts that surfaced as gaps, not from start. Schedule a recall retry in 24 hr.
- **User passes textbase but fails situation-model transfer**: the dual-rubric is doing exactly what it's supposed to do. Status stays `phase-3-pending`. Schedule a Step 2b-only retry in 24 hr; do not redo textbase. The user's goal between now and then is to attempt the transfer themselves on a new example of their choosing.
- **User aces situation-model transfer (1.0 across questions)**: still capture; this is good but rare. Promote 1-2 concepts to evergreen extraction immediately while signal is strong.
- **Phase 2 ran long, no time for Phase 3 today**: this is the default flow now, not an edge case. Set `status: phase-3-pending` and `phase_2_ended_at: <now>`. End the session. Calibrate runs at next session opening.
- **User wants to redo Phase 3 after seeing the gap**: log the redo (`phase_3_attempts: 2`). Coverage on retry is contaminated; don't replace original; append.
- **User insists on same-session calibrate**: check `now - phase_2_ended_at`. If less than 30 min, refuse with the remaining time plus a one-line reason (working-memory contamination). If at or above 30 min, proceed and log `calibrate_same_session: true`. Do not silently allow this path — the log is what makes the trend visible.
- **Calibrate window has aged out (5+ days)**: downgrade to 3-question retrieval quiz; do not run full Phase 3 by default. If the user explicitly wants full Phase 3 anyway, run it but flag the result in the chapter note: "coverage at this delay is dominated by long-term decay, not Phase 2 encoding."

---

## Why this matters

Without calibration, you're optimizing on the wrong signal. The user feels they understand; the LLM tells them they understand; the chapter note shows completed forms. Months later, the material is gone.

With calibration measured along *both* dimensions, the only signals that survive are the ones that matter: can you reproduce what the chapter said (textbase) and can you use it on something new (situation model). The two are dissociable; measuring only one masks the other. The *feeling* of understanding is well-known to be miscalibrated; the explicit two-rubric scoring is what breaks the illusion-of-explanatory-depth loop that AI mediation amplifies.

This is the single highest-leverage move the skill makes. Everything else can be skipped without breaking learning; Phase 3 cannot.

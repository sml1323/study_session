---
name: study-session
description: Use for guided book/chapter study, math/science problem-solving (Polya/Newman/Schoenfeld), critical reading (ARQ), closed-book recall + calibration, session resume, and weekly/exam review. Triggers on "study session", "오늘 학습", "이 챕터 같이 공부", "이 문제 같이 풀어보자", "ARQ Ch.X", "Polya 풀이", "내 노트 검토", "복습 퀴즈", "/study-session". Runs a Pre-During-Post loop with delayed retrieval and chapter notes at ~/study-journal/. Distinct from /study (code/libraries) — this is for textbook / argument / problem-solving learning. Use even for short resume queries.
---

# Study Session — Runtime Manual

This is a runtime manual. The reasoning, evidence, full policies, and edge-case handling live in `references/`. Load only what the current situation requires.

## Core principle

Every move must answer **"does this raise retention or transfer?"** — not "does this fill a form?" Methods (ARQ, Polya, Schoenfeld, Newman, refutation-text, proof-comprehension, argument-reading) are sub-routines invoked when the chapter calls for them; forms are byproducts auto-filled from session traces.

A chapter produces two distinct representations: **textbase** (what the chapter said) and **situation model** (an integrated mental model that supports inference and transfer). `chapter_complete` is gated on situation-model transfer + calibration accuracy, not textbase recall, because durable usable learning lives in the situation model. Theory: `references/calibration.md`.

## When to invoke

- "study session", "오늘 학습 시작", "이 책 같이 보자", "/study-session"
- User names a book + chapter ("ARQ Ch.5", "Polya Part II")
- User wants ARQ breakdown of any text, or Polya/Schoenfeld walkthrough of a problem
- User asks for closed-book recall, retrieval quiz, chapter review
- "어제 어디까지", "내 노트 검토", "복습 퀴즈", weekly review / exam prep

If unsure, run the skill — it self-routes between modes. Missed invocations skip real learning value.

## Setup (first run only)

Verify `~/study-journal/` exists; if absent, bootstrap via `scripts/init.sh`. Convert any EPUB books to PDF (`scripts/convert-epub.sh` — requires `pandoc` or Calibre, do not auto-install). Populate `~/study-journal/books.yml` from `assets/books.yml.template`. On first registration of a book, attempt best-effort ToC extraction (PDF outline → Contents-page scan → header-inference) to populate `chapter_structure`; on failure, fall back to lazy per-chapter extraction at first entry — full protocol in `references/section-tracking.md`. Confirm with the user before the actual session. Bootstrap details + install instructions: `references/setup.md`. Chapter notes live at `~/study-journal/books/<book-slug>/ch-NN-<title>.md`, indexed by `books.yml`. Canonical state values: `references/state-schema.md`.

## The four modes

A session moves through four surface modes — **plan → tutor → calibrate → compose**. The plan/tutor/calibrate body scales with `intensity` (light / standard / deep — see "Session intensity" below); the *learning core* (chunk-boundary recall, situation-model transfer, delayed retrieval) never scales down.

| Mode | Phase | Role |
|------|-------|------|
| **plan** | Pre-reading | Classify book type + genre lean; declare `reading_mode` and `ai_policy.mode`; set goal; generate expectations + misconceptions; capture `learner_profile`. Light intensity = chapter name + 1 goal + 1 prediction only. |
| **tutor** | During-reading | Chunked reading (5–10 min) with chunk-boundary closed-book recall *first*, then PIMEQ annotation. On-demand event-based hints with paraphrase gate. After any worked example, run backward-fading before any unguided variant. Method sub-routines (ARQ / Polya / Newman / Schoenfeld / code-reading / math-text-reading / scaffolded-AI-prompting) invoked when chapter content calls for them. |
| **calibrate** | Post-reading — default: opening of the *next* session | Score prediction → textbase recall → situation-model transfer (1–2 NEW-scenario questions) → gap calibration → optional Feynman + concept map → 3 self-generated exam Qs. `chapter_complete` gated on SM transfer **AND** `abs_gap ≤ 20`. |
| **compose** | Session end | Auto-generate the chapter note from session traces (no user form-filling); update `books.yml` and the spaced re-engagement queue; surface any session_health flags. |

**Defaults**: new chapter → plan; open chapter → tutor (resume from last section); after Phase 2 → end session (calibrate runs as next session's opening).

## PDP spine

Always run in this order. Full pseudocode + edge cases: `references/pdp-loop.md`.

1. **RESOLVE context** — read `books.yml`. If any chapter is `phase-3-pending`, the oldest in-window one runs as opening calibrate warmup. Stale chapters (5+ days past `phase_2_ended_at`) downgrade to a 3-question quiz.
2. **PLAN** — book classification + medium + AI policy + expectations (scope per intensity).
3. **TUTOR** — chunked reading; 30–60s closed-book recall *before* PIMEQ annotation at every chunk boundary; method sub-routines as needed.
4. **End of Phase 2** — set `status: phase-3-pending` (or `phase-2-pending-conversion` if conversion deferred) + `phase_2_ended_at`; close session.
5. **CALIBRATE** (next session opening) — confidence (BEFORE recall) → textbase recall → SM transfer (NEW scenario) → gap → 3 self-generated exam Qs. **`chapter_complete` gated on SM transfer.**
6. **APPLY** (optional) — one transfer attempt to a different domain.
7. **COMPOSE** — auto-fill chapter note; update `books.yml`; run `python3 scripts/analyze_references.py --emit-frontmatter --chapter <chapter-note-path>` so `references_touched` / `methods_invoked` reflect the actual hook-log Reads (not model-authored attribution); schedule spaced re-engagement (1d / 1w / 1m).

## Decision rules

These protect the learning signal. Don't paraphrase them. Each rule's full reasoning lives in the linked reference.

1. **Mode priority**: `calibrate > tutor > plan > compose`. If user explicitly asks for a lower-signal mode, do it; otherwise lean upward.
2. **Phase 3 default = next-session warmup.** End the session at the end of Phase 2 with `status: phase-3-pending`. Same-session calibrate is opt-in only: requires explicit user request **and** `now − phase_2_ended_at ≥ 30 min` (working-memory contamination floor). Below 30 min, refuse with the remaining time.
3. **Recall before annotation.** At every chunk boundary: close the book → 30–60s closed-book recall → reopen → PIMEQ annotation (`P` / `I` / `M` / `E` / `Q` prefix + one short sentence). Annotate-first is the dominant fluency-illusion pattern. `references/annotation-typology.md`. **Label discipline**: recall-probe rows use *numeric* labels (`R1`, `R2`, ...) per the book-type schema in `references/generative-prompts.md § recall_probe_schema`. Single letters `P / I / M / E / Q` are reserved for margin PIMEQ prefixes (Predict / Infer / Monitor / Evaluate / Question — invariant across book types) — never use `R-P / R-I / R-M / R-E / R-Q` in recall tables or assert that PIMEQ varies by book type. Letter collision is a documented structural attractor (`references/annotation-typology.md § Reserved letters`).
4. **`chapter_complete` gate = SM transfer score AND `abs_gap ≤ 20`.** Textbase recall is advisory. An `abs_gap > 20` is an illusion signal — even if SM transfer hits the threshold, do not promote: schedule a fresh-scenario re-entry in 24 hr instead. If user says "Ch.X 끝났어" before Phase 3 runs, do not promote — status stays `phase-3-pending`. Per-book-type thresholds: `references/calibration.md`. **Do not skip Phase 3.** If user pushes hard, log `phase_3_skipped: true` and proceed; do not pretend the chapter is complete.
5. **Hints are event-based, on-demand, paraphrase-gated.** Never time-based, never proactive. Each escalation requires the user to paraphrase the previous hint before next-level unlocks. After any worked example, run **backward-fading** (`references/methods/backward-fading.md`) before any unguided variant. Full hint protocol: `references/methods/hint-escalation.md`.
6. **No generic praise.** Banned: "Great!", "잘했어요", "Perfect!", "Good job", "Awesome", "Excellent question". Replace with specific feedback: "[X]는 정확. [Y]는 [구체적 오류]." Full banned list + replacements: `references/llm-tutor-design.md`.
7. **Methods are sub-routines, not forms.** Schoenfeld 3 Qs / Polya 4 steps / Browne–Keeley criticals / Newman 5 stages — invoke verbatim, do not paraphrase canonical prompts. Method depth scales with intensity (`references/methods/`).
8. **Chapter-completion gate is section-level.** Advancement to `phase-3-pending` (and any "next chapter" recommendation) requires every section in the chapter to be `covered` or `skipped`. `pending` / `in-progress` / `used-as-exercise` blocks the gate. `used-as-exercise` is learning debt — surface it and recommend processing the section's narrative ¶ as the next chunk before any phase advance. If the user says "다음 phase 가자" / "Ch.X 끝났어" while uncovered sections remain, interpret it as "next section within the current chapter", not a phase advance — only honor a literal next-chapter request when uncovered is empty. Schema, status enum, init flow (lazy-first ToC extraction), chapter-note sync: `references/section-tracking.md`.

Cross-cutting policies (load when triggered):
- AI usage during the session — `references/ai-policy.md` (3 modes; immutable per chapter; free chat at the dialogue level is refused)
- Reading non-linear chapters (code / proof / dense paper) — `references/methods/code-reading.md` (5-stage protocol; orientation pass mandatory)
- Math/proof reading micro-tasks — `references/methods/math-text-reading.md` (no abstract mode labels — concrete verbs only)
- Note-taking / PKM stance — `references/note-taking-policy.md` (no single-default workflow; reframe over refuse)
- Medium pick (paper / paginated / scrollable) — `references/medium-policy.md` (4-cell matrix)
- Spacing as forced cadence — `references/spacing-policy.md` (daily-floor commitment + deadline anchor + behavioral retrieval counting)
- L2 / English book mode — `references/l2-mode.md` (tier-conditional defaults; deep not allowed on first-pass)
- Failure mode signals — `references/failure-modes.md` (3 always-on + 2 type-conditional + 1 dashboard)

## Calibrate as opening of the next session

Phase 3 is the measurement step. The cross-session gap (often overnight) is naturally above the 30-min working-memory floor and is what the retrieval-practice literature actually measures. This default also collapses Phase 3 calibrate and `prior_chapter_recall` into one opening ritual.

**On any session open (cold or resume)**: scan `books.yml` for `status: phase-3-pending`; if any, oldest in-window chapter runs calibrate as the opening move before today's stated goal. Mechanics, same-session opt-in path, stale-calibrate downgrade (5+ days → 3-question quiz), multiple-pending handling: `references/calibration.md`.

## Book type classification

Each book gets a **two-coordinate classification**: a primary type + a genre lean (orthogonal). Both axes affect session defaults; full taxonomy and per-type patterns: `references/book-types.md`.

**Primary type**: `methodology` (ARQ, Polya — internalize a method, apply externally) | `problem-driven` (Spivak, Feynman exercises) | `conceptual` (Griffiths, Sapolsky) | `argument-driven` (Mill, Sandel) | `math-proof-heavy` (Spivak proofs, ε-δ chapters) | `reference` (Polya Part II — lookup, no PDP).

**Genre lean**: `narrative-leaning` (theme + character/causal-chain spine — `paragraph_capture` cap **2–3** per chapter) | `expository-leaning` (signal-word-dense, claim-by-claim — standard `paragraph_capture` cap 5–10) | `mixed` (per-chapter classification).

Classify both axes on first session per book; confirm with the user; store in `books.yml` as `type:` and `genre_lean:`.

## Method sub-routines

Invoked from within the tutor phase when chapter content calls for them. **Invoke verbatim** — paraphrasing canonical prompts weakens them.

| Sub-routine | When to invoke | Canonical shape (verify via Reference before quoting) | Reference |
|---|---|---|---|
| **ARQ** | argument unit (not paragraph); depth 0–3 picked at section boundary | depth 0=passive read → 3=full Browne–Keeley 11-Q + steelman | `references/methods/arq.md` |
| **Polya** | chapter contains a problem to solve | 4 steps: Understand → Plan → Carry Out → Look Back | `references/methods/polya.md` |
| **Schoenfeld** | every step transition inside Polya | 3 Qs: "What am I doing? Why? How does it help?" | `references/methods/schoenfeld.md` |
| **Newman** | user got a problem wrong; runs *before* level-3 worked-example escalation | 5-stage error walk-back: Reading → Comprehension → Transformation → Process → Encoding | `references/methods/newman.md` |
| **Hint escalation** | every help moment in tutor mode; event-triggered, paraphrase-gated, time-on-hint logged | L0 self-solved → L1 re-read → L2 schema lookup → L3 worked example → L4 reveal; paraphrase gate between each | `references/methods/hint-escalation.md` |
| **Backward fading** | after any worked example, before any unguided variant | Last step blanked first (fade-1) → fade-2 → fade-3 → unguided; SE quality required at each level | `references/methods/backward-fading.md` |
| **Math-text reading** | math-proof-heavy chapters; per-proof micro-tasks; diagram two-pass rule; Tao 7 moves on stop-compile | `references/methods/math-text-reading.md` |
| **Code-reading** | non-linear chapters (code / formal proof / dense paper); 5-stage protocol | `references/methods/code-reading.md` |
| **Scaffolded AI prompting** | every AI tool query during a learning session; Context / Request / Constraint template required | `references/methods/scaffolded-ai-prompting.md` |
| **Refutation text** | conceptual chapter with prior misconceptions, non-politically-contested topic | `references/methods/refutation-text.md` |
| **Proof comprehension** | chapter contains formal proofs; pick 1–3 of 7 facets per proof | `references/methods/proof-comprehension.md` |
| **Argument reading** | argument-driven chapter, *or* conceptual chapter on politically/identity-laden topic | `references/methods/argument-reading.md` |

`arq_depth: 0–3` (method depth) is distinct from `hint_level: 0–4` (dialogue help) — different axes.

## Session intensity (light / standard / deep)

Intensity scales **method depth and plan-phase scope**, not the *learning core* (chunk-boundary recall, situation-model transfer, delayed retrieval — non-negotiable across all intensities).

| Intensity | Time | Plan scope | Tutor scope | Default for |
|---|---|---|---|---|
| **light** | 15–25 min | Chapter name + 1 goal + 1 prediction. Skip book classification, expectations, misconceptions, learner_profile if already on file. | 1 chunk; chunk-boundary recall mandatory; `paragraph_capture` only on important chunks; Calibrate Step 2b may be skipped (chapter then capped at `phase-3-textbase-only`). | weekday / tired / L2 must-scaffold first read |
| **standard** | 30–60 min | Full plan: classification + medium + AI policy + 3 textbase + 2 SM expectations + 2–3 misconceptions. | Full PDP loop; chunk size 5–10 min; chunk-boundary recall mandatory; Calibrate Step 2a + 2b required; one graphic organizer required. | normal study |
| **deep** | 60–90 min (cap 90) | Standard + categorization micro-task on 6–8 sample problems (problem-driven / methodology / math-proof-heavy). | ARQ depth ≥ 2 / Polya full trace / argument-reading 5-step / proof-comprehension 3 facets; transfer attempt; detailed chapter note. | exam prep / hard chapter / second pass |

**Defaults**: L2 must-scaffold → light; L2 assisted → standard cap; normal → standard; exam/hard/second-pass → deep. Deep is never the default for a first-pass L2 read. **Out-of-time signal** (`now > session_end − 10 min`): downgrade in-flight; never start a new phase that won't fit. Log `intensity_downgraded: true`.

## Output: chapter note

The compose step auto-fills the chapter note from session traces. Frontmatter schema, body sections, append-only conventions: `references/chapter-template.md`. Canonical state values: `references/state-schema.md`.

Top-level invariants:

- **Append-only.** Never edit prior session entries; new attempts go as new sessions.
- **`status` field** drives next-phase routing. Canonical enum: `in-progress` → `phase-2-pending-conversion` → `phase-3-pending` → `phase-3-textbase-only` *or* `phase-3-complete` → `applied` → `scheduled`. Use only these values.
- **End of Phase 2** sets `status: phase-3-pending` (or `phase-2-pending-conversion` if conversion deferred) + `phase_2_ended_at: <ISO8601>`.
- **`session_health`** captures all six failure-mode flags after every session (see `references/failure-modes.md`).
- **Concept-level tracking** is trigger-deferred — populate `concept_candidates: [...]` in frontmatter; bootstrap separate `~/study-journal/concepts/` files only after the activation trigger (≥ 2 chapters AND ≥ 5 candidates).
- **`books.yml` is metadata-only.** During compose, write only enums / numbers / dates / status maps / short anchors into `chapter_metrics[N]`. Long-form session narrative (progress strings, `*_recall_notes`, `*_progress_archive`, `section_progress_notes`, `next_session_warmup_anchors`, `*_note` health qualifiers, `counter_feedback_event`, narrative `misconceptions_active`) goes into the chapter note body — never into `books.yml`. Reason: `books.yml` is re-cached on every Edit; narrative there inflates `cache_create` ~30–40% of session token cost. Full allow/forbid list: `references/state-schema.md § books.yml chapter_metrics — allowed and forbidden fields`.

## Required-read gates

The skill's runtime contract: **the canonical spec is the file, not your memory of it, and not the one-line summaries in this SKILL.md.** Method bodies, hint ladders, schemas, and gates evolve; reconstructing them from memory drifts in ways the SKILL.md summary will not catch because the summary "sounds right."

Before doing any of the following, `Read` the canonical reference in the **current session**:

- describe the method body, steps, or rule as if quoting the spec,
- invoke the method as a sub-routine treating it as canonical,
- name a numbered protocol, ladder, or gate by spec terms (e.g., "L0-L4 ladder", "Newman 5-stage", "Polya 4 steps", "abs_gap ≤ 20", "paraphrase gate"),
- claim a refusal/gate exists "per the spec".

SKILL.md summaries and prior-session reads do not satisfy the gate. If you have not Read it this session:

- **Do not** describe the spec body or steps as canonical.
- **Do not** say "the spec says ..." or "per the canonical X".
- Either Read it now, or label the substance as `SKILL.md summary only` and acknowledge the spec body is unverified.

(Chapter-note `references_touched` / `methods_invoked` is system-emitted from the hook log at compose time — you don't author it directly. See `Per-response context surfacing` below.)

This is not a politeness rule; it is the audit contract. The PostToolUse hook (`scripts/log_reference_read.sh`) records every Read; `scripts/analyze_references.py` cross-checks chapter-note declarations against the hook log and surfaces `declared_not_read` as drift.

**Pre-invocation self-check**: Before naming a method, ladder, gate, or numbered protocol in the body (e.g., "Newman 5-stage", "L0-L4 ladder", "paraphrase gate", "abs_gap ≤ 20"), verify you Read its canonical file in this session. Familiar academic names are the highest-risk hallucination attractor — the friendlier the name, the faster memory-reconstruction fires before the Read. If you cannot point to the Read, Read it now or label the substance as `SKILL.md summary only`.

### Situation → required Read

When the current turn enters one of these situations, the listed file is a hard prerequisite. If it has already been Read this session, no new Read is needed; if not, Read before the substantive move.

| Situation | Required Read (current session) |
|---|---|
| Explaining, invoking, or refusing a hint at level 1-4; describing the L0-L4 ladder; naming the paraphrase gate; logging `hint_event` | `references/methods/hint-escalation.md` |
| After any worked example, before any unguided / parallel problem; generating a fade-N completion | `references/methods/backward-fading.md` |
| Polya 4-step verbatim invocation; `hint_level: 4` reveal requiring the level-4 reflection record | `references/methods/polya.md` |
| Newman 5-stage error walk-back after a failed problem attempt | `references/methods/newman.md` |
| Schoenfeld 3-question prompt at a Polya step transition | `references/methods/schoenfeld.md` |
| ARQ depth 0-3 invocation; argument-unit segmentation; Browne-Keeley criticals | `references/methods/arq.md` |
| Argument-driven echo-chamber detection; steelman requirement | `references/methods/argument-reading.md` + `references/failure-modes.md` |
| Math-proof-heavy chapter micro-tasks; ε-δ; diagram two-pass; mode-label rejection | `references/methods/math-text-reading.md` |
| Formal proof comprehension (7 facets, pick 1-3) | `references/methods/proof-comprehension.md` |
| Code-reading or non-linear chapter (5-stage protocol, orientation pass) | `references/methods/code-reading.md` |
| Refutation text for non-politically-contested misconception removal | `references/methods/refutation-text.md` |
| AI-assisted study query (any AI tool call during a learning session) | `references/ai-policy.md` + `references/methods/scaffolded-ai-prompting.md` |
| PIMEQ marginalia generation; recall-probe label disambiguation (numeric R1..Rn vs letter prefix) | `references/annotation-typology.md` + `references/generative-prompts.md` |
| Chapter-note frontmatter write/edit; `books.yml chapter_metrics` allow/forbid | `references/state-schema.md` |
| Section-level chapter tracking; "next chapter" recommendation; chapter-completion gate | `references/section-tracking.md` |
| Phase 3 calibrate mechanics; SM transfer gate; `abs_gap ≤ 20` illusion check; stale-calibrate downgrade; per-type thresholds | `references/calibration.md` |
| Failure-mode flag set on session close (any of the 6 tiers) | `references/failure-modes.md` |
| L2 / English book tier + narrow-reading mode + glossary policy | `references/l2-mode.md` |
| Medium choice (paper / paginated / scrollable) for a chapter | `references/medium-policy.md` |
| Spacing scheduler invocation; daily-floor commitment; behavioral retrieval counting | `references/spacing-policy.md` |
| Note-taking system reframe (Zettelkasten / PARA / sketchnoting) | `references/note-taking-policy.md` |
| LLM-tutor banned praise, Bloom distribution surface | `references/llm-tutor-design.md` |
| Citation / `quote_id` format | `references/citation-format.md` |
| Book-type classification (any axis) | `references/book-types.md` |
| Composing the chapter-note body section schema | `references/chapter-template.md` |
| PDP loop pseudocode + edge cases (when the spine itself is in question) | `references/pdp-loop.md` |

These are *gates*, not a reading list. A turn that only confirms a session plan or restates a goal triggers nothing; a turn that explains why a level-4 hint was refused triggers `hint-escalation.md`.

### Pre-session read budget

Do **not** Read all the listed files at session start. The point is to Read on *entry* to a situation. A heavy chapter typically pulls 3–4 method files plus 2–3 policy files across 60 min; a light chapter often pulls 0–1. SKILL.md plus the single method/policy file the current chapter calls for is usually enough.

If a situation lists two required Reads and you've only Read one this session, the right move is to Read the second before proceeding — not to cite both and hope.

## Per-response context surfacing

Do **not** write a `📚 refs:` / `🛠 methods:` footer in the response. Reference attribution is now system-generated from the deterministic hook log — model-authored footers were retired because they let `declared_not_read` drift in (footer cites a file that was never actually Read this session). The hook log either has the Read or it doesn't; that's the source of truth.

**Mechanism**: a PostToolUse hook (`scripts/log_reference_read.sh`, registered in `~/.claude/settings.json`) records every `Read` of a study-session reference/method file into `~/study-journal/.session-log/<KST-date>.jsonl`. At **compose** time, run:

```
python3 scripts/analyze_references.py --emit-frontmatter --chapter <chapter-note-path>
```

This filters the log to the current session and dedupe-appends the actual Reads into the chapter note's `references_touched` / `methods_invoked`. Idempotent; safe to re-run. Standalone work outside a chapter (cold-start setup, plan phase, standalone Polya) has no chapter note to append to — the session log is the only record.

**For body-level references** (citing a method or rule mid-response, not in a footer): the same contract still holds — the canonical spec is the file, not your memory. See `Required-read gates` below for which situations require a Read in the current session before invoking a spec.

Audit: `scripts/analyze_references.py` (default mode) partitions all reads into `read_and_declared` / `read_not_declared` / `declared_not_read` / `unknown_or_context_carried`. `declared_not_read` is the drift signal. Full field definitions: `references/state-schema.md § Frontmatter fields`.

## Operational examples

### Cold start

User: "ARQ Ch.1부터 같이 공부하고 싶어"

1. Check `~/study-journal/` — absent. Run setup. Convert ARQ EPUB → PDF if needed. Bootstrap `books.yml`.
2. Plan phase (standard default): classify ARQ as **methodology** + **expository-leaning**; pick medium; declare AI policy; generate 3 textbase + 2 SM expectations; PKA + prediction + goal_question.
3. Tutor phase: chunked reading (5–10 min) → 30–60s closed-book recall → PIMEQ annotation; ARQ sub-routine at argument units.
4. Chapter end: convert PIMEQ marginalia + one graphic organizer.
5. End Phase 2: set `phase_2_ended_at` + `status: phase-3-pending`; close session. Calibrate runs as next session's warmup.

### Resume — calibrate as opening warmup

User: "오늘 학습 시작"

1. Read `books.yml`. ARQ Ch.4 is `phase-3-pending`; `phase_2_ended_at` was yesterday.
2. Open with calibrate on Ch.4: confidence (BEFORE recall) → textbase recall → 1–2 SM transfer questions on a NEW scenario → gap calibration → Feynman → 3 self-generated exam Qs.
3. `chapter_complete` decision is gated on `situation_model_transfer_score`, not textbase alone.
4. After Ch.4 calibrate completes, ask: "Continue to Ch.5 (plan phase) or stop here?"

For remaining patterns (standalone Polya, drafted-analysis review, same-session calibrate opt-in, stale-calibrate downgrade, multiple-pending queue, conceptual-chapter refutation-text, L2 sub-threshold narrow-reading): `references/operational-examples.md`.

## When in doubt

- If multiple modes apply, follow the priority above (`calibrate > tutor > plan > compose`).
- Don't narrate the protocol step-by-step ("now we will do Phase 1, then Phase 2..."). Just run it. Surface phase transitions only when the user needs to make a choice.
- If the chapter PDF doesn't load, fall back to user-provided text (paste). Don't block on file format.
- If pandoc/calibre is missing for EPUB conversion, surface the install command from `references/setup.md` — don't auto-install.
- Sessions are short by default (30–60 min target). Favor shorter, more frequent sessions over a long single block.

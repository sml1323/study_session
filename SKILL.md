---
name: study-session
argument-hint: "[--review --book <slug> --chapter <N> | --review --due | --review --scope chapter | --llm-translate | --help] {free-form intent}"
description: Use for guided book/chapter study, math/science problem-solving (Polya/Newman/Schoenfeld), critical reading (ARQ), closed-book recall + calibration, session resume, and weekly/exam review. Triggers on "study session", "오늘 학습", "이 챕터 같이 공부", "이 문제 같이 풀어보자", "ARQ Ch.X", "Polya 풀이", "내 노트 검토", "복습 퀴즈", "/study-session". Runs a Pre-During-Post loop with delayed retrieval and chapter notes at ~/study-journal/. Distinct from /study (code/libraries) — this is for textbook / argument / problem-solving learning. Use even for short resume queries.
---

# Study Session — Runtime Manual

This is a runtime manual. The reasoning, evidence, full policies, and edge-case handling live in `references/`. Load only what the current situation requires.

**Path resolution**: this skill's root is `${CLAUDE_SKILL_DIR}` (Claude Code renders this to an absolute path at load). Resolve every `references/...` and `scripts/...` path in this file against that root — never against the current working directory. If the path above appears as an unexpanded CLAUDE_SKILL_DIR placeholder (non-Claude-Code harness), resolve against the directory containing this SKILL.md.

## Argument Parsing

```
/study-session                                         # resume default: scan books.yml, route on the oldest pending state
/study-session {free-form}                             # natural-language entry — book/chapter/problem named in prose
/study-session --review --book <slug> --chapter <N>    # review-route this specific chapter (status-driven branch)
/study-session --review --due                          # process the oldest due item on the spaced-retrieval queue
/study-session --review --scope chapter                # restrict review-routing to chapter scope (skip cross-chapter interleave)
/study-session --llm-translate                         # activate translation-read mode on the current book (book-level persistent; mutex with L2 mode)
/study-session --help                                  # show this usage block, do not enter a mode
```

- **Bare invocation** (`/study-session` alone): scan `~/study-journal/books.yml`; if any `phase-3-pending` chapter is older than 5 days, downgrade to a 3-question quiz; otherwise run calibrate as the opening warmup on the oldest in-window pending chapter; if nothing pending, ask the user what to do.
- **Free-form intent**: see `When to invoke` below for the trigger lexicon.
- **`--review` flag family**: full branch logic (per chapter status) lives in `references/review-routing.md`. Natural-language equivalents ("ARQ Ch.4 복습하자", "어제 거 다시 보자", "복습 퀴즈") route through the same logic.
- **`--llm-translate` flag**: book-level persistent translation-read mode (LLM or official translation). First invocation per book asks `translation_mode.source` once in plan phase and persists to `books.yml`; subsequent sessions inherit. Mutex with `l2_mode` (forces `l2_mode: off`). Full protocol: `references/translation-mode.md`.
- **`--help`**: print this `## Argument Parsing` block, do not enter a mode.

If just `/study-session` is invoked and `books.yml` is empty / missing, run setup (`references/setup.md`) and ask what book to study.

## Session-open snapshot (injected at load)

Claude Code executes the line below at skill load and replaces it with its output — current `phase-3-pending` candidates from `books.yml`, with line numbers, before any Read. The snapshot is a routing *hint* and may be truncated (output capped at 40 lines): RESOLVE must still confirm against `books.yml` before selecting the opening calibrate chapter. If the block is empty, there are no pending chapters **or** `books.yml` is missing — distinguish by opening `books.yml`. If the block instead shows an unexecuted literal line (exclamation mark followed by a backtick-quoted grep command — non-Claude-Code harness), ignore it and scan `books.yml` manually.

!`grep -n -B3 -A5 'phase-3-pending' ~/study-journal/books.yml 2>/dev/null | head -40`

> **Runtime assumption — Claude Code PostToolUse hook.** The read-audit contract (`scripts/log_reference_read.sh` + `scripts/analyze_references.py`) depends on Claude Code's PostToolUse hook logging every reference `Read`. On harnesses without an equivalent hook (e.g. Codex CLI), Required-read gates still apply, but the audit signal degrades to model self-report and compose-mode `references_touched` / `methods_invoked` cannot be system-emitted.

## Core principle

Every move must answer **"does this raise retention or transfer?"** — not "does this fill a form?" Methods (ARQ, Polya, Schoenfeld, Newman, refutation-text, proof-comprehension, argument-reading) are sub-routines invoked when the chapter calls for them; forms are byproducts auto-filled from session traces.

A chapter produces two distinct representations: **textbase** (what the chapter said) and **situation model** (an integrated mental model that supports inference and transfer). `chapter_complete` is gated on situation-model transfer + calibration accuracy, not textbase recall, because durable usable learning lives in the situation model. Theory: `references/calibration.md`.

## When to invoke

- "study session", "오늘 학습 시작", "이 책 같이 보자", "/study-session"
- User names a book + chapter ("ARQ Ch.5", "Polya Part II")
- User wants ARQ breakdown of any text, or Polya/Schoenfeld walkthrough of a problem
- User asks for closed-book recall, retrieval quiz, chapter review
- "어제 어디까지", "내 노트 검토", "복습 퀴즈", weekly review / exam prep
- **Review-routing surfaces**: "ARQ Ch.4 복습하자", "어제 거 다시 보자", "복습 퀴즈", or the explicit `--review` flags — routes by chapter status per `references/review-routing.md`.

If unsure, run the skill — it self-routes between modes. Missed invocations skip real learning value.

## Setup (first run only)

Verify `~/study-journal/` exists; if absent, bootstrap via `scripts/init.sh`. Convert any EPUB books to PDF (`scripts/convert-epub.sh` — requires `pandoc` or Calibre, do not auto-install). Populate `~/study-journal/books.yml` from `assets/books.yml.template`. On first registration of a book, attempt best-effort ToC extraction to populate `chapter_structure`; on failure, fall back to lazy per-chapter extraction — full protocol: `references/section-tracking.md`. Confirm with the user before the actual session. Full bootstrap + reference-audit hook install (`scripts/install-hook.sh`, setup.md Step 8 — skip it and the read-audit pipeline silently no-ops): Read `references/setup.md`. Chapter notes live at `~/study-journal/books/<book-slug>/ch-NN-<title>.md`, indexed by `books.yml`. Canonical state values: `references/state-schema.md`.

## The four modes

A session moves through four surface modes — **plan → tutor → calibrate → compose**. The plan/tutor/calibrate body scales with `intensity` (light / standard / deep — see "Session intensity" below); the *learning core* (chunk-boundary recall, situation-model transfer, delayed retrieval) never scales down.

Each mode below names *when it runs* and *what it owns*, but not *how its body unfolds* — mode bodies are intentionally absent from SKILL.md, so the only way to drive a mode correctly is to Read its reference in the current session (see Required-read gates).

| Mode | When it runs | What it owns |
|------|--------------|--------------|
| **plan** | Pre-reading | Book classification + medium + AI policy + expectations + learner profile |
| **tutor** | During-reading | Chunked reading, chunk-boundary recall, active margin notes, on-demand hints, method sub-routines |
| **calibrate** | Post-reading — default: opening of the *next* session | Confidence + score prediction (BEFORE recall), recall, situation-model transfer on NEW scenario, gap, exam Qs; `chapter_complete` gate |
| **compose** | Session end | Auto-generate chapter note + update `books.yml` + run system-emit frontmatter + schedule spaced re-engagement |

Required Read per situation: see Required-read gates > Situation → required Read.

**Defaults**: new chapter → plan; open chapter → tutor (resume from last section); after Phase 2 → end session (calibrate runs as next session's opening).

## PDP spine

Always run in this order. Step names are *navigation only* — each step's body lives in `references/pdp-loop.md` and the per-step reference; Read the relevant one before driving a step.

1. **RESOLVE context** — start from the *Session-open snapshot* above for `phase-3-pending` candidates, then confirm against `books.yml` before acting on them (the snapshot is a hint and may be truncated); check staleness (handling: `references/pdp-loop.md`, `references/calibration.md § "The delay" stale-calibrate rule`).
2. **PLAN** — book classification + medium + AI policy + expectations (driven by intensity; references in *The four modes* table).
3. **TUTOR** — chunked reading + chunk-boundary closed-book recall *before* active margin notes + method sub-routines (driven by chapter content; per-method references in *Method sub-routines* table).
4. **End of Phase 2** — set status + timestamp and close session (allowed values: `references/state-schema.md`).
5. **CALIBRATE** (next session opening) — full per-step protocol, ordering rule (confidence/score_prediction BEFORE recall), and `chapter_complete` gate live in `references/calibration.md`.
6. **APPLY** (optional) — one transfer attempt to a different domain.
7. **COMPOSE** — auto-fill chapter note (`references/chapter-template.md`); update `books.yml` (`references/state-schema.md`); run `python3 ${CLAUDE_SKILL_DIR}/scripts/analyze_references.py --emit-frontmatter --chapter <chapter-note-path>` so `references_touched` / `methods_invoked` reflect the deterministic hook-log Reads; schedule spaced re-engagement (`references/spacing-policy.md`).

## Decision rules

These protect the learning signal. Don't paraphrase them. Each rule's full reasoning lives in the linked reference.

1. **Mode priority**: `calibrate > tutor > plan > compose`. If user explicitly asks for a lower-signal mode, do it; otherwise lean upward.
2. **Phase 3 default = next-session warmup.** End the session at the end of Phase 2 with `status: phase-3-pending`. Same-session calibrate is opt-in only: requires explicit user request **and** `now − phase_2_ended_at ≥ 30 min` (working-memory contamination floor). Below 30 min, refuse with the remaining time.
3. **Recall before annotation.** At every chunk boundary: close the book → 30–60s closed-book recall → reopen → 1–2 active margin notes (prose, no enforced prefix). Annotate-first is the dominant fluency-illusion pattern. **Before generating active margin notes OR a recall-probe table, Read `references/annotation-typology.md` AND `references/generative-prompts.md` in this session** — the label schema (`R1..Rn` numeric rows), move examples, conversion contract, and legacy-prefix migration policy live only there.
4. **`chapter_complete` = `learning_passed` (SM transfer ≥ book-type gate).** Textbase recall is advisory; calibration health is tracked *separately* and does not hard-block. The `calibration_health` enums, exact `abs_gap` thresholds, per-type SM gates, and `confirm_next_chapter` trigger live only in `references/calibration.md` + `references/state-schema.md` — do not quote them from memory. If user says "Ch.X 끝났어" before Phase 3 runs, do not promote — status stays `phase-3-pending`. **Do not skip Phase 3.** If user pushes hard, log `phase_3_skipped: true` and proceed; do not pretend the chapter is complete.
5. **Hints are event-based, on-demand, paraphrase-gated** — proactive or time-based hint-offering is the documented dependency-amplification pattern. After any worked example, run **backward-fading** (`references/methods/backward-fading.md`) before any unguided variant. Full hint protocol: `references/methods/hint-escalation.md`.
6. **No generic praise. This is the SOLE canonical banned-praise list — other references point here.** Banned (do not use unless immediately paired with specific justifying feedback; even then prefer the specific feedback alone): "Great!", "Perfect!", "Awesome!", "Excellent!", "Excellent question", "Good job!", "Nice!", "You got it!", "잘했어요", "정확해요!" (when used alone), "맞아요!" (when used alone). Replace with specific feedback: "[X]는 정확. [Y]는 [구체적 오류]." Tutor-design rationale + replacement patterns: `references/llm-tutor-design.md`.
7. **Methods are sub-routines, not forms — bodies live only in their reference.** Invoke a method only after Reading `references/methods/<method>.md` in the current session (full contract: *Method sub-routines* section below). Depth scales with intensity (see *Session intensity*).
8. **Chapter-completion gate is section-level.** Advancement to `phase-3-pending` (and any "next chapter" recommendation) requires every section in the chapter to be `covered` or `skipped`. `pending` / `in-progress` / `used-as-exercise` blocks the gate. `used-as-exercise` is learning debt — surface it and recommend processing the section's narrative ¶ as the next chunk before any phase advance. If the user says "다음 phase 가자" / "Ch.X 끝났어" while uncovered sections remain, interpret it as "next section within the current chapter", not a phase advance — only honor a literal next-chapter request when uncovered is empty. Schema, status enum, init flow (lazy-first ToC extraction), chapter-note sync: `references/section-tracking.md`.

Cross-cutting policies (load when triggered):
- AI usage during the session — `references/ai-policy.md` (3 modes; immutable per chapter; free chat at the dialogue level is refused)
- Reading non-linear chapters (code / proof / dense paper) — `references/methods/code-reading.md` (5-stage protocol; orientation pass mandatory)
- Math/proof reading micro-tasks — `references/methods/math-text-reading.md` (no abstract mode labels — concrete verbs only)
- Note-taking / PKM stance — `references/note-taking-policy.md` (no single-default workflow; reframe over refuse)
- Medium pick (paper / paginated / scrollable) — `references/medium-policy.md` (4-cell matrix)
- Spacing as opt-in cadence commitment (default off) — `references/spacing-policy.md` (daily-floor opt-in + deadline anchor + behavioral retrieval counting)
- L2 / English book mode — `references/l2-mode.md` (tier-conditional defaults; deep not allowed on first-pass)
- Translation-read mode (book-level; mutex with L2) — `references/translation-mode.md` (`--llm-translate`; vocab policy off; L2 paragraph loop steps 1-2 off; chunk-boundary recall mandatory in Korean; intensity uncapped; citation cap 0-1)
- Failure mode signals — `references/failure-modes.md` (3 always-on + 2 type-conditional + 1 dashboard)

## Calibrate as opening of the next session

Phase 3 is the measurement step. The cross-session gap (often overnight) is naturally above the 30-min working-memory floor and is what the retrieval-practice literature actually measures. This default also collapses Phase 3 calibrate and `prior_chapter_recall` into one opening ritual.

**On any session open (cold or resume)**: the *Session-open snapshot* surfaces `status: phase-3-pending` candidates; confirm the full set in `books.yml`, then the oldest in-window chapter runs calibrate as the opening move before today's stated goal. Mechanics, same-session opt-in path, stale-calibrate downgrade (5+ days → 3-question quiz), multiple-pending handling: `references/calibration.md`.

## Book type classification

Each book gets a **two-coordinate classification**: a primary type + a genre lean (orthogonal). Both axes affect session defaults; full taxonomy and per-type patterns: `references/book-types.md`.

**Primary type**: `methodology` (ARQ, Polya — internalize a method, apply externally) | `problem-driven` (Spivak, Feynman exercises) | `conceptual` (Griffiths, Sapolsky) | `argument-driven` (Mill, Sandel) | `math-proof-heavy` (Spivak proofs, ε-δ chapters) | `reference` (Polya Part II — lookup, no PDP).

**Genre lean**: `narrative-leaning` (theme + character/causal-chain spine — `paragraph_capture` cap **2–3** per chapter) | `expository-leaning` (signal-word-dense, claim-by-claim — standard `paragraph_capture` cap 5–10) | `mixed` (per-chapter classification).

Classify both axes on first session per book; confirm with the user; store in `books.yml` as `type:` and `genre_lean:`.

## Method sub-routines

Invoked from within the tutor phase when chapter content calls for them. **Preserve core meaning of canonical prompts** — check the Reference for the exact wording, translate for delivery as needed; paraphrases that drift from the original cognitive move (e.g., "summarize" for "anticipate") weaken the effect. Each method's full body (steps, prompts, gates, examples — including step counts like "Polya 4 steps" / "Newman 5 stages") lives only in its Reference file; SKILL.md intentionally omits the canonical shape, so the only correct invocation path is Reading the Reference in the current session. Reconstructing a method body from memory drifts in ways that look right but aren't.

| Sub-routine | When to invoke | Reference (REQUIRED Read this session before invoke) |
|---|---|---|
| **ARQ** | argument unit (not paragraph); depth 0–3 picked at section boundary | `references/methods/arq.md` |
| **Polya** | chapter contains a problem to solve | `references/methods/polya.md` |
| **Schoenfeld** | every step transition inside Polya | `references/methods/schoenfeld.md` — **Schoenfeld runs *inside* Polya: if `polya.md` was not Read this session, Read it first** |
| **Newman** | user got a problem wrong; runs *before* level-3 worked-example escalation | `references/methods/newman.md` |
| **Hint escalation** | every help moment in tutor mode; event-triggered, paraphrase-gated, time-on-hint logged | `references/methods/hint-escalation.md` |
| **Backward fading** | after any worked example, before any unguided variant | `references/methods/backward-fading.md` |
| **Math-text reading** | math-proof-heavy chapters; per-proof micro-tasks; diagram two-pass | `references/methods/math-text-reading.md` |
| **Code-reading** | non-linear chapters (code / formal proof / dense paper) | `references/methods/code-reading.md` |
| **Scaffolded AI prompting** | every AI tool query during a learning session | `references/ai-policy.md` (gates whether AI is allowed at all — under `strict-no-ai` this template never fires) **+** `references/methods/scaffolded-ai-prompting.md` |
| **Refutation text** | conceptual chapter with prior misconceptions, non-politically-contested topic | `references/methods/refutation-text.md` |
| **Proof comprehension** | chapter contains formal proofs | `references/methods/proof-comprehension.md` |
| **Argument reading** | argument-driven chapter, *or* conceptual chapter on politically/identity-laden topic | `references/methods/argument-reading.md` |

The "## The four modes" mode→file mappings and the full per-situation gate live in **Required-read gates > Situation → required Read** (the single comprehensive source); this table keeps the method→file path inline because methods are the highest-frequency, highest-hallucination-risk invocation.

`arq_depth: 0–3` (method depth) is distinct from `hint_level: 0–4` (dialogue help) — different axes.

## Session intensity (light / standard / deep)

Intensity scales **method depth and plan-phase scope**, not the *learning core* (chunk-boundary recall, situation-model transfer, delayed retrieval — non-negotiable across all intensities).

| Intensity | Time | Plan scope | Tutor scope | Default for |
|---|---|---|---|---|
| **light** | 15–25 min | Chapter name + 1 goal + 1 prediction. Skip book classification, expectations, misconceptions, learner_profile if already on file. | 1 chunk; chunk-boundary recall mandatory; `paragraph_capture` only on important chunks; Calibrate Step 2b may be skipped (chapter then capped at `phase-3-textbase-only`). | weekday / tired / L2 must-scaffold first read |
| **standard** | 30–60 min | Full plan: classification + medium + AI policy + 3 textbase + 2 SM expectations + 2–3 misconceptions. | Full PDP loop; chunk size 5–10 min; chunk-boundary recall mandatory; Calibrate Step 2a + 2b required; one graphic organizer required. | normal study |
| **deep** | 60–90 min (cap 90) | Standard + categorization micro-task on 6–8 sample problems (problem-driven / methodology / math-proof-heavy). | ARQ depth ≥ 2 / Polya full trace / argument-reading 5-step / proof-comprehension 3 facets; transfer attempt; detailed chapter note. | exam prep / hard chapter / second pass |

**Defaults**: L2 must-scaffold → light; L2 assisted → standard cap; normal → standard; exam/hard/second-pass → deep. Deep is not the default for a first-pass L2 read (cognitive load is already high; user may override). **Out-of-time signal** (`now > session_end − 10 min`): downgrade in-flight; avoid starting a new phase that won't fit. Log `intensity_downgraded: true`.

## Output: chapter note

The compose step auto-fills the chapter note from session traces. Frontmatter schema, body sections, append-only conventions: `references/chapter-template.md`. Canonical state values: `references/state-schema.md`.

Top-level invariants:

- **Append-only.** Never edit prior session entries; new attempts go as new sessions.
- **`status` field** drives next-phase routing. Canonical enum: `in-progress` → `phase-2-pending-conversion` → `phase-3-pending` → `phase-3-textbase-only` *or* `phase-3-complete` → `applied` → `scheduled`. Use only these values.
- **End of Phase 2** sets `status: phase-3-pending` (or `phase-2-pending-conversion` if conversion deferred) + `phase_2_ended_at: <ISO8601>`.
- **`session_health`** captures all six failure-mode flags after every session (see `references/failure-modes.md`).
- **Concept-level tracking** is trigger-deferred — populate `concept_candidates: [...]` in frontmatter; bootstrap separate `~/study-journal/concepts/` files only after the activation trigger (≥ 2 chapters AND ≥ 5 candidates).
- **`books.yml` is metadata-only AND Edited at most once per session.** During compose, write only enums / numbers / dates / status maps / short anchors into `chapter_metrics[N]`. Long-form session narrative goes into the chapter note body — never into `books.yml`. Reason: `books.yml` is re-cached on every Edit; narrative there inflates `cache_create` ~30–40% of session token cost. Full allow/forbid list: `references/state-schema.md § books.yml chapter_metrics — allowed and forbidden fields`.

  **Pre-Edit self-check** (run before EVERY `books.yml` Edit during compose):
    1. Is this the only `books.yml` Edit this session? Compose mode batches *all* `chapter_metrics[N]` updates into a single Edit. Multiple per-session Edits is an anti-pattern — observed 2026-05-18 to burn ~5KB extra cache_create per redundant Edit.
    2. For every new key being added, verify it is on the allowlist in `references/state-schema.md § books.yml chapter_metrics`. If not, the value belongs in the chapter note body or `_archived/books-yml-snapshot-<date>.md`, not `books.yml`.
    3. `session_health.*` keys: enum/bool only. Narrative qualifiers like `illusion: <hyphen-glued-narrative>` are forbidden — the enum value is `true | false`; the narrative belongs in the chapter note Session-N block.
    4. `spaced_retrievals[].anchors` (narrative list) is forbidden in `books.yml`. Keep only `{date, type, q_count, score}` per row.

  After the single Edit, run `python3 ${CLAUDE_SKILL_DIR}/scripts/lint_state.py ${CLAUDE_SKILL_DIR} --books-yml ~/study-journal/books.yml` as a **mandatory** compose step. Only close the session when the lint passes; on violations, fix `books.yml` (move offending values to the chapter note body) and re-run.

## Required-read gates

The skill's runtime contract: **the canonical spec is the file, not your memory of it, and not the one-line summaries in this SKILL.md.** Method bodies, hint ladders, schemas, and gates evolve; reconstructing them from memory drifts in ways the SKILL.md summary will not catch because the summary "sounds right."

**Default to SKILL.md alone. Read exactly ONE reference at the moment you ENTER its situation — never pre-load a batch at session start.** The point is to Read on *entry* to a situation. A heavy chapter typically pulls 3–4 method files plus 2–3 policy files across 60 min; a light chapter often pulls 0–1. If a situation lists two required Reads and you've only Read one this session, Read the second before proceeding — don't cite both and hope. After the canonical full Read of a file this session, targeted re-lookups in that same file may use `grep -n` or a section-scoped Read (files >300 lines carry a `## Contents` TOC for navigation) — but grep alone never satisfies a gate.

Before doing any of the following, `Read` the canonical reference in the **current session**:

- describe the method body, steps, or rule as if quoting the spec,
- invoke the method as a sub-routine treating it as canonical,
- name a numbered protocol, ladder, or gate by spec terms (e.g., "L0-L4 ladder", "Newman 5-stage", "Polya 4 steps", "abs_gap ≤ 20", "paraphrase gate"),
- claim a refusal/gate exists "per the spec".

SKILL.md summaries and prior-session reads do not satisfy the gate. If you have not Read it this session, either Read it now, or label the substance as `SKILL.md summary only` and acknowledge the spec body is unverified — do not describe the spec body or steps as canonical, and do not say "the spec says ...".

(Chapter-note `references_touched` / `methods_invoked` is system-emitted from the hook log at compose time — you don't author it directly. See `Per-response context surfacing` below.)

This is not a politeness rule; it is the audit contract. The PostToolUse hook (`scripts/log_reference_read.sh`) records every Read; `scripts/analyze_references.py` cross-checks chapter-note declarations against the hook log and surfaces `declared_not_read` as drift.

**Pre-invocation self-check**: Before naming a method, ladder, gate, numbered protocol, schema label, marginalia prefix, or policy mode in the body, verify you Read its canonical file in this session. Trigger lexicon (non-exhaustive): step-counted method names ("Newman 5-stage", "Polya 4-step", "Browne–Keeley criticals"), hint-protocol terms ("L0–L4 ladder", "paraphrase gate"), calibration terms ("abs_gap ≤ 20", "learning_passed", `calibration_health` enums), marginalia/probe labels ("R1/R2 recall-probe row", legacy `P:` / `R-P` prefix migration), AI-policy modes ("scaffold / refuse-chat / refuse-all"), and state enums ("used-as-exercise", "phase-2-pending-conversion").

### Situation → required Read

When the current turn enters one of these situations, the listed file is a hard prerequisite. If it has already been Read this session, no new Read is needed; if not, Read before the substantive move.

| Situation | Required Read (current session) |
|---|---|
| Explaining, invoking, or refusing a hint at level 1-4; describing the L0-L4 ladder; naming the paraphrase gate; logging `hint_event` | `references/methods/hint-escalation.md` |
| After any worked example, before any unguided / parallel problem; generating a fade-N completion | `references/methods/backward-fading.md` |
| Polya 4-step invocation (preserve core wording from the reference); `hint_level: 4` reveal requiring the level-4 reflection record | `references/methods/polya.md` |
| Newman 5-stage error walk-back after a failed problem attempt | `references/methods/newman.md` |
| Schoenfeld 3-question prompt at a Polya step transition | `references/methods/schoenfeld.md` (+ `references/methods/polya.md` — Schoenfeld runs inside Polya; if Polya was not Read this session, Read it first) |
| ARQ depth 0-3 invocation; argument-unit segmentation; Browne-Keeley criticals | `references/methods/arq.md` |
| Argument-driven echo-chamber detection; steelman requirement | `references/methods/argument-reading.md` + `references/failure-modes.md` |
| Math-proof-heavy chapter micro-tasks; ε-δ; diagram two-pass; mode-label rejection | `references/methods/math-text-reading.md` |
| Formal proof comprehension (7 facets, pick 1-3) | `references/methods/proof-comprehension.md` |
| Code-reading or non-linear chapter (5-stage protocol, orientation pass) | `references/methods/code-reading.md` |
| Refutation text for non-politically-contested misconception removal | `references/methods/refutation-text.md` |
| AI-assisted study query (any AI tool call during a learning session) | `references/ai-policy.md` + `references/methods/scaffolded-ai-prompting.md` |
| Active margin-note generation; recall-probe row labeling (numeric `R1..Rn` convention); legacy chapter notes that carry `P:` margin prefixes or `R-P` recall rows | `references/annotation-typology.md` + `references/generative-prompts.md` |
| Chapter-note frontmatter write/edit; `books.yml chapter_metrics` allow/forbid | `references/state-schema.md` |
| Section-level chapter tracking; "next chapter" recommendation; chapter-completion gate | `references/section-tracking.md` |
| Phase 3 calibrate mechanics; SM transfer gate; `learning_passed` / `calibration_health` split; stale-calibrate downgrade; per-type thresholds | `references/calibration.md` |
| Review-routing branch (natural-language or `--review` flag); status-based routing to Phase 3 / spaced retrieval / Step 2b retry / in-chapter recap / conversion | `references/review-routing.md` |
| Failure-mode flag set on session close (any of the 6 tiers) | `references/failure-modes.md` |
| L2 / English book tier + narrow-reading mode + glossary policy | `references/l2-mode.md` |
| `--llm-translate` mode activation / mutex toggle with `l2_mode` / loaded-language chapter alert firing / plan-phase `translation_mode.source` question | `references/translation-mode.md` |
| Medium choice (paper / paginated / scrollable) for a chapter | `references/medium-policy.md` |
| Spacing scheduler invocation; daily-floor commitment; behavioral retrieval counting | `references/spacing-policy.md` |
| Note-taking system reframe (Zettelkasten / PARA / sketchnoting) | `references/note-taking-policy.md` |
| LLM-tutor banned praise, Bloom distribution surface | `references/llm-tutor-design.md` |
| Citation / `quote_id` format | `references/citation-format.md` |
| Book-type classification (any axis) | `references/book-types.md` |
| Composing the chapter-note body section schema | `references/chapter-template.md` |
| PDP loop pseudocode + edge cases (when the spine itself is in question) | `references/pdp-loop.md` |
| First-run setup / `~/study-journal` bootstrap / EPUB→PDF conversion / reference-audit hook install | `references/setup.md` |

These are *gates*, not a reading list. A turn that only confirms a session plan or restates a goal triggers nothing; a turn that explains why a level-4 hint was refused triggers `hint-escalation.md`.

## Per-response context surfacing

Do **not** write a `📚 refs:` / `🛠 methods:` footer in the response. Reference attribution is now system-generated from the deterministic hook log — model-authored footers were retired because they let `declared_not_read` drift in (footer cites a file that was never actually Read this session). The hook log either has the Read or it doesn't; that's the source of truth.

**Mechanism**: a PostToolUse hook (`scripts/log_reference_read.sh`, registered in `~/.claude/settings.json`) records every `Read` of a study-session reference/method file into `~/study-journal/.session-log/<KST-date>.jsonl`. At **compose** time, run:

```
python3 ${CLAUDE_SKILL_DIR}/scripts/analyze_references.py --emit-frontmatter --chapter <chapter-note-path>
```

This filters the log to the current session and dedupe-appends the actual Reads into the chapter note's `references_touched` / `methods_invoked`. Idempotent; safe to re-run. Standalone work outside a chapter (cold-start setup, plan phase, standalone Polya) has no chapter note to append to — the session log is the only record.

Audit: `scripts/analyze_references.py` (default mode) partitions all reads into `read_and_declared` / `read_not_declared` / `declared_not_read` / `unknown_or_context_carried`. `declared_not_read` is the drift signal. Full field definitions: `references/state-schema.md § Frontmatter fields — chapter note`.

## Operational examples

### Cold start

User: "ARQ Ch.1부터 같이 공부하고 싶어"

1. Check `~/study-journal/` — absent. **Read `references/setup.md`**, then run setup: `scripts/init.sh` bootstrap → convert ARQ EPUB → PDF if needed → populate `books.yml` → **install the reference-audit hook (Step 8, `scripts/install-hook.sh`); skipping it makes the read-audit a no-op.**
2. Plan phase (standard default): classify ARQ as **methodology** + **expository-leaning**; pick medium; declare AI policy; generate 3 textbase + 2 SM expectations; PKA + prediction + goal_question.
3. Tutor phase: chunked reading (5–10 min) → 30–60s closed-book recall → 1–2 active margin notes (prose); ARQ sub-routine at argument units.
4. Chapter end: convert margin notes (post-hoc bucket per `references/annotation-typology.md § Conversion contract`) + one graphic organizer.
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
- If pandoc/calibre is missing for EPUB conversion, Read `references/setup.md` and surface its exact install-command block (Step 5) — don't auto-install.
- Sessions are short by default (30–60 min target). Favor shorter, more frequent sessions over a long single block.

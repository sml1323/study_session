# Annotation Typology — Active Margin Notes + Order + Conversion
<!-- TODO evidence-tag - see references/evidence-labels.md; this files thresholds/policies are not yet labeled -->

Highlighting alone — selecting passages without an accompanying generative move — does not improve comprehension on standardized testing. The signal that *does* predict learning is the *constructive* move that follows the highlight: a margin question, a paraphrase, an objection, an inferred connection. This file specifies what an "active margin note" is, the order in which it must come (recall first), and the chapter-end conversion contract.

This file is referenced from `SKILL.md` § "Generative prompts" and from `references/generative-prompts.md` § "selective_annotation".

> **History note (Cut B simplification, 2026-05-21).** Earlier versions of this skill required each margin note to carry one of five single-letter prefixes — **P / I / M / E / Q** — bundled into a synthesized "PIMEQ" acronym. The 5 underlying *moves* (predict / infer / monitor / evaluate / question) are research-grounded — they are the verbal-protocol categories Pressley & Afflerbach 1995 mapped in expert adult readers. But the "PIMEQ" acronym wrapper itself was a skill-internal coinage from the source wiki's design-suggestion notes, not a published label, and the per-note prefix classification at write time generated cognitive overhead that did not translate to retention benefit. The current rule keeps the 5 moves as **examples of what an active margin note looks like**, drops the enforced prefix, and moves all categorization to chapter end (where it can be done in one pass, post-hoc, based on what each note actually says). Legacy chapter notes that used the prefix system remain valid (append-only; see § "Legacy migration" below).

## Active margin notes — the constructive move that satisfies annotation

An **active margin note** is a short prose note (one short sentence is enough) tagged to a passage that goes *beyond highlighting* — it generates new content (a paraphrase, a question, an inference) or marks new metacognitive state (a confusion flag, an objection, a prediction). A bare highlight (a selected passage with no accompanying prose) does **not** count as an active margin note and will not satisfy the chapter's annotation requirement.

Constructive reading moves documented by Pressley & Afflerbach 1995 — the verbal-protocol categories expert adult readers spontaneously produce while reading — are the canonical examples of what an active margin note does:

| Move | Korean | What it looks like in the margin |
|---|---|---|
| **Predict** | 예측 | "다음 단락에서 저자가 X에 대한 반례를 제시할 듯" |
| **Infer** | 추론 | "결국 저자의 핵심 주장은 Y" |
| **Monitor** | 점검 | "여기 잘 모르겠음 — 'X'가 정의된 곳이 어디?" |
| **Evaluate** | 평가 | "동의 안 함 — 반례 Z가 있음" / "이 reason은 결론을 뒷받침 못함" |
| **Question** | 질문 | "왜 X가 Y로 이어지지?" |

These are **examples, not enforced labels**. The user writes prose; the note does not need a prefix letter or a category tag. The list exists so that (a) the user has a checklist if "what kinds of active notes are possible" is unclear, and (b) the chapter-end conversion step has a vocabulary for post-hoc classification.

## Order — recall first, annotate second

Annotation must come **after** the chunk-boundary closed-book recall (see `references/generative-prompts.md` interim_recall and SKILL.md § "Things to avoid"). The order matters because the dominant failure mode is "annotate-while-reading-fluently → mark looks meaningful → don't actually struggle to retrieve → fluency illusion". The fix is structural:

```
1. Read chunk (5-10 min).
2. Close the book.
3. 30-60s closed-book recall of what just happened: "what did this chunk say?"
4. Open the book.
5. Add 1-2 active margin notes — including marking the spots the recall failed (those naturally surface as "monitor" / confusion-flag notes).
6. Move to next chunk.
```

**Annotating before recall is forbidden.** If the user habitually annotates first, surface the rule once and proceed; if the pattern persists across chapters, log it as a session_health note for trend review.

## Annotation density cap

- **Hard cap**: 1-2 active margin notes per page. More than that is a signal that either (a) the chunk is too dense and should be split into smaller chunks for the next read, or (b) the user is reverting to highlight-everything mode.
- **Bare highlights** (no accompanying prose) do not count toward or against the cap; they are advisory only and should be converted at chapter end (see § "Conversion contract") or stripped.
- **Override**: a methodology chapter may legitimately want a higher density on a definitions-heavy section. Allow up to 3 per page on those, log `density_override_section: <section>` once.

## Graphic organizer requirement (intensity ≥ standard)

For chapters at standard or deep intensity, **one graphic organizer per chapter is required** before chapter complete: a mind map, matrix, hierarchy, comparison table, or sequence diagram that captures the chapter's core relational structure. The organizer is an integration move; active margin notes are local; the organizer is the cross-chunk synthesis.

The organizer:
- is user-constructed (not skill-generated; constructed organizers outperform consumed ones)
- has 3-9 nodes (Cowan capacity bound; if more than 9 nodes the chapter has been over-decomposed and the user should pick the load-bearing structure)
- has labeled edges (relationship type: `causes`, `requires`, `is-a`, `contradicts`, `enables`, `precedes`, etc.)
- includes at least one cross-reference to a prior chapter or a prior concept

Light-intensity sessions may skip the organizer; in that case `chapter_complete` is restricted to `phase-3-textbase-only`.

## Conversion contract — chapter end

Raw active margin notes are not the final state. At chapter end (Phase 2 → compose), each margin note (and any bare highlights still in the chapter) is converted into one of three durable artifacts. The decision is **post-hoc, made by reading each note** — no per-note label was required during writing, so the categorization happens here in one pass:

| What the note records | Conversion target | When |
|---|---|---|
| An **unresolved question or gap** (the note flags something the user did not understand by chapter end, or a question the chapter never answered) | retrieval card on the gap + open thread | always |
| A **question that the chapter later answered** | retrieval card on the question (these are usually the best self-test items) | always |
| A **prediction that was confirmed** | concept note row in chapter note (or drop if trivial) | always |
| A **prediction that was disconfirmed** | retrieval card with the contrast ("expected X; chapter showed Y because ...") | always |
| An **inference / synthesis** worth resurfacing — the user's own conceptual move that recurs or seems generative | concept note candidate; promote to a standalone concept entry if it recurs across ≥ 2 chapters | always |
| An **evaluation or objection** | source note (with original text quote anchor) + open-thread entry for follow-up | always |
| A **resolved confusion** (the user flagged "I don't understand X", and the rest of the chapter resolved it) | drop (the resolution itself was the work; no card needed) | usually |
| A **bare highlight** still in the chapter | source note (with original text quote) — at minimum | always |

If the user ends a chapter with **unresolved margin notes or unconverted bare highlights**, the chapter sits at `phase-2-pending-conversion` (not `phase-3-pending`) until the conversion pass runs. This is the structural enforcement of "raw highlight is not learning". Once converted, the chapter advances to `phase-3-pending`. Canonical enum: `references/state-schema.md`.

The conversion pass is fast (~5 min for a 1-hour chapter at proper density); if it feels long, the user has over-annotated and the next chapter should reduce density.

### Optional: Bloom distribution check at conversion

While running the conversion pass, glance across the chapter's margin notes and note the distribution of move-types (predict / infer / monitor / evaluate / question — informally; no enforced labels). A chapter whose margin notes are entirely "monitor" / confusion-flag is a low-Bloom chapter and the user can be nudged toward inference and evaluation on the next chapter. This is a soft signal at compose time, not a gate; skip if it adds friction. (The Bloom-distribution heuristic itself is unsourced — it predates Cut B and is retained because the underlying intuition is plausible, not because it has cited evidence.)

## Recall-table row labels — `R1`, `R2`, ... (numeric, append-only-safe)

Closed-book recall tables in the chapter note body (Phase 2 chunk-boundary recalls, Phase 3 calibrate textbase recall) use **numeric row labels**: `R1`, `R2`, `R3`, ...

The descriptive category word (proposition / paraphrase / setup / statement / thesis / image / mechanism / equation / open_q / …) lives as a subscript on the schema key (`R1_proposition`) and is optional as a parenthetical aide-mémoire in surface output (`R1 (proposition): ...`). Per-book-type probe schemas live in `references/generative-prompts.md § recall_probe_schema`.

**Why numeric, not letter labels** — numeric labels are unambiguously recall rows, never confusable with any other annotation in the chapter note. Letter labels (`R-P`, `R-I`, etc.) tied to category first letters are a structural attractor: across sessions the `R-` falls off and the surface form drifts, and the same letters can be silently reinterpreted by book type. Numeric labels are stable across sessions and append-only-safe.

This rule is independent of the Cut B simplification — even without margin-prefix letters in play, numeric recall row labels remain the convention because the append-only stability matters on its own.

## Legacy migration — chapter notes that used the prefix system

Chapter notes written before Cut B (2026-05-21) may carry margin notes prefixed with `P:` / `I:` / `M:` / `E:` / `Q:`, or recall rows labeled `R-P` / `R-I` / `R-M` / `R-E` / `R-Q`. These are **valid history**, not violations — chapter notes are append-only. Do not rewrite them silently.

On first re-entry to a chapter that contains either legacy form, surface the affected lines in one short message:

> "Ch.X Session N에 옛 prefix 포맷 보임 (`P:` margin 또는 `R-P` recall). 새 컨벤션은 prose margin note + 숫자 recall row. 둘 중 하나 골라: (a) in-place rename (히스토리 손실), (b) 그대로 두고 새 chunk부터 새 컨벤션 사용."

Log the user's choice in `session_health.label_migration: pending | renamed | left-as-is`.

Do not auto-rename without user confirm. Do not block the session on this — surface once per affected chapter and proceed.

## Anti-patterns

- **Annotation as a substitute for retrieval**: dense margin notes + zero retrieval = the failure pattern. The order rule above exists to prevent this.
- **Bare highlights as final state**: highlighting without conversion does not teach; it only marks where the eye stopped.
- **Skill generates the graphic organizer**: defeats the construction move. Skill *can* offer to format a user-described organizer (ASCII / mermaid), but the structure must come from the user.
- **Annotation inflation**: writing a margin note on every paragraph to satisfy a perceived quota. The 1-2 per page cap exists to prevent this.
- **Re-introducing the prefix at write time**: the Cut B simplification removed per-note prefix classification deliberately — it generated cognitive overhead without retention benefit. If a session output ever starts asking the user to tag each margin note with `P:` / `I:` / `M:` / `E:` / `Q:`, that is drift back toward the pre-Cut-B protocol. Classification belongs at conversion time (chapter end), not at write time (chunk boundary).
- **Reintroducing "PIMEQ" as a label**: the acronym was a wiki-synthesis brand without a published source. Use "active margin notes" as the term going forward.

## Cross-references

- `references/generative-prompts.md` — `selective_annotation` prompt (active margin notes; bare highlights deprecated as default); `recall_probe_schema` (numeric `R1..Rn` convention with per-book-type category words as subscripts)
- `references/calibration.md` — Step 2b transfer questions can be drawn from margin notes that recorded questions or evaluations (Pressley & Afflerbach's question / evaluate moves are the highest-leverage source for self-test items)
- `SKILL.md` § "Things to avoid" — annotate-before-recall ban, raw-highlight-as-final ban
- `references/state-schema.md` — `session_health.label_migration` enum; `phase-2-pending-conversion` status (the lifecycle position for chapters with raw margin notes still to convert)

# Annotation Typology — PIMEQ + Order + Conversion

Highlighting alone — selecting passages without an accompanying generative move — does not improve comprehension on standardized testing. The signal that *does* predict learning is the *constructive* move that follows the highlight: a margin question, a paraphrase, an objection, an inferred connection. This file specifies the typology, the order, and the chapter-end conversion contract.

This file is referenced from `SKILL.md` § "Generative prompts" and from `references/generative-prompts.md` § "selective_annotation".

## PIMEQ — the five constructive prefixes

Margin notes during a Phase 2 reading chunk are tagged with one of five single-letter prefixes. A bare highlight (no prefix, no marginal text) does **not** count as PIMEQ and will not satisfy the chapter's annotation requirement.

| Prefix | Move | Example marginal text |
|---|---|---|
| **P** | **Predict** | "P: 다음 단락에서 저자가 X에 대한 반례를 제시할 듯" |
| **I** | **Infer** | "I: 결국 저자의 핵심 주장은 Y" |
| **M** | **Monitor** | "M: 여기 잘 모르겠음 — 'X'가 정의된 곳이 어디?" |
| **E** | **Evaluate** | "E: 동의 안 함 — 반례 Z가 있음" / "E: 이 reason은 결론을 뒷받침 못함" |
| **Q** | **Question** | "Q: 왜 X가 Y로 이어지지?" |

The five categories cover the documented constructive-reading moves of skilled adult readers. They are also Bloom-distributed: P/I sit higher (apply/analyze), M/Q sit at understand/analyze, E sits at evaluate. A chapter whose marginal notes are all M is a low-Bloom chapter and the user should be nudged toward I and E on the next chapter.

### Light-intensity reduction

Light-intensity sessions may use only **P / M / Q** (3 prefixes). Drop I and E. The reduction is documented; do not silently revert to bare highlights.

## Reserved letters — do not collide

The single-letter labels **P / I / M / E / Q** are reserved for marginal-annotation prefixes only. Other parts of the chapter note (closed-book recall tables, summaries, calibration blocks, concept-candidate lists) must not use these letters as schema keys. The semantics of P/I/M/E/Q are permanently the five constructive moves above — **Predict / Infer / Monitor / Evaluate / Question** — and do not vary by book type.

Use numeric labels (`R1`, `R2`, ...) for recall-probe rows, with the category word as a subscript on the schema key (`R1_proposition`, `R2_image`, `R3_mechanism`) and as an optional parenthetical in surface output (`R1 (proposition): ...`). Per-book-type probe schemas live in `references/generative-prompts.md § recall_probe_schema`.

### Why this rule exists — letter-collision attractor

When the recall probe row lacks an explicit label format, the model invents one on the spot and tends to borrow the first letter of each probe category. For methodology/ARQ books the natural categories begin with *Paraphrase / Inference / Misconception / Example / Question* — `P / I / M / E / Q`. For conceptual/physics books they begin with *Proposition / Image / Mechanism / Equation / Question* — also `P / I / M / E / Q`. In one session this looks like a benign `R-P` row prefixed onto a recall table. Across 3–4 sessions the `R-` falls off and the model writes a "book-type-specific PIMEQ" table where `P = Paraphrase` for ARQ and `P = Proposition` for Feynman — redefining the *margin* PIMEQ vocabulary by book type, which it is never supposed to do. The 4-session drift was observed in real chapter notes (ARQ Ch.1, Feynman Vol.1 Ch.1) before this rule existed; the table itself never appeared anywhere in the skill — it was a structural hallucination produced by the schema vacuum at the recall-probe seat.

The fix is structural, not exhortative: numeric row labels make the surface form of a recall row unambiguous (`R1`, never `P`), and the reserved-letter rule explicitly forbids single-letter P/I/M/E/Q outside margin prefixes. The category word is metadata on the row, not the row's primary label.

### Anti-pattern fixtures

- `R-P 명제 / R-I image / R-M mechanism` rows in a Feynman recall table while `P:` / `I:` / `M:` margin notes use the canonical Predict/Infer/Monitor meanings in the same session — shared letter induces drift on next session
- `R-P Paraphrase / R-I Inference / R-M Misconception / R-E Example / R-Q Question` table in an ARQ recall — even with the `R-` prefix, the letter overlap means the next session writes the same categories as plain `P / I / M / E / Q` margin prefixes
- A summary that asserts `"PIMEQ for argumentation = Paraphrase·Prediction / Inference / Misconception / Example·Elaboration / Question"` and `"PIMEQ for physics = Proposition / Image / Mechanism / Equation / Question"` — this table was never in the skill; it was hallucinated from the letter collision. PIMEQ does not vary by book type.

### Migration of existing notes

If a chapter note already contains `R-P` / `R-I` / `R-M` / `R-E` / `R-Q` rows in a recall table, do *not* rewrite them silently — chapter notes are append-only. Instead, on first re-entry to that chapter:

1. Surface the affected lines to the user in one short message ("Ch.X Session N의 recall 표에 R-P 형식이 보임 — 새 규칙(R1/R2 numeric)으로 정정 가능").
2. Ask: rename the labels in-place (preserves history but breaks append-only), or leave the historical rows and start fresh with the new labels going forward.
3. Log the choice in `session_health.label_migration: pending | renamed | left-as-is`.

Do not auto-rename without user confirm. Do not block the session on this — surface once per affected chapter and proceed.

## Order — recall first, annotate second

Annotation must come **after** the chunk-boundary closed-book recall (see `references/generative-prompts.md` interim_recall and SKILL.md § "Things to avoid"). The order matters because the dominant failure mode is "annotate-while-reading-fluently → mark looks meaningful → don't actually struggle to retrieve → fluency illusion". The fix is structural:

```
1. Read chunk (5-10 min).
2. Close the book.
3. 30-60s closed-book recall of what just happened: "what did this chunk say?"
4. Open the book.
5. Annotate with PIMEQ prefixes — including marking the spots the recall failed (those get `M` prefix automatically).
6. Move to next chunk.
```

**Annotating before recall is forbidden.** If the user habitually annotates first, surface the rule once and proceed; if the pattern persists across chapters, log it as a session_health note for trend review.

## Annotation density cap

- **Hard cap**: 1-2 PIMEQ notes per page. More than that is a signal that either (a) the chunk is too dense and should be split into smaller chunks for the next read, or (b) the user is reverting to highlight-everything mode.
- **Bare highlights** (no prefix) do not count toward or against the cap; they are advisory only and should be converted at chapter end (see § "Conversion contract") or stripped.
- **Override**: a methodology chapter may legitimately want a higher density on a definitions-heavy section. Allow up to 3 per page on those, log `density_override_section: <section>` once.

## Graphic organizer requirement (intensity ≥ standard)

For chapters at standard or deep intensity, **one graphic organizer per chapter is required** before chapter complete: a mind map, matrix, hierarchy, comparison table, or sequence diagram that captures the chapter's core relational structure. The organizer is an integration move; PIMEQ notes are local; the organizer is the cross-chunk synthesis.

The organizer:
- is user-constructed (not skill-generated; constructed organizers outperform consumed ones)
- has 3-9 nodes (Cowan capacity bound; if more than 9 nodes the chapter has been over-decomposed and the user should pick the load-bearing structure)
- has labeled edges (relationship type: `causes`, `requires`, `is-a`, `contradicts`, `enables`, `precedes`, etc.)
- includes at least one cross-reference to a prior chapter or a prior concept

Light-intensity sessions may skip the organizer; in that case `chapter_complete` is restricted to `phase-3-textbase-only`.

## Conversion contract — chapter end

Raw PIMEQ marginalia are not the final state. At chapter end (Phase 2 → compose), each PIMEQ note is converted into one of three durable artifacts:

| Note origin | Conversion target | When |
|---|---|---|
| **P** (Predict) — confirmed | concept note row in chapter note (or skipped if trivial) | always |
| **P** (Predict) — disconfirmed | retrieval card with the contrast ("expected X; chapter showed Y because ...") | always |
| **I** (Infer) | concept note candidate; promote if recurs across ≥2 chapters | always |
| **M** (Monitor) — resolved later | nothing (conversion not needed; the resolution itself was the work) | usually drop |
| **M** (Monitor) — unresolved | open thread + retrieval card on the gap | always |
| **E** (Evaluate) | source note (with original text quote), and an open-thread entry for follow-up | always |
| **Q** (Question) — answered later in chapter | retrieval card on the question (these are usually the best self-test items) | always |
| **Q** (Question) — still open | open thread + spaced re-engagement queue entry | always |
| **bare highlight** | source note (with original text quote) — at minimum | always |

If the user ends a chapter with **unconverted bare highlights or unresolved marginalia in the chapter note**, the chapter sits at `phase-2-pending-conversion` (not `phase-3-pending`) until the conversion pass runs. This is the structural enforcement of "raw highlight is not learning". Once converted, the chapter advances to `phase-3-pending`. Canonical enum: `references/state-schema.md`.

The conversion pass is fast (~5 min for a 1-hour chapter at proper density); if it feels long, the user has over-annotated and the next chapter should reduce density.

## Anti-patterns

- **Annotation as a substitute for retrieval**: dense margin notes + zero retrieval = the failure pattern. The order rule above exists to prevent this.
- **Bare highlights as final state**: highlighting without conversion does not teach; it only marks where the eye stopped.
- **Skill generates the graphic organizer**: defeats the construction move. Skill *can* offer to format a user-described organizer (ASCII / mermaid), but the structure must come from the user.
- **PIMEQ inflation**: tagging every paragraph with a prefix to satisfy a perceived quota. The cap exists to prevent this.
- **PIMEQ letter collision**: using P / I / M / E / Q letters in any non-margin-prefix context (recall probe row labels, summary keys, calibration block keys). Even with an `R-` prefix the letter overlap induces drift across sessions. Use `R1..R5` numeric labels for recall probes. PIMEQ is permanently *Predict / Infer / Monitor / Evaluate / Question* and does not vary by book type. See § "Reserved letters" above.

## Cross-references

- `references/generative-prompts.md` — selective_annotation prompt (uses PIMEQ)
- `references/calibration.md` — Step 2b transfer questions can be drawn from Q (Question) and E (Evaluate) PIMEQ notes
- `SKILL.md` § "Things to avoid" — annotate-before-recall ban, raw-highlight-as-final ban

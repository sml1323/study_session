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

## Cross-references

- `references/generative-prompts.md` — selective_annotation prompt (uses PIMEQ)
- `references/calibration.md` — Step 2b transfer questions can be drawn from Q (Question) and E (Evaluate) PIMEQ notes
- `SKILL.md` § "Things to avoid" — annotate-before-recall ban, raw-highlight-as-final ban

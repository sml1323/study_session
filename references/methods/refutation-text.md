# Refutation Text — Conceptual Chapter Sub-routine
<!-- TODO evidence-tag - see references/evidence-labels.md; this files thresholds/policies are not yet labeled -->

When invoked: a chapter classified `conceptual` (any sub-genre — physics, biology, social science, philosophy of science, etc.) where the topic plausibly carries widespread misconceptions in its audience. The sub-routine generates the misconception → correction structure as a learning activity, even when the chapter itself is written in plain expository style. Strong evidence base across science, math, and social-science topics; persists at 1-month delay.

## Why this sub-routine exists

When a chapter explicitly names a misconception, denies it, and then states the accepted view ("Many people believe X, but in fact Y, because Z"), readers learn the correct concept measurably better than from chapters that present only the correct concept. The mechanism (Knowledge Revision Components / KReC framework): naming the misconception activates its representation in working memory; the correction then competes with it; the correction wins activation priority and the misconception is *suppressed* (not erased — it can re-emerge later without ongoing reinforcement).

The dissociation matters: this effect lives in the **situation model**, not the textbase (see `references/calibration.md`). Textbase rehearsal of the correct definition does not suppress the misconception; the explicit refutation structure does. This is why this sub-routine is invoked specifically on conceptual chapters.

When the chapter is *not* written in refutation form, the reader can generate the structure themselves; that generation is the learning move this sub-routine specifies.

## When to invoke

Invoke when **all** of the following hold:

- chapter is classified `conceptual` (or `argument-driven` with conceptual-change content)
- the topic carries documented widespread misconceptions in the user's likely audience (biology, physics, statistics, economics, philosophy, social cognition, history-of-science topics typically qualify; pure derivations and reference material typically don't)
- the user has any prior exposure to the topic (PKA dump shows non-empty content)

Do **not** invoke when:

- the topic is procedural-only (recipes, lookups, syntax)
- the topic is politically or identity-laden (climate policy, vaccines, contested values) — the refutation structure can backfire on identity-laden belief; for these topics, use the argument-reading sub-routine instead (`references/methods/argument-reading.md`) which scaffolds steelman engagement
- the user has zero PKA on the topic — there are no prior misconceptions to refute; the standard PDP loop is enough

## The 3-phase protocol

### Phase 1 (Plan) — Misconception elicitation

After the standard PKA dump and prediction, add one explicit step:

> "이 주제에 대해 흔히 잘못 알려진 생각 2-3개를 적어줘 — 본인이 갖고 있을 수도 있는 것, 또는 다른 사람들이 흔히 잘못 안다고 본인이 느끼는 것."

Capture as `prior_misconceptions: [<m1>, <m2>, <m3>]` in the chapter note Phase 1 section.

If the user can name fewer than 2 misconceptions, prompt for one more by surfacing common-misconception categories for the topic (cause/effect direction reversal, scale confusion, single-cause-thinking, anthropomorphism, present bias, etc.). At light intensity, one misconception is acceptable.

If the user genuinely cannot name any (very low PKA), this sub-routine doesn't apply for this chapter — fall back to the standard PDP loop.

### Phase 2 (Tutor) — Contradiction marking

During reading, the user marks any passage where the chapter explicitly contradicts a prior misconception. Use the PIMEQ `E` (Evaluate) prefix with a specific format:

> "E: 나는 [misconception-1을 짧게]로 알았는데, 저자는 [the chapter's correction]을 명시. 그 이유는 [the chapter's reason / mechanism]."

If the chapter does not explicitly refute the misconception but the corrected view can be inferred from the chapter content, mark it `I` (Infer) with the same format. The point is to name the contrast between prior belief and chapter content, not to require the chapter to be written in refutation form.

If the chapter contradicts a misconception that the user did **not** list in Phase 1 (the chapter surfaced a misconception the user didn't know they had), add it to `prior_misconceptions` retroactively and mark it `E` — this is high-value learning and should be logged.

### Phase 3 (Calibrate) — Refutation paragraph generation

After Step 2a (textbase recall) and Step 2b (situation-model transfer), add one obligatory writing step:

> "각 misconception에 대해 짧은 refutation 단락 작성: '나는 X라고 알고 있었는데, 실제로는 Y. 그 이유는 Z.' 챕터 §locator 명시."

Capture as:

```yaml
refutation_paragraphs:
  - misconception: "<m1 from Phase 1>"
    correction: "<chapter's view>"
    reason: "<the mechanism the chapter gives>"
    chapter_locator: "§3.2"
    confidence: 0-1   # user's self-rated confidence in the corrected view
  - misconception: "<m2>"
    ...
```

Each refutation paragraph becomes a high-value retrieval card automatically — these are the items most worth re-engaging at the 1-week and 1-month spaced retrieval points (see `references/calibration.md` § "Spaced re-engagement"). They are also strong situation-model transfer prompts: a 1-month spaced retrieval can ask "what would you say to someone who claimed [misconception]?"

## Robustness and limits

- **Robust across delay**: the effect persists at 1-month follow-up, so the spaced retrieval items derived from refutation paragraphs do real work over time.
- **Robust across age and prior knowledge**: works at most expertise levels.
- **Backfire risk on identity-laden topics**: do not invoke on politically or morally contested topics (use the argument-reading sub-routine instead).
- **Latent persistence**: because misconceptions are suppressed not erased, the 1-week and 1-month re-engagement matter. Without re-engagement, the original misconception can re-emerge.

## Cross-references

- `references/calibration.md` — Step 2a/2b structure; refutation paragraphs feed the SM transfer score
- `references/methods/argument-reading.md` — alternative for politically contested topics
- `references/annotation-typology.md` — `E` prefix usage during Phase 2 contradiction marking
- `references/book-types.md` — conceptual book type classification

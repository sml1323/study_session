# Medium Policy — 4-axis decision tree

When invoked: at plan phase, decide what reading medium the user should default to for this chapter. Medium effects on comprehension are real but not "screen bad" simple — the variance is captured by 4 axes, and the decision-tree below makes the right tradeoff visible.

This file is referenced from `SKILL.md` § "The PDP master loop" (PLAN PHASE) and from `references/pdp-loop.md`.

## The 4 axes

A medium choice is a 4-coordinate, not a binary:

1. **Device class**
   - **Paper / e-ink**: paper-like reading; eye fatigue low at long sessions
   - **Tablet (paginated)**: paper-like reliably; in current evidence, tablet under paginated mode is not measurably worse than paper
   - **Computer screen / phone (any mode)**: small but consistent comprehension penalty vs paper, especially when content is expository and time is constrained

2. **Navigation**
   - **Paginated**: discrete page turns; good for deep comprehension
   - **Scrolling**: continuous; the dominant interface-side culprit for screen comprehension penalty in current network-meta evidence; aggressive chunking required if used

3. **Content type**
   - **Expository / textbook / scientific paper**: medium effect strongest; paper / e-ink / paginated tablet preferred
   - **Narrative (novel, essay, biography)**: medium-neutral; do not impose paper friction

4. **Pacing**
   - **Self-paced / time-loose**: medium effect smaller
   - **Time-pressured (exam prep, deadline, "I have to finish this today")**: medium effect amplified ~3× in current evidence; if screen reading is unavoidable, force closed-book recall every page or every chunk and treat self-reported understanding as systematically over-estimated

## The decision tree

Pick the first row that matches:

| Situation | Recommended medium | Notes |
|---|---|---|
| High-stakes expository + time pressure (exam prep, deadline reading) | **paper** or **paginated tablet** or **e-ink** | If screen unavoidable, activate `force_chunk_boundary_recall: true` and treat self-report as over-estimate (calibrate against `textbase_recall_coverage`, not user's "I got it") |
| Long-form learning expository (≥ 90 min planned session) | **e-ink** preferred, then **paginated tablet** or **paper** | LCD visual fatigue accumulates over long sessions; e-ink reduces fatigue without comprehension penalty |
| Standard expository / textbook chapter, no special pressure | **paginated tablet** or **paper** | Computer scrolling PDFs allowed only with aggressive chunking (5-min chunks, mandatory chunk-boundary recall) |
| Narrative chapter (novel, essay, memoir, biography) | **medium-neutral** — pick whatever the user prefers | Genre cap on `paragraph_capture` already applies (see `references/generative-prompts.md`); medium friction does not need to be added |
| Preview, capture, search, low-stakes browsing | **phone / laptop OK** | Not the deep comprehension pass; if the chapter later reaches deep mode, switch medium |

## Specific rules

- **Scrolling PDFs are deprecated** as a default for deep comprehension. If the user is on a scrolling-PDF reader for an expository chapter, surface the option to switch to paginated mode (most modern PDF readers have a setting). If they decline, force chunk size to 5 minutes and require chunk-boundary recall.
- **Tabbed reading / multi-window reading** during a deep-comprehension chapter is the worst case in current evidence. Surface and ask the user to close other tabs / put phone away for the chunk.
- **`workflow_purpose: retention | reuse | resurfacing`** (from chapter note frontmatter) interacts with medium: retention-first benefits most from paper/e-ink; reuse-first can tolerate computer screen with copy-out workflow; resurfacing-first depends on whatever surfaces well in the user's spaced-repetition tool.
- **Calibration warning**: digital reading produces over-confidence on self-reports (g ≈ +0.2 paper vs screen on calibration alone). When the chapter was read on screen, the chapter_complete decision must rely on `situation_model_transfer_score` measured in Phase 3, not on the user's self-rated understanding.

## What this policy is *not*

- Not "paper good, screen bad". The narrative finding above shows medium is genre-conditional and pacing-conditional. Imposing paper on a narrative chapter the user wants to read on Kindle is friction without benefit.
- Not a vendor recommendation. The decision tree picks the *class* of medium; the user picks the device.
- Not a hard ban. If the user only has a laptop and is reading an expository chapter, the answer is not "don't read" — it is "read with chunk-boundary recall and treat self-report as over-estimate."

## Frontmatter field

The chapter note records the medium decision:

```yaml
medium:
  device: paper | e-ink | tablet | laptop | phone
  navigation: paginated | scrolling
  content_type: expository | narrative | reference
  pacing: self-paced | time-pressured
  force_chunk_boundary_recall: true | false   # auto-true on screen + time-pressured
```

## Cross-references

- `references/generative-prompts.md` — `interim_recall` (chunk-boundary recall, mandatory at intensity ≥ standard)
- `references/calibration.md` — situation-model transfer scoring; the gate that screen-reading self-reports cannot substitute for
- `references/book-types.md` — narrative ↔ expository orthogonal axis (used to fill `content_type` here)
- `references/l2-mode.md` — L2 medium policy intersects with vocabulary scaffolding (separate decision)

# Medium Policy — 4-axis decision tree + 4-cell pagination × device-class matrix

When invoked: at plan phase, decide what reading medium the user should default to for this chapter. Medium effects on comprehension are real but not "screen bad" simple — the variance is captured by 4 axes, and the decision-tree below makes the right tradeoff visible.

The R10 v3 patch (and earlier rounds) framed medium choice as a 4-axis decision. The R11 v4 patch sharpens this: Clinton-Lisell & Litzinger 2025 (network meta n=56 / 79 effect sizes) localizes the screen-vs-paper effect to **scrolling specifically**, with paginated digital reading dropping to g = 0.03–0.12 vs paper (no reliable difference). Frontiers 2025 distractions meta (n=32 studies / 124 experiments) shows distraction interference is medium-invariant once a distractor is present (Hedges' g = −0.64) — the e-ink advantage is upstream from display physics, in **distraction availability**. The v4 reframing is therefore: collapse the messy device taxonomy into a **2-axis (pagination_mode × device_class) 4-cell matrix** and surface the cell label (recommended / allowed / triage-only) at plan time.

This file is referenced from `SKILL.md` § "PDP spine" (PLAN step) and from `references/pdp-loop.md`.

## The 4 axes (background — the matrix below runs first)

The matrix in the next section is the load-bearing decision; these four axes are the variance it compresses, kept here as background:

1. **Device class** — paper / e-ink and paginated tablet read paper-like; computer screen / phone (any mode) carry a small but consistent comprehension penalty vs paper, worst on expository content under time pressure.
2. **Navigation** — paginated (discrete page turns) is good for deep comprehension; scrolling is the dominant interface-side culprit and needs aggressive chunking if used.
3. **Content type** — expository / textbook / paper: medium effect strongest, prefer paper / e-ink / paginated tablet. Narrative: medium-neutral, do not impose paper friction.
4. **Pacing** — time-pressured reading (exam prep, deadline) amplifies the medium effect ~3× in current evidence; if screen reading is unavoidable, force closed-book recall every page/chunk and treat self-reported understanding as systematically over-estimated.

## The decision tree

Pick the first row that matches:

| Situation | Recommended medium | Notes |
|---|---|---|
| High-stakes expository + time pressure (exam prep, deadline reading) | **paper** or **paginated tablet** or **e-ink** | If screen unavoidable, activate `force_chunk_boundary_recall: true` and treat self-report as over-estimate (calibrate against `textbase_recall_coverage`, not user's "I got it") |
| Long-form learning expository (≥ 90 min planned session) | **e-ink** preferred, then **paginated tablet** or **paper** | LCD visual fatigue accumulates over long sessions; e-ink reduces fatigue without comprehension penalty |
| Standard expository / textbook chapter, no special pressure | **paginated tablet** or **paper** | Computer scrolling PDFs allowed only with aggressive chunking (5-min chunks, mandatory chunk-boundary recall) |
| Narrative chapter (novel, essay, memoir, biography) | **medium-neutral** — pick whatever the user prefers | Genre cap on `paragraph_capture` already applies (see `references/generative-prompts.md`); medium friction does not need to be added |
| Preview, capture, search, low-stakes browsing | **phone / laptop OK** | Not the deep comprehension pass; if the chapter later reaches deep mode, switch medium |

## The 4-cell matrix (R11 v4 — load-bearing summary)

The decision-tree above is still correct; this matrix is the v4 simplification that should run **first**. The 4 axes collapse to 2 load-bearing axes when you compress device-class (paper / e-ink / tablet / laptop / phone) into "single-purpose" vs "multi-purpose" and navigation into "paginated" vs "scrolling".

| | **single-purpose device** (Kindle, reMarkable, Supernote, Boox-strict, paper book) | **multi-purpose device** (laptop with apps, tablet with apps, phone, Boox-with-apps installed) |
|---|---|---|
| **paginated** | **RECOMMENDED** for high-stakes long-form. Within ~0.03–0.12 SD of paper (Clinton-Lisell 2025 network meta, scrolling-removed condition). Distraction-availability also blocked (Frontiers 2025 upstream mechanism). | **ALLOWED with caveat**. Pagination preserves comprehension; distraction-availability survives. Surface to user: "close other tabs / put phone away for the chunk." Activate `force_chunk_boundary_recall: true`. |
| **scrolling** | **ALLOWED with caveat**. Scrolling is the dominant interface-side culprit but single-purpose blocks distraction. Useful for narrative or low-stakes chapters where scrolling is unavoidable (e.g., a Kindle PDF that doesn't paginate well). Activate `force_chunk_boundary_recall: true`. | **TRIAGE-ONLY recommendation**. paper-vs-digital effect ~0.35–0.48 SD (Clinton-Lisell 2025 scrolling condition) AND distraction availability uncapped. Recommended use: orientation / search / preview only, with user-encouraged medium switch before deep-reading entry. User can override and continue on this cell; if they do, log `medium_recommendation_overridden: true` and force chunk-boundary recall. |

Capture both axes into chapter note frontmatter (`medium.pagination_mode`, `medium.device_class`). The **cell label** itself (recommended / allowed-with-caveat / triage-only) goes into `medium.recommendation` so the long-term `medium_used × actual_score` cross-tab can be computed by compose mode.

> ⚠ **Patch source caveat — `study-session-skill-patch-v4-2026-05-03.md` (Round 11)**: Clinton-Lisell 2025's g 0.03–0.12 (paginated) and 0.35–0.48 (scrolling) bands are direct citations. Frontiers 2025 g = −0.64 (distraction) is a direct citation. The cell labels (recommended / allowed-with-caveat / triage-only) are **operational placeholders** chosen to make the matrix actionable — they reflect the skill's risk tolerance, not a published threshold. Replace with R12-validated thresholds when available.

### Writable e-ink caveat (reMarkable / Boox Note Air / Kindle Scribe)

No comprehension or retention RCT exists for writable e-ink as of R11; Android-open devices (e.g. Boox) re-introduce the distraction-availability the matrix's "single-purpose" cell is supposed to block. The skill therefore treats writable e-ink as **single-purpose if app installs are restricted**, multi-purpose otherwise. The user declares this at plan time as `medium.device_class_attestation: single-purpose-restricted | multi-purpose`.

## Specific rules

- **Scrolling PDFs are deprecated** as a default for deep comprehension. If the user is on a scrolling-PDF reader for an expository chapter, surface the option to switch to paginated mode (most modern PDF readers have a setting). If they decline, force chunk size to 5 minutes and require chunk-boundary recall.
- **Tabbed reading / multi-window reading** during a deep-comprehension chapter is the worst case in current evidence. Surface and ask the user to close other tabs / put phone away for the chunk.
- **`workflow_purpose: retention | reuse | resurfacing`** (from chapter note frontmatter) interacts with medium: retention-first benefits most from paper/e-ink; reuse-first can tolerate computer screen with copy-out workflow; resurfacing-first depends on whatever surfaces well in the user's spaced-repetition tool.
- **Calibration warning**: digital reading produces over-confidence on self-reports (g ≈ +0.2 paper vs screen on calibration alone). When the chapter was read on screen, the chapter_complete decision must rely on `situation_model_transfer_score` measured in Phase 3, not on the user's self-rated understanding.

## Frontmatter field

The chapter note records the medium decision:

```yaml
medium:
  device: paper | e-ink | tablet | laptop | phone
  pagination_mode: paginated | scrolling                          # v4 axis (Clinton-Lisell 2025 mechanism)
  device_class: single-purpose | multi-purpose                    # v4 axis (Frontiers 2025 mechanism)
  device_class_attestation: single-purpose-restricted | multi-purpose | n/a   # for writable e-ink with optional app installs
  navigation: paginated | scrolling                                # legacy alias for pagination_mode
  content_type: expository | narrative | reference
  pacing: self-paced | time-pressured
  recommendation: recommended | allowed-with-caveat | triage-only  # cell label from the v4 matrix
  force_chunk_boundary_recall: true | false                        # auto-true on screen + time-pressured OR allowed-with-caveat cell
```

## Cross-references

- `references/generative-prompts.md` — `interim_recall` (chunk-boundary recall, mandatory at intensity ≥ standard)
- `references/calibration.md` — situation-model transfer scoring; the gate that screen-reading self-reports cannot substitute for; v4 adds `medium_used × actual_score` cross-tab to long-term metrics
- `references/book-types.md` — narrative ↔ expository orthogonal axis (used to fill `content_type` here)
- `references/l2-mode.md` — L2 medium policy intersects with vocabulary scaffolding (separate decision)
- `references/translation-mode.md` — translation-read mode (`--llm-translate`) is **orthogonal** to medium choice. The 4-cell pagination × device-class matrix applies independently of source-language choice; a user can read a Korean translation on any cell, and the cell's `force_chunk_boundary_recall` recommendation still applies (and is in fact extra load-bearing in translation mode, where chunk-boundary recall is the sole protected learning event)
- `references/ai-policy.md` — AI usage and medium choice are independent axes; both captured at plan

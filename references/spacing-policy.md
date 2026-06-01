# Spacing Policy — Opt-in Commitment, Behavioral Retrieval, Deadline Anchor, Self-Diagnostic

The cadence numbers in this file are *guidelines* for the user to set their own floor against, not hard rules.

When invoked: the chapter just transitioned to `phase-3-pending` or `phase-3-complete`, and the skill is composing the spaced re-engagement schedule. This file defines what the skill **invites the user to commit to** (opt-in, default off), how it counts a retrieval (behavior, not exposure), how it anchors discipline against intrinsic-motivation drift, and how it surfaces the FCI/BEMA-style self-diagnostic that tells the user whether the protocol is working at all.

## Shift 1 — Opt-in cadence commitment (default off)

### Daily floor commitment device (opt-in)

At the moment a chapter enters `phase-3-pending` or `phase-3-complete`, the skill **offers** a daily floor commitment and writes it to `books.yml` *only if the user opts in*. The default is no commitment device — the user decides whether the cadence is helpful in their context.

```yaml
daily_floor:
  chapter: arq/4
  committed_at: 2026-04-30
  target_distinct_days: 5            # the user must execute at least one retrieval on N distinct calendar days
  retrievals_per_day_min: 2          # at least M retrievals per executed day
  window_end: 2026-05-14             # 14 days from commitment, hard end
  status: active                     # active | met | missed
```

The numbers (`target_distinct_days`, `retrievals_per_day_min`, `window_end`) are agreed with the user at plan mode and stored on the chapter, not computed from a hard-coded table.

> ⚠ The per-book-type cadence numbers below are conservative placeholders, not RCT-grounded — surface them as placeholders and let the user set their own floor against their `external_deadline` rather than treating the defaults as authoritative.

| Book type | distinct days (placeholder) | retrievals/day min (placeholder) | window (placeholder) |
|---|---|---|---|
| methodology | 5 | 2 | 14 days |
| problem-driven | 7 | 3 | 21 days |
| conceptual | 5 | 2 | 14 days |
| argument-driven | 4 | 2 | 14 days |
| math-proof-heavy | 7 | 2 | 21 days |
| reference | n/a | n/a | n/a (lookup mode skips) |

*All rows above: evidence: placeholder. These trace to no published cadence study; they are first-cut conservative numbers chosen so the floor is non-trivial without being punishing.* **Replace with the user's own commitment** or with R11-validated cadence whichever lands first.

Surface the commitment to the user at chapter close, in user language:

> "Ch.4 closes. Would you like to commit to a retrieval floor? Suggested: 2 retrievals on each of 5 distinct days within the next 14 days (opt in or set your own). The skill will count behavior (closed-book recall executed), not exposure (book reopened). If you commit and the window slips, you'll see the catch-up cost on the next session."

This is the YeckehZaare 2025 daily-floor finding: 94.7% of learners fail to space spontaneously when only suggested. A commitment device with explicit cadence and behavioral counting captures the gap — but the device itself is most effective when the user chose it, so opt-in. *[evidence: observational — YeckehZaare 2025 is the source for the 94.7% spontaneous-fail finding; commitment-device-as-fix is operational.]*

### Cross-chapter touch points

When the skill schedules a new chapter (Ch.N+1) into Phase 1, it inserts a **prior-chapter retrieval** for one or more older chapters into the Phase 1 opening. This is a default behavior the user may decline. The chapter selected is the oldest one in the spaced re-engagement queue that is due. *[evidence: rct-strong — interleaved retrieval is well-supported (Karpicke 2008/2011, Roediger & Butler 2011); the specific "Phase 1 opening" placement is operational.]*

```yaml
phase_1_opening:
  prior_chapter_retrievals:
    - chapter: arq/2
      due_type: 1w
      prompt: "Without looking, name the 3 most important things from Ch.2."
    - chapter: arq/3
      due_type: 1d
      prompt: "What was Ch.3's key argument?"
```

Two retrievals max per opening — more than that re-creates form fatigue.

## Shift 2 — Behavioral retrieval, not exposure

A retrieval **counts** only when the user has executed a closed-book recall (the chapter is not visible; the user has typed or spoken the recall and the skill has captured it). Hartwig & Malain 2022 and similar app-instrumented studies find that "opened the e-book", "scrolled through the chapter PDF", or "tapped the flashcard" are not learning behaviors — they are exposure behaviors that the user mistakes for retrieval. *[evidence: observational — Hartwig & Malain 2022 app-instrumentation; converged with other behavior-vs-exposure findings.]*

The skill's counting rule:

| Action | Counts as retrieval? |
|---|---|
| User opens chapter PDF / EPUB | No (exposure) |
| User opens chapter note file | No (exposure) |
| User scrolls past their highlights | No (exposure) |
| User executes closed-book recall on prompt; recall captured | **Yes** |
| User attempts a transfer question on a NEW scenario; answer captured | **Yes** |
| User self-tests on their generated exam Qs without looking | **Yes** |
| User says "yeah I remember it" without typed/voiced recall | No (self-report; not behavior) |

When `daily_floor.status` is computed, the count uses only the rows that count.

## Shift 3 — External deadline anchor

The intrinsic-motivation default ("you'll do it because you want to learn") is a known failure mode at scale (Reich 2019, MOOC platform retention). At the moment a chapter enters spaced re-engagement, the skill prompts the user for an **external deadline anchor**:

> "What is the external deadline that this chapter is in service of? (semester end / cohort exam / mock exam / your own self-set test on YYYY-MM-DD / boss review on...)"

The deadline is captured in the chapter note frontmatter:

```yaml
external_deadline:
  type: semester-end | mock-exam | self-set | cohort-exam | other
  date: 2026-06-15
  description: "med school 4th-year mock 2 (KMLE prep)"
  social_anchor: "study group meets every Monday"   # optional but encouraged
```

**Deadline-aware gap derivation.** When `external_deadline.date` is known, do NOT use the fixed 1d/1w/1m `due_type` defaults. Instead derive the schedule from the retention interval: the optimal first gap scales with how long the material must be retained (Cepeda et al. 2008). Set the **first** gap to ~10–20% of the time-to-deadline, then expand each subsequent gap from there (roughly 1.5–2× the prior gap), capping the last retrieval at the deadline itself. Example: a 60-day time-to-deadline gives a first gap of ~6–12 days, then ~15d, ~30d, with the final review landing on the deadline. The 1d/1w/1m `due_type` defaults apply **only when `external_deadline` is null** (no retention interval to scale against).

If the user refuses to set a deadline, log `external_deadline: null` and surface the consequence:

> "No external deadline set. Reich 2019 found that intrinsic-motivation-only learning has high attrition at scale; the skill cannot enforce the daily floor against a deadline that does not exist. The catch-up cost message will be omitted."

When the user enters a session and the daily floor is on track, surface nothing. When the floor is at risk:

> "Daily floor at risk: 1 of 5 distinct days completed in the first 6 of the 14-day window. To meet by 2026-05-14, you need [N] retrievals across the remaining [M] days. The catch-up curve is in the chapter note."

The catch-up cost is computed as: how many retrievals per remaining day are needed to meet the floor. Surfacing the curve visibly is the anchor.

**Social commitment, when available**: if the user named a study group or cohort in the deadline anchor, surface a once-per-week prompt: "Has your study group reviewed Ch.4? Bringing the chapter to the group is a retrieval event." This is opt-in support; the skill does not message the group itself.

## Shift 4 — FCI/BEMA-style self-diagnostic

After the chapter has had a spaced retrieval at +1 month (or after the external deadline arrives, whichever is sooner), the skill runs a **self-diagnostic** on the chapter's normalized gain. Rather than judging the chapter against an absolute external effect-size band, compare it **within-learner**: against the running median of this learner's own normalized gains across their completed chapters. Absolute FCI/BEMA bands (e.g. 0.30–0.40) are physics-education cohort norms and do not transfer cleanly to one solo learner's chapters; the learner's own running median is the meaningful baseline. The Colvin 2014 norm-of-self-study-expectation framing still applies — the learner needs an objective benchmark rather than a subjective sense of progress — but here the benchmark is their own track record, not a borrowed cohort band.

For each completed chapter, the skill computes:

```yaml
self_diagnostic:
  metric: normalized_gain                              # post-pre / (max-pre)
  pre_score: 0.35                                      # Phase 1 expectations / misconceptions baseline
  post_score: 0.78                                     # +1 month spaced retrieval coverage on the same items
  normalized_gain: 0.66                                # (0.78 - 0.35) / (1 - 0.35)
  learner_running_median: 0.58                         # median normalized_gain across this learner's completed chapters
  diagnosis: above_self                                # below_self | near_self | above_self
```

The running median needs at least ~3 completed chapters to be meaningful; until then report the raw gain and note that no within-learner baseline exists yet. Classify a chapter as `below_self` only when it is a clear self-outlier (e.g. meaningfully below the running median, not within normal chapter-to-chapter noise).

| Diagnosis | What it means | What the skill says |
|---|---|---|
| `near_self` | Gain is around this learner's usual. | "Chapter X's normalized gain is 0.56 — about your usual (running median 0.58). No protocol change recommended." |
| `above_self` | Gain is above this learner's usual. | "Chapter X's normalized gain is 0.74 — above your usual (median 0.58). The protocol is doing more than your baseline here; if you want to scale back, this is a chapter where you could." |
| `below_self` | Gain is a clear outlier below this learner's usual. | "Chapter X's normalized gain is 0.31 — below your usual (median 0.58). **This is below your own track record, not a verdict on you** — consider re-entering Ch.X with a different micro-task, refutation-text mode, or a worked-example-first variant. See suggested re-entry options." |

The framing matters: a below-self gain surfaces as **below your usual — try a different micro-task**, not as the learner failing. The skill's response is to suggest re-entry options (different micro-task, different mode), not to escalate effort. The within-learner median absorbs the self-blame and turns it into actionable protocol change.

## Anti-patterns

- ❌ **"Suggesting" spacing without offering the commitment device.** Suggestion-only fails 94.7% of learners (YeckehZaare 2025); offer the opt-in daily-floor commitment device with cadence + window as part of the suggestion. If the user declines, log it but do not enforce — the device's effectiveness depends on the user choosing it.
- ❌ **Counting exposure as retrieval.** Opening the file is not a learning event. Only closed-book recall captured by the skill counts.
- ❌ **Assumed intrinsic motivation.** Without an external deadline anchor, the floor is enforceable only against the user's wish to learn; that is the failure mode.
- ❌ **Judging a chapter against a borrowed absolute band.** Absolute FCI/BEMA bands (e.g. 0.30–0.40) are physics-education cohort norms; for one solo learner, compare within-learner against their own running median instead.
- ❌ **Below-self as learner blame.** Re-frame as "below your usual — try a different micro-task," with re-entry suggestions; do not push the user to "try harder."
- ❌ **Stacking 5+ retrievals on a single day to "catch up".** The window's `retrievals_per_day_min` is a floor, not a target; piling many retrievals onto one day defeats the spacing mechanism. Catch-up is more days, not more per day.

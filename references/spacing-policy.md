# Spacing Policy — Forced Cadence, Behavioral Retrieval, Deadline Anchor, Self-Diagnostic

When invoked: the chapter just transitioned to `phase-3-pending` or `phase-3-complete`, and the skill is composing the spaced re-engagement schedule. This file defines what the skill **commits the user to** (not "suggests"), how it counts a retrieval (behavior, not exposure), how it anchors discipline against intrinsic-motivation drift, and how it surfaces the FCI/BEMA-style self-diagnostic that tells the user whether the protocol is working at all.

The four shifts vs. an earlier suggestion-based spacing module:

1. Spacing schedule is **forced cadence**, not "suggested" intervals.
2. Retrieval is counted as a **behavior** (closed-book recall executed), not an **exposure** (e-book reopened).
3. Discipline is anchored to an **external deadline**, not assumed-intrinsic motivation.
4. The skill periodically **self-diagnoses** whether the protocol is producing learning at the expected effect-size band, and surfaces failure to the user as a protocol problem (not a learner-blame problem).

## Shift 1 — Forced cadence (not suggested intervals)

### Daily floor commitment device

At the moment a chapter enters `phase-3-pending` or `phase-3-complete`, the skill writes a **daily floor commitment** to `books.yml`:

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

> ⚠ **Patch source caveat — `study-session-skill-patch-v3-2026-04-30.md` (Round 10) names the daily-floor commitment device but does NOT specify per-book-type cadence numbers.** The defaults below are conservative placeholders pending Round 11 RCT-grounded values. When operating, surface the placeholder to the user and let them set their own floor against their `external_deadline` instead of treating the defaults as authoritative.

| Book type | distinct days (placeholder) | retrievals/day min (placeholder) | window (placeholder) |
|---|---|---|---|
| methodology | 5 | 2 | 14 days |
| problem-driven | 7 | 3 | 21 days |
| conceptual | 5 | 2 | 14 days |
| argument-driven | 4 | 2 | 14 days |
| math-proof-heavy | 7 | 2 | 21 days |
| reference | n/a | n/a | n/a (lookup mode skips) |

These placeholders trace to no published cadence study; they are first-cut conservative numbers chosen so the floor is non-trivial without being punishing. **Replace with the user's own commitment** or with R11-validated cadence whichever lands first.

Surface the commitment to the user at chapter close, in user language:

> "Ch.4 closes. Floor: 2 retrievals on each of 5 distinct days within the next 14 days. The skill will count behavior (closed-book recall executed), not exposure (book reopened). On a missed window, you'll see the catch-up cost on the next session."

This is the YeckehZaare 2025 daily-floor finding: 94.7% of learners fail to space spontaneously when only suggested. A commitment device with explicit cadence and behavioral counting captures the gap.

### Cross-chapter touch points

When the skill schedules a new chapter (Ch.N+1) into Phase 1, it inserts a **prior-chapter retrieval** for one or more older chapters into the Phase 1 opening. This is automatic; the user does not opt in. The chapter selected is the oldest one in the spaced re-engagement queue that is due.

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

A retrieval **counts** only when the user has executed a closed-book recall (the chapter is not visible; the user has typed or spoken the recall and the skill has captured it). Hartwig & Malain 2022 and similar app-instrumented studies find that "opened the e-book", "scrolled through the chapter PDF", or "tapped the flashcard" are not learning behaviors — they are exposure behaviors that the user mistakes for retrieval.

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

If the user refuses to set a deadline, log `external_deadline: null` and surface the consequence:

> "No external deadline set. Reich 2019 found that intrinsic-motivation-only learning has high attrition at scale; the skill cannot enforce the daily floor against a deadline that does not exist. The catch-up cost message will be omitted."

When the user enters a session and the daily floor is on track, surface nothing. When the floor is at risk:

> "Daily floor at risk: 1 of 5 distinct days completed in the first 6 of the 14-day window. To meet by 2026-05-14, you need [N] retrievals across the remaining [M] days. The catch-up curve is in the chapter note."

The catch-up cost is computed as: how many retrievals per remaining day are needed to meet the floor. Surfacing the curve visibly is the anchor.

**Social commitment, when available**: if the user named a study group or cohort in the deadline anchor, surface a once-per-week prompt: "Has your study group reviewed Ch.4? Bringing the chapter to the group is a retrieval event." This is opt-in support; the skill does not message the group itself.

## Shift 4 — FCI/BEMA-style self-diagnostic

After the chapter has had a spaced retrieval at +1 month (or after the external deadline arrives, whichever is sooner), the skill runs a **self-diagnostic** that compares the chapter's measured outcomes against an expected effect-size band. This is the Colvin 2014 norm-of-self-study-expectation framing: students need to know whether their effort is producing the standard gain or not, and the answer must be calibrated against an objective expected band, not against their subjective sense of progress.

For each completed chapter, the skill computes:

```yaml
self_diagnostic:
  metric: normalized_gain                              # post-pre / (max-pre)
  pre_score: 0.35                                      # Phase 1 expectations / misconceptions baseline
  post_score: 0.78                                     # +1 month spaced retrieval coverage on the same items
  normalized_gain: 0.66                                # (0.78 - 0.35) / (1 - 0.35)
  expected_band: { low: 0.30, high: 0.40 }             # FCI/BEMA-style expected normalized gain
  diagnosis: above_band                                # below_band | in_band | above_band
```

| Diagnosis | What it means | What the skill says |
|---|---|---|
| `in_band` (0.30–0.40) | Protocol is working as expected. | "Chapter X's normalized gain is 0.34 — in the expected band. No protocol change recommended." |
| `above_band` (> 0.40) | Protocol is producing above-expected gain. | "Chapter X's normalized gain is 0.55 — above the expected band. The protocol is doing more than baseline; if you want to scale back, this is a chapter where you could." |
| `below_band` (< 0.30) | Protocol is **not** working on this chapter for this learner. | "Chapter X's normalized gain is 0.18 — below the expected band. The protocol is not producing the expected gain. **This is a protocol issue, not a learner issue** — re-enter Ch.X with a different micro-task, refutation-text mode, or a worked-example-first variant. See suggested re-entry options." |

The framing matters: a below-band gain surfaces as **the protocol failed, not the learner failed**. The skill's response is to suggest re-entry options (different micro-task, different mode), not to escalate effort. This is what Colvin's "norm of self-study expectation" gives the learner: an objective benchmark that absorbs the self-blame and turns it into actionable protocol change.

## What the chapter note carries

Add to frontmatter:

```yaml
daily_floor:
  target_distinct_days: 5
  retrievals_per_day_min: 2
  window_end: 2026-05-14
  retrievals_executed:                # behavior-counted; exposure does not appear here
    - { date: 2026-05-01, count: 2, types: [chunk_recall, transfer_attempt] }
    - { date: 2026-05-03, count: 3, types: [chunk_recall, self_test, transfer_attempt] }
  status: active                      # active | met | missed
external_deadline:
  type: mock-exam
  date: 2026-06-15
  description: "med school 4th-year mock 2"
  social_anchor: "study group Mondays"
self_diagnostic:
  metric: normalized_gain
  pre_score: 0.35
  post_score: 0.78
  normalized_gain: 0.66
  expected_band: { low: 0.30, high: 0.40 }
  diagnosis: above_band
  computed_at: 2026-05-30
```

## Anti-patterns

- ❌ **"Suggesting" spacing.** The default of suggestion-only fails 94.7% of learners; replace with a daily-floor commitment device with cadence + window.
- ❌ **Counting exposure as retrieval.** Opening the file is not a learning event. Only closed-book recall captured by the skill counts.
- ❌ **Assumed intrinsic motivation.** Without an external deadline anchor, the floor is enforceable only against the user's wish to learn; that is the failure mode.
- ❌ **Single-cohort effect-size assumptions.** The expected band (0.30–0.40 normalized gain) is from FCI/BEMA literature; learner populations vary. The skill surfaces the band as guidance, not as a verdict on the learner.
- ❌ **Below-band as learner blame.** Re-frame as a protocol failure with re-entry suggestions; do not push the user to "try harder."
- ❌ **Stacking 5+ retrievals on a single day to "catch up".** The window's `retrievals_per_day_min` is a floor, not a target; piling many retrievals onto one day defeats the spacing mechanism. Catch-up is more days, not more per day.

## Cross-references

- `references/calibration.md` — Phase 3 mechanics; spaced retrieval log fields
- `references/note-taking-policy.md` — refusal list and reframe map; spacing is one of the recommended-set moves
- `references/methods/hint-escalation.md` — paraphrase gate; behavior-not-exposure is the same principle (time-on-hint as behavior)
- `references/state-schema.md` — `phase-3-pending` / `phase-3-complete` transitions that trigger commitment-device write

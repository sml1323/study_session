# Review Routing — Natural-Language Triggers, --review Flags, and Status-Based Branching

When invoked: the user opens a session expressing intent to *review* an already-touched chapter rather than start a new one. This file defines the UX contract layer between the surface trigger (natural language or `--review` flag) and the underlying behavior (which mode runs, which Phase 3 sequence kicks in, whether the chapter status branches into spaced-retrieval vs full calibrate vs in-chapter recap).

Evidence labels: see `references/evidence-labels.md`. The branch logic is `operational-heuristic` (chosen for actionability); the underlying mechanisms it routes to (Phase 3 calibrate, spaced retrieval, conversion, recap) carry their own evidence tags in their respective references.

## Trigger surfaces

The skill accepts two trigger surfaces. Both resolve to the same routing logic.

### Natural-language triggers (loose match)

The skill enters review-routing when the user's prompt expresses review intent. Non-exhaustive examples:

- "ARQ Ch.4 복습하자"
- "어제 거 다시 보자" / "어제 학습 리뷰"
- "복습 퀴즈"
- "Polya Ch.3 review"
- "Feynman Ch.1 spaced retrieval"
- "review the chapter I closed yesterday"
- "let's re-engage with Spivak Ch.5"

Heuristic: any prompt naming a *chapter the user has already touched* (i.e., the chapter exists in `books.yml` with a non-`null` status) AND a review verb (복습 / review / re-engage / 다시 / spaced retrieval / 리뷰 / quiz) triggers review-routing. If the chapter is *new* (no `books.yml` entry), the verb is ignored and the prompt is routed to the normal plan-phase entry.

When the natural-language trigger is ambiguous (e.g., "study this", chapter not named), the skill asks: "Which chapter and how — review, calibrate, or resume?" before routing.

### `--review` flag (explicit)

For unambiguous routing, the user can use an explicit flag form:

- `--review --book <slug> --chapter <N>` — route this specific chapter through review-routing.
- `--review --due` — process every chapter currently due on the spaced-retrieval queue (oldest first; default cap of 1 per opening to avoid form fatigue).
- `--review --scope chapter` — when multiple chapter-level activities would normally interleave (e.g., chunk-boundary recall + spaced retrieval on a different chapter), restrict to chapter-scope only.

`--review --due` is the most common shape after onboarding: the user opens a session, runs `--review --due`, and the skill picks the oldest queued chapter and routes it by its status.

## Branch logic (status-based)

Once review-routing is entered for a specific chapter, the branch is determined by the chapter's `status` field in `books.yml`. Each branch leads to a different behavior.

| Chapter status | Branch | What runs | Reference |
|---|---|---|---|
| `phase-3-pending` | **Phase 3 calibrate** | Full Phase 3 sequence (confidence + score_prediction → textbase recall → SM transfer → gap + calibration_health → Feynman → self-test) as the session's opening. Stale-calibrate downgrade applies if `now − phase_2_ended_at > 5 days`. | `references/calibration.md` |
| `phase-3-pending` AND `now − phase_2_ended_at > 5 days` | **Stale 3-question quiz (downgrade)** | 3-question retrieval quiz instead of full Phase 3. Log `phase_3_downgraded_to_quiz: true`. Quiz feeds the spaced-retrieval log, not the Phase 3 metrics. | `references/calibration.md § "The delay" stale rule` |
| `phase-3-textbase-only` | **Step 2b retry** | Step 2b (situation-model transfer) only — textbase recall does not get redone; the chapter is held at `phase-3-textbase-only` until Step 2b lands. | `references/calibration.md § Step 2b` |
| `phase-3-complete` / `applied` / `scheduled` | **Spaced retrieval** | Check `review_queue`; if a 1d / 1w / 1m entry is due, run a short prior-chapter-retrieval prompt and capture into `chapter_metrics[N].spaced_retrievals[]`. If nothing is due, surface the upcoming due date and offer a voluntary recall pass. | `references/spacing-policy.md` (queue), `references/calibration.md § Phase 4` |
| `in-progress` | **Section recap + next-chunk recommendation** | Show the last covered section, propose the next pending section as the next chunk (per `references/section-tracking.md` § resume rules), and re-enter tutor mode at the chunk boundary. Not a "review" in the spaced-retrieval sense — the chapter is mid-read. | `references/section-tracking.md`, `references/pdp-loop.md § TUTOR` |
| `phase-2-pending-conversion` | **Conversion first** | The chapter is read end-to-end but raw PIMEQ marginalia or bare highlights still need to be converted to source / concept / retrieval cards. Run conversion before any review-style move; surface the conversion gate. | `references/annotation-typology.md § Conversion`, `references/state-schema.md` |
| no `books.yml` entry | **Not a review — fall through to plan phase** | The user thinks they're reviewing but the chapter has not been touched. Route to plan phase and ask whether they meant a different chapter. | `references/pdp-loop.md § PLAN PHASE` |

### `confirm_next_chapter` interaction

If the chapter being reviewed has `confirm_next_chapter: true` set (B1 split — see `references/calibration.md § B1 split`), the review-routing branch runs **but** prompts the user for confirmation before queueing the next chapter for advance. Specifically:

- For the `phase-3-complete` / `scheduled` branch (spaced retrieval): the skill surfaces "Last Phase 3 showed `calibration_health: over_confident` with gap > 30. Continue with the spaced retrieval pass and confirm chapter advance, or run a fresh Step 2b retry first?"
- For the `in-progress` branch: no special handling (the chapter has not yet reached Phase 3).
- For the `phase-3-pending` branch: the Phase 3 sequence runs normally; the new `calibration_health` and `confirm_next_chapter` are recomputed at the end.

## Multiple-due handling

When `--review --due` finds more than one chapter due, the rule mirrors the multiple-pending-chapters rule in `references/calibration.md § Multiple pending chapters`:

- Default: **oldest-due first, one review per opening**. Do not stack multiple full calibrates or full retrieval passes into a single warmup — that re-creates the form-fatigue failure mode.
- If a chapter is stale beyond 5 days, downgrade it to the 3-question quiz and run a full Phase 3 / spaced retrieval on the next chapter still in window.
- Surface the queue at session start: "Ch.4 (1d due), Ch.7 (1w due), Ch.2 (5+ day stale). Run Ch.4 as warmup; defer Ch.7 to next session; downgrade Ch.2 to quiz?"

The user can override and run more than one in a single session; log `multiple_reviews_same_session: true` so the form-fatigue trend is visible.

## Logging

Every review-routed session logs:

```yaml
review_routing:
  trigger: natural-language | flag                  # which surface fired
  trigger_text: "ARQ Ch.4 복습하자"                 # verbatim if natural-language
  resolved_book: arq
  resolved_chapter: 4
  resolved_status: phase-3-pending                  # status at time of routing
  branch: phase_3_calibrate                         # name of the matched branch
  downgrade_applied: false                          # true if stale-calibrate downgrade fired
  confirm_next_chapter_surfaced: true               # true if the B1 flag triggered a prompt
```

This goes into the chapter note's session block, not into `books.yml` (which stays metadata-only — see `references/state-schema.md`).

## Anti-patterns

- ❌ **Routing every "study" prompt through review-routing.** Review intent requires either a verb signal (복습 / review / re-engage) or the explicit `--review` flag. "Study Ch.5" without those is plan phase, not review.
- ❌ **Stacking multiple full Phase 3 calibrates in one session.** Default is one per opening; form fatigue compounds fast on calibrate.
- ❌ **Treating `--review --due` as a queue drain.** It picks one due chapter, not all of them. Stacking is opt-in via repeated calls.
- ❌ **Routing a `phase-2-pending-conversion` chapter to spaced retrieval.** Conversion is the prerequisite; spaced retrieval on raw marginalia under-scores the chapter.
- ❌ **Bypassing `confirm_next_chapter: true` silently.** The flag exists to surface a confirmation prompt; review-routing must honor it or the B1 calibration-health signal becomes invisible.

## Cross-references

- `SKILL.md § When to invoke` — review natural-language triggers listed in the entry table
- `references/pdp-loop.md § RESOLVE context` — review-routing fires inside RESOLVE before the rest of the loop runs
- `references/calibration.md` — Phase 3 sequence, stale-calibrate downgrade, B1 split (`confirm_next_chapter`)
- `references/spacing-policy.md` — spaced-retrieval queue mechanics that the `phase-3-complete` branch consumes
- `references/section-tracking.md` — section-level resume that the `in-progress` branch uses
- `references/annotation-typology.md § Conversion` — the conversion step required by the `phase-2-pending-conversion` branch
- `references/state-schema.md` — canonical status enum that the branch logic switches on

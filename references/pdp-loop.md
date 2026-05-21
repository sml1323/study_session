# The PDP Master Loop — Detailed Pseudocode
<!-- TODO evidence-tag - see references/evidence-labels.md; this files thresholds/policies are not yet labeled -->

The pseudocode for the Pre-During-Post learning cycle. SKILL.md carries the spine (the 4 modes table + decision rules); this file carries the executable detail.

The loop is opinionated. If the user pushes to skip Phase 3, see the rationale at the bottom of this file.

```
ON skill_invoked(maybe_book, maybe_chapter, maybe_mode):

  RESOLVE context:
    read ~/study-journal/books.yml

    # Review-routing pre-check (B3 — see references/review-routing.md)
    # Triggered by natural-language review intent ("ARQ Ch.4 복습하자",
    # "어제 거 다시 보자", "복습 퀴즈") OR the --review flag.
    if user_prompt matches review-intent OR --review flag present:
      resolve target_book + target_chapter from prompt / flag args
      if no books.yml entry for target:
        fall through to plan-phase entry (not a review)
      else:
        switch on books.yml[target].status:
          phase-3-pending             → run Phase 3 calibrate (stale-downgrade if > 5d)
          phase-3-textbase-only       → run Step 2b retry only
          phase-3-complete / applied  → check review_queue; if due, run spaced retrieval;
            / scheduled                  else surface upcoming due date + offer voluntary recall
          in-progress                 → section recap + recommend next pending section
          phase-2-pending-conversion  → run conversion first; surface gate
        if books.yml[target].confirm_next_chapter == true:
          surface confirmation prompt before any chapter-advance recommendation
        log review_routing.{trigger, branch, downgrade_applied, confirm_next_chapter_surfaced}
        return from RESOLVE after the review pass (do not run plan/tutor for a new chapter
        in the same session unless user explicitly requests it; default cap 1 review per opening)

    SCAN for any chapters with status: phase-3-pending
    if any pending:
      pick the oldest by phase_2_ended_at
      if (now - phase_2_ended_at) > ~5 days:
        downgrade to retrieval quiz (see references/calibration.md § "The delay" stale rule)
      else:
        run calibrate as opening warmup, then proceed to the rest of RESOLVE
    determine current_book + current_chapter from args, last session, or user prompt
    open the chapter PDF/markdown via Read tool (or pages: range for large books)
    open the chapter note file (create if absent)
    determine current_phase (plan/tutor/calibrate) from chapter note state

    # Section-level resolution within the current chapter
    # (full spec: references/section-tracking.md)
    sections = book.chapter_structure[current_chapter].sections   # may be missing
    if sections is missing:
      run lazy mini-extraction on this chapter (PDF outline sub-entries, or
      first 1-2 pages, or ask the user to paste the section headers)
      save the result back into books.yml
    uncovered = [s for s in sections if s.status not in ("covered", "skipped")]
    if uncovered:
      next_section = uncovered[0]
      if next_section.status == "in-progress":
        recommend resuming next_section from where the previous chunk stopped
      elif next_section.status == "used-as-exercise":
        surface as learning debt; recommend that section's narrative ¶
        (closed-book recall + active margin notes) as the next chunk before any other move
      else:  # pending
        recommend starting next_section as a fresh chunk
      # If the user says "다음 phase 가자" / "Ch.X 끝났어" while uncovered exists,
      # interpret it as "next section within the current chapter", not phase-3
      # or next-chapter. Only honor a literal next-chapter request when uncovered
      # is empty OR the user explicitly accepts that the rest will be `skipped`.
    else:
      chapter is eligible for phase-3-pending transition / next-chapter prompt

  PLAN PHASE (if entering chapter for first time):
    classify book_type per references/book-types.md
      (also classify on the narrative ↔ expository orthogonal axis — see book-types.md)
    if book_type is "reference": switch to lookup mode, exit
    select session_pattern from book_type
    select medium policy per references/medium-policy.md
    elicit PKA (write what you know about this topic, 3 minutes)
    elicit prediction (what will the chapter argue/prove/teach)
    elicit goal_question (one specific question)
    generate expectations as 3 textbase + 2 situation-model items
      (textbase: "user can state X"; situation-model: "user can apply X to a NEW case where ...")
    generate misconceptions (2-3 wrong ideas commonly held)
    if book_type is conceptual: also elicit user's prior misconceptions on the topic
      (Phase 3 will check whether the chapter explicitly refuted them — see references/methods/refutation-text.md)
    if book_type is argument-driven: invoke argument-reading sub-routine
      (see references/methods/argument-reading.md — structure pass + argument map + IH prime)
    write all of the above into the chapter note Phase 1 section

  TUTOR PHASE (during reading):
    enforce chunk_size 5-10min (see references/generative-prompts.md interim_recall)
    for each chunk boundary (every 5-10 min of reading):
      30-60s closed-book recall of what the chunk just said (forward effect)
        pick recall_probe_schema for chapter.type from
          references/generative-prompts.md § recall_probe_schema
        label recall rows R1, R2, R3, ... (numeric only — append-only-safe across sessions)
        NEVER write R-P, R-I, R-M, R-E, R-Q — letter labels on recall rows are
          a structural attractor (across sessions the prefix part falls off and
          the surface form drifts); see references/annotation-typology.md
          § "Recall-table row labels" and § "Legacy migration"
      then active margin notes on the chunk (see references/annotation-typology.md):
        annotate AFTER recall, never before
        each note is short prose (one sentence); no enforced prefix at write time
        examples of constructive moves (Pressley & Afflerbach 1995):
          predict / infer / monitor (confusion flag) / evaluate / question
        respect 1-2 active margin notes per page cap
        categorization happens at chapter end (conversion contract), not at write time
      pick one of: concept_define / next_predict / monitoring_check
      ask the user
      receive answer
      reviewer move:
        identify which expectations are satisfied
        identify any misconception that fired
        give specific feedback (not generic praise — see "Things to avoid")
        if missing or wrong, escalate: pump → hint → prompt → assertion
        log hint level invoked (0-4)
      if section contains an argument: invoke ARQ extract (references/methods/arq.md)
      if section contains a problem: invoke Polya log (references/methods/polya.md)
      if user fails problem: invoke Newman error analysis (references/methods/newman.md)
      if section contains a proof: invoke proof-comprehension facets (references/methods/proof-comprehension.md)
    chapter end: graphic organizer construction (intensity ≥ standard) — references/annotation-typology.md
    chapter end: convert raw margin notes to source/concept/retrieval cards
      (post-hoc bucket per references/annotation-typology.md § "Conversion contract")

    # At chunk close: update section status (references/section-tracking.md)
    for each section touched in this chunk:
      if recall + active margin notes ran on the section's own narrative: status = covered
      elif section's prose was used as training material only:    status = used-as-exercise
      elif chunk ended mid-section:                               status = in-progress
      elif user explicitly skipped:                               status = skipped
    sync the Section progress block in the chapter note from books.yml

  WHEN reading complete (or session time up):
    save Phase 2 traces to chapter note
    set phase_2_ended_at: <ISO8601 now>
    # Chapter-completion gate (references/section-tracking.md):
    # Only set phase-3-pending when every section is `covered` or `skipped`.
    # If any section is `pending`, `in-progress`, or `used-as-exercise`,
    # leave chapter status as `in-progress` and surface uncovered sections to
    # the user. `used-as-exercise` is learning debt — recommend processing the
    # section's narrative ¶ as the next chunk before any phase advance.
    if all sections in (covered, skipped):
      set status: phase-3-pending
    else:
      keep status: in-progress
      surface uncovered/debt sections; do not offer phase-3 or next-chapter
    end session with: "Saved. Calibrate runs as the warmup of your next study
                       session — the gap between sessions is the delay that
                       retrieval-practice research calls for. No need to wait
                       around now."

  CALIBRATE PHASE (default: opening of the next session;
                   same-session opt-in only when user explicitly requests it
                   AND now - phase_2_ended_at >= 30 min):
    Step 1 — confidence_check (BEFORE recall):
      ask confidence (0-100) that the user can reproduce + apply the chapter
    Step 2a — textbase recall (decisive for textbase score):
      ask user to write a 1-page summary without looking
      capture as textbase_recall
    Step 2b — situation-model transfer (drives learning_passed):
      generate 1-2 transfer questions tailored to book type
        (templates in references/calibration.md § "Step 2b: situation-model transfer")
      ask user to answer without looking
      score each 0 / 0.5 / 1
    Step 3 — gap_calibration:
      open chapter; score textbase_recall_coverage and situation_model_transfer_score separately
      see references/calibration.md § "Coverage Rubrics"
    Step 4 — calibration gaps (B1 split, 2026-05-17):
      compute calibration_gap_abs = |score_prediction - actual_score|
      compute calibration_health enum from gap + sign (over_confident / under_confident / loose / well_calibrated / unknown)
      compute confidence_accuracy_gap = confidence - (SM * 100)    # legacy trend
    Step 5 — feynman_explain
    Step 6 — concept_map_build (optional but recommended)
    Step 7 — self_test_generate (3 questions + answers)
    set learning_passed = (situation_model_transfer_score >= book-type gate)
    set chapter_complete = learning_passed                            # B1: calibration health no longer hard-blocks
    set confirm_next_chapter = (calibration_gap_abs > 30)
    log textbase + SM + calibration_health separately to chapter note Phase 3 section

  APPLY (optional sub-step at session end — skip if user is out of time):
    prompt for one transfer attempt (different domain or example)
    log result as transfer_attempt: { domain, mapping, result }
    chapter is NOT incomplete without this; it is a bonus signal for far transfer

  COMPOSE (always; closes the session):
    auto-fill any remaining structured fields in chapter note
    update books.yml progress
    update chapter index

  SCHEDULE re-engagement:
    insert a retrieval quiz on this chapter into next 1-2 sessions
    link to spaced-repetition (1-day, 1-week, 1-month touch points)

  SURFACE health signals:
    if any session_health flag triggered (see references/failure-modes.md), tell the user
```

## Why the loop is opinionated

If the user says "skip Phase 3, I already understand it", explain (briefly, once per chapter): self-reports of understanding are systematically miscalibrated against delayed recall (this is the illusion-of-explanatory-depth pattern, amplified by AI mediation). Chapter completion must depend on delayed closed-book recall + a transfer attempt, not on "I got it." Calibrate exists specifically to break the illusion. If the user still skips, log it as `phase_3_skipped: true` so the trend is visible later.

## Why textbase and situation-model are scored separately

A reader can have a strong textbase (can reproduce what the chapter said) and a weak situation model (cannot apply it to a new case), or the reverse — both patterns are documented (Kintsch construction-integration model). Scoring only one signal makes the dissociation invisible. The skill scores both and gates `learning_passed` (≡ `chapter_complete`, post-B1) on the situation model because durable usable learning lives there. Calibration health is tracked separately as a metacognition signal that does not hard-block advancement. See `references/calibration.md` for the full rubrics, book-type thresholds, and the B1 split rationale.

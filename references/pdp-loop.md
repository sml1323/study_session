# The PDP Master Loop — Detailed Pseudocode

The pseudocode for the Pre-During-Post learning cycle. SKILL.md carries the spine (the 4 modes table + decision rules); this file carries the executable detail.

The loop is opinionated. If the user pushes to skip Phase 3, see the rationale at the bottom of this file.

```
ON skill_invoked(maybe_book, maybe_chapter, maybe_mode):

  RESOLVE context:
    read ~/study-journal/books.yml
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
      then PIMEQ annotation of the chunk (see references/annotation-typology.md):
        annotate AFTER recall, never before
        prefix every margin note with P / I / M / E / Q
        respect 1-2 PIMEQ notes per page cap
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
    chapter end: convert raw PIMEQ marginalia to source/concept/retrieval cards
      (see references/annotation-typology.md § "Conversion contract")

  WHEN reading complete (or session time up):
    save Phase 2 traces to chapter note
    set phase_2_ended_at: <ISO8601 now>
    set status: phase-3-pending
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
    Step 2b — situation-model transfer (gate for chapter_complete):
      generate 1-2 transfer questions tailored to book type
        (templates in references/calibration.md § "Step 2b: situation-model transfer")
      ask user to answer without looking
      score each 0 / 0.5 / 1
    Step 3 — gap_calibration:
      open chapter; score textbase_recall_coverage and situation_model_transfer_score separately
      see references/calibration.md § "Coverage Rubrics"
    Step 4 — confidence_accuracy_gap:
      compute confidence - (situation_model_transfer_score * 100)
    Step 5 — feynman_explain
    Step 6 — concept_map_build (optional but recommended)
    Step 7 — self_test_generate (3 questions + answers)
    set chapter_complete based on situation_model_transfer_score gate (book-type table in calibration.md)
    log textbase + SM separately to chapter note Phase 3 section

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

A reader can have a strong textbase (can reproduce what the chapter said) and a weak situation model (cannot apply it to a new case), or the reverse — both patterns are documented (Kintsch construction-integration model). Scoring only one signal makes the dissociation invisible. The skill scores both and gates `chapter_complete` on the situation model because durable usable learning lives there. See `references/calibration.md` for the full rubrics and book-type thresholds.

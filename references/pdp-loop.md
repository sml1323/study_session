# The PDP Master Loop — Detailed Pseudocode

The pseudocode for the Pre-During-Post learning cycle. SKILL.md carries the spine (the 4 modes table + decision rules); this file carries the executable detail.

The loop is opinionated. If the user pushes to skip Phase 3, see the rationale in references/calibration.md.

```
ON skill_invoked(maybe_book, maybe_chapter, maybe_mode):

  RESOLVE context:
    read ~/study-journal/books.yml

    RESOLVE review intent → branch per references/review-routing.md.

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

    gate per references/section-tracking.md (advance only when every section covered|skipped).

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
      then feedback micro-step (BEFORE the next chunk): surface the 1-2 items the
        user missed or got wrong on this recall (testing effect is amplified by
        feedback; an un-fed-back error consolidates the wrong form)
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
        give specific feedback (not generic praise — see SKILL.md § "Decision rules" rule 6, the canonical banned-praise list)
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
    Step 1 — elicit BEFORE recall (matches references/calibration.md Step 1):
      ask score_prediction: "이 챕터로 시험 보면 100점 만점에 몇 점?" (BEFORE recall)
        — this is the ±10pt gate input (Step 4 computes the gap from it)
      ask confidence (0-100) that the user can reproduce + apply the chapter
    full Phase-3 sequence + gate: references/calibration.md.

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

Rationale (delay, dissociation, skip-refusal): references/calibration.md.

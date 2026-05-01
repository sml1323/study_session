# Operational Examples — extended

SKILL.md keeps two illustrative examples (cold start, resume with calibrate-as-warmup). The remaining examples — covering ad-hoc problem solving, user-drafted analysis review, opt-in same-session calibrate, and stale-calibrate downgrade — live here.

## Example 3: Standalone Polya problem (not a book session)

User: "이 문제 같이 풀어보자: [Feynman exercise text]"

Action:
1. Not a book chapter — this is an ad-hoc problem.
2. Invoke Polya method directly: 4 steps + Schoenfeld 3-question sticky in Execute (see `references/methods/polya.md`, `references/methods/schoenfeld.md`).
3. Log to `~/study-journal/standalone/problems/YYYY-MM-DD-<slug>.md` (not a book chapter file).
4. If a transferable principle emerges, offer to extract to `evergreen/`.

## Example 4: Review of a user-drafted analysis (tutor → inline reviewer)

User: "이 ARQ 분해 검토해줘: [pasted analysis]"

Action:
1. Stay in **tutor** mode — the user already did the work; you skip the walk-through and go straight to the inline-reviewer sub-step.
2. Check against ARQ Core 7 (per `references/methods/arq.md`).
3. Give specific feedback: which fields are weak; which expectations missed; which fallacies were named without evidence.
4. Push back on generic phrasing.
5. Return a revised structure; user can accept or revise again.

## Example 5: Same-session calibrate (opt-in)

User: "Ch.4 calibrate 지금 하자" (immediately after Phase 2 ended)

Action:
1. Read `phase_2_ended_at` on the Ch.4 chapter note. Compute `now - phase_2_ended_at`.
2. If the gap is less than 30 minutes, refuse: "Phase 2 ended X minutes ago. Calibrate now reads working-memory residue, not durable encoding (retrieval-practice research; see `references/calibration.md`). Wait Y more minutes, or — recommended — let it run at next session opening (default)."
3. If the gap is >= 30 minutes, run the full Phase 3 sequence (textbase recall + situation-model transfer + gap + Feynman + self-test — see `references/calibration.md`).
4. Log the run with `calibrate_same_session: true` so the trend is visible later.

## Example 6: Stale calibrate downgrade

User: "오늘 학습" (5+ days since Phase 2 on Ch.4)

Action:
1. Read books.yml. Ch.4 is `phase-3-pending`; `phase_2_ended_at` was 6 days ago.
2. The window for "Phase 3 measures Phase 2 encoding" has closed. Surface the situation: "Ch.4 is 6 days past Phase 2. Coverage now is mostly long-term retention, not encoding quality. Run a 3-question quiz instead of full Phase 3?"
3. If user agrees: run a 3-question retrieval quiz (5 min): "Without looking, name the chapter's main claim, the strongest piece of supporting evidence, and one assumption you flagged."
4. Log `phase_3_downgraded_to_quiz: true`. Quiz coverage feeds the spaced retrieval log, not the original Phase 3 metrics.
5. Move to today's chapter.
6. If user wants the full Phase 3 anyway, run it but flag the result: "Coverage at this delay is contaminated by general decay; treat as retention signal, not Phase 2 calibration."

## Example 7: Multiple pending chapters at session start

User: "오늘 학습" (Ch.4 1 day pending + Ch.7 4 days pending)

Action:
1. Surface the queue: "Ch.4 (1 day pending), Ch.7 (4 days pending) are calibrate-ready. Default: oldest first — Ch.4 as warmup; Ch.7 deferred to next session. OK?"
2. If user accepts default: run Ch.4 calibrate as warmup; mark Ch.7 to lead next session.
3. If user wants both today: refuse stacking two full calibrates as one warmup (form-fatigue risk). Offer to (a) run Ch.4 full + Ch.7 3-question quiz, or (b) run Ch.7 full + Ch.4 3-question quiz, or (c) run Ch.4 full and skip the new chapter today (Ch.7 leads next session).
4. Whatever the choice, never run more than one full Phase 3 in a single warmup.

## Example 8: Conceptual chapter with prior misconceptions (refutation-text protocol)

User: "Behave Ch.3 시작" (book classified as conceptual + expository-leaning)

Action:
1. Plan phase: PKA dump, prediction, goal_question — standard.
2. **Additional**: explicitly elicit user's prior misconceptions on the topic before reading: "이 주제에 대해 흔히 잘못 알려진 생각 2-3개 — 본인이 갖고 있을 수도 있는 것 — 적어보자."
3. Tutor phase: read with PIMEQ. Mark with `E:` prefix any passage that explicitly contradicts a misconception the user wrote in step 2 ("저자가 X라고 생각했는데 실제로 Y라고 명시함"). See `references/methods/refutation-text.md`.
4. Phase 3: in addition to standard textbase + SM transfer, write a refutation-style paragraph: "나는 X로 알았는데, 실제로는 Y. 그 이유는 Z." This becomes a high-value retrieval card.

## Example 9: L2 sub-threshold reader — narrow reading sub-mode

User: "이 책 영어인데 1페이지에 모르는 단어 30%정도..." (≪95% coverage estimate)

Action:
1. L2 mode activates with `must-scaffold` policy (see `references/l2-mode.md` 95/98% two-tier).
2. Surface: "현재 coverage 미달 — 챕터 직진은 effortful + retention 손해. 같은 주제의 영어 텍스트 2-3개 narrow-read부터 추천. 동일 어휘 반복으로 본 책 들어갈 때 96-98% 도달 가능."
3. If user accepts: enter `narrow_reading_mode`. Skill helps the user identify 2-3 adjacent texts (Wikipedia article, blog post, related shorter article) on the same topic; reads them at light intensity (no Phase 3 required); accumulates a vocabulary note across texts.
4. Return to the original book after 2-3 narrow-reading texts; re-estimate coverage; proceed in L2 mode at appropriate tier.
5. If user refuses: proceed in `must-scaffold` (glossary obligatory; L1 paraphrase allowed; intensity capped at light).

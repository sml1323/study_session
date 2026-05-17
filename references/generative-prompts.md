# Generative Prompts — Verbatim Library
<!-- TODO evidence-tag - see references/evidence-labels.md; this files thresholds/policies are not yet labeled -->

Core-meaning preservation matters; "anticipate" / "predict" / "self-explain" elicit different cognitive moves than "summarize" / "review." Bisra et al. 2018 self-explanation meta (Bisra, Liu, Nesbit, Salimi & Winne, *Educ Psychol Rev*) reports overall self-explanation effect of approximately g=0.55; specific sub-conditions (including "anticipatory / predictive" prompts) are reported in the meta but the exact g=1.37 figure cited here is not verifiable against the published meta — *citation: unverified*. Use the canonical English wording from the source for the prompt, translate to Korean for delivery. *[evidence: observational — Bisra 2018 meta-analysis aggregates non-RCT and RCT studies; cited effect sizes are best treated as observational. Specific g=1.37 figure: placeholder until citation verified.]*

Each prompt has:
- **Purpose**: what learning move it serves
- **Verbatim (EN)**: the canonical English wording (from the source paper)
- **Korean delivery**: a faithful translation for the user
- **Trigger**: when to use it
- **Avoid**: common mistake versions

---

## Phase 1 — Pre-reading

### pka_dump

- **Purpose**: activate prior knowledge before reading; surface misconceptions early
- **Source**: Hattan, Alexander, Lupo 2024 RER — open-ended PKA most evidenced
- **Verbatim**: "Write everything you already know about [topic]. Three minutes. No editing."
- **Korean**: "[주제]에 대해 알고 있는 걸 다 써봐. 3분. 편집하지 말고."
- **Trigger**: first move of every Phase 1 (except reference type)
- **Avoid**: "Tell me your background" (closed); "What is X?" (yields textbook answer not personal knowledge)

### prediction

- **Purpose**: prime expectation; create prediction error opportunity
- **Source**: Pressley & Afflerbach 1995 (skilled-reader protocol)
- **Verbatim**: "Predict what this chapter will argue, prove, or teach."
- **Korean**: "이 챕터가 무엇을 주장/증명/가르칠지 예측해봐."
- **Trigger**: after pka_dump, before reading
- **Avoid**: "What do you think this is about?" (vague); accepting passive "I don't know" — push for at least one concrete prediction

### goal_question

- **Purpose**: focus reading, create retrieval cue
- **Source**: gradual release / inquiry pedagogy
- **Verbatim**: "What's one specific question you want answered by the end of this chapter?"
- **Korean**: "이 챕터를 다 보면 답을 얻고 싶은 구체적 질문 하나가 뭐야?"
- **Trigger**: after prediction
- **Avoid**: "What's your goal?" (too abstract)

---

## Phase 2 — During-reading

### chunk_size + interim_recall (mandatory at intensity ≥ standard)

- **Purpose**: prevent fluency-illusion accumulation across long unbroken reads; create forward-effect cueing for the next chunk.
- **Spec**:
  - default chunk_size = **5-10 min** of reading, broken at the nearest natural section boundary
  - 30-min unbroken reading blocks are auto-rejected at intensity ≥ standard (light may extend to 15 min)
  - at every chunk boundary: 30-60s **closed-book free recall** of what the chunk just said, *before* turning the page or scrolling forward
- **Verbatim** (instruction to user, at chunk boundary): "잠깐 멈춤 — 책 닫고 30초: 방금 읽은 내용 핵심을 입으로/머리로 다시 말해봐. 못 떠오르는 부분 있으면 그게 다음 chunk에서 다시 마주칠 portion."
- **Trigger**: every 5-10 min during reading; never skipped at standard or deep intensity.
- **Why this is non-negotiable**: chunk-boundary recall improves the *next* chunk's acquisition substantially, not just the current chunk's retention (forward effect). Skipping it loses not only the recall but also the next chunk's encoding boost.
- **Avoid**: silent re-reading at the chunk boundary instead of recall — this is the fluency-illusion failure mode the rule exists to prevent. The book stays closed during the 30-60s.

#### recall_probe_schema — book-type-specific probe categories (numeric labels)

The 30-60s closed-book recall is *free* in form but *structured* in what it probes for. A free recall (`"무엇 읽었지?"`) measures a noisy union of textbase + situation model + open-question; making the probe categories explicit lets the next chunk's encoding focus and the chapter-end calibrate compare like with like (Karpicke & Blunt 2011; Kintsch construction-integration). Without an explicit schema the recall row is a schema vacuum and the model fills it on the fly — historically by borrowing the PIMEQ first-letter (`R-P / R-I / R-M`), which then drifted across sessions into hallucinated "book-type-specific PIMEQ" tables. See `references/annotation-typology.md § Reserved letters` for the structural fix.

**Row labels are numeric: `R1`, `R2`, `R3`, ...** The descriptive word (proposition / paraphrase / setup / …) is a subscript on the label key (`R1_proposition`) and an aide-mémoire in the schema definition. In the *output* recall, write the label as `R1` (optionally with the category in parentheses: `R1 (proposition)`). Do **not** write `R-P`, `R-I`, `R-M`, `R-E`, `R-Q` — single-letter forms collide with margin PIMEQ prefixes and re-induce the hallucination. P/I/M/E/Q single letters are reserved for margin prefixes only.

Pick the schema by chapter `type` (and `genre_lean` where the table calls it out). The schema rows are the *targets* — actual recall rows are populated by the user; rows where the chunk has nothing relevant are omitted (`R4_equation` for a non-mathy chunk, etc.).

##### conceptual / conceptual-physics

```
recall_probe_schema:
  R1_proposition:   핵심 명제 한 문장 (저자의 주장; textbase 측정)
  R2_image:         결정적 이미지 한 개 (visualizable; situation model)
  R3_mechanism:     결과를 만든 메커니즘 (인과 사슬 1–2 단계; situation model)
  R4_equation:      수식/관계 — 있을 때만 (없으면 omit)
  R5_open_q:        청크가 남긴 본인의 자력 질문 — 선택 (R4 tow에서 surface 시)
```

##### methodology / argumentation (ARQ etc.)

```
recall_probe_schema:
  R1_paraphrase:    저자가 한 일을 본인 말로 한 문장 (method step or argument move)
  R2_inference:     본문에 명시 안 됐지만 함축된 한 점
  R3_open_q:        저자 framing 에 대한 본인 질문 / 반박 후보 — 선택
```

##### problem-driven

```
recall_probe_schema:
  R1_setup:         문제 setup 재진술 (조건 + 미지수)
  R2_strategy:      Polya 어느 단계까지 갔나 (understand / plan / execute / look-back)
  R3_block:         막힌 자리 — 있을 때 (Schoenfeld 3 Qs 로 surface)
```

##### math-proof-heavy

```
recall_probe_schema:
  R1_statement:     증명할 명제 재진술
  R2_structure:     증명 골격 (induction / contradiction / direct / case-on-which-variable)
  R3_load_bearing:  본인이 "그 줄 못 빠뜨린다" 고 판단한 핵심 1–2 줄
  R4_gap:           못 따라간 자리 — 있을 때 (Tao 7 moves 적용 후보)
```

##### argument-driven

```
recall_probe_schema:
  R1_thesis:        저자 결론 한 문장
  R2_reasons:       그 결론을 받치는 reason 2–3 개
  R3_assumptions:   명시 안 된 전제 (Browne–Keeley 5 종 중 surface 된 것)
  R4_open_q:        응답할 자리 — 선택
```

##### reference

PDP 미적용 책 — `recall_probe_schema` 없음. lookup 패턴에는 recall probe 자체가 부적합.

**Why numeric labels** — across the 6 schemas the row words (proposition / paraphrase / setup / statement / thesis) all begin with letters that overlap PIMEQ first-letters or near-overlap (P → Predict, I → Infer/Inference, M → Monitor/Mechanism). A single-letter row label is a structural attractor: shared first letter induces post-hoc generalization across sessions, and the recall row's *category word* gets re-labeled as a margin prefix in the *next* session. The `R1..R5` convention forces the surface label to be unambiguously a recall row, never a margin prefix. The category word lives as a subscript or parenthetical aide-mémoire, never as the row's primary label.

**Avoid**: writing `R-P`, `R-I`, `R-M`, `R-E`, `R-Q`; redefining PIMEQ as "Proposition / Image / Mechanism / Equation / Question" or "Paraphrase / Inference / Misconception / Example / Question" — these are recall *probe categories*, not the margin PIMEQ vocabulary. Margin PIMEQ is permanently `P=Predict / I=Infer / M=Monitor / E=Evaluate / Q=Question` regardless of book type. See `references/annotation-typology.md § Reserved letters` for the structural ban + anti-pattern fixtures.

### concept_define

- **Purpose**: targeted self-explanation in own words; high-leverage retention move
- **Source**: Bisra 2018 self-explanation meta — overall g~0.55; specific sub-condition g=0.87 for "conceptualize" *[citation: unverified — exact figure not confirmed against published meta]*
- **Verbatim**: "Define [concept] in your own words. Where does it apply? Give one example."
- **Korean**: "[개념]을 본인 말로 정의해봐. 어디에 적용되나? 예시 하나."
- **Trigger**: every new technical term in the section; every chapter section break
- **Avoid**: "Did you understand X?" (yields yes/no, no learning); "Summarize section 3" (verbatim summary, low utility)

### next_predict

- **Purpose**: anticipate next derivation/argument step before reading it
- **Source**: Bisra 2018 — anticipatory/predictive sub-condition reported in meta as larger than the overall g~0.55; "highest in meta" claim and exact g=1.37 figure *[citation: unverified — verify against published meta before next major release]*
- **Verbatim**: "Predict what the next [step / paragraph / proof line] will conclude. Why?"
- **Korean**: "다음 [단계/문단/증명줄]이 무엇을 결론낼지 예측해봐. 왜?"
- **Trigger**: at section break in conceptual/problem-driven; before each derivation step
- **Avoid**: revealing the answer in the prompt ("the next step uses calculus, what will it conclude?")

### monitoring_check

- **Purpose**: detect comprehension failure; force the user to slow on confusion
- **Source**: Pressley & Afflerbach 1995; Block & Pressley monitoring research
- **Verbatim**: "Paraphrase the last paragraph. If you can't, mark it as a confusion point."
- **Korean**: "마지막 문단을 본인 말로 다시 설명해봐. 못하면 confusion으로 표시."
- **Trigger**: every 2-3 paragraphs; when user has been quiet for 5+ min
- **Avoid**: "Are you following?" (yes-bias)

### paragraph_capture (selective, with genre cap)

- **Purpose**: capture a short row when one of four triggers fires — new concept introduced / argument transition / confusion / counterexample. Default cap: 5-10 captures per chapter; hard ceiling 15.
- **Genre cap (narrative chapters)**: a narrative-leaning chapter (chapter classified narrative on the orthogonal axis — see `references/book-types.md`) reduces the cap to **2-3 captures per chapter**. Detail fixation hurts narrative comprehension; theme + character/causal-chain tracking is the work, not micro-capture.
- **Genre cap (expository chapters)**: standard 5-10, hard ceiling 15.
- **Trigger**: only when one of the four triggers fires. Without an active trigger, do not record.
- **Avoid**: capturing on every paragraph (this is the form-fatigue failure mode); applying expository cap to narrative chapters.

### graphic_organizer_required (intensity ≥ standard)

- **Purpose**: integrate the chapter's local PIMEQ notes into one cross-chunk relational structure. Constructed organizers outperform consumed ones; the structure must come from the user.
- **Verbatim** (instruction to user): "Build one mind map / matrix / hierarchy / comparison table / sequence diagram for this chapter. 3-9 nodes. Edges have labeled relationships. Include at least one cross-reference to a prior chapter or concept."
- **Trigger**: chapter end, before chapter complete, on standard or deep intensity sessions. Light intensity may skip — in that case `chapter_complete` is restricted to `phase-3-textbase-only`.
- **Spec details**: see `references/annotation-typology.md` § "Graphic organizer requirement".
- **Avoid**: skill generates the organizer for the user (loses the construction effect); >9 nodes (over-decomposition).

### selective_annotation (PIMEQ — bare highlights are deprecated)

- **Purpose**: capture 1-2 *constructive* margin notes per page tagged with one of the five PIMEQ prefixes (Predict / Infer / Monitor / Evaluate / Question). Bare highlights — selecting passages without an accompanying generative move — do not improve comprehension and are deprecated as a default; if used, they must be converted at chapter end.
- **Verbatim** (instruction to user): "Mark up to 2 places on this page with a PIMEQ prefix — P (predict what comes next), I (infer the implication), M (monitor your confusion), E (evaluate / object), Q (question). Each note has the prefix and one short sentence. Bare highlights without text don't count."
- **Korean**: "이 페이지에서 PIMEQ prefix 붙인 마진노트 최대 2개 — P(다음 예측) / I(함의 추론) / M(모르겠음 표시) / E(평가·반박) / Q(질문). prefix + 한 문장. 그냥 색칠은 카운트 안 함."
- **Trigger**: at the chunk boundary, **after** the closed-book recall, never before. See `references/annotation-typology.md` for the order rule + per-prefix examples + the chapter-end conversion contract.
- **Avoid**: bare highlights as final state; annotating before recall (this is the dominant fluency-illusion pattern); more than 2 PIMEQ notes per page (signal of either over-dense chunk or revert to highlight-everything mode).

---

## Phase 3 — Post-reading (DELAYED — not immediate)

### closed_book_recall

- **Purpose**: actual learning measurement (vs self-report)
- **Source**: Karpicke & Blunt 2011 Science; Yang 2023 metacomprehension meta
- **Verbatim**: "Without looking at the chapter, write a 1-page summary covering: the main claim, the key concepts introduced, and one example. Take 10 minutes."
- **Korean**: "챕터를 보지 말고, 1페이지 요약을 써봐: 핵심 주장, 새로 등장한 핵심 개념들, 예시 하나. 10분."
- **Trigger**: at the start of Phase 3 — by default this is the opening of the *next* session (cross-session gap = the delay). Same-session opt-in only when `now - phase_2_ended_at ≥ 30 min`.
- **Critical**: do not let the user open the chapter file. If running in chat, take their typed recall before showing any chapter content.
- **Avoid**: shortening to less than 5 minutes; allowing peeking

### gap_calibration

- **Purpose**: compare self-recall to chapter; surface what was missed/wrong
- **Source**: Yang 2023 — calibration is what delayed retrieval repairs
- **Procedure**:
  1. After closed_book_recall is captured, open the chapter
  2. List expectations (from Phase 1) and check which were covered
  3. List concept_defines (from Phase 2) and check which appear in recall
  4. Identify wrong claims in recall (factual errors)
  5. Output: `{ missed: [...], wrong: [...], coverage: 0-1 }`
- **Korean delivery**: "비교해보자. 빠진 것: [...]. 틀린 것: [...]. Coverage: 65%."
- **Critical**: do not soften the gap. Yang 2023 r=0.18 means most users overestimate their understanding by 30-50%.

### confidence_check

- **Purpose**: measure confidence-accuracy gap; detect illusion of understanding
- **Source**: Aslanov 2025 (AI mediation amplifies IOED); Yang 2023
- **Verbatim**: "Before I show you the gap analysis: how confident are you that your recall is accurate? Give a percentage 0-100."
- **Korean**: "Gap 보여주기 전에 묻는다: 본인 recall이 정확하다고 얼마나 자신해? 0-100으로."
- **Trigger**: after closed_book_recall, BEFORE gap_calibration
- **Output**: `confidence_accuracy_gap = confidence - actual_coverage`. If > 30%, surface as illusion signal.

### feynman_explain

- **Purpose**: teaching expectancy + delivery effect; high-leverage delayed retention
- **Source**: Fiorella & Mayer 2014 — d=0.79 delayed for explanation with delivery
- **Verbatim**: "Explain [main concept] as if to a beginner who knows nothing about [field]. No jargon."
- **Korean**: "[핵심 개념]을 [분야]를 모르는 초보자에게 설명한다고 생각하고 말해봐. 전문용어 없이."
- **Trigger**: after gap_calibration, on the highest-stakes concept of the chapter
- **Output**: capture full explanation. Read for jargon leakage and gaps. Push back on anything that requires prior knowledge to follow.

### concept_map_build

- **Purpose**: organize chapter's concepts into a structure; relate to prior chapters
- **Source**: Nesbit & Adesope 2006 — g=0.82 for *constructing* (but only g=0.37 for studying provided maps)
- **Verbatim**: "Sketch a concept map: nodes for the main ideas, edges for relationships. Include at least one link to a concept from a prior chapter."
- **Korean**: "Concept map 그려봐: 노드는 핵심 아이디어, 엣지는 관계. 이전 챕터 개념과 연결되는 link 최소 1개."
- **Trigger**: after feynman_explain; optional but high-value
- **Output**: ASCII art, mermaid, or text description (link to file if user sketches in tool)
- **Critical**: must be user-constructed. Skill providing a map yields the lower-effect study mode.

### self_test_generate

- **Purpose**: user-generated retrieval items; test-generation effect; preview future retrieval
- **Source**: Roediger retrieval lit; user-generated items > provided items
- **Verbatim**: "Generate 3 questions an exam on this chapter would ask. Then answer them without looking."
- **Korean**: "이 챕터로 시험 보면 나올 만한 문제 3개 만들어봐. 그리고 보지 말고 답해."
- **Trigger**: end of Phase 3
- **Output**: `[{q, a, correct}]` triples; the q's get added to next session's spaced re-engagement queue

---

## Phase 4 — Cross-chapter / Apply

### prior_chapter_recall

- **Purpose**: spaced retrieval of prior chapter; opens next session
- **Source**: Cepeda 2008 spacing meta; retrieval-practice
- **Verbatim**: "Before we start chapter [N+1]: name the three most important things from chapter [N]. No looking."
- **Korean**: "Ch.[N+1] 시작 전에: Ch.[N]에서 가장 중요한 3가지를 답해. 보지 말고."
- **Trigger**: start of every session that follows a completed chapter
- **Output**: capture answer; compare to prior chapter's expectations; log result

### interleave_compare

- **Purpose**: connect related chapters / problem types; deep-structure recognition
- **Source**: interleaving meta (d=0.83-1.21 for math/physics)
- **Verbatim**: "How does this chapter's [main idea / method / problem type] relate to chapter [X]? Same? Different? Where do they diverge?"
- **Korean**: "이 챕터의 [핵심 아이디어/방법/문제 유형]이 Ch.[X]와 어떤 관계? 같음/다름? 어디서 갈리나?"
- **Trigger**: after a chapter completes that has a related prior chapter
- **Output**: a 3-5 sentence comparison; goes into both chapters' "cross-references" sections

### transfer_attempt

- **Purpose**: far transfer; the most stringent learning evidence
- **Source**: Bisra 2018 self-explanation meta — transfer sub-condition; specific g=0.53 figure *[citation: unverified]*. Bartz transfer literature is a general anchor, not a specific citation.
- **Verbatim**: "Apply [chapter's principle / method] to a different domain you know — work, hobby, prior reading. Where does it map? Where does it break?"
- **Korean**: "[챕터의 원리/방법]을 본인이 아는 다른 도메인 — 일/취미/이전에 읽은 것 — 에 적용해봐. 어디서 매핑되고 어디서 깨지나?"
- **Trigger**: end of every fully-completed chapter (Phase 1-3 done)
- **Output**: capture the transfer attempt + result (success / partial / failure / domain mismatch). Successful transfers become evergreen note candidates.

---

## Wording rules

1. **Use the verbatim source wording in the planning prompt to yourself**, then translate to Korean naturally for the user. Do not invent new wording.
2. **Avoid yes/no framing**. "Did you understand X?" yields yes-bias. Replace with "Define X."
3. **Avoid hedge language**. "Maybe try to predict..." weakens the prompt. Use imperative.
4. **Avoid generic praise after answers**. "Great!" / "잘했어요!" / "Perfect!" are banned. Replace with specific feedback (see `references/llm-tutor-design.md`).
5. **Push back on short answers**. If user gives 4-word concept_define, that's not a definition. "More — give me one full sentence and an example."

## Anti-patterns (DO NOT use)

- ❌ "Summarize the chapter." (verbatim summary, low utility per Dunlosky)
- ❌ "Reread the section." (low utility, default behavior we're trying to displace)
- ❌ "What's the main point?" (vague)
- ❌ "Highlight the important parts." (highlighting hurts inference per Dunlosky)
- ❌ "Tell me what you learned." (forces self-report; we want closed-book recall)
- ❌ "How confident are you that you understand?" — instead, measure with retrieval

## Quick sequence reference

A typical 45-min Phase 2 + Phase 3 (split across two sittings) hits:

```
Phase 1 (5 min):
  pka_dump
  prediction
  goal_question

Phase 2 (25-30 min, single block):
  every section break:
    concept_define OR next_predict (alternate)
    monitoring_check (every 2-3 paragraphs)
  selective_annotation (rolling, 1-2 per page)
  ARQ or Polya invocation as content calls for it

[END PHASE 2 — session ends; status: phase-3-pending]

Phase 3 (15 min, opens the *next* session by default):
  closed_book_recall
  confidence_check
  gap_calibration
  feynman_explain
  concept_map_build (optional, recommended)
  self_test_generate

Phase 4 (5 min, anytime after Phase 3):
  transfer_attempt
  schedule prior_chapter_recall for next session
```

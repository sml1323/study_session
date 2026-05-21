# Translation-Read Mode (`--llm-translate`)
<!-- TODO evidence-tag - see references/evidence-labels.md; this files thresholds/policies are not yet labeled -->

When the user reads a non-native book via a Korean translation (LLM-generated or officially published) instead of the original source, this mode activates. The goal is **concept learning at native-language reading speed**, accepting the nuance loss in exchange for completion velocity, while preserving the chunk-boundary recall that is the actual PDP learning event.

This mode is **mutually exclusive with L2 mode** (`references/l2-mode.md`). Activating one forces the other off. The rationale: L2 mode's paragraph loop steps 1-2 (read English original → write Korean summary from memory) is *undefined* when the user already reads Korean — there is no second language to translate from.

## Why this mode exists (the explicit trade-off)

The motivating case: a `methodology` book like Browne & Keeley *Asking the Right Questions* (`ARQ`) at L2 must-scaffold tier, where the user is pacing at ~10 hours per 10 pages. At that velocity the book cannot finish in a realistic time horizon, AND the chapter arc decays out of working memory between sessions (pace itself is a retention variable — too slow erodes the integrated mental model the book is teaching).

The exchange this mode accepts:

- **Preserved (80–90% of value)**: the book's *language-independent cognitive tools*. For ARQ this is the 10 critical questions (issue / reasons / ambiguous words / value & descriptive assumptions / fallacies / evidence / rival causes / statistics / omitted information / reasonable conclusions). For Polya it is the 4-step heuristic shape. These transfer through translation with negligible loss because they are *moves of thought*, not turns of phrase.
- **Sacrificed**: (a) the loaded-language register of meta-chapters that *are about* English rhetoric (ARQ Ch.5 on loaded language is the canonical example), (b) the side-effect of building L2 signal-word vocabulary (`therefore` / `however` / `nevertheless` etc.) that L2 mode's bucket B grants. Neither is the book's central learning goal.
- **Retained as non-negotiable**: chunk-boundary closed-book recall in the user's L1 (Korean). The PDP loop's learning event is recall, not reading. Reading a translation without recall is passive consumption and produces no measurable retention — that *is* the documented failure mode this mode must guard against.

This trade-off is *opinionated*: if the user is reading the book primarily *to* practice L2, this mode is the wrong tool — stay in L2 mode and accept the slower pace as part of the goal. This mode is for users whose *primary* goal is the conceptual content and whose L2 endurance is a velocity constraint, not a learning target.

## When this mode applies

Activate when any of the following:

- explicit flag: `/study-session --llm-translate` (book-level activation)
- book metadata in `~/study-journal/books.yml` has `translation_mode.active: true` (auto-inherited per chapter)
- explicit user signal mid-session: "이 책은 번역으로 읽고 있어", "ARQ는 한국어로 읽을게"

**Scope is book-level and persistent.** Confirm activation once per book; persist as `translation_mode: {...}` in book metadata. Do not re-prompt on every chapter — once a book is in translation mode, every chapter inherits.

## Activation flow (first time per book)

When `--llm-translate` is invoked on a book whose `translation_mode` is unset:

1. **Ask `translation_mode.source` once.** Two values: `llm` or `official_kr_translation`.
   - If `llm`: append a one-line warning about nuance flattening — LLM translation can flatten loaded register, idiomatic argument, and rhetorical hedge that the original carried. The 10 critical questions still transfer; the *texture* of the argument may not. The user is responsible for the translation quality (out of scope for this skill).
   - If `official_kr_translation`: no warning. Note the translator/edition in the book metadata if the user volunteers it.
2. **Ask `translation_loss_chapters` (optional).** Phrase: "이 책에서 영어 원문을 읽는 게 학습에 본질적인 챕터가 있어? (예: ARQ Ch.5는 loaded language가 *주제 자체*임. 모르면 빈 채로 둬도 됨 — 챕터 진입 시 다시 물어볼 수 있음.)" Accept a list of chapter numbers or empty.
3. **Force `l2_mode: off`** in the same `books.yml` edit (mutex enforcement). If `l2_mode` was previously `on`, log the transition in the activation note for traceability.
4. **Persist** to `books.yml` per `references/state-schema.md § translation_mode field`. Single edit.
5. **Confirm to user**: one short sentence — "Translation-read mode 활성화. 어휘 트래킹 끔, L2 paragraph loop 끔, chunk-boundary recall (한국어)은 유지."

Subsequent sessions on this book read `translation_mode` from `books.yml` and apply the protocol below without re-asking.

## Mutex with L2 mode — enforcement

The two modes cannot coexist. The enforcement points:

- **On `--llm-translate` activation**: force `l2_mode: off` in the same edit.
- **On book metadata write**: if both `translation_mode.active: true` AND `l2_mode: on` are about to be written, refuse the edit and surface the conflict to the user. They must pick one.
- **On session entry**: if a book somehow has both set (legacy state, manual edit), prefer `translation_mode.active: true` (the more recent mode), force `l2_mode: off`, and log the auto-correction.

The reason this matters: L2 mode's anti-pattern table forbids "translating the passage before the user attempts a summary" because that destroys the active processing the L2 paragraph loop is designed to preserve. Translation-read mode *deliberately accepts* that pattern because the user reads the translation *as their primary text*, not as a crutch around a primary English text. The two stances are incompatible and must not silently coexist.

## What turns OFF in this mode

| L2 mode feature | Translation mode | Reason |
|---|---|---|
| L2 paragraph loop step 1 (read English original) | OFF | User reads Korean as primary text |
| L2 paragraph loop step 2 (Korean summary from memory) | OFF | Undefined — there is no separate L1 to translate *into* |
| Vocabulary policy 7-vocab cap | OFF | No English-original vocabulary to track |
| A/B/C vocabulary bucket classification | OFF | Same — no source vocabulary |
| Glossary entries (`key_concept` bilingual rows) | OFF | Korean terms suffice; the book's named concepts can still be tracked in the chapter note's `concept_candidates` field via the regular path |
| L2 tier coverage estimate (95% / 98%) | OFF | Coverage is a property of reading the English source |
| Intensity caps by L2 tier (must-scaffold → light, assisted → standard) | OFF | The L2 caps existed because of English cognitive load. Reading translation removes that load — `light` / `standard` / `deep` are all user-choice |
| `narrow_reading_mode` sub-mode | OFF | Coverage-pushing intervention; irrelevant when reading translation |
| `er_session` / extensive-reading recommendation | OFF | Same — L2-coverage intervention |

## What stays ON (non-negotiable)

| Mechanic | Translation mode | Reason |
|---|---|---|
| **Chunk-boundary closed-book recall** (30–60 s in Korean) | MANDATORY | This is the PDP loop's learning event. Reading without recall = passive consumption. Skipping this *is* the mode's primary anti-pattern — see below. |
| Active margin notes (short prose; see `references/annotation-typology.md`) | per default mode | The constructive moves work in any language |
| Recall-probe table numeric labels (`R1`, `R2`, …) | per default mode | Same |
| ARQ depth 0–3 at argument-unit boundaries (or other method sub-routines) | per default mode | Methods are language-independent cognitive moves; ARQ's 10 critical questions apply to Korean text directly |
| Phase 3 calibrate (confidence → recall → SM transfer) | MANDATORY | Calibration measures concept learning, not language — and concept learning is what this mode targets |
| `chapter_complete` gate (SM transfer ≥ book-type threshold) | per default mode | Unchanged |
| `books.yml` edit discipline (one edit per session, allowlist) | per default mode | Unchanged |

## Paragraph loop (variant)

The L2 paragraph loop (7 steps) collapses to the standard PDP chunk loop because steps 1–2 disappear. For each chunk in a translation-read session:

```
1. user reads the chunk (Korean translation)
2. CHUNK BOUNDARY:
   a. close the book → 30–60 s closed-book recall (in Korean) → reopen
   b. 1–2 active margin notes (prose, in Korean) on what was just read
3. method sub-routine fires at its trigger (ARQ at argument-unit boundary, Polya
   at a problem, etc.) — invoke per its reference file in Korean
4. proceed to next chunk
```

The paragraph-role classification step (definition / example / claim / reason / transition / objection / summary) from L2 mode is **optional** in translation mode — invoke only when the chunk's structure is ambiguous to the user. In L2 mode it was mandatory because role-identification was scaffolding for the language barrier; without that barrier, structural fluency is the user's baseline.

## Citation policy

When citing the source mid-session or in the chapter note:

- **Cap: 0–1 English original quote per chapter** (L2 mode caps at 1–2).
- Format unchanged — see `references/citation-format.md` `quote_id` discipline.
- If a quote is included, it's because the original phrasing carries something the translation doesn't (e.g., a definitional sentence where the English word matters). Otherwise cite the translation directly without the bilingual block.
- Citing the translation: use the translator/edition for the citation anchor, not the original. Example:
  ```
  > "단순히 한 사건이 다른 사건보다 먼저 일어났다는 사실은 인과관계를 입증하지 못한다."
  > — Browne & Keeley (한국어판), p.142
  ```

The cap exists to prevent the chapter note from becoming a translation log; the chapter note's purpose is concept learning trace, not parallel-text record.

## Loaded-language / signal-word chapter alert

Some books have meta-chapters where the *topic itself* is English rhetoric — ARQ Ch.5 (loaded language) is the canonical example. For these chapters, reading the translation *flattens the chapter's own examples*: the chapter teaches "notice when an author uses 'massacre' vs 'incident'" and the translation has already made that choice for you.

**Alert mechanism**:

- At chapter entry, check `books.yml[<slug>].translation_loss_chapters`. If the current chapter number is in the list, fire the alert before plan-phase questions.
- Alert text (one short line): "이 챕터는 영어 원문 5–10분 stretch 권장 — loaded language가 챕터 주제 자체임. 번역으로는 챕터의 예시가 이미 한 번 압축된 상태로 들어옴."
- User can accept (continue in translation), partially accept (read the chapter's *examples* in English while keeping the body in translation), or override (full English). Log the choice in the chapter note as `translation_alert: {fired: true, response: accepted | partial | overridden}`.
- Do not block — the alert is informational. The user already knows the trade-off (they activated this mode deliberately).

If `translation_loss_chapters` is empty (user didn't fill it at plan time), no alert fires automatically. The user can still hand-flag a chapter mid-session ("이 챕터는 원문 좀 봐야겠어"), in which case the skill switches to L2 mode *for that chapter only* with explicit user confirmation — and logs the transition; the book-level `translation_mode` is not toggled off.

## Plan-phase additions

When a book has `translation_mode.active: true`, the standard plan-phase scope (per `references/book-types.md` and SKILL.md "The four modes") changes in one place:

- The L2-tier coverage question (95% / 98%) is **skipped** (irrelevant when reading translation).
- Everything else (book-type classification, medium pick, AI policy, expectations, learner profile) runs as usual.

## Anti-patterns (this mode)

The first and most dangerous:

- ❌ **Skipping chunk-boundary closed-book recall because "the user already read it in Korean."** This is the mode's primary failure: the entire trade-off of accepting translation depends on preserving the recall. Skip recall and the mode collapses to "read a book in your native language without learning from it." If the user pushes to skip recall ("recall 스킵하자, 어차피 한국어로 읽었어"), refuse with the rationale: the PDP loop's learning event is recall, not reading; reading in any language without recall produces no measurable retention. Offer to shorten the recall (compressed 20–30 s) but do not zero it.

Others:

- ❌ **Defaulting to L2 paragraph loop steps 1–2 in this mode.** Those steps are *undefined* here — there is no separate L1 to translate into. Use the standard PDP chunk loop.
- ❌ **Re-prompting `translation_mode.source` on every session.** Ask once at activation; persist; inherit.
- ❌ **Adding glossary entries for "key Korean terms"** when the user reads translation. The book's named concepts can go into the chapter note body or `concept_candidates`; the L2 glossary structure (bilingual rows with English term + page anchor) does not apply.
- ❌ **Citing the English original ≥ 2 times per chapter** when reading translation. Each English quote should justify itself (the original phrasing carries something the translation lost); routine citation back to English is a residue of L2 mode habits.
- ❌ **Silently switching to L2 mode mid-chapter when a passage is ambiguous.** If the user wants the original for a passage, ask once and log the local switch (`translation_alert: partial`); do not flip the book-level mode.
- ❌ **Treating the loaded-language chapter alert as a hard block.** It's an informational nudge; the user can decline and proceed in translation. Log the decline; do not refuse.

## Output language conventions

| Surface | Language |
|---|---|
| Tutor output | Korean (user's UI language) — no bilingual default |
| User output | Korean |
| Chapter note body | Korean. English original appears only inside the 0–1 quote cap, formatted per `references/citation-format.md` |
| Closed-book recall | Korean |
| Phase 3 calibrate prompts | Korean |
| Method sub-routine prompts (ARQ critical questions, Polya 4 steps, etc.) | Preserve the core meaning per the method's reference file; deliver in Korean. If the canonical wording's force comes from the English phrasing (e.g., a specific ARQ critical question), include the English phrase parenthetically once per chapter. |

## Interaction with other policies

- **Medium policy (`references/medium-policy.md`)**: orthogonal. The 4-cell pagination × device-class matrix applies independently — translation-read is about *source language*, medium is about *display / device*. A user can read an LLM translation on a paginated tablet (recommended cell) or on a phone (triage cell) with the medium recommendation logic unchanged.
- **AI policy (`references/ai-policy.md`)**: orthogonal. The 3 AI policy modes (scaffold / refuse-chat / refuse-all) apply independently. Note: if the `translation_mode.source` is `llm`, the *translation itself* is an upstream AI artifact, but that's a generation event outside the session — within the session, AI policy controls in-session AI use.
- **Spacing policy (`references/spacing-policy.md`)**: unchanged. Spaced retrieval intervals, daily-floor commitment, behavioral retrieval counting all apply.
- **Failure-mode signals (`references/failure-modes.md`)**: unchanged. The 6 failure-mode flags still fire; recall-skip in this mode trips the `surface` / `illusion` flags exactly as it would in any other mode.
- **Section tracking (`references/section-tracking.md`)**: unchanged. Section-level status enum and chapter-completion gate work identically.

## What this mode is *not*

- Not a Generalized "non-native language" mode. It is single-flag, English-source-only as of v1. Future generalization (`--de-translate`, `--ja-translate`, etc.) is deferred — start narrow.
- Not a hybrid (some chapters in translation, others in original). Scope is book-level. If the user wants per-chapter mixing, the activation flow's `translation_loss_chapters` field is the only supported "hybrid" — and even there, the local L2 switch is per-chapter opt-in, not a structural hybrid.
- Not a translation-quality measurement. The skill does not evaluate whether the translation is faithful. That is the user's responsibility — they chose the translation source.
- Not a permanent commitment. The user can deactivate (manually edit `books.yml`, or via future `--llm-translate=off` toggle) at any chapter boundary. Deactivation flips the book back to whatever its previous mode was (L2 or default).

## Cross-references

- `SKILL.md § Argument Parsing` — flag registration and bare-invocation behavior
- `references/l2-mode.md` — mutex partner; the anti-pattern table there carries the explicit exception clause for this mode
- `references/state-schema.md § translation_mode field` — book metadata schema; mutex with `l2_mode`
- `references/calibration.md` — Phase 3 mechanics unchanged; recall language is Korean (same as in L2 mode)
- `references/citation-format.md` — `quote_id` discipline; the 0–1 quote cap is enforced via this format
- `references/medium-policy.md` — orthogonal axis; medium decision is unchanged
- `references/methods/arq.md` — ARQ depth 0–3 applies directly to Korean text; the 10 critical questions are language-independent cognitive moves

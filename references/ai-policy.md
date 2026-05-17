# AI Policy — Single Source of Truth for AI Usage in the Skill

Evidence labels: see `references/evidence-labels.md`. The retention-loss range (11–20pp) below is `rct-strong` (8-study convergence); IOED diagnosis bands and the 3-mode structure are `operational-heuristic`.

When invoked: any session that involves an external AI tool (ChatGPT / Claude / NotebookLM / Gemini / Perplexity / Custom GPT / Claude Project / etc.). This file specifies the **3 allowed modes** (high-stakes default; user may override per chapter), the **per-chapter declaration mechanic**, the **per-turn AI usage log**, the **IOED counter gate**, and the **Newport strict-abstention path** as a first-class option.

This is the cross-cutting policy file referenced by SKILL.md. The per-template prompt format lives in `references/methods/scaffolded-ai-prompting.md`; the calibration gate lives in `references/calibration.md`. This file is the policy spine that the others hang on.

## The empirical floor

Eight studies (Bastani 2024 SSRN/SCALE — *not* "Bastani 2025 PNAS"; corrected per A2 fact-check / Barcaui 2025 n=120 / Benedek-Sziklai 2025 / Georgiou 2025 / Kosmyna MIT 2025 n=54 EEG / Lee Microsoft CHI 2025 n=319 / Aslanov 2025 n=102 / MDPI 2025) converge:

- **Free-form chat with an LLM during learning produces measurable retention damage**: −11 to −20 percentage points on delayed exam vs. no-AI controls. Bastani's Turkish HS RCT (SCALE 2024 working paper) showed practice +48% in-session but exam −17% after AI access removed. Barcaui's 45-day delayed test: 57.5% (ChatGPT) vs 68.5% (traditional). Benedek-Sziklai: −20pp on paper test vs prior years. *[evidence: rct-strong — 8-study convergence on the retention-loss direction and magnitude.]*
- **Scaffolded prompting neutralizes the damage**: Bastani's GPT Tutor (scaffolded prompt) condition showed no exam decline. MDPI 2025 reproduced on a different population: structured prompting reduced offloading + improved critical reasoning + improved reflection, while unguided AI did not. *[evidence: rct-strong — Bastani 2024 + MDPI 2025 are RCTs; the neutralization is the load-bearing claim.]*
- **Mechanism is consistent**: cognitive offloading + IOED amplification (Aslanov) + EEG brain-connectivity decline (Kosmyna) + retrieval skipping. The harm is not in *seeing* AI output; it is in *not having to do the load-bearing thinking* before/while reading the output. *[evidence: observational — Aslanov 2025 and Kosmyna 2025 are observational/quasi-experimental; the mechanism convergence is the strength.]*
- **Frontiers 2026 systematic review** (n=136 articles 2023-2025): no published intervention beats **no-AI** for high-baseline readers on retention or critical-thinking outcomes. Hybrid (AI + peer + instructor) beats AI-alone but does not flip the offloading sign for high-baseline readers. *[evidence: observational — systematic review aggregating mixed-design primary studies.]*

This skill therefore treats free-form chat as a **high-stakes default refusal** during deep-reading work (per-chapter user override allowed), treats scaffolded prompting as **damage-prevention not net gain**, and supports **strict abstention** as a first-class choice rather than an extreme position.

## The 3 modes

Every chapter declares one of these at plan time. Stored as `ai_policy.mode` in chapter note frontmatter. Cannot be changed mid-chapter (the lock is to keep `ai_policy` from contaminating that chapter's calibration metrics; user can change policy on the next chapter). *[evidence: operational-heuristic — the 3-mode partition is operational; the underlying choice (no-AI / orientation-only / scaffolded) is observational from practitioner ethnography (Newport, NotebookLM 2025-26, Konik 2025) + Bastani GPT Tutor.]*

### Mode 1 — `strict-no-ai` (Newport-style abstention)

No AI use during any phase of the chapter. The chapter's Phase 1 / 2 / 3 / 4 all happen with the learner's own cognition + chapter source + chapter notes.

**Why offered as a first-class choice**: Newport's *Slow Productivity* (2024) and his deep-reading critique frame AI summaries as actively bypassing two of the four cognitive rewards of slow reading — distraction-resistance training, comfort with ambiguity. For learners who treat reading as a cognitive resistance training practice (not just information acquisition), this is the right mode. The Frontiers 2026 evidence supports it: no published intervention beats no-AI for high-baseline readers.

**Default when**: high-baseline reader / high-stakes chapter / chapter is methodology or argument-driven / learner explicitly picks Newport stance.

### Mode 2 — `triage-only`

AI is allowed in Phase 1 (orientation / plan) and Stage 1-2 of `references/methods/code-reading.md` (orientation pass + strategic entry). AI is **prohibited** in deep reading (Stage 3 analytical loop), Phase 3 calibrate, and chapter compose.

The AI is used for "what is this chapter about?" / "what are the 5 most important things to read?" / "what's the prerequisite I should review first?" — never for "explain section 3 to me" or "summarize the whole chapter."

**Why this mode exists**: practitioner convergence (NotebookLM 2025-2026 ethnography, Konik 2025 method, CodeMap finding) shows AI is most useful for triage and orientation; it is least useful (and most damaging) for deep reading. The skill respects the practitioner pattern by allowing it scoped.

**Default when**: chapter is dense / paper / unfamiliar field / long codebase / learner needs to decide what to read deeply.

### Mode 3 — `scaffolded-only`

AI is allowed at any phase, but **only via the scaffolded prompting template** in `references/methods/scaffolded-ai-prompting.md`. Free-form chat is blocked at the dialogue level. Every AI turn is logged with the IOED follow-up question.

**Why this mode exists**: Bastani GPT Tutor + MDPI 2025 + Konik 2025 demonstrate that template-restricted AI use does not produce the offloading harm that free chat does. For learners who actively use AI (Konik-style) in their normal workflow, this mode keeps them aligned with the empirical floor without forcing them to abstain.

**Default when**: learner explicitly uses AI as part of their workflow and is committed to scaffolded discipline.

## Per-chapter declaration

At plan mode, the skill captures `ai_policy` into the chapter note frontmatter:

```yaml
ai_policy:
  mode: strict-no-ai | triage-only | scaffolded-only
  allowed_in_phases: []                       # auto-derived from mode
  declared_at: 2026-05-03T10:00:00+09:00
  rationale: "high-stakes mock exam prep — no AI"  # optional one-line user reason
```

The `allowed_in_phases` list is auto-filled:
- `strict-no-ai` → `[]`
- `triage-only` → `[plan, tutor-orientation]` (orientation = code-reading Stage 1-2)
- `scaffolded-only` → `[plan, tutor, calibrate, compose]` (any phase, but scaffolded template required)

`ai_policy.mode` is **locked for the lifetime of the chapter** as a strong default. Changing AI policy mid-chapter contaminates the chapter's calibration metrics. If the learner wants to change policy, they close the current chapter and the next chapter takes the new policy. User can override the lock per-chapter for a specific reason — log `ai_policy_mid_chapter_override: true` with the reason so the contamination is visible at audit time.

## Per-turn AI usage log

Every AI turn is captured (regardless of mode, even strict-no-ai if the learner violated and the violation must be logged):

```yaml
ai_use_log:
  - turn: 5
    timestamp: 2026-05-03T10:23:00+09:00
    tool: notebooklm | chatgpt | claude | gemini | perplexity | custom-gpt | claude-project | other
    mode_compliance: triage | scaffolded-prompting | free-chat | strict-violation
    query_summary: "asked NotebookLM for chapter 4 figure overview"
    ai_followup_question_attempted: true | false | n/a
    ai_followup_correct: true | false | n/a
    ioed_amplified: true | false | n/a
```

Two derived metrics that go to session_health and dashboard:

- `ai_turns_count`: total AI turns this chapter
- `scaffolded_ratio`: scaffolded-template turns / total AI turns (target ≥ 1.0; <1.0 means free-chat or violations occurred)
- `ioed_gap_avg`: mean of `ioed_amplified` events across AI turns (high = AI is creating illusion-of-understanding; low = AI is doing scaffold work)

## IOED counter gate (calibrate Phase 3)

When `ai_use_log` is non-empty for a chapter, Phase 3 Step 2b runs **twice** for the situation-model transfer question:

1. **First pass — no AI**: learner answers the transfer question with no AI tool open. Capture `sm_score_no_ai`.
2. **Second pass — with AI** (their normal usage pattern): learner answers the same question with whatever AI usage they normally would. Capture `sm_score_with_ai`.

The IOED gap is `|sm_score_no_ai − sm_score_with_ai| × 100`. Stored as:

```yaml
calibration:
  ioed_gap_pp: 18
  ioed_diagnosis: low | borderline | high   # ≤10 low, 11-30 borderline, >30 high
```

> ⚠ **Patch source caveat — `study-session-skill-patch-v4-2026-05-03.md` (Round 11) sets the IOED diagnosis bands (≤10 / 11-30 / >30) as first-cut placeholders.** Aslanov 2025 measured IOED amplification but did not publish a calibration band for individual learners. The bands here are conservative defaults pending R12 RCT-grounded values; treat as guidance, not authoritative thresholds. *[evidence: operational-heuristic — Aslanov 2025 is observational on IOED amplification; the band cutoffs are operational and chosen for actionability.]*

If `ioed_diagnosis: high`:
- Surface the gap to the learner in one short line ("AI is amplifying your sense of understanding by 30+pp; the next chapter goes strict-no-ai unless you object")
- Recommend the next chapter use `ai_policy.mode: strict-no-ai`
- Do not block chapter_complete on this metric — that is the score_prediction_gap's job (per `references/calibration.md` Step 4a). IOED is a *forward-looking* signal (next chapter) rather than a *blocking* signal (current chapter).

## Banned features (across all 3 modes, including scaffolded-only)

These features hallucinate or substitute for learning regardless of how the prompt is structured:

- **NotebookLM Audio Overview** — synthesized hosts pull on background knowledge for well-known topics rather than strictly the uploads. Treat as listening, not as citation. Banned for any learning use.
- **ChatGPT "tell me about this" / general knowledge mode** without source attachment — hallucination rate too high (Frontiers 2026: 46% false references in ChatGPT-4o citations).
- **Vendor "Recall summary" / "Glasp AI summary" / similar auto-summary features** — vendor self-studies only; no independent retention RCT.
- **Speed-reading apps with AI summarization** — combines two banned categories (speed-reading per `references/note-taking-policy.md` + auto-summary).
- **AI-generated quiz questions** as a substitute for the skill's Step 7 self_test_generate — the value is the learner generating their own questions, not the AI generating questions for them.

## What about good-faith hybrid use (AI + peer + instructor)?

Frontiers 2026 found hybrid feedback (AI + peer + instructor) outperforms AI-alone. For solo learners, the analogue is AI + own retrieval + delayed self-review:

1. Use AI in scaffolded mode for one specific micro-task (per the template)
2. Do the next retrieval attempt with no AI (self-explanation, closed-book recall)
3. Compare the two; the gap is data, not noise

This pattern is the legitimate hybrid for solo learners. It lives inside `scaffolded-only` mode; the skill does not need a separate `hybrid` mode.

## Cross-references

- `references/methods/scaffolded-ai-prompting.md` — the per-query template that `scaffolded-only` and `triage-only` modes use
- `references/calibration.md` — Phase 3 Step 2b "no-AI retry" gate is implemented there
- `references/methods/code-reading.md` — Stage 1-2 are the AI-allowed stages under `triage-only`
- `references/note-taking-policy.md` — Konik LLM middle-layer pattern is reframed as scaffolded-only AI use, not as note-taking-system endorsement
- `references/power-user-ethnography.md` (if it exists; otherwise the concept article in the wiki) — Newport / Konik / Lee positions on AI use

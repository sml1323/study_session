# Scaffolded AI Prompting — Template + Rationale

Evidence labels: see `references/evidence-labels.md`. The 8-study free-chat-damage finding is `rct-strong`; the specific template structure (Context/Request/Constraint) is `operational-heuristic` — derived from Bastani GPT Tutor + MDPI 2025 patterns but not RCT-validated as the *only* working template shape.

When invoked: the learner asks the skill to use AI (ChatGPT / Claude / NotebookLM / Custom GPT / etc.) for any part of a study session. This file specifies the **recommended prompt format** the learner should use for the AI tool, and the rationale for why free-form chat is treated as the high-stakes default refusal.

The empirical anchor: 8 studies (Bastani 2024 SCALE — *corrected from "Bastani 2025 PNAS"* / Barcaui 2025 / Benedek-Sziklai 2025 / Georgiou 2025 / Kosmyna MIT 2025 / Lee Microsoft CHI 2025 / Aslanov 2025 / MDPI 2025) converge that **free-form chat with an LLM during learning produces measurable retention damage of 11-20 percentage points**, while **scaffolded prompting templates neutralize the damage**. Bastani's GPT Tutor (scaffolded) showed no exam decline; the same model under free-form access showed −17%. MDPI 2025 demonstrated the mitigation on a different population. The mechanism (cognitive offloading + IOED + EEG connectivity decline + retrieval skipping) is robust across the 8 studies. *[evidence: rct-strong — direction and magnitude of the retention loss is RCT-derived; the template shape that neutralizes it is operational, derived from Bastani GPT Tutor + MDPI 2025.]*

The skill's stance: free chat is the high-stakes default refusal in deep-reading work. Scaffolded prompting is the recommended AI usage shape when AI is used at all; the user may override per-chapter by selecting a different `ai_policy.mode`.

## The recommended template

When the learner is about to query an AI tool (any tool, any model), the skill recommends this three-part structure. The skill produces it on demand and asks the learner to paste it before sending. Free-form questions ("can you explain X?" / "what does this mean?") are surfaced as the high-stakes default refusal at the dialogue level; the learner can override per-turn with `ai_freeform_override: true` and a one-line reason. *[evidence: operational-heuristic — the three-part structure is operational; the underlying neutralization is rct-strong but does not name *this specific* template.]*

```
## Context
I'm studying [book] [chapter] for [exam_target]. The current concept is [X].
[1-2 sentences of what I currently understand and where I'm stuck.]

## Request
Help me [SPECIFIC MICRO-TASK]. Pick exactly one:
- verify my current understanding (I will state it; you check)
- find a counterexample to a claim I will state
- simplify a derivation step I will paste
- check whether my proof outline matches the paper's
- list the assumptions a claim relies on (no explanation, just the list)
- confirm or reject a one-sentence summary I will write

Do NOT summarize the chapter. Do NOT explain the concept from scratch. Do NOT do the work for me.

## Constraint
After your answer, ask me ONE question that tests whether I actually understood your answer — a question that requires applying the answer to a NEW case I have to come up with, not paraphrasing your answer back.
```

The template's three parts each load-bearing:

- **Context** forces the learner to articulate where they are and what they understand. The articulation is itself a retrieval-practice event (Karpicke). Skipping it converts the AI into a substitute for the chapter.
- **Request** restricts the AI to a verifying / counter-checking / structural role. The 8 RCTs all measured generative free-form chat; restricted-task chat is empirically untested but mechanistically distinct (no opportunity for offloading the load-bearing thinking).
- **Constraint** is the IOED counter-move (Aslanov 2025): forcing a NEW-case application question makes IOED detectable. If the learner cannot answer the AI's follow-up question, IOED is amplified — the learner thought they understood; they did not. The session logs this gap.

## What the skill does at the dialogue level

When the learner says "I'll just ask ChatGPT" / "let me check with Claude" / "I'll have NotebookLM summarize this" mid-session:

1. **Surface the recommendation once per session** (not every turn — that is form fatigue):
   > "Free-form AI chat during a learning session is the skill's high-stakes default refusal — Bastani 2024 SCALE + 7 other studies measured 11-20pp retention loss with free chat, neutralized by scaffolded prompting. Use this template and paste your output back here so I can log the AI usage; if you want to override and free-chat anyway, say so and I'll log `ai_freeform_override: true`."

2. **Generate the template** with the chapter context pre-filled:
   ```
   ## Context
   I'm studying [chapter title] for [exam_target from frontmatter]. The current concept is [X — derived from current section].
   ```

3. **Wait for the learner to paste back the AI's response** + the AI's follow-up question + the learner's attempt at the follow-up question. All three go into the chapter note `ai_use_log[]`.

4. **Score the IOED gap** if the learner attempted the follow-up question:
   - If they can answer it correctly on a NEW case → low IOED, AI use was scaffold-shaped
   - If they cannot, or paraphrase the AI's answer back → high IOED, mark `ioed_amplified: true` for this turn
   - Cumulative `ioed_gap_avg` across turns becomes a Phase 3 calibrate input (see `references/calibration.md` § "AI-mediated chapter Step 2b retry")

## What is NEVER allowed

- ❌ "Summarize this chapter for me"
- ❌ "Explain X to me from scratch"
- ❌ "What's the main idea of this section?"
- ❌ "Write me a study guide"
- ❌ "Quiz me on this chapter" (the skill's own Step 3 self_test_generate is the legitimate path)
- ❌ Free-form chat without the template
- ❌ Voice / Audio Overview features (NotebookLM Audio Overview etc.) — these hallucinate beyond sources per the AI co-reader workflow file; treat as listening, never as study material

## Per-tool notes

- **NotebookLM**: source-grounded Q&A is the strongest sub-feature. Use only for Stage 1-2 (orientation / strategic entry per `references/methods/code-reading.md`). Audio Overview is banned. Hard caps (50 sources / ~500K words / per-notebook) make it inappropriate for thesis-scale literature.
- **ChatGPT / Claude (free chat)**: template required. Without template, blocked.
- **Custom GPT / Claude Project**: same template required. The "custom instructions" do not substitute for the per-query Context block — context is per-chapter, not per-tool.
- **Code-reading-specific AI**: CodeMap-style hierarchical pinning (global → local → detailed) is the right interface for code reading per `references/methods/code-reading.md`. The template applies; the level pinning is an additional Context-block element ("level: detailed; current location: src/auth/login.ts:45").

## What this protocol does NOT promise

- It does not promise that scaffolded AI use **beats no-AI** for high-baseline readers. The Frontiers 2026 systematic review (n=136) explicitly notes that no published intervention beats no-AI on retention for high-baseline readers. Scaffolded prompting is **damage-prevention**, not net gain.
- It does not promise that following the template eliminates IOED. It makes IOED detectable (via the constraint's NEW-case follow-up question), which is a different and weaker claim.
- It is not a recommendation to USE AI. The skill's default is `ai_policy: strict-no-ai` for deep-reading sessions. Scaffolded prompting only kicks in when the learner has explicitly opted into `triage-only` or `scaffolded-only` mode at plan time.

## Newport-style strict abstention path

If the learner picks `ai_policy: strict-no-ai` at plan time (per `references/ai-policy.md`), this file is not invoked. The Newport critique (AI summaries actively bypass the cognitive resistance training that is the *point* of slow reading) is a coherent and respectable position; the skill supports it as a first-class choice, not a fallback.

## Cross-references

- `references/ai-policy.md` — overall AI policy (3 modes, IOED gate, Newport abstention path) that this template lives inside
- `references/calibration.md` § Step 2b retry — how IOED gap from AI usage interacts with chapter_complete promotion
- `references/methods/code-reading.md` — Stage 1-2 are the only stages where AI is allowed under triage-only policy
- `references/note-taking-policy.md` — popular-system reframe map; AI tools that are part of those systems (Konik's LLM middle layer) get reframed as scaffolded-prompting use, not endorsed as systems

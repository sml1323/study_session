# Book Types and Default Session Patterns

A book gets a **two-coordinate classification**:

1. **Primary type** (one of: methodology / problem-driven / conceptual / argument-driven / reference / math-proof-heavy) — drives the default session pattern (sequence + timing).
2. **Genre axis** (orthogonal: narrative ↔ expository) — drives `paragraph_capture` density cap and reading granularity.

A conceptual chapter on memory written like a story (Sapolsky on stress and brain) is `conceptual` × `narrative-leaning`; the same topic in Griffiths-style derivation prose is `conceptual` × `expository-leaning`. Same primary type, different reading patterns. The user can override per session, but the two-coordinate classification is the starting point.

## The narrative ↔ expository orthogonal axis

| Lean | What the chapter is doing | Reading pattern |
|---|---|---|
| **narrative-leaning** | theme + character/causal-chain across paragraphs; example-driven | track theme and causal chain; avoid detail fixation; `paragraph_capture` cap **2-3 per chapter**; expect comprehension to come from arc-tracking, not micro-summary |
| **expository-leaning** | argument-by-claim + signal words (`however`, `therefore`, `in contrast`); structure-driven | track signal words; force per-paragraph or per-section summary on the load-bearing units; standard `paragraph_capture` cap 5-10 per chapter |
| **mixed** | many books are mixed; classify by which lean dominates the chapter you're about to read, not the whole book | apply the dominant lean's pattern; flip the lean for individual chapters where it changes |

Why this axis matters: narrative and expository content reward different reading moves. Applying expository defaults (signal-word tracking, per-paragraph capture, structure mapping) to a narrative chapter under-engages the chapter (the user spends effort on micro-structure that the chapter isn't using). Applying narrative defaults (theme tracking, low capture density) to an expository chapter under-processes the load-bearing argument structure. Classify both axes; the genre axis influences several Phase 2 prompts (see `references/generative-prompts.md` paragraph_capture).

Genre lean is recorded in the chapter note frontmatter:

```yaml
type: conceptual            # primary type
genre_lean: narrative       # narrative | expository | mixed
```

## The six primary types

### 1. methodology

**Examples**: Browne & Keeley *Asking the Right Questions*, Polya *How to Solve It*, Cialdini *Influence*, Heuer *Psychology of Intelligence Analysis*.

**What learning looks like**: internalize a method (a checklist, a heuristic set, a sequence of moves), then apply it to external material. The book explains the method; the work happens elsewhere.

**Sessions are not done when the chapter is read**. They're done when the method has been applied to a real outside example at least once.

**Default pattern (35-50 min)**:
- Phase 1 (5 min): PKA + prediction + which external example you'll apply this to
- Phase 2 (25 min): read chapter; trace each method step; mental rehearsal on chosen example
- End session here. Schedule Phase 3 for next sitting.
- Phase 3 (10-15 min, delayed): closed-book method recall; apply method to the chosen external example; identify where it broke
- Phase 4: invoke ARQ or Polya sub-routine on the external example to formalize the application

**Method invocations during reading**:
- ARQ → invoked on external arguments the user brings
- Polya → invoked on external problems

### 2. problem-driven (textbook)

**Examples**: Spivak *Calculus*, Polya Part III worked examples, Feynman exercises, K&R exercises, *Cracking the Coding Interview*.

**What learning looks like**: problem-solving is the work. Reading is preparation; solving is learning.

**Default pattern (40-60 min)**:
- Phase 1 (5 min): problem-type prediction; which schemas/tools you have for this category
- Phase 2 (35-45 min): **productive failure first** — give the user 15-30 min on a problem before any hint. Then worked example if needed. Then a faded-scaffolding follow-up problem.
- Phase 3 (10-15 min, delayed): closed-book problem variant generation; Schoenfeld 3-question reflection on what worked; Newman analysis if the problem was failed

**Method invocations**:
- Polya → primary loop, every problem
- Schoenfeld 3-question → at every transition inside Polya execute
- Newman → if problem was wrong on first attempt

**Special rule**: hints inside the productive failure window (first 15-30 min) require explicit user override. Auto-hint is disabled. The struggle is the desirable difficulty.

### 3. conceptual (textbook)

**Examples**: Feynman *Lectures* body, Griffiths *Introduction to Electrodynamics*, Sapolsky *Behave*, Penrose *Road to Reality*.

**What learning looks like**: concepts accumulate and interlock. You trace derivations, build a mental model, and revisit prior chapters as new concepts depend on them.

**Default pattern (40-60 min)**:
- Phase 1 (5-10 min): PKA dump on the chapter topic; advance organizer if the book provides one; prediction of what the chapter will derive
- Phase 2 (30-40 min): read with single-line derivation tracing (do not skip steps); concept_define on every new term; next_predict on every derivation step (Bisra g=1.37)
- Phase 3 (15 min, delayed): closed-book free recall + Feynman explanation + concept map sketch
- Phase 4: cross-chapter — does this depend on / extend chapter X? If yes, retrieval quiz on X

**Method invocations**:
- Polya → invoked on chapter exercises if present
- Cross-chapter retrieval quiz → mandatory before starting next chapter in same volume

**Special rule**: derivation tracing must be active. If the user reads passively, prompt: "Pause. The last derivation step was [X]. Why does that follow?"

### 4. argument-driven

**Examples**: Mill *On Liberty*, Sandel *Justice*, *Nature* / *Science* op-ed, philosophy papers, policy whitepapers.

**What learning looks like**: claims, assumptions, alternative conclusions. Reading without ARQ-style breakdown leaves you at surface comprehension.

**Default pattern (30-50 min)**:
- Phase 1 (5 min): PKA + your prior position on the issue
- Phase 2 (20-35 min): read with ARQ Core 7 always-on (issue, conclusion, reasons+evidence, assumptions, alternatives, judgment, self-explanation); ARQ Optional 5 conditionally (fallacy if nameable, statistics if cited, etc.)
- Phase 3 (10-15 min, delayed): steelman the opposing view; record your position update before/after
- Phase 4: transfer to a different case the same framework would handle

**Method invocations**:
- ARQ → primary, always-on
- Schoenfeld 3-question → folded into ARQ self-explanation move

**Special rule (echo chamber prevention)**: after the user articulates their judgment, force them to steelman the opposing view at full strength. If they refuse or do it weakly, push back. The session is not complete without this.

### 5. math-proof-heavy

**Examples**: Spivak *Calculus* main text (proofs and definitions, not just exercises), Rudin *Principles of Mathematical Analysis*, Apostol, Griffiths *Introduction to Electrodynamics* derivation chapters, EE/CS textbook chapters with circuit/signal-flow analysis, formal CS / theoretical computer-science chapters, university-level physics derivation chapters.

**What learning looks like**: load-bearing content is **proofs, derivations, and formal definitions**, not expository prose. The dominant failure mode is *prose-skip*: skim the prose between symbols, miss the role each line plays in the proof. Telling a reader to "read in validation mode" or "read like a mathematician" does not change behavior — only concrete, line-level **micro-tasks** do (Panse, Alcock & Inglis 2018 eye-tracking).

This type is distinct from `problem-driven`: a problem-driven chapter expects the user to *solve* problems; a math-proof-heavy chapter expects the user to *read* proofs as the load-bearing reading unit. Many advanced textbooks have both — classify by what the **chapter** is doing, not the book as a whole.

**Default pattern (40-60 min)**:
- Phase 1 (5-10 min): PKA + which proofs / derivations the chapter contains; identify proof structures (induction / contradiction / construction / direct / ε-δ / quantifier-heavy)
- Phase 2 (30-45 min): per-proof, pick **1-2 micro-tasks** from the menu in `references/methods/math-text-reading.md`; for engineering diagrams, run the **two-pass rule** (30s component-naming pass before scrutiny pass); when user draws a diagram, label `plan` or `verify` purpose; **no prose-skip allowed** — every load-bearing line gets a verb
- Phase 3 (15-20 min, delayed): closed-book reproduction of one proof's structure (not the symbols verbatim — the structural moves: "induction on N, base case is ..., inductive step uses hypothesis at line ..."); transfer to a NEW proof in the same family
- Phase 4: cross-chapter — does this proof technique recur in earlier chapters? If yes, retrieval quiz on the prior instance

**Method invocations**:
- math-text-reading micro-tasks → primary loop, every proof in the chapter
- Polya → invoked on chapter exercises if present (problem-solving sub-routine, distinct from proof-reading)
- backward-fading → after any worked example or fully-shown proof, before unguided variant

**Special rule**: do **not** use abstract reading-mode labels ("read this in validation mode"). Replace with concrete micro-tasks ("circle the inductive hypothesis", "predict the next line", "name the rule being invoked at line N"). Compliance with mode labels does not produce comprehension; behavioral verbs do.

**Special rule (Productive Failure entry guard)**: PF mode (struggle-first on a problem) requires all six fidelity conditions (`references/methods/math-text-reading.md` § "Productive Failure entry guard"). Without all six, default to worked-example-first → backward-fading. Time thresholds do not authorize PF entry; only the six conditions do.

### 6. reference / lookup

**Examples**: Polya Part II (heuristic dictionary), K&R reference appendix, regex docs, language reference manuals.

**What learning looks like**: not learning. Lookup. The book is a tool; sessions don't need PDP.

**Default mode**: skip the protocol. The skill enters lookup mode:
- Take the user's question
- Read the relevant entry
- Answer with citation back to the book
- If the user explicitly says "I want to learn this entry", escalate to conceptual or methodology pattern (their choice).

**No chapter notes are generated** by default; the looked-up content is cross-referenced into whichever book they were actively learning.

## Classifying a new book

When the skill encounters a book without a type in books.yml, classify both axes before the first session.

**Primary type heuristics** (pick the first that fits):

1. **Title pattern**: "How to ...", "The Art of ...", "<Method> Guide" → likely methodology.
2. **Has worked examples + exercises in every chapter** → problem-driven.
3. **Chapter content is dominantly proofs / derivations / formal definitions; symbols outweigh prose; theorem-proof or definition-theorem-proof structure** → math-proof-heavy.
4. **Sequential derivations, building on prior chapters, named in equations, but presented expositorily rather than as formal theorem-proof** → conceptual.
5. **Argues a thesis, references opposing views, ends with conclusions** → argument-driven.
6. **Alphabetical or topic-indexed entries, no narrative spine** → reference.

**math-proof-heavy vs conceptual**: a chapter with the same equations is `math-proof-heavy` if the symbols and lemmas are doing the load-bearing work (Spivak's proofs, Griffiths' explicit derivations) and `conceptual` if the prose is doing the load-bearing work and the equations are illustrative (Sapolsky, Penrose narrative chapters). When in doubt, ask: does skipping the prose between equations preserve the chapter's argument? If yes, math-proof-heavy. If no, conceptual.

If multiple types fit (a book can be hybrid — Polya is methodology + problem-driven + reference depending on Part), classify by Part. Polya:
- Part I (the method): methodology
- Part II (heuristic dictionary): reference
- Part III (worked examples): problem-driven

**Genre lean heuristics** (orthogonal — applied after primary type):

1. **Story-driven prose, character or case-study spine** → narrative-leaning.
2. **Signal-word-dense (`however`, `therefore`, `in contrast`), claim-by-claim structure** → expository-leaning.
3. **Both at chapter granularity** (some chapters story, some structure) → mixed; classify per chapter.

Examples:

| Book | Primary type | Genre lean |
|---|---|---|
| Browne & Keeley *Asking the Right Questions* | methodology | expository |
| Polya *How to Solve It* | methodology | mixed (Part I expository, Part III narrative-ish via worked examples) |
| Spivak *Calculus* (main text — proofs, definitions) | math-proof-heavy | expository |
| Spivak *Calculus* (exercise sets) | problem-driven | expository |
| Rudin *Principles of Mathematical Analysis* | math-proof-heavy | expository |
| Sapolsky *Behave* | conceptual | narrative |
| Griffiths *Electrodynamics* (derivation chapters) | math-proof-heavy | expository |
| Griffiths *Electrodynamics* (motivation/narrative chapters) | conceptual | expository |
| Mill *On Liberty* | argument-driven | expository |
| Sandel *Justice* | argument-driven | mixed (case-narrative chapters + argument chapters) |

Confirm with user. Store under `books.yml`:

```yaml
polya:
  path: ~/wiki/tmp_books/polya.pdf
  parts:
    - id: I
      type: methodology
      pages: 1-36
    - id: II
      type: reference
      pages: 37-150
    - id: III
      type: problem-driven
      pages: 151-end
```

## Session pattern overrides

User can override the default pattern for any session:

- "Today I want productive failure first even though this is conceptual" — fine, log it.
- "Skip Phase 1 for this chapter" — accept, but warn once that PKA effect is well-supported.
- "I just want to read; no tutoring" — switch to a reading-only mode that still triggers Phase 3 calibrate at the end.

## Defaults summary

| Type | Phase 1 | Phase 2 | Phase 3 (delayed) | Phase 4 | Method default |
|------|---------|---------|------------------|--------|----------------|
| methodology | PKA + prediction + external example pick | Read + step trace + mental rehearsal | Method recall + apply to example | Formalize ARQ/Polya on example | per-chapter content |
| problem-driven | Type prediction + tool review | **Productive failure** → worked example → backward-fading → unguided | Variant generation + Schoenfeld + Newman | Cross-problem schema check | Polya always; backward-fading after every worked example |
| math-proof-heavy | Identify proof structures + PKA | Per-proof micro-tasks (1-2/proof); two-pass diagrams; diagram-purpose label | Proof-structure recall + transfer to new proof in same family | Cross-chapter proof-technique retrieval | math-text-reading always; Polya on exercises |
| conceptual | PKA + advance organizer + derivation prediction | Trace single-line, concept_define, next_predict | Free recall + Feynman + concept map | Cross-chapter retrieval | Polya on exercises |
| argument-driven | PKA + prior position | Read + ARQ always-on + Optional triggers | Steelman opposite + position update | Transfer to different case | ARQ always |
| reference | — | lookup → answer → cite | — | cross-ref to active book | — |

## Cross-references

- `references/generative-prompts.md` — verbatim prompts used in each phase
- `references/methods/arq.md` — ARQ Core 7 + Optional 5 + Critical Questions canonical list
- `references/methods/polya.md` — 4-step + Schoenfeld + hint hierarchy
- `references/methods/math-text-reading.md` — micro-task menu for proofs + two-pass diagram + diagram-purpose label + PF entry guard (math-proof-heavy default Phase 2)
- `references/methods/backward-fading.md` — completion-problem fade sequence after worked examples (problem-driven and math-proof-heavy)
- `references/methods/hint-escalation.md` — event-based hint triggers + paraphrase gate
- `references/failure-modes.md` — productive struggle window enforcement, echo chamber prevention
- `references/calibration.md` — delayed retrieval mechanics
- `references/spacing-policy.md` — daily floor commitment + behavioral retrieval + deadline anchor + FCI/BEMA self-diagnostic

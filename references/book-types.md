# Book Types and Default Session Patterns

A book gets a **two-coordinate classification**:

1. **Primary type** (one of: methodology / problem-driven / conceptual / argument-driven / reference / math-proof-heavy) — drives the default session pattern (sequence + timing).
2. **Genre axis** (orthogonal: narrative ↔ expository) — drives `paragraph_capture` density cap and reading granularity.

A conceptual chapter written like a story (Sapolsky on stress and brain) is `conceptual` × `narrative-leaning`; the same topic in Griffiths-style derivation prose is `conceptual` × `expository-leaning`. Same primary type, different reading patterns. The user can override per session, but the two-coordinate classification is the starting point.

## The narrative ↔ expository orthogonal axis

| Lean | What the chapter is doing | Reading pattern |
|---|---|---|
| **narrative-leaning** | theme + character/causal-chain across paragraphs; example-driven | track theme and causal chain; avoid detail fixation; `paragraph_capture` cap **2-3 per chapter**; expect comprehension to come from arc-tracking, not micro-summary |
| **expository-leaning** | argument-by-claim + signal words (`however`, `therefore`, `in contrast`); structure-driven | track signal words; force per-paragraph or per-section summary on the load-bearing units; standard `paragraph_capture` cap 5-10 per chapter |
| **mixed** | many books are mixed; classify by which lean dominates the chapter you're about to read, not the whole book | apply the dominant lean's pattern; flip the lean for individual chapters where it changes |

Why this axis matters: narrative and expository content reward different reading moves, so applying one lean's defaults to the other under-engages or under-processes the chapter. Classify both axes; the genre axis influences several Phase 2 prompts (see `references/generative-prompts.md` paragraph_capture).

Genre lean is recorded in the chapter note frontmatter:

```yaml
type: conceptual            # primary type
genre_lean: narrative       # narrative | expository | mixed
```

## The six primary types

### 1. methodology

**Examples**: Browne & Keeley *Asking the Right Questions*, Polya *How to Solve It*, Cialdini *Influence*, Heuer *Psychology of Intelligence Analysis*.

**What learning looks like**: internalize a method (a checklist, a heuristic set, a sequence of moves), then apply it to external material. The book explains the method; the work happens elsewhere.

**Sessions are not done when the chapter is read**. They're done when the method has been applied to a real outside example at least once. (Phase 1-4 defaults: see Defaults summary table; total 35-50 min. Phase 2 ends the session; schedule Phase 3 for next sitting.)

### 2. problem-driven (textbook)

**Examples**: Spivak *Calculus*, Polya Part III worked examples, Feynman exercises, K&R exercises, *Cracking the Coding Interview*.

**What learning looks like**: problem-solving is the work. Reading is preparation; solving is learning. (Phase 1-4 defaults + method invocations: see Defaults summary table; total 40-60 min.)

**Phase 2 sequence detail**: **PF-first if the entry guard passes** (give the user 15-30 min on a problem before any hint, then worked example if needed, then backward-fading per `references/methods/backward-fading.md`); **worked-example-first → backward-fading if the entry guard fails** (any condition misses — child learner, procedural drill, no prerequisite, no time budget, etc.). PF is not the unconditional default — the entry guard (`references/methods/math-text-reading.md` § "Productive Failure entry guard"), checked at Phase 1, decides. backward-fading runs after any worked example (whether shown by chapter or by hint level 3), always before the unguided variant.

**Special rule (PF window when entry guard passes)**: hints inside the productive failure window (first 15-30 min) require explicit user override. Auto-hint is disabled. The struggle is the desirable difficulty. When entry guard fails, this special rule does not apply — the chapter goes worked-example-first instead and there is no PF window to protect.

### 3. conceptual (textbook)

**Examples**: Feynman *Lectures* body, Griffiths *Introduction to Electrodynamics*, Sapolsky *Behave*, Penrose *Road to Reality*.

**What learning looks like**: concepts accumulate and interlock. You trace derivations, build a mental model, and revisit prior chapters as new concepts depend on them. (Phase 1-4 defaults: see Defaults summary table; total 40-60 min. Phase 2 next_predict on every derivation step is Bisra g=1.37. Cross-chapter retrieval quiz is mandatory before starting the next chapter in the same volume.)

**Special rule**: derivation tracing must be active. If the user reads passively, prompt: "Pause. The last derivation step was [X]. Why does that follow?"

### 4. argument-driven

**Examples**: Mill *On Liberty*, Sandel *Justice*, *Nature* / *Science* op-ed, philosophy papers, policy whitepapers.

**What learning looks like**: claims, assumptions, alternative conclusions. Reading without ARQ-style breakdown leaves you at surface comprehension. (Phase 1-4 defaults: see Defaults summary table; total 30-50 min. Phase 2 ARQ Core 7 = issue, conclusion, reasons+evidence, assumptions, alternatives, judgment, self-explanation; ARQ Optional 5 conditionally — fallacy if nameable, statistics if cited, etc. Schoenfeld 3-question folds into the ARQ self-explanation move.)

**Special rule (echo chamber prevention)**: after the user articulates their judgment, force them to steelman the opposing view at full strength. If they refuse or do it weakly, push back. The session is not complete without this.

### 5. math-proof-heavy

**Examples**: Spivak *Calculus* main text (proofs and definitions, not just exercises), Rudin *Principles of Mathematical Analysis*, Apostol, Griffiths *Introduction to Electrodynamics* derivation chapters, EE/CS textbook chapters with circuit/signal-flow analysis, formal CS / theoretical computer-science chapters, university-level physics derivation chapters.

**What learning looks like**: load-bearing content is **proofs, derivations, and formal definitions**, not expository prose. The dominant failure mode is *prose-skip*: skim the prose between symbols, miss the role each line plays in the proof. Telling a reader to "read in validation mode" or "read like a mathematician" does not change behavior — only concrete, line-level **micro-tasks** do (Panse, Alcock & Inglis 2018 eye-tracking).

This type is distinct from `problem-driven`: a problem-driven chapter expects the user to *solve* problems; a math-proof-heavy chapter expects the user to *read* proofs as the load-bearing reading unit. Many advanced textbooks have both — classify by what the **chapter** is doing, not the book as a whole. (Phase 1-4 defaults: see Defaults summary table; total 40-60 min.)

**Phase 2 detail**: per-proof, pick **1-2 micro-tasks** from the menu in `references/methods/math-text-reading.md`; for engineering diagrams, run the **two-pass rule** (30s component-naming pass before scrutiny pass); when the user draws a diagram, label `plan` or `verify` purpose; **no prose-skip allowed** — every load-bearing line gets a verb. backward-fading runs after any worked example or fully-shown proof, before the unguided variant.

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

**math-proof-heavy vs conceptual**: a chapter with the same equations is `math-proof-heavy` if the symbols and lemmas are doing the load-bearing work and `conceptual` if the prose is doing the load-bearing work and the equations are illustrative. When in doubt, ask: does skipping the prose between equations preserve the chapter's argument? If yes, math-proof-heavy. If no, conceptual.

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
| problem-driven | Type prediction + tool review + **PF entry-guard check** | **PF-first → worked example → backward-fading → unguided** *if guard passes*; **worked-example-first → backward-fading → unguided** *if guard fails* | Variant generation + Schoenfeld + Newman | Cross-problem schema check | Polya always; backward-fading after every worked example; PF gated on entry guard |
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

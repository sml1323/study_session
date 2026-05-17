# Code Reading — Non-Linear 5-Stage Protocol
<!-- TODO evidence-tag - see references/evidence-labels.md; this files thresholds/policies are not yet labeled -->

When invoked: chapter or session contains **code, formal proofs, or dense scientific papers** as the load-bearing reading unit. The chapter is non-linear by necessity — top-to-bottom + highlight + review (the consumer-tool default) does not work for these domains. The protocol below is the workflow that senior developers, mathematicians, and code auditors converge on independently.

The empirical anchor is the Code Review as Decision-Making (CRDM) study (n=10 senior developers averaging 8 years of review experience, 1,159 coded segments from 34 real reviews). 27% of segments were the orientation phase (linear); 73% were the analytical phase (iterative). The "selecting next action" sub-step was itself a primary cognitive activity even at 8 years of experience — code-base navigation is its own load. Tao's 2017 "On Compilation Errors in Mathematical Reading" gives the same shape for proof reading.

This file is the cross-domain protocol. Math-specific micro-tasks (circle hypothesis / mark contradiction / quantifier scope) live in `references/methods/math-text-reading.md` and run *inside* the analytical loop here.

## The 5 stages

Run in order; do not collapse the orientation pass into the analytical loop.

### Stage 1 — Orientation pass (linear, ~5-10 min)

Before opening the file / chapter / paper, the reader answers a 5-question framework. This is the senior-engineer pre-reading checklist (CRDM orientation segments + Senior-Engineers-Read-Code 2025 essay):

1. **What is this trying to achieve?** (purpose, not mechanism)
2. **Where does data / dependency / proof-flow come from and go?** (data flow, not execution order)
3. **What are the invariants?** (preconditions / postconditions / quantifier scope / load-bearing assumptions)
4. **What changed recently?** (git history, paper revision dates, "this lemma was added in v3")
5. **Who knows more than me?** (the social layer: author, maintainer, advisor, prior reviewer; for solo learners: prior chapters in the same book that already established the framework)

For paper-specific adaptation: question 4 becomes "Which earlier paper does this build on / refute?" and question 5 stays as "Who has reviewed or cited this?"

Capture into the chapter note Phase 1 as an `orientation_pass` block. Orientation is **mandatory before analytical loop entry** for non-linear chapters; without it, the reader loses the global topology and pattern-matches on local features.

### Stage 2 — Strategic entry points

Pick high-leverage starting locations instead of file/page order. CRDM senior reviewers picked "the top of the call stack"; mathematicians pick the main theorem statement; auditors pick the public API surface; paper readers pick abstract → conclusion → figures before any prose.

Strategic entry checklist (pick 1-2):
- **Code**: top of call stack / public API / test files / README → src
- **Proof**: theorem statement → conclusion line → first inductive step or contradiction line
- **Paper**: abstract → conclusion → figures + tables → first paragraph of each section → introduction last
- **Dense textbook chapter**: chapter summary → exercises → derivation results → derivations themselves last

Anti-pattern: opening at line 1 / page 1 and reading forward. This is the consumer-tool default; non-linear domains do not reward it.

### Stage 3 — Iterative analytical loop

This is where 73% of CRDM time was spent. Track which sub-mode you are in at each turn (the explicit naming reduces working-memory load — "selecting next action" was its own coded activity in CRDM):

| Sub-mode | What you are doing |
|---|---|
| `understanding` | reading the local content; grasping what this line / function / lemma says |
| `assessing` | judging correctness, fit, completeness against the invariants from Stage 1 |
| `simulating` | mentally executing / instantiating; "if X happens, then Y" |
| `navigating` | deciding where to look next; this is itself work, not a side activity |

Capture mode transitions inline in the chapter note Phase 2:

```yaml
analytical_loop:
  - turn: 3
    sub_mode: understanding
    target: "lemma 4.2 statement"
    note: "..."
  - turn: 4
    sub_mode: simulating
    target: "lemma 4.2 with X = small constant"
    note: "..."
  - turn: 5
    sub_mode: navigating
    target: "where is X defined"
    decision: "jump to definition (chapter 2 page 31)"
```

Math-specific micro-tasks (`references/methods/math-text-reading.md`) and Tao's 7 moves run inside this loop on individual proof units.

### Stage 4 — Failure-as-trigger protocol

When the reading "stops compiling" — you can't simulate, you've lost the topology, you've re-read the same paragraph three times — that is a **strategy-switch signal**, not a push-harder signal. Tao's framing: even strong mathematicians on hard papers "lose their higher reading skills and revert to a more formal, tedious line-by-line interpretation"; the move is not to push, it is to switch.

Failure-trigger menu (pick the first that fits):

| Failure shape | Switch to |
|---|---|
| "I can't simulate" | strategic simplification (specialize to lower dimensions / ignore error terms / pick concrete instance) |
| "I've lost the topology" | re-orient (Stage 1) — return to the 5 questions |
| "This step doesn't follow" | suspect the text first (Tao move 2: typo / missing word / cryptic comment) before suspecting yourself |
| "I've re-read the same lines" | jump to a strategic entry point (Stage 2) elsewhere; come back |
| "I can't decide what's next" | next-action queue (Stage 5) |
| "I'm dependent on details I haven't seen" | read ahead 1-2 lines (Tao move 1 — most "compilation errors" resolve in the next 1-2 lines) |

Capture failure events in the chapter note as `failure_triggers: [{ turn, shape, switch_to, outcome }]`. A pattern of repeated same-shape failures is a calibration signal that the chapter is above the reader's current scaffolding.

### Stage 5 — Next-action queue

"Selecting next action" is a primary cognitive activity; CRDM reviewers spent measurable time on it even at 8 years of experience. Externalizing it removes the working-memory load. Maintain a small queue of pending investigations:

```yaml
next_actions:
  - "Verify lemma 4.2 holds for X = 0 edge case"
  - "Read section 5.1 — referenced as 'standard technique' but I don't recognize it"
  - "Re-check whether the convergence proof uses dominated convergence or Fatou"
```

After each analytical-loop turn, either pop one item from the queue (becomes the next turn's target) or push one (newly surfaced unknown). The queue replaces "what should I do next" with "what's at the top of the queue" — the latter is a mechanical decision.

## Cognitive load of navigation itself

The CRDM finding that bears repeating: even at 8 years of experience, navigating the codebase is its own primary task, not a side concern. The same is true for proof / paper / dense chapter reading. The skill should NOT treat "where to look next" as overhead between substantive turns — it is substantive turn work, and naming it (Stage 5) makes the load shareable with the explicit queue instead of carried entirely in working memory.

## When to invoke this protocol vs the linear default

| Chapter type | Default protocol |
|---|---|
| methodology / argument-driven / narrative-leaning conceptual / reference | linear with chunk-boundary recall (the SKILL.md default) |
| problem-driven (textbook exercises) | Polya 4-step (`references/methods/polya.md`); code-reading not invoked unless the exercise involves reading code |
| math-proof-heavy | code-reading 5 stages + math-text-reading micro-tasks (this file is the outer loop, math-text-reading runs inside Stage 3) |
| code chapter (e.g., reading a real codebase, K&R chapter with significant source) | code-reading 5 stages |
| dense scientific paper (research paper, not textbook expository) | code-reading 5 stages with paper-specific adaptations to questions 4 and 5 |
| dense expository chapter (graduate-level theory section) | code-reading 5 stages with reduced Stage 5 queue (chapters have less navigation surface than codebases) |

The classifier runs at plan-mode time per the chapter's `reading_mode_declaration` in chapter-template.md frontmatter.

## Anti-patterns

- ❌ **Opening at line 1 / page 1 of a non-linear chapter.** Strategic entry first.
- ❌ **Skipping the orientation pass.** Without the 5 questions, analytical-loop turns pattern-match on local features and the global topology never forms.
- ❌ **Pushing harder when reading stops compiling.** That is exactly when to switch strategies (Stage 4).
- ❌ **Treating "what's next" as overhead.** It's primary work; externalize via the next-action queue.
- ❌ **Running this protocol on a narrative or methodology chapter.** Linear protocol is correct for those; running 5-stage code-reading on Sapolsky is form fatigue.
- ❌ **Collapsing Stages 1-2 ("just start reading and orient as you go").** The empirical record is that orientation done first is qualitatively different from orientation done lazily mid-read.

## Cross-references

- `references/methods/math-text-reading.md` — micro-tasks that run inside Stage 3 for proof units; Tao 7 moves are interleaved here
- `references/methods/polya.md` — for *solving* problems (Polya 4-step is the outer loop); code-reading is for *reading* problems and code
- `references/book-types.md` — math-proof-heavy primary type defaults to invoking this protocol
- `references/ai-policy.md` — if AI co-reader is in use, the orientation pass and analytical loop are the two stages where AI is allowed (per the triage-only policy); deep reading inside Stage 3 stays AI-free

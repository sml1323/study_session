# Math / Proof-Heavy Text Reading — Micro-Task Protocol

When invoked: chapter is from a university math, physics, or engineering text where the load-bearing content is **proofs, derivations, or formal definitions** rather than expository prose. Examples: Spivak *Calculus* main text (proofs, not just exercises), Rudin, Griffiths derivations, EE/CS textbook chapters with circuit/signal-flow analysis, theoretical chapters in formal CS texts.

The failure mode this protocol is built against: **prose-skip**. Confronted with a page that is half symbols and half short prose, novices skim the prose. Skim mode preserves a feeling of progress without producing comprehension of the proof structure or the role each line plays. The replacement is not "read more carefully" (that label does not change behavior) but a small set of **concrete micro-tasks** that force the eye to do specific work on each load-bearing line.

## Why abstract mode labels do not work

The intuitive instruction "read this in validation mode, not comprehension mode" sounds reasonable but does not change reader behavior in practice (Panse, Alcock & Inglis 2018 eye-tracking study of mathematicians and undergraduates). Telling a reader to switch reading mode produces compliance language without behavioral change. What does change behavior is concrete, line-level micro-tasks the reader has to *do* — not modes they are supposed to *be in*.

**Banned**:
- "Read this proof in validation mode."
- "Switch to comprehension reading."
- "Read more carefully this time."
- "Read like a mathematician."

**Allowed** (each is a verb the reader's pen/highlighter performs):
- "Circle the inductive hypothesis."
- "Mark the line where the contradiction enters."
- "Predict the next line before scrolling."
- "Highlight the symbol that changes meaning between line N and line N+1."
- "Name the rule (theorem, axiom, definition) being invoked at line N."

## The micro-task menu (pick 1-2 per proof, never all)

Pick the micro-task that best matches the proof structure. Running all of them on every proof creates form fatigue and is the failure mode the rest of the skill is engineered to avoid.

| Proof structure | Micro-task | Verbatim prompt |
|---|---|---|
| Induction proof | Circle the inductive hypothesis | "Circle the line where the inductive hypothesis is stated. Then circle the line where it is invoked in the inductive step." |
| Proof by contradiction | Mark the contradiction entry | "Mark the line where the contradiction is introduced. What was the assumption that the contradiction refutes?" |
| Construction / existence proof | Identify the construction | "Highlight the line that constructs the object whose existence the theorem claims. What property must the construction satisfy?" |
| Direct derivation | Line prediction | "Cover the next line. Predict it from the current line. Reveal. Where did your prediction differ?" |
| Algebraic manipulation | Rule invocation | "At each line transition, name the rule (axiom / lemma / theorem) being used. If you can't name it, that line is the gap." |
| Substitution / change of variables | Symbol-meaning tracking | "At the substitution line, write down what each symbol means before and after. The change in meaning is the proof's move." |
| ε-δ / quantifier-heavy | Quantifier scope marking | "Underline each universal and existential quantifier. Where does each quantifier's scope end?" |

Capture micro-task results inline in the chapter note Phase 2 section under the relevant proof:

```yaml
proof_micro_tasks:
  - proof_ref: "Theorem 3.2 (page 47)"
    structure: induction
    micro_task: "circle inductive hypothesis"
    user_output: "Hypothesis at line 4; invoked at line 7"
    gap: null   # or describe what the user missed
```

## Two-pass rule for engineering / scientific diagrams

Engineering diagrams (circuit schematics, P&ID, signal-flow graphs, free-body diagrams, mechanical drawings) reward a different protocol than text-only proofs. Lohmeyer & Meboldt 2015 (mechanical-engineering eye-tracking) finds that successful readers do **two passes**, never one:

| Pass | Time budget | Goal |
|---|---|---|
| Pass 1 | 30 seconds, max | Skim the diagram naming each component without reading any prose. "There is a [X], a [Y] connected to [X] via [Z]." Do not yet try to interpret behavior. |
| Pass 2 | as long as the prose calls for | The chapter prose names elements; on each named element, scrutinize that element on the diagram. |

**Anti-pattern**: entering pass 2 (scrutinize) without pass 1 (component naming). Without pass 1, the reader scrutinizes whichever element happens to be near the first named term and never gets a global topology of the diagram. Pass-1-skipped readings predict comprehension failure in the eye-tracking data.

Surface this as a concrete prompt at the moment a diagram appears:

> "Diagram on this page. First: 30 seconds — name every component aloud, do not interpret. Then we read the prose."

Capture:

```yaml
diagram_passes:
  - diagram_ref: "Figure 4.3 — RC circuit"
    pass_1_components: ["resistor R1", "capacitor C1", "voltage source V", "ground"]
    pass_1_seconds: 28
    pass_2_done: true
```

## Tao 7 moves — compilation-error meta-trigger (R11 v4)

Tao's "On Compilation Errors in Mathematical Reading" (2017) frames the strategy-switch protocol for proof reading: even strong mathematicians, on first read of a hard paper, "lose their higher reading skills and revert to a more formal, tedious line-by-line interpretation." The move is not to push harder; it is to **switch strategies**.

The 7 moves below run inside the analytical-loop stage (per `references/methods/code-reading.md` Stage 3). Each is a behavioral verb the reader executes when a specific failure shape appears. Pick 1-2 per "stop-compile" event, never all.

| # | Move | When | What the reader does |
|---|---|---|---|
| 1 | **Read ahead** | line N "doesn't follow" | jump to line N+1 or N+2; most "compilation errors" resolve in the next 1-2 lines (the dependency was forward-referenced) |
| 2 | **Suspect typo before yourself** | derivation produces wrong-looking step | if you can derive B' instead of B, the paper is wrong, not you. Try deriving the conclusion that follows from your B'; if it is consistent, the source has a typo |
| 3 | **Examine missing keywords** | conclusion seems to derive from elsewhere | the absence of "thus" / "therefore" / "by" is itself a signal — the conclusion was derived earlier and is now being recalled. Search backwards for the actual derivation |
| 4 | **Return to cryptic comments** | a step uses a hypothesis you don't see in the current page | passages skipped on first pass often contain the load-bearing hypothesis; return there before pushing forward |
| 5 | **Strategic simplification** | symbol-density too high to simulate | specialize to lower dimensions, ignore error terms, focus on the near-counterexample case. Solve the easier instance, then re-read the general statement |
| 6 | **Blackboard logical mapping** | proof depends on multiple lemmas | diagram dependencies between lemmas / theorems on a separate sheet. The dependency structure is itself the load-bearing object, not the lines |
| 7 | **Author intent** | a statement seems pointless | try to understand the *purpose* behind each statement — what is the author warning against / pointing toward / preparing to use? |

### "Compilation error" as the meta-trigger

The 7 moves all share a precondition: **the reader noticed that reading stopped compiling**. That noticing is itself the metacognitive trigger and is more important than which specific move you pick. Hardcoded rule:

- **stop-compile (you've re-read the same lines, you can't simulate, the next step doesn't follow) → switch strategies (one of the 7 moves above), do not push harder.**

Push-harder is the dominant failure mode in formal-text reading; the 7 moves are operational alternatives.

Capture into the chapter note Phase 2 alongside `failure_triggers` (per `references/methods/code-reading.md` Stage 4):

```yaml
tao_moves:
  - turn: 7
    failure_shape: "next step doesn't follow"
    move_picked: 1   # read ahead
    outcome: "resolved at line N+2 (forward-referenced lemma)"
  - turn: 12
    failure_shape: "symbol-density too high to simulate"
    move_picked: 5   # strategic simplification
    outcome: "specialized to dim 2; saw the symmetry; re-read general"
```

> ⚠ **Patch source caveat — `study-session-skill-patch-v4-2026-05-03.md` (Round 11)**: the 7 moves are direct citations from Tao 2017. The pick-1-2-per-event rule and the "stop-compile" hardcoded trigger are **operational placeholders** chosen to make the protocol actionable; Tao's original essay does not enumerate per-event move counts. Replace with R12-validated structure if RCT becomes available.

## Diagram-purpose tracking (Kohl & Finkelstein 2006)

When the user *draws* a diagram (during problem solving, derivation, or note-taking), the diagram serves one of two purposes; the user must label which:

| Purpose | When | What it captures |
|---|---|---|
| `plan` | before computation | guesses topology / sets up unknowns / sketches expected behavior |
| `verify` | after computation | re-draws to check that the computed answer matches the topology / behavior |

A diagram drawn without a labeled purpose is a learning-neutral artifact. **Diagram count is not a learning signal**; **purpose density is the learning signal**. A reader who draws three diagrams and labels none has produced no diagram-based comprehension; a reader who draws one labeled `plan` and one labeled `verify` has done the cognitive work the diagrams are for.

After computation, if the user did not redraw, prompt:

> "Sanity check: redraw the situation with the answer plugged in. Does it match what your `plan` diagram predicted?"

## Productive Failure entry guard for math/proof chapters

Productive failure (Sinha & Kapur 2021) — letting the user struggle on a problem before any scaffold — is a real effect, but it is not a default.

> ⚠ **Patch source caveat — `study-session-skill-patch-v3-2026-04-30.md` (Round 10) requires "성인 학습자 + 개념 문제 + 6 충실도 조건 충족 가능 → PF 모드", but does NOT enumerate the specific 6 fidelity conditions.** The list below is an operational placeholder reconstructed from typical Sinha & Kapur 2021 protocol descriptions; the exact six items in the source patch are unverified. Treat as a checklist to discuss with the user, not as canon. Replace with the verified list when R11 nails them down.

Activate PF mode only when the conditions below all hold (placeholder list):

1. **Adult learner** — PF effect is conditional; younger-learner literature is mixed (this and #2 are the two patch-named conditions)
2. **Conceptual problem** — not a procedural drill; PF needs a problem with a deep structure to discover (this and #1 are the two patch-named conditions)
3. *(placeholder)* The user has the prerequisite knowledge to attempt the problem at all
4. *(placeholder)* The problem has a generative-solution structure (multiple plausible attempts, each exposing a piece of the deep structure)
5. *(placeholder)* The user has explicit time budget for the struggle (15-30 min unguarded)
6. *(placeholder)* A worked example or expert explanation will follow the struggle (PF without consolidation is just struggle)

Without all six, default to **worked-example-first** (study the example, then run backward-fading per `references/methods/backward-fading.md`).

PF is event-triggered, not time-triggered: do not set a clock and force struggle. The trigger is a problem the chapter presents that meets the conditions.

## What never scales down on math/proof chapters

Even at light intensity:

- Pass 1 of the two-pass diagram rule (30 seconds is cheap)
- One micro-task per proof (circle the hypothesis, mark the contradiction)
- Diagram purpose label when the user draws a diagram

These are the load-bearing learning behaviors; cutting them produces prose-skip in disguise.

## Anti-patterns

- ❌ **"Read like a mathematician."** Abstract label without behavioral anchor.
- ❌ **Running every micro-task on every proof.** Pick 1-2 that match structure.
- ❌ **Pass-2-only diagram reading.** Skim component naming first, always.
- ❌ **Counting diagrams as a learning signal.** Purpose-label density is the signal.
- ❌ **Productive failure as the default for any math problem.** PF needs all six fidelity conditions; without them, worked-example-first.

## Cross-references

- `references/methods/code-reading.md` — 5-stage non-linear protocol; Stage 3 (analytical loop) is where micro-tasks and Tao moves run; Stage 4 (failure-as-trigger) is where the "stop-compile" detection lives
- `references/methods/backward-fading.md` — what to do after a worked example
- `references/methods/polya.md` — Polya 4-step is the outer loop for problem chapters; micro-tasks here run inside the Understand and Carry Out steps
- `references/methods/proof-comprehension.md` — Mejía-Ramos 7-facet proof comprehension framework (this file is the per-line micro-task layer; that file is the per-proof comprehension assessment layer)
- `references/book-types.md` — math/proof-heavy primary type uses this protocol as default Phase 2

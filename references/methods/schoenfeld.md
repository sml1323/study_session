# Schoenfeld 3-Question Metacognitive Sticky

The single most important metacognitive prompt in problem solving. Verbatim wording matters; do not paraphrase.

## The three questions

> 1. **What am I doing?**
> 2. **Why am I doing it?**
> 3. **How does it help me?**

Korean delivery:
> "지금 무엇을 하고 있나? 왜 하고 있나? 이게 어떻게 도움이 되나?"

## When to apply

Inside Polya step 3 (Carry Out), at every step transition. Not at the start of the problem (that's Plan); not at the end (that's Look Back). At every move *during execution*.

A "transition" means moving from one operation to another:
- Computing X → computing Y
- Applying lemma A → applying lemma B
- Substituting → simplifying
- Trying approach 1 → switching to approach 2

Each transition gets all three questions. Capture answers in the polya_logs `carry_out.steps[i].schoenfeld` block:

```yaml
- { do: "introduce variable t", schoenfeld: { what: "변수 도입", why: "대칭성 활용", how: "미분 가능하게 만들어 극값 추출" } }
```

## Effort-without-progress trigger — "stop and check the map"

The transition-based prompt is necessary but not sufficient. Schoenfeld's *signature* executive-control intervention fires **independent of any operation transition**: when the user has been expending effort *without making progress* — grinding inside one approach, computing more and more without getting measurably closer to the goal — interrupt with a control prompt even though no transition occurred:

> "Stop. Step back and check the map: is this approach actually getting you closer to the goal, or are you just generating work? How much longer do you keep going before you try something else?"

Korean delivery:
> "잠깐 멈추자. 지도를 다시 보자 — 이 접근이 정말 목표에 가까워지고 있나, 아니면 그냥 계산만 쌓고 있나? 다른 방법으로 갈아탈 시점은 언제인가?"

This is the **monitor-and-allocate** behavior that most separates experts from novices: experts periodically suspend execution to evaluate whether the current path is worth continuing, then reallocate effort if it is not. Novices stay locked in a non-productive approach far too long. Fire this trigger on effort-without-progress regardless of whether the user just changed operations — it is not gated on a transition. Log it as a `monitor_check` event with the user's decision (persist vs. switch approach).

## Why this works

This triad is **a scaffold inspired by Schoenfeld**, not a transcript of a literally-observed expert behavior. Schoenfeld 1985 (*Mathematical Problem Solving*, Academic Press) and 1992 ("Learning to think mathematically," in *Handbook of Research on Mathematics Teaching and Learning*) video-protocol research showed that what distinguishes experts is active *executive control / self-monitoring* during problem solving — experts notice when an approach isn't paying off and reallocate, whereas novices execute procedures mechanically, drift from the plan, and accumulate computation that doesn't connect to the goal. Experts do not necessarily voice these three exact questions; the "what / why / how does it help" triad is a teachable proxy that externalizes that monitoring for a learner who does not yet do it spontaneously. *[evidence: observational — video-protocol study, not RCT; the triad is a pedagogical operationalization of the observed monitoring behavior, not a quoted expert script.]*

The 3 questions force the user to maintain plan-execution coherence: each computation must serve a purpose connected to the goal.

## Patterns

### When user can answer all three crisply

Good. Continue. Mark step as `schoenfeld: aligned`.

### When user can answer "what" and "why" but not "how does it help"

Common. The user is executing a habit move without understanding its purpose for *this* problem. This is a stop signal.

> "Pause here. You're computing [X] but you can't articulate how it gets you to [goal]. Does this step actually serve the plan, or is it a habit?"

Often the answer is "habit" — the user is computing something familiar that doesn't lead to the goal. Re-plan from this step.

### When user can answer "what" only

The user has lost the plan. Stop the computation; redo Plan step.

### When user paraphrases the question instead of answering

> "What am I doing?" → "Solving the problem" — not an answer. Push for the *specific* current operation.

## Anti-patterns

- ❌ Asking only at the start of the problem (that's Plan)
- ❌ Asking only at the end (that's Look Back)
- ❌ Asking once per problem, not per transition
- ❌ Paraphrasing to "what's your plan?" — different question, different effect
- ❌ Letting user skip "how does it help me?" — this is the leverage question

## Schoenfeld outside Polya

The 3-question generalizes. It can be applied to:
- ARQ during Phase 2: at each critical question, "what am I extracting? why this question for this argument? how does it help me evaluate?"
- Conceptual textbook reading at section breaks: "what am I tracing? why this derivation? how does it connect to the chapter goal?"

In these cases, frequency drops to once per major section (not per micro-transition like in Polya). The principle is the same: maintain plan-execution coherence.

## Source

- Schoenfeld 1985 *Mathematical Problem Solving*
- Schoenfeld 1992 "Learning to think mathematically" handbook chapter
- wiki concept: `schoenfeld-framework`

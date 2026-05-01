# Hint Escalation — Event-Based, Not Time-Based

When invoked: every help moment in tutor mode. The level (0-4) chosen, the trigger that authorized escalation, and the user's response to the hint are all logged. This file is the canonical specification of *when* a hint is allowed and *how* the next escalation gates open.

The failure mode this protocol is built against: **hint-as-shortcut**. Time-based hint rules ("if 5 minutes pass with no progress, give a hint") produce hint-spam: the user learns to wait out the timer and consume the answer without engaging the problem. Aleven et al. 2016 (intelligent tutoring system meta) and Razzaq & Heffernan 2010 found that:

- Hint *availability* alone correlates with abuse (rapid clicking through hints to the bottom level).
- Time spent on each hint distinguishes learning from abuse: < 10 seconds on a hint correlates with non-learning; ~20 seconds correlates with use.
- Event-triggered, on-demand hints with a paraphrase gate produce learning gains; time-triggered or proactive hints do not.

The skill therefore enforces three rules around every hint event.

## Rule 1 — Hints are on-demand only, never proactive

The skill **does not volunteer hints**, even after a wrong answer. Specifically:

- **Banned**: silently revealing the next step after a failed attempt.
- **Banned**: "It looks like you're stuck — here's the answer."
- **Banned**: showing the correct answer alongside the user's wrong answer "for comparison."
- **Banned**: any time-based escalation ("you've been stuck 5 minutes, here's hint 1").

**Allowed** triggers (each is an explicit user-or-content event):

| Trigger | What it looks like |
|---|---|
| Explicit request | User says "hint", "도움", "힌트 줘", "다음 단계", or names a level ("level 2 hint please") |
| Unfamiliar-step start | User identifies a step they have not seen before and explicitly asks for a worked move |
| Self-correct-impossible error | User attempts, sees the error, attempts again, and explicitly states they cannot self-correct |
| Hint-not-understood | User received a hint and explicitly states they do not understand it; next-level hint is allowed only on this trigger |

Without one of these triggers, the skill does not hint. If the user is silent or struggling, the skill **prompts for a Schoenfeld 3-question** ("What are you doing? Why? How does it help?"), not a hint.

## Rule 2 — Read-and-paraphrase gate between escalations

Once a hint is given (any level, level 1 onwards), the next escalation requires the user to **paraphrase the hint in their own words** before the skill will issue the next-level hint. The paraphrase is the gate.

Concrete sequence:

1. User triggers hint → skill issues level-N hint
2. Skill prompts: "Before continuing, paraphrase that hint in your own words. What is it asking you to do?"
3. User paraphrases.
4. **If paraphrase matches the hint's intent**: user attempts the problem with the hint applied. If still stuck, the next-level hint is now available on a new explicit-request trigger.
5. **If paraphrase is missing, surface-only, or wrong**: skill says "Re-read the hint and try again — what are the words actually telling you to do?" The next escalation is **blocked** until the paraphrase passes.

This implements the 9-vs-19-second finding: the gate forces the user to spend processing time on the hint, which is the difference between learning and abuse.

If the user types only "ok" or moves directly to "next hint please", the gate is not satisfied.

## Rule 3 — Time-on-hint logging and abuse detection

For each hint event, log:

```yaml
hint_event:
  level: 2
  trigger: "explicit_request" | "unfamiliar_step" | "self_correct_impossible" | "hint_not_understood"
  hint_text: "<the hint shown>"
  paraphrase: "<user's paraphrase>"
  paraphrase_passed: true | false
  time_on_hint_seconds: 14   # from hint shown to user's next action
  next_action: "attempted_problem" | "requested_next_hint" | "abandoned"
```

**Abuse signal**: `time_on_hint_seconds < 10` AND `next_action == "requested_next_hint"`. When detected:

1. The next escalation is **refused** with a one-line reason: "That hint had less than 10 seconds of attention; sit with it before the next one."
2. The session-end `session_health.hint_abuse` flag is set if this fires more than once per chapter.

## The hint level ladder (with event-trigger gating)

This replaces the time-window ladder. Each level has a specific trigger condition; without the trigger, the level is not authorized.

| Level | Description | Authorized when |
|---|---|---|
| 0 | Self-solved, no hint | Always; default state |
| 1 | Re-read prompt | User explicitly requests; or after one failed attempt that the user has stated they cannot self-correct |
| 2 | Schema lookup ("which category is this?") | Level 1 hint paraphrased; user explicitly requests next |
| 3 | Worked example shown; user re-attempts | Level 2 paraphrased; user explicitly requests next; **and** the chapter has a related worked example available |
| 4 | Full reveal of the solution | Level 3 paraphrased + user-attempted; user explicitly requests; **and** the user provides the level-4 reflection record (per `references/methods/polya.md` § "Level-4 reflection") *before* the reveal |

**Productive failure window** (problem-driven chapters): inside the first 15-30 minutes of a problem, levels 2-4 are rate-limited. Level 1 (re-read) is always available. The window itself is event-triggered, not time-triggered: it begins when the user starts the problem and ends when the user explicitly says "I am stuck and want a level-2+ hint" or 30 minutes have elapsed (this is the only time-bounded gate in the protocol, and it is a *cap* on struggle, not a *trigger* for help).

After level 3 (worked example) is shown, the **backward-fading completion-problem sequence** runs before any further unguided attempts (see `references/methods/backward-fading.md`). Going from "saw worked example" directly to "tried unguided variant and got it" without fading is the worked-example-fluency-illusion failure mode.

## What the skill says when refusing a hint

When a hint is requested without an authorized trigger or with the gate unsatisfied, the skill responds with the **specific reason** (not generic refusal):

- "You haven't paraphrased the previous hint yet. What is it telling you to do, in your own words?"
- "That hint had 6 seconds of attention; the next-level hint is blocked until you sit with this one."
- "You're at minute 8 of the productive-failure window. Level 1 (re-read the problem) is available; level 2+ opens at minute 15 or when you explicitly say you're stuck."
- "No new evidence since your last attempt — what specifically did you try? If you've tried something and it failed, name the failure first."

The refusal is data: log it as `hint_refused: { reason, level_requested }`. A pattern of refusals on the same trigger is a calibration cue that the user is treating hints as the path of least resistance, which is exactly what the protocol is designed to surface.

## Anti-patterns

- ❌ **Time-window auto-hints.** "5 minutes passed → hint." Replace with event triggers.
- ❌ **Proactive answer disclosure.** Showing the next step after a wrong attempt without a request.
- ❌ **Skipping the paraphrase gate.** Issuing level-N+1 hint right after level-N without intermediate paraphrase.
- ❌ **Counting requests as triggers.** A request is necessary but not sufficient; the previous-level paraphrase must also have passed.
- ❌ **Logging only the level.** Without the trigger, paraphrase, and time-on-hint, the abuse signal is invisible.
- ❌ **Refusing without naming the reason.** The user needs to know why the hint is blocked, otherwise the refusal looks arbitrary and erodes trust.

## Cross-references

- `references/methods/polya.md` — hint hierarchy basic structure and level-4 reflection record
- `references/methods/backward-fading.md` — what runs after a level-3 worked example
- `references/failure-modes.md` Failure 1 (hint abuse) — session-level signal threshold (level 4 called > 3× per session)
- `references/methods/newman.md` — when the user gets a problem wrong, Newman runs *before* level-3 worked-example escalation, not after

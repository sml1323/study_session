# Backward Fading — Completion Problems After Worked Examples

When invoked: the user just studied a worked example (or the chapter just presented one) and asks for "비슷한 문제 줘" / "another one to practice" / "더 풀어볼 문제". This is the moment that decides whether the worked example produces a transferable schema or a fluency illusion.

The default move — handing the user a parallel **unguided** problem — is wrong. Without scaffolding, surface-feature mapping dominates and the deep structure the worked example just demonstrated does not transfer. The replacement is **backward fading completion problems** (Renkl & Atkinson worked-example research): the next problem the user attempts is structurally identical to the worked example except the **last step** is blanked out. Each successful completion fades one more step from the back. The user reaches an unguided problem only after several faded passes.

## The fading sequence

Run this sequence after every worked example, problem-driven chapter or otherwise. Do not skip steps.

| Pass | What you give the user | What the user does |
|---|---|---|
| 0 (study) | full worked example with all steps shown | reads + self-explains each step |
| 1 (fade-1) | full problem statement; all steps shown except the **last** is replaced with `[ … ]` | completes the last step; explains why it follows |
| 2 (fade-2) | same problem family; steps 1..N-2 shown; last 2 blanked | completes the last 2 steps with self-explanation at each |
| 3 (fade-3) | only the first 2 steps shown | completes the rest |
| ... | continue fading from the back | self-explanation prompt at every blank |
| N (unguided) | problem statement only | full solution attempt |

Two invariants:

1. **Fade from the back, never from the front.** The first step is the hardest to recover (problem identification + plan); leaving it visible scaffolds the most fragile part. Removing the last step first scaffolds the part the user is most likely to be able to complete and gives a calibration signal: if the user fails the last step, they have not yet encoded the final move; do not advance.
2. **Self-explanation prompt at every blank.** "Why does this step follow from the previous one? What rule / theorem / move is being applied?" — captured in the polya log alongside the step. A blank without the SE prompt is just hidden work; it does not produce schema.

## When to advance vs hold

After each fade pass:

- **All blanks completed correctly + SE matches the principle** → advance to next fade level
- **Blank completed but SE missing or surface-paraphrase** → repeat the same fade level with fresh SE prompt; do not advance
- **Blank wrong** → drop back one fade level (re-show one more step); never fade further until that level passes
- **User explicitly asks for unguided** → allow it, but log `fading_skipped: true` and do not retroactively credit subsequent attempts as evidence of schema

## What to log

Inside the chapter note `polya_logs[].fading`:

```yaml
fading:
  source_worked_example: "Polya Part III Ex.7"   # the example studied at pass 0
  passes:
    - level: 1
      blanks: ["last step (substitute t = ...)"]
      user_completion: "..."
      self_explanation: "..."
      result: pass | fail | partial
    - level: 2
      blanks: ["substitute t = ...", "differentiate"]
      ...
  reached_unguided: true | false
  fading_skipped: false
```

## Anti-patterns

- ❌ **Parallel unguided after a worked example.** "Here's a similar problem, solve it from scratch." This is the default the skill is replacing. It produces surface-feature transfer at best.
- ❌ **Fading from the front.** Hiding the problem statement / plan first and showing the execution. The execution is the part the user can already mimic; the plan is the part that schema-forms.
- ❌ **Fading without self-explanation.** Blanks alone reduce to fill-in-the-blank pattern matching.
- ❌ **Advancing on a fail or partial.** The fade level is a calibration signal; do not soften it.
- ❌ **One faded pass then unguided.** A single fade is not the protocol; the sequence runs through several fade levels before unguided.

## When the chapter only has one worked example

Generate the fading variants from the single example:

- Pass 0: study the example
- Pass 1: same problem, last step blanked, with **slightly different numbers** (so the user is not just recalling)
- Pass 2: same problem family, fade-2, **different specific instance** (preserve deep structure, change surface)
- ...continue until unguided on a fresh instance

The variation comes from the surface (numbers, named entities) while the deep structure (the move sequence) is preserved. This is what distinguishes Renkl/Atkinson fading from rote drill.

## Interaction with productive failure window (problem-driven chapters)

The productive-failure window (15-30 min unguided struggle before any worked example) and backward fading are sequential, not alternative:

1. Productive failure first — user attempts the problem unguided
2. If failure or partial: study the worked example
3. **Then run the backward-fading sequence** on related problems before returning to unguided

Without step 3, the worked example is consumed but the schema does not form for transfer. The fading is the bridge from worked-example consumption to unguided solution.

## Cross-references

- `references/methods/polya.md` — 4-step + Schoenfeld; fading nests inside Step 3 (Carry Out) for follow-up problems
- `references/failure-modes.md` Failure 4 — productive struggle window
- `references/methods/hint-escalation.md` — hint level 3 (worked example) is the entry to backward fading
- `references/book-types.md` problem-driven — sequence is: productive failure → worked example (level 3 hint) → backward-fading completion problems → unguided variant

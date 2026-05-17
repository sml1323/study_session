# Argument Reading — Argument-driven Chapter Sub-routine (5-step)
<!-- TODO evidence-tag - see references/evidence-labels.md; this files thresholds/policies are not yet labeled -->

When invoked: a chapter classified `argument-driven`, or a conceptual chapter on a politically/identity-laden topic where refutation-text would risk backfire. The sub-routine is a 5-step protocol designed to engage the chapter's argument as an argument (not as content to summarize), and to do it in the specific way that distinguishes top-tier critical readers from the median: structure first, then map, then dialogic engagement, then targeted re-reading. Plain repeated reading does not improve argument comprehension; structure-aware reading does.

## Why this sub-routine exists

When a passage is read for surface comprehension, even skilled adult readers identify the central claim only at chance levels in some studies. When given explicit instruction in claim/reason/warrant structure first, identification jumps substantially and stays elevated on transfer. A second finding consistently replicates: plain re-reading on top of structure instruction adds essentially zero — the active ingredient is the structure scaffold, not the time-on-text. The 5-step protocol below turns those two findings into a sequence the user can run on every argument-driven chapter.

## When to invoke

Invoke when:

- chapter classified `argument-driven` (Mill, Sandel, philosophy paper, op-ed, policy whitepaper)
- chapter classified `conceptual` but on a politically/identity-laden topic where refutation-text would backfire
- user explicitly requests "I want to break this argument down" on any chapter

Do **not** invoke on:

- pure exposition chapters (textbook concepts; use refutation-text if conceptual + non-political)
- problem-driven chapters (use Polya / Newman / proof-comprehension)
- reference / lookup material

## The 5-step protocol

### Step 1 — Structure pass (no paraphrase)

First read of the chapter. The reader's *only* task is to identify the chapter's argumentative skeleton:

- the central claim (one sentence; the chapter's punchline)
- the principal reasons given for it (1-5; not every supporting paragraph, the load-bearing ones)
- the warrants — implicit or explicit — that connect each reason to the claim
- any explicit objections the chapter addresses, and the chapter's response to each

Output as:

```yaml
argument_structure:
  central_claim: "<one sentence>"
  reasons:
    - reason: "<r1>"
      warrant: "<the bridge from r1 to claim — often unstated; reader infers>"
    - reason: "<r2>"
      warrant: "<...>"
  objections_addressed:
    - objection: "<o1>"
      chapter_response: "<...>"
```

**Forbidden during Step 1**: paraphrasing the chapter's full content, taking PIMEQ notes, evaluating, agreeing or disagreeing. The structure pass is structure only. Eval comes in Step 4.

If the user cannot identify the central claim after one structure pass, that is itself a signal — surface it: "Central claim was not identified on structure pass. Skip ahead to Step 4 dialogic; you'll re-read targeted passages there."

### Step 2 — Argument map (3-7 nodes)

Build a small node-and-edge map of the structure from Step 1. Hard limits:

- **3-7 nodes total** (Cowan capacity bound; more than 7 means the chapter has been over-decomposed)
- nodes: one per claim or reason
- edges: labeled with `supports`, `requires`, `refutes`, `assumes`, `presupposes`
- explicit-only — do not add inferred sub-arguments at this stage; the map is for the chapter's own structure

The map can be ASCII, mermaid, hand-sketch, or a graphic-organizer style. The constraint is the node count, not the medium. **Skill does not generate the map**; user constructs it (constructed graphic organizers outperform consumed ones).

If the user maps every paragraph as a separate node, the map has the wrong granularity — it is not an argument map but a paragraph map. Reduce to the 3-7 load-bearing nodes.

### Step 3 — IH prime (30 seconds, before Step 4)

Just before Step 4 (dialogic engagement), a 30-second intellectual-humility prime:

> "If the chapter's central claim turns out to be right, what would that imply about [adjacent case the chapter doesn't discuss]? If it turns out to be wrong, what would have to be true instead?"

Both branches are answered briefly (1-3 sentences each). The point is to re-orient the user from default acceptance/rejection to *evaluation conditional on evidence*. This step is short and non-recursive — do not let it expand into a full debate.

Capture as:

```yaml
ih_prime:
  if_claim_right: "<implication>"
  if_claim_wrong: "<what would have to be true>"
```

### Step 4 — Solo dialogic engagement

The user constructs the **strongest** counterclaim to the chapter's argument — not a strawman, the version of the opposing view that would be hardest to defeat. Then the user traces how the chapter does or does not respond to that strongest counterclaim, and weighs in.

Output:

```yaml
dialogic:
  strongest_counterclaim: "<the user's steelman of the opposing view>"
  chapter_response: "<does the chapter address this? where? how?>"
  gap: "<what the chapter does NOT address; or where the chapter's response is weakest>"
  user_position: "<after considering the gap — do you accept, partially accept, or reject the chapter's claim, and why?>"
```

If the user's counterclaim is weak (short, easily defeated, or mostly identity-coded), surface it: "이건 strawman에 가까움. 더 강한 버전 — 이 입장을 진지하게 옹호하는 사람은 어떤 reason을 들까?" Push back until the steelman is genuinely strong.

This step replaces the standard `failure-modes.md` Failure 6 (echo chamber) check on argument-driven chapters — the steelman discipline is now structurally enforced as part of the chapter, not as a session-end guard.

### Step 5 — Context-stance reading + targeted re-reading

After Steps 1-4, if any node in the argument map is still weakly understood (the user's reasoning at Step 4 surfaced gaps in specific reasons), do a **targeted re-reading** of just the relevant passages — not a full re-read of the chapter. Plain re-reading from the start adds essentially nothing on top of Step 1 + 2; targeted re-reading on identified gaps is what works.

Set context and stance for the re-read:

> "Re-read §X with this question: does the author's argument here actually support the claim in §Y, or is it support for a weaker / different claim? Read with that question in mind, not for general comprehension."

Do not re-read sequentially. If the gap is in the chapter's response to a counterclaim, re-read that section. If the gap is in a key warrant, re-read the section that justifies it.

## Calibrate phase (Step 2b transfer for argument chapters)

The Step 2b situation-model transfer question for an argument-driven chapter is naturally framed as:

- "Here is a NEW case [briefly described]. If the chapter's central claim is right, what does it imply about this case? If it's wrong, what should you conclude about this case instead?"

This forces the user to apply the chapter's argument structure to a case the chapter didn't discuss — exactly the situation-model test.

For high-stakes argument chapters, also include a structural transfer:

- "Here is a different argument with similar structure (claim + reasons + objections). Map it using the same skeleton you built in Step 2. Where do its load-bearing reasons sit relative to the chapter's?"

## What this protocol is *not*

- Not Toulmin schema reading. Toulmin is strong for argument *writing*; reading-comprehension RCTs are mixed, and argument-schema instruction (claim/reason/warrant) is more robust.
- Not full ARQ Core 7 on every paragraph. ARQ stays at the argument unit and is invoked from inside Step 1's structure pass when a specific Optional 5 trigger fires; see `references/methods/arq.md` ARQ Trigger Discipline.
- Not unlimited debate. Step 3 is 30 seconds; Step 4 is one counterclaim, well-constructed; Step 5 is targeted re-reading only.

## Cross-references

- `references/methods/arq.md` — ARQ depth ladder; Step 1 structure pass calls into ARQ Level 1 (issue / conclusion / reasons)
- `references/methods/refutation-text.md` — alternative for non-political conceptual chapters
- `references/calibration.md` — Step 2b transfer template for argument-driven chapters
- `references/failure-modes.md` — Failure 6 (echo chamber) is structurally enforced by Step 4 of this protocol
- `references/annotation-typology.md` — `E` (Evaluate) and `Q` (Question) PIMEQ prefixes are used during Step 1's structure pass

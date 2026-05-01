# Proof Comprehension — Math Chapter Sub-routine (7-facet)

When invoked: a chapter contains one or more proofs. The sub-routine spec is from Mejía-Ramos et al.'s 7-facet model of mathematical proof comprehension, which decomposes "did you understand this proof?" into 3 local facets (line-by-line) and 4 holistic facets (whole-proof). Reading a proof differently from reading prose is the point: prose is read for content, a proof is read for *warrant verification* (each line must be checked against the line above).

## Why this sub-routine exists

A reader who is comfortable with prose can often replay the surface of a proof — "the proof shows X using technique Y" — without having actually verified that line N+1 follows from line N. Eye-tracking work on expert vs novice proof reading shows the experts' distinguishing move is **inter-line gaze**: looking at line N+1, then back to line N, then forward again, checking that the warrant holds. Novices stay on the surface (notation, reformulating each line in isolation).

The 7 facets give a checklist that splits "I followed the proof" into measurable parts, so the user can self-check at the right granularity instead of vaguely "getting it."

## When to invoke

Invoke when a chapter contains:

- formal proofs (mathematics, mathematical logic, theoretical CS, rigorous physics derivations)
- informal-but-deductive arguments where line-to-line warrant matters (philosophy proofs, formal economics derivations)

Do **not** invoke on:

- back-of-envelope estimations (Fermi problems): use Polya instead
- experimental result narratives (here's the data, here's the conclusion): use the standard PDP loop
- proof sketches without enough detail to verify line-by-line: the sub-routine has nothing to operate on; ask the user to flag this and read the chapter as conceptual prose

## The 7 facets

For each proof in the chapter, the sub-routine asks the user to engage with **at least 1-3 facets** (chosen at plan time based on intensity and chapter centrality). Running all 7 on every proof is overkill and reproduces the form-fatigue failure mode the rest of the skill is designed to avoid.

### Local facets (line-by-line, 3)

1. **Statement meaning** — for each non-trivial line, can the user paraphrase the line's claim in plain language? (catches: notation that the user reads but doesn't parse)
2. **Logical status** — does the user know what *role* this line plays (assumption / definition unfolding / lemma application / case split / contradiction setup / final assertion)?
3. **Chaining** — at any chosen line N, can the user explain how N follows from the lines preceding it (which premises, which inference rule, which lemma)? This is the inter-line gaze move made explicit.

### Holistic facets (whole-proof, 4)

4. **High-level idea** — can the user state the proof's core idea in **one sentence** without notation? ("Diagonalize the relation and show the diagonal can't be on the list.")
5. **Modules / proof structure** — can the user list the proof's major sections (setup → key lemma → main argument → discharge → conclusion) and what each contributes?
6. **Methods / techniques** — can the user name the proof technique (induction, contradiction, contrapositive, construction, pigeon-hole, ε-δ, generating function, ...) and recognize it as one they could deploy elsewhere?
7. **Examples / non-examples** — can the user produce one example the proof's conclusion applies to, and one near-miss case where the proof would *not* apply (a hypothesis is needed)?

## Operational protocol

### Plan phase (per chapter)

1. Identify each proof in the chapter (locator: `§3.2 Theorem 3.4 proof`, etc.).
2. For each proof, decide a **facet sample**: 1-3 facets chosen by intensity + chapter centrality.
   - Light intensity: 1 facet (default: facet 4 — high-level idea).
   - Standard intensity: 2 facets (default: facets 4 + 6 — high-level idea + technique name; pick a third specific to the proof if it teaches a method).
   - Deep intensity: 3 facets, including at least one local facet (default: facets 3 + 4 + 6 — chaining at one chosen line + high-level idea + technique).
3. For the **chapter's central proof** (if any), always include facet 3 (chaining) at one user-chosen line — this is the move that distinguishes proof-reading from prose-reading.
4. Log the selection as:

```yaml
proof_protocol:
  - proof: "§3.2 Thm 3.4"
    facets_to_check: [4, 6]
    is_central: false
  - proof: "§4.1 Main Theorem"
    facets_to_check: [3, 4, 6]
    is_central: true
    chaining_line_choice: "user picks at execution"
```

### Tutor phase (during proof reading)

For each proof, after the user has read it once:

- **Facet 4 (high-level idea)**: "이 증명의 main idea를 한 문장으로 — notation 없이."
- **Facet 6 (methods)**: "어떤 기법? 이 기법을 본 다른 증명이 있어?"
- **Facet 3 (chaining)**: User picks any line N (>3) in the proof. "Line N이 어떻게 line N-1, N-2, ... 에서 따라오는지 설명. 어떤 premise / inference rule / lemma?"
- **Facet 1 (statement meaning)**: "Line K의 statement를 plain language로 — notation 없이."
- **Facet 2 (logical status)**: "Line K는 어떤 역할? definition? lemma application? case split? contradiction setup?"
- **Facet 5 (modules)**: "이 증명의 큰 단락은? setup, key lemma, main argument, ...?"
- **Facet 7 (examples)**: "이 결론이 성립하는 예시 하나. 그리고 거의 성립하지만 hypothesis 하나가 빠져서 무너지는 near-miss 하나."

If the user fails a chosen facet on first attempt, do not immediately reveal — apply the standard pump → hint → prompt → assertion ladder (see `references/llm-tutor-design.md`). The most common failure is facet 3 (chaining); the typical hint is "look at line N-1 — what definition is being unfolded?" or "this line uses lemma X from §Y; recall what X says."

### Calibrate phase (Step 2b transfer for proofs)

For situation-model transfer (Step 2b) on a proof-heavy chapter, the transfer question is *adapt the proof technique*, not "explain the proof":

- "Here is a NEW theorem statement. Sketch a proof using the same technique as §3.2 Thm 3.4. Where does it adapt directly? Where does an analog of the key lemma have to be re-established?"

This catches readers who memorized the proof's surface but did not internalize the technique.

## Common failure modes

- **Notation as evidence of understanding**: user re-reads the proof and feels the notation flow; this is fluency illusion at the proof level. Facet 3 (chaining) breaks it.
- **Technique-name without recognition**: user can name the technique ("oh, that's a diagonal argument") without being able to deploy it on a new theorem. Step 2b transfer on a NEW theorem statement breaks it.
- **Skipping non-trivial lines**: user reads the line, says "yes, OK", moves on, but cannot reproduce why the line follows. Facet 1 (statement meaning) on a randomly chosen line catches this.
- **One-shot facets-all**: doing all 7 facets on every proof creates form fatigue and burns the protocol's credibility. Stick to the 1-3 facet sample.

## Cross-references

- `references/calibration.md` — Step 2b transfer template for problem-driven / proof-heavy chapters
- `references/methods/polya.md` — Polya is for problem-solving (open-ended); proof-comprehension is for verifying given proofs. Different work, different sub-routines.
- `references/llm-tutor-design.md` — pump → hint → prompt → assertion ladder for facet failures
- `references/book-types.md` — problem-driven and conceptual chapters (math sub-genre) trigger this sub-routine

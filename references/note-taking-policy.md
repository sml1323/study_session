# Note-Taking Policy — Refusal List, Reframe Map, Recommended Set
<!-- TODO evidence-tag - see references/evidence-labels.md; this files thresholds/policies are not yet labeled -->

When invoked: the user mentions a popular note-taking system, asks "should I use [system]?", or describes a workflow built around one. This policy file defines what the skill **refuses to recommend**, **how to reframe** when the user is already using a refused system, and **what the skill recommends instead**.

The empirical claim: most popular note-taking systems sold under productivity branding lack direct retention-or-transfer evidence. Their effects, where measured, reduce to retrieval practice + spacing + generative encoding — mechanisms the skill already enforces through its core protocol. Recommending the system instead of the underlying mechanism wastes operator overhead and gives the user a productivity-hobby that competes with the actual learning behavior.

The skill's stance is:

- **Do not recommend** systems on the refusal list.
- **Do not refuse the user** when they are already invested in one of these systems.
- **Reframe** their existing practice in mechanism terms, so the parts that produce learning are kept and the ritual overhead is dropped.
- **Recommend** only the moves with direct evidence.
- **Do not adopt a single default workflow.** R11 ethnography of 6 first-party power-user voices found load-bearing disagreements on highlighting, organization, AI use, and even on whether the apparatus is the problem. The defensible recommendations are *operations*, not tool stacks. See "The 6 power-user voices" below.

## The 6 power-user voices (R11 power-user-ethnography-extended)

The convergence Round 9 reported on PKM workflow shape is **shallower than it appears**. Round 11 widened the sample to 6 first-party voices that disagree with each other on load-bearing questions:

| Voice | Capture stance | Highlight stance | Organization | AI use |
|---|---|---|---|---|
| **Sönke Ahrens** | pen-paper while reading | reject — no marking books | atomic permanent notes (Zettels), sentence-embedded links | none named |
| **Maggie Appleton** | mobile inbox → Craft/Obsidian → public garden | implicit (notes carry stage markers) | stage (seedling / budding / evergreen) + content-type stratification | none named |
| **Linus Lee** | Pico (ephemeral) + Ligature (long-term) | build-your-own AI overlay on the reading surface | collapse task/notes binary — unit is "thing-I-might-act-on" | self-built (Notation, Monocle, Reverie) |
| **Cal Newport** | minimal — monthly reading-list reflection | reject — book in your hand is the system | none — depth-first cognitive practice | **anti-AI-summary on principle** |
| **Steph Ango (Obsidian CEO)** | unique-note hotkey, timestamped | implicit | self vs other (vault root vs References vs Clippings) — anti-PARA | none named |
| **Eleanor Konik** | Readwise Reader as universal funnel | embrace, tagged with action-tags at capture | LLM converts highlights → claim statements → Obsidian atomic notes | LLM as middle layer; Version History Diff for verification |

### Where they agree (the operations)

- **Capture surface must be one place.** Multi-app capture loses material. The specific app does not matter; the *one place* property does.
- **Source notes and personal-thought notes must be separable**, regardless of which split semantics you use.
- **Review is required.** None treat highlights or saved articles as the final state.

### Where they disagree (the disagreements are the point — do not paper over)

- **Highlighting**: Ahrens and Newport reject outright. Forte (R9), Konik, Readwise users embrace. Half the canonical voices reject the "highlight everything then process" pattern.
- **Organization**: PARA, Zettelkasten ID schemes, self-vs-other, stage-based, action-readiness, and "no system / just deep work" all coexist among practitioners with strong outcomes. Wiki's prior implication that "MOC + tag + project structure" is the convergent answer is **overstated**.
- **AI**: Konik integrates LLMs as a middle layer with explicit verification. Lee builds his own AI-overlay reading interface. **Newport treats AI summaries as actively harmful** to the cognitive rewards of slow reading. The "AI co-reader is inevitable" stance has at least one strong dissenter.
- **The system itself**: Newport is the strongest contrarian. He uses almost no PKM apparatus and asserts that the dominant tooling **may itself substitute for the deep work it claims to support**. Round 9's silence on this critique was a gap.

### The Newport critique (quote when the user wants to add tools)

> Power users frequently report that the apparatus they built to support their reading has become the work itself — they spend more time tending the system than reading. The Newport position is that this is not a bug; it is the central failure mode of the entire PKM category. When the skill is asked to recommend "what tool should I add," the honest answer often is "none."

Surface this critique once per session when the user asks the skill to recommend a new tool / system / workflow layer. Do not lecture; one short paraphrase is enough.

### Implications for skill recommendations

- The skill **does not recommend a single default workflow**. The defensible recommendations are the *operations* (atomic rewriting, reflection forcing function, single capture surface, anti-throughput) — not specific tool stacks.
- The skill **respects strict-no-PKM as a first-class choice** (Newport mode), not a fallback.
- Highlighting-first workflows carry an empirical caveat: popular but annotation alone is null on comprehension without layered mechanisms (see `references/annotation-typology.md`).

## Refusal list — systems the skill will not recommend

| System | Why on the list |
|---|---|
| **Adler — *How to Read a Book* 4-step marking** | The four reading levels (elementary, inspectional, analytical, syntopical) and the marking discipline are coherent prescription but lack RCT-grade direct evidence for retention or transfer over single-careful-read + chunk-boundary recall + Phase 3 calibrate. |
| **Full Zettelkasten / Luhmann slip-box ritual** | The atomic-note + linking discipline is appealing and produces a well-organized archive, but the learning effect (when measured at all) reduces to retrieval practice on the cards. The ritual overhead (atomic granularity, IDs, link-density audits) competes with retrieval frequency. |
| **PARA structural framework** | A directory taxonomy (Projects / Areas / Resources / Archive) is a productivity scheme, not a learning intervention. No retention evidence. |
| **Multi-page sketchnoting ritual** | Drawing entire-chapter visual notes. The Wammes 2016 drawing-effect evidence is for **isolated key terms / definitions**, not for chapter-scale visual summary. Chapter-scale sketchnoting consumes the time that retrieval should occupy. |
| **Speed-reading apps (Spritz / Reedy / Spreeder / Outread)** | RSVP and saccade-reduction techniques cap effective reading rate around 250-300 wpm for prose with comprehension intact (`references/reading-rate-evidence.md` if present). Apps that promise 600-1000+ wpm trade comprehension for fluency. |

When the user names one of these systems and asks whether to use it: name the empirical gap directly, suggest the underlying mechanism as the recommendation. Do not equivocate.

## Reframe map — when the user is already using a refused system

If the user is committed to a refused system (already has 2,000 Zettelkasten cards; already runs a PARA tree; already sketchnotes), the skill does **not** insist they abandon it. The investment is sunk and the system is not actively harmful in itself. Reframe instead: keep the artifacts, surface the mechanism that does the learning work, and shift the user's attention to that.

| User's existing practice | Reframe (what to call it from now on) | What the skill helps with |
|---|---|---|
| **Zettelkasten cards** | "Each card is a retrieval-practice cue. The card's title is the prompt; the card's body is the answer." | Generate spaced retrieval queue from cards (1d/1w/1m); track per-card recall accuracy; do not micromanage card linking. |
| **PARA Projects folder** | "PARA Projects is your spaced re-engagement queue. Each project's chapter notes are the items." | Hook the spaced-retrieval scheduler into the Projects folder; ignore Areas/Resources/Archive for learning purposes. |
| **Sketchnotes** | "Drawing for key-term encoding (Wammes 2016)." Limit to 3-5 key terms per chapter, drawn after Phase 3 textbase recall. | Replace whole-page sketches with key-term drawings; the chapter's sketchnote becomes a 5-term icon set, not a 1-page narrative. |
| **Adler-style chapter marking** | "Selective annotation with PIMEQ prefixes (`references/annotation-typology.md`)." Adler's marking discipline is one source of the underlying behavior; rename it and align the prefixes. | Convert any existing un-prefixed annotations to PIMEQ at chapter end; do not run Adler's analytical-reading 4-stage as a separate ritual. |
| **Highlight-only (no prefix)** | "Bare highlights without a PIMEQ prefix do not satisfy chapter annotation." | Conversion at chapter end is required; raw highlights are intermediate state, not the end state. |

The reframe is the move. Do not lecture the user about why the system is empirically thin — name the mechanism, show how their existing artifacts feed it, move on.

## Recommended set — the moves with direct evidence

These are the moves the skill recommends affirmatively. Each is grounded in the citations in `references/calibration.md` and `references/llm-tutor-design.md`.

| Move | Evidence anchor | Where the skill applies it |
|---|---|---|
| **Retrieval practice (closed-book recall)** | Karpicke & Blunt 2011; Roediger & Karpicke testing-effect literature | Chunk-boundary recall every 5-10 min during Phase 2; Phase 3 textbase recall (Step 2a); spaced retrievals at 1d/1w/1m. |
| **Spacing** | Cepeda et al. 2008 (spacing-effect meta) | Phase 3 default = next-session warmup; spaced re-engagement queue; daily-floor commitment device (`references/spacing-policy.md`). |
| **Interleaving** | Rohrer & Taylor 2007; problem-driven cross-chapter mixing | `references/book-types.md` problem-driven and methodology — interleave related chapters before starting a new one. |
| **Drawing for KEY TERMS / definitions** | Wammes et al. 2016 (drawing-effect on isolated-word free recall; *QJEP*) — *citation: verified* | Phase 3 optional sub-step: pick 3-5 key terms from the chapter and sketch each. Not whole-chapter sketchnoting. |
| **Refutation text reading (for prior-misconception topics)** | Tippett 2010 meta on refutation texts | `references/methods/refutation-text.md` — invoked on conceptual chapters where the user has known prior misconceptions and the topic is not politically/identity-laden. |
| **Backward fading worked examples** | Renkl & Atkinson worked-example research | `references/methods/backward-fading.md` — runs after every worked example before unguided practice. |
| **Reading rate ceiling 250-300 wpm for prose with comprehension** | Reading-rate empirical literature | Speed-reading app claims above this are flagged; default skill pace assumes ~250 wpm for expository prose. |

## How to handle the user's "what should I use?"

Three default responses depending on context:

1. **User has no current system, asks what to use**: "Skill itself is the system. The four modes (plan / tutor / calibrate / compose) plus chunk-boundary recall and Phase 3 calibrate is the protocol. Chapter notes are the artifact. No separate note-system on top."
2. **User names a refused system, asks whether to adopt it**: "[System] does not have direct retention or transfer evidence beyond what retrieval practice + spacing already produce. The skill already enforces those. Adopting [system] adds ritual without adding evidence."
3. **User already uses a refused system**: reframe per the table above. Keep the artifacts, rename the activity to the mechanism, ignore the parts of the system that do not feed the mechanism.

## Korean STEM learner caveat

Most popular note-taking-system studies are in Western, English-language, undergraduate-or-graduate populations. Recommendations for Korean STEM learners (medical-school KMLE prep, PEET, CSAT advanced, engineering entrance prep) are **transfer hypotheses** — the underlying retrieval-practice / spacing mechanisms have broad evidence but the specific note-taking adaptations have not been measured in Korean STEM populations. Mark the hypothesis explicitly when surfacing recommendations to a Korean STEM user; do not present transfer as established.

The single recommendation with direct Korean STEM evidence is: **mock exams as the dominant retrieval signal in clinical/medical preparation** (Chung 2024 on Korean medical 4th-year mock exam outcomes). This is the only domain-specific anchor; everything else is transfer.

## Anti-patterns

- ❌ **Refusing the user's existing system without offering a reframe.** Sunk-cost commitment is real; the user will leave the skill before abandoning a 2,000-card Zettelkasten.
- ❌ **Treating Zettelkasten / PARA / sketchnote as primary learning interventions.** They are organizational schemes; the learning effect is in the retrieval and spacing they enable.
- ❌ **Recommending Adler as a reading framework.** Selective-annotation discipline is fine, but the four-level reading hierarchy adds ceremony without measured gain.
- ❌ **Whole-chapter sketchnoting.** The drawing effect is for isolated terms; chapter-scale visual notes are not what Wammes 2016 measured.
- ❌ **Speed-reading recommendations above 300 wpm with comprehension claims.** The evidence is the other direction.
- ❌ **Presenting a Western-population finding as established for Korean STEM users without the transfer caveat.** Honesty about the evidence gap is a feature, not a hedge.

## Cross-references

- `references/annotation-typology.md` — PIMEQ prefix discipline (the skill's own annotation system, which is what Adler-style marking gets reframed to)
- `references/spacing-policy.md` — daily floor, deadline anchor, FCI/BEMA self-diagnostic
- `references/methods/backward-fading.md` — what to do after a worked example
- `references/calibration.md` — retrieval practice as the load-bearing learning move
- `references/methods/refutation-text.md` — when refutation reading is invoked
- `references/ai-policy.md` — Konik's LLM middle layer (one of the 6 voices) is reframed as `scaffolded-only` AI use, not as note-taking-system endorsement
- wiki concept `power-user-ethnography-extended` — the source for the 6-voice table

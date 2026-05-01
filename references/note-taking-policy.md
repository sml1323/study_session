# Note-Taking Policy — Refusal List, Reframe Map, Recommended Set

When invoked: the user mentions a popular note-taking system, asks "should I use [system]?", or describes a workflow built around one. This policy file defines what the skill **refuses to recommend**, **how to reframe** when the user is already using a refused system, and **what the skill recommends instead**.

The empirical claim: most popular note-taking systems sold under productivity branding lack direct retention-or-transfer evidence. Their effects, where measured, reduce to retrieval practice + spacing + generative encoding — mechanisms the skill already enforces through its core protocol. Recommending the system instead of the underlying mechanism wastes operator overhead and gives the user a productivity-hobby that competes with the actual learning behavior.

The skill's stance is:

- **Do not recommend** systems on the refusal list.
- **Do not refuse the user** when they are already invested in one of these systems.
- **Reframe** their existing practice in mechanism terms, so the parts that produce learning are kept and the ritual overhead is dropped.
- **Recommend** only the moves with direct evidence.

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
| **Drawing for KEY TERMS / definitions** | Wammes et al. 2016 (isolated-word memory effect) | Phase 3 optional sub-step: pick 3-5 key terms from the chapter and sketch each. Not whole-chapter sketchnoting. |
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

# Evidence Labels — How Thresholds and Policies Are Tagged

The skill's reference files cite a mix of RCT-grounded findings, observational evidence, operational heuristics chosen for actionability, and placeholders waiting for verification. Treating all of them as equally authoritative produces over-confident hard rules where evidence does not support them. The four tags below name the gradient explicitly so reference content can be cited at the appropriate strength.

## The four tags

| Tag | Meaning | How the skill may cite it |
|---|---|---|
| `rct-strong` | Direct RCT verification exists for this threshold or claim. The specific number / shape is what the RCT measured. | **OK as a hard rule.** Can be cited in `Decision rules` and audit gates. |
| `observational` | Verified by observational study (eye-tracking, ethnography, network meta over non-RCT data, app-instrumentation) but no direct RCT on the specific threshold. | **OK as a strong guideline.** Cite with the study type; do not treat as hard rule unless converged across multiple observational sources. |
| `operational-heuristic` | Operational threshold chosen for actionability. No direct verification — picked so the protocol could run. May be named in a primary source but the *specific value* was not measured. | **Guideline only.** Do not cite as a hard rule in SKILL.md body. Surface as "first-cut" or "placeholder" when surfacing to user. |
| `placeholder` | Number or shape is undetermined — citation pending or evidence not yet located. May be wrong; flagged for replacement. | **Disclose to user.** Use only as a discussion starter, not as the protocol's commitment. Eligible for user override before being applied. |

## How tags appear in reference files

Tags are inline next to the threshold, table, or policy they qualify. Format varies by context:

- **In tables** — appended as an `Evidence` column, or a one-line note under the table summarizing per-row evidence levels.
- **In prose thresholds** — italic suffix on the sentence: `*[evidence: operational-heuristic]*`.
- **In YAML examples** — comment on the line: `score_prediction_gap: 5    # evidence: operational-heuristic`.

## Hard rule citation gate

When SKILL.md's body cites a numeric threshold or policy as a hard rule (e.g., "`abs_gap > 20` is an illusion signal — block promotion"), the cited reference's evidence tag must be `rct-strong` or `observational` with cross-source convergence. `operational-heuristic` and `placeholder` may still appear in body prose but must be surfaced as guidelines, not gates.

The audit signal: a `Decision rule` whose backing reference is tagged `operational-heuristic` is a drift candidate — surface it during the next iteration's review.

## How to escalate a tag

A tag can be upgraded when new evidence arrives:

1. `placeholder` → `operational-heuristic`: a primary source names the protocol or qualitative direction (even without the specific value).
2. `operational-heuristic` → `observational`: an observational study measures the specific threshold or close to it.
3. `observational` → `rct-strong`: an RCT measures the specific threshold.

Downgrades are also allowed (e.g., a re-read of a primary source reveals the claimed RCT was actually a single-cohort study with no control — downgrade to `observational`). Each tag change should be noted in the file's revision history.

## Coverage status (as of current iteration)

This iteration labels 6 high-risk reference files:

- `references/calibration.md`
- `references/spacing-policy.md`
- `references/ai-policy.md`
- `references/medium-policy.md`
- `references/methods/math-text-reading.md`
- `references/methods/scaffolded-ai-prompting.md`

Remaining reference files carry a `<!-- TODO evidence-tag -->` marker and will be labeled in a later iteration. Their thresholds should be cited cautiously until labeled.

## Cross-references

- All labeled reference files (see list above)
- `SKILL.md` — Decision rules cite labeled thresholds; hard rule citation gate above governs which tags may be cited

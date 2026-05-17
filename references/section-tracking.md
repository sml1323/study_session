# Section-Level Chapter Tracking
<!-- TODO evidence-tag - see references/evidence-labels.md; this files thresholds/policies are not yet labeled -->

The chapter is the *unit of completion*, but its interior is a sequence of sections. Tracking only `current_chapter` lets the skill mistakenly recommend "next chapter" when six conceptual sections of the current one are still unread. This file specifies how the skill records, advances, and gates on section state.

## Why section state is needed

The bug pattern that motivated this: a chapter with 7 conceptual sections, the user worked through sections 1.1–1.3, and the skill — seeing only `current_chapter: 1` — surfaced "Ch.2 가자?" as the next move. The remaining six sections of Ch.1 were invisible to the skill. The fix is to give the skill a structural view of the chapter so "어디까지 했나" is verifiable, not inferred from vibes.

The cost is one ToC scan per book at init (best-effort). The benefit is every subsequent session-start gets an unambiguous answer to "what comes next".

## Schema — `chapter_structure` in `books.yml`

Each book entry gets an optional `chapter_structure:` map, keyed by chapter id (string-quoted to keep YAML happy with mixed numeric/alpha ids like Polya's `"I"`).

```yaml
arq:
  current_chapter: 1
  chapter_structure:
    "1":
      title: "The Benefit of Asking the Right Questions"
      sections:
        - id: "1.1"
          title: "Critical Thinking to the Rescue"
          pages: "3-5"           # optional; verbatim from book if available
          status: covered
        - id: "1.2"
          title: "The Sponge and Panning-for-Gold: Alternative Thinking Styles"
          status: covered
        - id: "1.3"
          title: "An Example of the Panning-for-Gold Approach"
          status: used-as-exercise   # passage was training material; section's own narrative ¶ unprocessed
        - id: "1.4"
          title: "Panning for Gold: Asking Critical Questions"
          status: pending
        - id: "1.5"
          title: "The Myth of the Right Answer"
          status: pending
```

### Field reference

| Field | Type | Notes |
|---|---|---|
| `id` | string | Stable identifier. Prefer the book's own numbering (`"1.3"`, `"§2.4"`); fall back to `"1"`, `"2"`, … if the book doesn't number subsections. Keep it stable across PDF reflows. |
| `title` | string | Verbatim header text from the book. Don't rewrite or translate. |
| `pages` | string | Optional page range (`"13-15"`). Helps citation discipline; skip if uncertain. |
| `status` | enum | See below. Default `pending`. |

### Section status enum

A section is in **exactly one** of the following states. This enum is distinct from the chapter-level status enum in `state-schema.md` — they live on different axes (a chapter is `in-progress` while its sections are mostly `pending` with one `in-progress`).

| Status | Meaning | Set by |
|---|---|---|
| `pending` | Not yet processed. Default for a freshly extracted section. | init / lazy extraction |
| `in-progress` | Current chunk is inside this section; session ended before the section's chunk-boundary recall + PIMEQ closed out. | tutor mode (mid-section session close) |
| `covered` | Closed-book recall **and** PIMEQ annotation both ran on the section's narrative content. | tutor mode (clean section close) |
| `used-as-exercise` | The section's *prose was used as training material* for some method (ARQ application, Polya target, etc.) but the section's *own narrative claims* (the surrounding conceptual paragraphs that frame the example) were not processed via recall + PIMEQ. **This is learning debt.** | tutor mode (when the chunk targeted the embedded artifact, not the surrounding narrative) |
| `skipped` | User explicitly chose to bypass this section. The reason goes in the chapter note's Section progress block (see below). | explicit user request |

`covered` and `used-as-exercise` are *not interchangeable*. The latter means the user practiced a technique on the section's example but never wrote down or recalled what the section's own argument was. Treat it as a debt that surfaces at the next session-start.

## Decision rule — chapter completion gate

This rule joins the existing decision rules in `SKILL.md`:

> A chapter advances to `phase-3-pending` (or any "next chapter" recommendation) only when **every section has status `covered` or `skipped`**. If any section is `pending`, `in-progress`, or `used-as-exercise`, the chapter is incomplete. `used-as-exercise` sections specifically surface as **learning debt** — the next-chunk recommendation must propose processing the section's narrative ¶ before any other move.

Why: the chapter-level `phase-3-pending` is a measurement promise — Phase 3 will measure situation-model transfer over *the chapter's content*. Running calibrate over a chapter where one-third of the conceptual sections were never read produces a transfer score that doesn't mean what it claims.

## RESOLVE-time logic (next-chunk recommendation)

Inside the existing `RESOLVE context` step in `references/pdp-loop.md`, after determining `current_chapter`:

```
sections = book.chapter_structure[current_chapter].sections   # may be missing → see "lazy fallback"
uncovered = [s for s in sections if s.status not in ("covered", "skipped")]

if uncovered:
    next = uncovered[0]
    if next.status == "in-progress":
        recommend resuming `next` from where the previous chunk stopped
    elif next.status == "used-as-exercise":
        surface learning debt: "Section <id> was used as an exercise but its
        narrative ¶ was not processed. Next chunk = closed-book recall + PIMEQ
        on the section's own claims."
        recommend that as the next chunk
    else:  # pending
        recommend starting `next` as a fresh chunk
else:
    # chapter is complete at the section level
    chapter is eligible for `phase-3-pending` transition / next-chapter prompt
```

`chapter_structure` may be absent for older books (this feature is additive). Treat absence the same as the lazy-extraction failure case below: surface a one-shot "extract this chapter's section headers" sub-step on first re-entry, then proceed.

## Disambiguation — "다음 phase 가자"

If the user says "다음 phase로 가자" / "calibrate 가자" / "Ch.X 끝났어" while uncovered sections remain, **interpret it as "next section within the current chapter"**, not as a phase advance. Surface what's still uncovered and recommend the next section. Only honor a literal phase-3 / next-chapter request when the user names the next chapter explicitly ("Ch.2 가자") *and* the current chapter has no uncovered sections (or the user explicitly accepts that they're skipping the rest, in which case mark the remaining sections `skipped` with a note).

This protects against a known fluency-illusion path: the user feels they understood the example and wants to move on, while the conceptual scaffold around the example is still unread.

## Status transitions at chunk close

At the end of every chunk, the skill updates section status:

| Chunk shape | Section status set to |
|---|---|
| Closed-book recall + PIMEQ both ran on the section's narrative | `covered` |
| Section's prose was used as training material; narrative ¶ not processed | `used-as-exercise` |
| Session ended mid-section (no clean close) | `in-progress` |
| User said "이 섹션 건너뛸래" | `skipped` (record the reason in Section progress) |

If a chunk crosses multiple sections, update each section by what actually happened to *its own content*. A chunk that fully covered 1.4 and started 1.5 leaves 1.4 = `covered` and 1.5 = `in-progress`.

## Init flow — when `chapter_structure` is built

The skill prefers full ToC at first registration but **degrades gracefully**. The intent is to never block book registration on section extraction.

### Step 1 — book registration (existing)

User says "X 책 같이 보자" → skill writes the book entry to `books.yml`, confirms PDF path, etc. (Existing flow, unchanged.)

### Step 2 — best-effort ToC extraction

Try in this order, stopping at the first that yields a usable structure:

1. **PDF outline / bookmarks** — read with `pdftk dump_data` or equivalent; if the outline has a depth ≥ 2 (chapters with sub-entries), use it directly.
2. **Contents page scan** — Read the first ~30 pages; locate a "Contents" / "Table of Contents" / "목차" header; parse the lines that follow until the listing ends.
3. **Inline header inference** — open the first chapter and scan for visual header levels (font-size jumps, bold-only lines, numbered prefixes like `1.3`). Heuristic; flag confidence as low.

Show the user a *concise* confirmation: "ARQ Ch.1 7개 섹션 잡혔어요. 맞나요?" with the title list. On confirm, write to `books.yml`. On reject, fall through to lazy mode.

### Step 3 — lazy fallback (the default for any chapter without structure)

When entering a chapter whose `chapter_structure` entry is missing, the skill runs a one-shot mini-extraction on **just that chapter** at the start of its first chunk:

- Read the chapter's first 1–2 pages and the chapter's bookmark sub-entries (if any).
- Propose section titles. If extraction is uncertain, ask the user: "이 챕터의 섹션 헤더들 알려주실 수 있을까요? (또는 챕터 첫 페이지를 paste해 주셔도 돼요.)"
- Save into `books.yml` once confirmed.

The lazy path is the operating mode when init-time extraction fails entirely. It's also fine as the **only** path — books with no PDF outline never need a global scan.

## Chapter-note synchronization

The chapter note's body carries a `## Section progress` block that mirrors `chapter_structure[current_chapter]`:

```markdown
## Section progress
- [x] 1.1 Critical Thinking to the Rescue (covered, Session 2)
- [x] 1.2 The Sponge and Panning-for-Gold (covered, Session 3-4)
- [△] 1.3 An Example of Panning-for-Gold (used-as-exercise, Session 5 Round 3 — narrative ¶ 미처리, debt)
- [ ] 1.4 Panning for Gold: Asking Critical Questions
- [ ] 1.5 The Myth of the Right Answer
- [-] 1.6 Thinking and Feeling (skipped — user said "이 섹션은 익숙해서 건너뛸래")
```

Box conventions: `[x]` = covered, `[△]` = used-as-exercise (debt), `[ ]` = pending or in-progress (annotate inline if `in-progress`), `[-]` = skipped.

**`books.yml` is the source of truth.** When the chapter-note Section progress drifts (e.g., a manual edit), the next session sync writes from `books.yml` to the note, not the other way. The note version is convenience read-out for the user, not a parallel state store.

## Out of scope

- Sub-sub-section depth (1.3.2). Current schema is one level deep below chapter.
- Auto-update of page numbers when the PDF is re-released. Pages are best-effort metadata.
- EPUB / HTML direct parsing. Convert to PDF first via `scripts/convert-epub.sh`.

## Regression test cases

These cases gate any future change to section tracking. See `evals/section-tracking/` for fixtures.

1. **ToC extraction succeeds end-to-end.** ARQ-style chapter with 7 sections; init-time PDF outline extraction populates `chapter_structure` correctly; the user's confirmation prompt lists all 7 titles.
2. **`used-as-exercise` debt surfaces.** A chunk that uses section 1.3's gun-control passage as ARQ training material leaves 1.3 = `used-as-exercise`, and the next-chunk recommendation explicitly proposes processing 1.3's own narrative ¶ before anything else.
3. **Ambiguous "다음 phase" stays in chapter.** With 1.4–1.7 still pending, the user says "다음 phase 가자". The skill interprets it as "next section within Ch.1" and recommends 1.4, *not* phase-3 / Ch.2.
4. **Phase-3 gate honors section completeness.** `phase-3-pending` is set only when *every* section in the chapter is `covered` or `skipped`. A chapter with one `used-as-exercise` section blocks phase-3 transition.
5. **Lazy fallback path works.** A book whose PDF has no outline registers without `chapter_structure`. Entering Ch.1 triggers the lazy mini-extraction; if heuristic extraction is uncertain, the user is asked to paste the chapter's first page; section list is saved to `books.yml` after confirmation.

## Cross-references

- `SKILL.md` — chapter-completion-gate decision rule references this file
- `references/state-schema.md` — chapter-level status enum (orthogonal axis)
- `references/pdp-loop.md` — RESOLVE step calls into the section logic above
- `references/chapter-template.md` — Section progress body block lives here
- `assets/books.yml.template` — example `chapter_structure` block

# Speaker notes rewrite — status and conventions

Multi-session work in progress on the ADK course speaker notes. This file is the
source of truth for what's done, what's pending, and the rules to apply. If
you're Claude opening this repo for the first time on a new machine, read this
end to end before touching any `speaker_notes.md` file.

## Status

### Done

| Module | Topic | What was applied |
|---|---|---|
| M00 | Course intro | speaker notes rewritten |
| M01 | Mental model | rewritten + 2 notebook breaks |
| M02 | Tools | rewritten + 5 notebook breaks |
| M03 | Sessions, state, events, artifacts | rewritten + 1 notebook break |
| M04 | One-line model swap | rewritten + 2 notebook breaks |
| M05 | Workflow agents | rewritten + 4 notebook breaks |
| M06 | Multi-agent hierarchies | rewritten + 2 notebook breaks |
| M07 | Callbacks as middleware | rewritten + 3 notebook breaks |
| M08 | Memory | rewritten + 2 notebook breaks |
| M09 | Evaluation | rewritten + 1 notebook break |
| M10 | Deployment | rewritten + 1 notebook break |

### Pending

| Module | Topic |
|---|---|
| M11 | Gemini grounding + caching |
| M12 | Thinking budgets |
| M13 | Live API voice |
| M14 | A2A protocol |

## Conventions

### Slide deck structure

- The slide deck stays theory-only. No "Live" amber transition slides in any
  module that's been rewritten. The four-flavor pattern in M02 and the
  three-demo pattern in M07 illustrate the shape.
- The Jupyter notebook is the runnable code. During recording, the speaker
  switches their screen to the notebook at deliberate breakpoints, runs cells
  live, narrates the output, and switches back to the slide deck.
- There is no separate end-of-module notebook walkthrough video. Notebook
  segments are inline screen-switches within the same module video.

### Notebook breaks in speaker notes

Marked as a sub-section between two slide sections in `speaker_notes.md`:

```markdown
## Slide N — Title

[normal slide speaker notes]

---

### Notebook break — short title

[Switch the screen to the notebook.]

[1–3 paragraphs narrating what to run and what the student should observe]

[Switch back to the slide deck.]

---

## Slide N+1 — Title
```

The slide that follows a notebook break should NOT re-walk-through what the
student just saw live. Treat it as a static recap or reference rather than a
re-demo. The two notebook-break openings (`[Switch the screen to the
notebook.]` and `[Switch back to the slide deck.]`) are both spoken cues for
the recorder and signposts for the video editor.

How many breaks per module is a judgment call based on natural pedagogical
climaxes, typically 1–5 per module. The ones already in place:

- M01: 2 (greeter run, weather agent with tool)
- M02: 5 (one per flavor + guarded delete)
- M03: 1 (cross-session memory)
- M04: 2 (5-provider demo, priority-tier jailbreak)
- M05: 4 (Sequential, Parallel, Loop wow, Composition)
- M06: 2 (transfer routing, consultant calls)
- M07: 3 (blocklist, PII redaction, mocking)
- M08: 2 (write-restart-recall, long-term recall)
- M09: 1 (strict eval fails on ROUGE-1)

### Visible slide content

When rewriting a module, also fix visible slide-content violations of the
same rules. Two specific patterns to look for in `index.html`:

- Headers that count modules like "Seven modules, one problem" or "Three
  modules in", which need to become "Up to now" / "The persistence problem"
  / "So far".
- "Live" amber section-title slides that need to be deleted from the deck
  entirely when notebook breaks replace them. The HTML comment numbering
  (`<!-- NN Title -->`) is renumbered to stay consistent after deletions.

The visible "M0N — Title" prefix on Up-next slides is left alone for now;
that's a project-wide decision to revisit later if the course structure
changes.

### Rules for speaker note prose

These rules also live in the local memory store at
`~/.claude/projects/-Users-jankagecelovska-git-repos/memory/`. They are
duplicated here so they survive cross-machine work. Treat them as hard rules
during any final-pass review.

1. **No em-dashes in prose.** Em-dashes are fine only in slide section headers
   (`## Slide N — Title`). In body prose, replace with periods, commas, or
   "which/where/meaning/because" connectors. Reserve colons for the
   occasional quote, single named item, or short list; do not make them the
   default em-dash replacement. Frequent colons across a slide create a
   mechanical, label-like rhythm that breaks when narrated.

2. **No short fragment sentences anywhere.** Not at lead-ins, not in the
   middle of paragraphs. Anything under five or six words sitting between
   two normal-length sentences is suspect. Specific patterns to rewrite:
   - One-word sentences ("Unavoidable.", "Failed.")
   - Label-style fragments ("Three commands and a feedback loop.")
   - Parallel staccato ("Re-run eval. Repeat.")
   - Quote labels ("Expected response: '..'. Actual response: '..'.")

3. **No module counts, video durations, or specific module numbers in
   speaker notes.** Course structure shifts. Use relative pointers like
   "this module", "the next module", "earlier in the course", "later in the
   course". Avoid "fourteen modules", "fifteen minutes", "in module eight",
   "Module 3 introduced…", and similar.

4. **No cross-module meta-references** like "As we learned in module one".
   End-of-module sign-offs to "the next module" or "later in the course" are
   fine. Forward-pointers within the same module ("we'll see in a few
   slides") are fine.

5. **Title-slide openers must vary across modules.** Don't always open with
   "Welcome to module N: <topic>". Rotate alternatives like "Hi and welcome
   back. This module is on…", "<Topic>. That's what this module is about.",
   content-first hooks, and so on. The title-slide naming rule still applies
   (the module topic must be named in the opener) but the phrasing must
   rotate.

6. **No opener-phrase repetition across slides.** "Here on the slide…",
   "Here's…", and similar used four or more times across a deck become
   audible. Audit by listing the first two words of every section; if the
   same word leads more than two or three sections, mix variants in.

7. **Introduce code before concept on code-bearing slides.** When a slide
   shows code, the speaker notes first say what the student is looking at
   (name the function, say what it does in one sentence) before going into
   the broader concept the code illustrates.

8. **Use real-world analogies. Don't assume prior framework knowledge.**
   Casual references to "graphs, crews, chains, swarms" (i.e., LangGraph,
   CrewAI, LangChain, AutoGen) shut out beginners. Anchor abstract concepts
   to known domains: HTTP middleware, game-engine main loop, request
   pipelines, switch statements, JSON serialization.

9. **Consolidate inter-slide repetition.** Read each slide's notes alongside
   the next. If both say the same thing in slightly different words,
   restructure so one slide owns the point and the next slide advances.

10. **Don't enumerate slide data on data-heavy slides.** If a slide already
    shows a table of N items, don't recite each row. Pick the two or three
    most striking and refer the student to the slide for the rest. Exception:
    course-preview or structure slides where the listener really does need
    the items named aloud, like the four-tool-flavors slide in M02.

11. **No "If you remember one thing from this module" patterns.** Introduce
    the concept directly. "The core idea behind X is this. …" works.

12. **Avoid the "On the slide is X" pattern more than once or twice per
    deck.** Rotate "Here we have…", "What you see on the slide is…", "Look
    at the code…", "Take a look at…", "The slide shows…".

### Slovak-translation note

The English speaker notes are the canonical artifact. They get translated to
Slovak later. Some idiomatic touches matter for the translator:

- "Flavor" is used in M02 onward to mean "variant / kind / type". This is
  a deliberate informal-tech-idiom choice and translates to slovak as "typ"
  or "druh".
- Company examples use "Anthropic" rather than "Acme Corp" (see M08 S13/S14).

### Reference style

The gold-standard reference for tone, pacing, sentence length, and overall
flow is `hcai_style_reference.md` at the repo root. It's a copy of the M01
speaker notes from the HCAI course, used as the model for the ADK course
speaker notes voice. Note that some rules above (no module counts, no
cross-module meta-refs) post-date that reference, so the reference itself
violates them in places. Take tone and pacing from it, not those specific
violations.

### Git workflow

- Commit directly to `main` and push. No feature branches.
- Keep commit messages short. One sentence saying what changed; a short
  paragraph only if needed for context. Don't enumerate every file. Janka
  has flagged long commit messages twice; treat short as a hard rule.
- All commits should include
  `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`.

### User context

The user is Janka, who creates Udemy courses and communicates in Slovak.
Respond in Slovak. The ADK course is one of her active course projects; HCAI
is a separate course referenced as the style reference.

## Final-pass checklist before commit

Run these checks for every module rewrite before committing:

1. `grep "—" speaker_notes.md` — em-dashes should match only `## Slide N —`
   headers and `### Notebook break —` sub-headers, never body prose.
2. `grep -ni "module [0-9a-z]" speaker_notes.md` — module references should
   match only the title-slide opener and generic "this module" /
   "the next module" / "later in the course". No "module five", "module
   eight", "first eight modules", "module 9 stops doing that".
3. Count colons in body prose. One or two per slide max. None preceding a
   direct quote. None used as bare labels.
4. List the first two or three words of each section's speaker notes. If
   the same opener pattern leads more than two or three sections, mix
   variants in.
5. Read each slide's notes alongside the next slide. If they overlap,
   consolidate.
6. Read each notebook break alongside the slide that follows. The slide
   must not re-walk-through what the break just demonstrated live.

## When you next sit down with this repo

1. Read this file end to end.
2. Read `hcai_style_reference.md` if you haven't worked from it before.
3. Check the "Pending" table for which module is next.
4. For that module:
   - Read the current `slides/module-NN-XXX/speaker_notes.md` and
     `index.html`.
   - Skim the notebook at `notebooks/NN_XXX.ipynb` to identify natural
     pedagogical climaxes for notebook breaks.
   - Remove any "Live" amber transition slides from the deck HTML, renumber
     any `<!-- NN Title -->` comments that need it.
   - Fix any visible slide content that violates the rules (module counts
     in headers, etc.).
   - Rewrite the speaker notes following all the rules above.
   - Add notebook breaks at the chosen climaxes.
   - Run the final-pass checklist before committing.
   - Present what changed; stop for Janka's approval before moving to the
     next module.
5. Keep the commit message short. Push.

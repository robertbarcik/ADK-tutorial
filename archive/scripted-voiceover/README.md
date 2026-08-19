# Archived: the scripted-voiceover production format (parked 2026-08-19)

Everything here is the course's earlier production format, kept intact — not deleted — after
Robert decided (2026-08-19) to film the ADK course the way he filmed *Testing GenAI*: free talk
over the notebooks, no script. If that style turns out worse for this course, this folder is the
fallback.

| What | Where |
|---|---|
| 15 HTML slide decks (M00–M14, 249 module slides + M00), self-contained, open via `file://` | `slides/module-NN-slug/index.html` |
| EN speaker notes (spoken-delivery script, notebook-break markers) | `slides/module-NN-slug/speaker_notes.md` |
| SK speaker notes (~27k words, glossary-driven, May–July 2026) | `slides/module-NN-slug/speaker_notes_sk.md`, `slides/GLOSSARY_SK.md` |
| The 77-lecture Skillmea/Udemy plan this format mirrored | `LECTURE_PLAN.md` |
| Conventions + status of the speaker-notes rewrite | `SPEAKER_NOTES_STATUS.md` |
| Slides portal (course front page for this format) | `index.html` (textbook link now points to `../../textbook/index.html`) |
| Build tooling | `slides/build_slides.py` (inlines shared CSS/JS), `slides/render_slides.py` (1920×1080 JPGs → `slides-jpg/`, gitignored) |

The decks and notes were last aligned with the notebooks on ADK 2.4 (2026-07-11). The notebooks
moved on (ADK 2.7.1, minor demo fixes on 2026-08-19); nothing here was updated to match — if the
format is revived, re-check the notebook-break sections first.

Current filming plan: `../../FILMING_PLAN.md`.

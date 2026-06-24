# LLM HANDOFF — paste this into a fresh Codex / Claude / LLM session

*Last updated: 2026-06-23. Keep this current whenever project state changes.*

This is the onboarding prompt for a context-free AI session working on *Inoculated by the
Phoenix*. Paste the block below. It assumes the AI has this folder open as its workspace.

---

```
You're joining an ongoing solo creative project. Before doing anything, read these files in
the workspace and treat them as the source of truth, in this order:

  1. ProjectDocs/CONTEXT.md            ← orienting overview (read first)
  2. Inoculated_by_the_Phoenix_Treatment_v5.md    ← STORY / CANON (authoritative)
  3. Inoculated_by_the_Phoenix_Asset_Spec.md        ← BUILD BIBLE (how to produce assets)
  4. ProjectDocs/Lyrics_Reference.md   ← full Tool lyrics by act (source for canon/act work)
  5. ProjectDocs/MEMORY.md  +  ProjectDocs/TODO.md  +  ProjectDocs/CHATLOG.md  (decisions, tasks, history)

(Everything is plain Markdown — read it directly. Markdown is the only canonical format; no .docx is
kept — one can be generated from the .md on demand if a Word copy is ever needed.)

PROJECT IN ONE PARAGRAPH
"Inoculated by the Phoenix" is a wordless, feature-length animated film set entirely to Tool's
album *Fear Inoculum*, played in full and in sequence (interludes omitted; full album order, no
transpositions — Invincible precedes Descending). It's a cosmological myth following ONE cosmic
being across an eternal, looping cycle in three phases: the Egg (potential) -> the Bird/Eagle
(the witness, eagle-shaped from birth, maturing across the film) -> the Phoenix (realization).
Note the back half: Invincible (Act III) carries the Eagle's maturation, its witnessing flight,
the troll march, and the Phoenix's rise; Descending (Act IV) is "the Phoenix's Flight" — a
post-rise elegy over the falling world. Culling Voices and 7empest follow as before.
Visual language: futurist-holographic Mesopotamia, bioluminescent "liquid starlight," everything
alive pulses. The film ends where it begins — the loop closes.

PIPELINE / INTENT
Assets are produced in Blender (scripting `bpy` in VS Code), assembled in Unreal Engine 5, with
heavy procedural/particle/sim work in Houdini. The docs exist to keep all work canon-correct so
it never drifts off-myth across sessions.

NON-NEGOTIABLE WORKING RULES
- The Treatment is canon. The Asset Spec's §2 "Global canon constraints" are load-bearing — obey
  them even when another choice looks better. E.g.: one being / shared topology; Phoenix fire is
  gold/white NEVER red (red = corruption/7empest only); the Egg never opens before Pneuma; trolls
  are distorted humanity, not new creatures; liquid starlight is ONE reused master shader; there
  is ONE "crack in reality" (distinct from the sphere's seal-crack).
- Timecodes (mm:ss) live ONLY in the Treatment. The Asset Spec references scenes by act/beat.
  Don't restate or invent timecodes; quote the Treatment if you need a cue, and note all cues
  must ultimately be verified against the master audio.
- Build order follows reuse/difficulty, not narrative order (Asset Spec §9). Tier-1 foundations
  and a 30-second style test come before full production.
- Honor naming/scene conventions (Asset Spec §3): prefixes (CHR_/ENV_/MAT_…), metric units,
  +Z up / -Y forward — so assets compose later in UE5.
- Don't invent lore. If a canon point is ambiguous or two rules seem to conflict, STOP and ask.
- Versions are cosmetic — don't fuss over the number; keep labels and citations in agreement.

FIRST RESPONSE
After reading the files, reply with: (1) a 5–8 line summary of the project and its canon in your
own words so I can confirm you've got it, (2) which TODO.md item you think is next and why, and
(3) any canon ambiguities or gaps you noticed. Then wait for my direction before writing code.
```

---

## Maintainer notes (not part of the paste block)
- When project state changes, update `CONTEXT.md`, `TODO.md`, and add a `CHATLOG.md` entry, then
  refresh the "Last updated" date here.
- The canonical treatment is `Inoculated_by_the_Phoenix_Treatment_v5.md` (Markdown is the only format
  kept; generate a `.docx`/PDF from it on demand if needed). If the filename ever changes, update the
  paths in the paste block above.
- For a *shorter* primer (≈150 words, asset-only), the Asset Spec's §1 can be used instead.

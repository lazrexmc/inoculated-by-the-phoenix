# LLM HANDOFF — paste this into a fresh Codex / Claude / LLM session

*Last updated: 2026-06-29. Keep this current whenever project state changes.*

This is the onboarding prompt for a context-free AI session working on *Inoculated by the
Phoenix*. Paste the block below. It assumes the AI has this folder open as its workspace.

---

```
You're joining an ongoing solo creative project. Before doing anything, read these files in
the workspace and treat them as the source of truth, in this order:

  1. ProjectDocs/CONTEXT.md            ← orienting overview (read first)
  2. Inoculated_by_the_Phoenix_Treatment.md    ← STORY / CANON (authoritative)
  3. Inoculated_by_the_Phoenix_Asset_Spec.md        ← BUILD BIBLE (how to produce assets)
  4. ProjectDocs/Lyrics_Reference.md   ← full Tool lyrics by act (source for canon/act work)
  5. ProjectDocs/MEMORY.md  +  ProjectDocs/TODO.md  +  ProjectDocs/CHATLOG.md  (decisions, tasks, history)
  6. ProjectDocs/Acts/Act_*.md  ← per-act working files (Story+lyrics+flags; derived from the Treatment) + Acts/README.md
  7. mastershotlist.md          ← master shot list (Acts I–V + VII drafted; CCT/VI deferred)
  8. blender/README.md + audio/README.md  ← PRODUCTION: the Blender asset scripts (Tier-1 built) and the
     music-sync pipeline. Tool paths + the "never write to C:" drive policy live in project memory.

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

PRODUCTION STATE (2026-06-29) — HERO production underway
Tier-1 foundations built; MAT_LiquidStarlight is now HERO (deep near-black-blue glassy cosmos, white/gold
star-speckle, resin flow). ACT I is built end-to-end as first-pass hero stills (genesis -> Egg -> shadow
-> inoculation -> false peace): CHR_Egg + MAT_EggShell_Iridescent (sealed every frame of Act I),
ENV_Plateau + MAT_Plateau_Rock, twin springs, Creator cradle, FX_Shadow_Deceiver (formless), and
FX_InoculationGlow, assembled by blender/act1_scene.py; shot list audited to FI-001..025. See
ProjectDocs/Acts/Act_I_BUILD_NOTES.md + Act_I_contact_sheet.png. A GEN-AI pipeline is online (the prompt
lever): ComfyUI at F:\genai\ComfyUI (torch 2.6+cu124, RTX 3080) + SDXL, driven by genai/comfy_gen.py
(prompt->image). All four DCCs located; the audio/ music-sync pipeline (Demucs stems + librosa, Python
3.12 venv) drives animation from the album.

DIVISION OF LABOR (load-bearing — supersedes Asset Spec §5)
Lance is a proven LLM prompt-writer with NO formal art / 3D-software / UI training; he CANNOT hand-author
hero art. So the §5 "the owner hand-authors the hero meshes/shaders/look-dev" assumption is RETIRED.
Claude PRODUCES the finished hero art: (a) procedural shaders/materials/geo to hero quality in Blender,
and (b) prompt-driven gen-AI (ComfyUI/SDXL) that Lance directs by prompt. Never tell Lance to "open it in
Blender and refine the shader" or "do your hero pass" — bring the look up and present renders for his
prompt-feedback. (See user-role-and-art-pipeline in project memory.)

NON-NEGOTIABLE WORKING RULES
- The Treatment is canon. The Asset Spec's §2 "Global canon constraints" are load-bearing — obey
  them even when another choice looks better. E.g.: one being / shared topology; Phoenix fire is
  gold/white, red = corruption/7empest (a strong preference, not a hard lock — creativity first, filter second); the Egg never opens before Pneuma; trolls
  are distorted humanity, not new creatures; liquid starlight is ONE reused master shader; there
  is ONE "crack in reality" (distinct from the sphere's seal-crack).
- Timecodes (mm:ss) live ONLY in the Treatment. The Asset Spec references scenes by act/beat.
  Don't restate or invent timecodes; quote the Treatment if you need a cue, and note all cues
  must ultimately be verified against the master audio.
- Build order follows reuse/difficulty, not narrative order (Asset Spec §9). Tier-1 foundations
  and a 30-second style test come before full production.
- Claude PRODUCES the hero art (procedural + prompt-driven gen-AI) — the §5 "owner hand-authors hero"
  rule is RETIRED (Lance can't; he directs by prompt). Script the parametric/batch parts AND bring the
  hero look up yourself; don't ship a bare scaffold and call it done, and never defer a "hero pass" to Lance.
- Never write heavy output to the C: drive (system, chronically low on space) — use E:/F: (D: ok; G:/H:
  are USB). Tool paths + this drive policy are in project memory.
- Honor naming/scene conventions (Asset Spec §3): prefixes (CHR_/ENV_/MAT_…), metric units,
  +Z up / -Y forward — so assets compose later in UE5.
- Don't invent lore. If a canon point is ambiguous or two rules seem to conflict, STOP and ask.
- The Treatment is **intentionally unversioned** (git tracks history) — do NOT add a version to the filename or title. (Older drafts and the `.docx` were deleted; Markdown only.)
- **SYNC RULE (bidirectional):** the Treatment is the source of truth; the per-act files
  (`ProjectDocs/Acts/`) and the shot list (`mastershotlist.md`) are derived and must NEVER drift from
  it. Change the Treatment → update the acts + shot list; change an act/shot → update the Treatment,
  then re-sync. Each act's Story stays a verbatim copy of its Treatment section. (Regenerate
  `Act_II_Pneuma.md` via a script — its Pneuma lyrics trip an output content-filter when typed.)

FIRST RESPONSE
After reading the files, reply with: (1) a 5–8 line summary of the project and its canon in your
own words so I can confirm you've got it, (2) which TODO.md item you think is next and why, and
(3) any canon ambiguities or gaps you noticed. Then wait for my direction before writing code.
```

---

## Maintainer notes (not part of the paste block)
- When project state changes, update `CONTEXT.md`, `TODO.md`, and add a `CHATLOG.md` entry, then
  refresh the "Last updated" date here.
- The canonical treatment is `Inoculated_by_the_Phoenix_Treatment.md` (Markdown is the only format
  kept; generate a `.docx`/PDF from it on demand if needed). If the filename ever changes, update the
  paths in the paste block above.
- For a *shorter* primer (≈150 words, asset-only), the Asset Spec's §1 can be used instead.

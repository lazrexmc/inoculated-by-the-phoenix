# CONTEXT — Inoculated by the Phoenix

*Last updated: 2026-06-23*

## What this project is
A **wordless, feature-length animated film** set entirely to Tool's album *Fear Inoculum*
(2019), played in full and in sequence. No dialogue, no title cards — pure visual myth.
Created by Lance. Personal, non-commercial creative work.

It is a cosmological myth about **one cosmic being** moving through three phases across a single
eternal, repeating cycle:
- **The Egg** — pure potential, untouched consciousness. Never opens during *Fear Inoculum*.
- **The Bird / Eagle** — the witness. Eagle-shaped from birth (hatches as an eaglet), matures
  into the full mythical Eagle. Discovers purpose through suffering.
- **The Phoenix** — realization made fire. Remembers what the Egg always held.

The story is cyclical: it ends exactly where it begins, and the loop closes in the final seconds.

## The two canon documents (source of truth)
1. **`Inoculated_by_the_Phoenix_Treatment_v5.md`** — STORY / CANON. Authoritative source of truth.
   Owns all timecodes (mm:ss cues). Nothing else should restate them.
2. **`Inoculated_by_the_Phoenix_Asset_Spec.md`** — BUILD BIBLE. Canon constraints, asset
   catalog (with tiers), shader library, rigs, build order. References scenes by act/beat,
   not timecodes. Its §1 is a paste-this-first primer for a fresh LLM session.

> The canon is plain Markdown and is the sole canonical format — read it directly. No `.docx` is
> kept; generate one from the `.md` on demand if you ever need a Word/print copy.

## Act structure (full album order, no transpositions)
Interlude tracks (Litanie contre la Peur, Legion Inoculant, Mockingbeat) are omitted.
The album plays in full sequence; *Invincible* precedes *Descending*.

| Act | Track | Runtime | Theme | Key beat |
|---|---|---|---|---|
| I | Fear Inoculum | 10:21 | Creation | Cosmos born; Egg materializes; Egg inoculates (never hatches) |
| II | Pneuma | 11:53 | Unity & Growth | Egg hatches; bird grows from hatchling; mankind forms; oneness peaks under a looming (unbroken) shadow — carries unbroken into Invincible |
| III | Invincible | ~12:44 | Awareness & Crisis | Bird matures to full Eagle; soars a corrupting world; troll march; near-destruction; freeze; Phoenix rises and **spares** the Tree |
| IV | Descending | ~13:38 | The Phoenix's Flight | Post-rise elegy over a world that still seems whole; the Dire Reveille (unheeded); beauty fades into despair |
| V | Culling Voices | 10:05 | Reckoning | Phoenix's internal resolve (NOT the literal gathering — that's 7empest) |
| VI | Chocolate Chip Trip | 4:48 | Inside the Sphere | Psychedelic chaos; no palette/rules; *not yet specced for assets* |
| VII | 7empest | 15:43 | Eternal Cycle | Sealing, the crack, the sacrifice, the speck — the loop closes |

> All cues must be verified frame-accurately against the **master audio** before storyboarding.
> Highest priority: the Invincible climax (march → freeze) which is load-bearing for the film.

## Pipeline & intent
Assets are produced in **Blender** (scripting `bpy` in **VS Code**), assembled in **Unreal Engine 5**,
with heavy procedural/particle/sim work in **Houdini**. The two canon docs exist to keep all asset
and story work on-myth so nothing drifts across sessions.

## Load-bearing canon (see Asset Spec §2 for the full list)
- One being across time; share topology so transformations read as continuity, not swaps.
- Phoenix fire is **gold/white, NEVER red**. Red is reserved exclusively for corruption/7empest.
- The Egg never cracks before the *Pneuma* hatch; glow is independent of any fracture state.
- **Liquid starlight is ONE** reused master shader (rivers, springs, Egg interior, Tree, Phoenix base).
- Trolls are **distorted humanity** (one mankind base mesh), not from-scratch monsters.
- One "crack in reality" (creation seam) — distinct from the sphere's seal-fracture in 7empest.
- The Creator = the Holding Device (cradle of contained light); dissolves into ambient world-light
  after the hatch.
- Feathers = soul-fragments, one asset with a 0–1 state range; final feather → first speck (loop).
- Everything alive pulses (shared, tempo-syncable control).
- Continuity between songs is the default (silent connective passages or hard cuts), not a hard rule — fades are allowed when the moment calls for it (even mid-song). The bird's growth carries unbroken Pneuma→Invincible, completing into the Eagle as Invincible opens.

## Current state
- Canon consolidated to a **single** treatment file (v5) + the Asset Spec. Older drafts removed.
- Timecodes live only in the treatment; Asset Spec references act/beat.
- **No assets built yet** — production has not started.
- Version numbers are cosmetic to the project owner; keep labels/citations in agreement, don't fuss.

See `TODO.md` for next steps, `MEMORY.md` for durable decisions, `LLM_HANDOFF.md` to onboard a new session.

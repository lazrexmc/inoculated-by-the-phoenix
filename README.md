# Inoculated by the Phoenix

A **wordless, feature-length animated film** set entirely to Tool's album *Fear Inoculum* (2019),
played in full and in sequence. A cosmological myth following one cosmic being across an eternal,
looping cycle — the **Egg** (potential) → the **Bird/Eagle** (the witness) → the **Phoenix**
(realization). Created by Lance. Personal, non-commercial creative work.

Produced in **Blender** (`bpy` scripting in VS Code) → **Unreal Engine 5**, with **Houdini** for sims.

## Front door
- **New here (human or AI)? Start with [`ProjectDocs/CONTEXT.md`](ProjectDocs/CONTEXT.md).**
- Onboarding a fresh LLM session? Use [`ProjectDocs/LLM_HANDOFF.md`](ProjectDocs/LLM_HANDOFF.md)
  (paste-ready prompt).

## The canon documents (source of truth)
| File | Role |
|---|---|
| `Inoculated_by_the_Phoenix_Treatment.md` | **Story / canon.** Authoritative source of truth. Owns all timecodes. |
| `Inoculated_by_the_Phoenix_Asset_Spec.md` | **Build bible.** Canon constraints, asset catalog, shaders, build order. |

> Markdown is the sole canonical format — there is no `.docx` kept in the repo. Generate a Word/PDF
> copy from the `.md` on demand if you ever need one.

> **`interpretation.md`** — the *why* companion: how the author reads the film and why it's built this
> way (authorial intent, not canon-mechanics; nothing in it is meant to reach the screen). Separate
> from the canon docs.

## Reference docs (`ProjectDocs/`)
| File | Role |
|---|---|
| `CONTEXT.md` | Orienting overview — read first. |
| `MEMORY.md` | Durable decisions & facts. |
| `TODO.md` | Tasks and next steps. |
| `CHATLOG.md` | Working-session history. |
| `LLM_HANDOFF.md` | Paste-ready onboarding prompt for a fresh AI session. |
| `Lyrics_Reference.md` | Full Tool lyrics by act — source text for canon/act development. |
| `Acts/Act_*.md` | **Per-act working files** (one per act; Story + lyrics + canon flags). Derived from the Treatment, verbatim-synced — see `Acts/README.md` and the bidirectional sync rule. |

## Production artifacts
| File | Role |
|---|---|
| `mastershotlist.md` | **Master shot list** (authoring source). Canon-locked to Treatment; per-shot blocks whose fields map to the Excel columns. **Acts I–V & VII drafted** (full-film unit-audited) — everything but VI/CCT (deferred). |
| `Fear_Inoculum_ShotList.xlsx` | Excel shot list — filled *from* the master `.md`. (An earlier-version Act I; being superseded by the v5-aligned master.) |

## Production code
| Dir | Role |
|---|---|
| `blender/` | `bpy` asset scripts (Blender → UE5 pipeline). **Tier-1 foundations built** — `bootstrap`, `ENV_Tree`, `MAT_LiquidStarlight`/`NG_LiquidStarlight`, `NG_BioPulse`, `FX_Feather`+`MAT_Feather_StateRange`, `CHR_OneBeing` proxy + `RIG_OneBeing`. Verification previews in `blender/previews/`. See `blender/README.md`. |
| `audio/` | **Music-sync pipeline** — Demucs stems (the Four Instruments) + librosa frame-mapped analysis (Python 3.12 venv) so the album *drives* the animation. See `audio/README.md`. (venv/stems/analysis are git-ignored; source MP3s are copyrighted/ignored.) |
| `genai/` | **Prompt-driven gen-AI** — `comfy_gen.py` turns a prompt into an image via the ComfyUI server (SDXL on the RTX 3080). Lance's art-direction lever (concept art / skies / textures / matte). See `genai/README.md`. (The ComfyUI install itself lives at `F:\genai\ComfyUI`, outside the repo.) |

## Status
**HERO production underway (2026-06-29).** `MAT_LiquidStarlight` is now hero, and **Act I is built
end-to-end as first-pass hero stills** (genesis → Egg → shadow → inoculation → false peace) — see
[`ProjectDocs/Acts/Act_I_BUILD_NOTES.md`](ProjectDocs/Acts/Act_I_BUILD_NOTES.md) and the
`Act_I_contact_sheet.png`. A **prompt-driven gen-AI pipeline** (ComfyUI + SDXL on the RTX 3080) is online
as Lance's art-direction lever. Day-to-day next steps live in [`ProjectDocs/TODO.md`](ProjectDocs/TODO.md).

> **Division of labor (load-bearing):** Lance directs by prompt; **Claude produces the finished hero art**
> (procedural Blender + prompt-driven gen-AI). The Asset Spec §5 "owner hand-authors the hero" assumption
> is retired — see `ProjectDocs/LLM_HANDOFF.md`.

---
*`FearInoculum_Resolve/` is the DaVinci Resolve working project (audio/edit), separate from asset production.*

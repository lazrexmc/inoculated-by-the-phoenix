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
| `Inoculated_by_the_Phoenix_Treatment_v5.md` | **Story / canon.** Authoritative source of truth. Owns all timecodes. |
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

## Production artifacts
| File | Role |
|---|---|
| `mastershotlist.md` | **Master shot list** (authoring source). Canon-locked to Treatment v5; per-shot blocks whose fields map to the Excel columns. **Acts I–V drafted** (unit-audited); Act VII to come (VI/CCT deferred). |
| `Fear_Inoculum_ShotList.xlsx` | Excel shot list — filled *from* the master `.md`. (An earlier-version Act I; being superseded by the v5-aligned master.) |

## Status
Pre-production. Canon docs consolidated and consistent. No assets built yet — next steps are in
[`ProjectDocs/TODO.md`](ProjectDocs/TODO.md).

---
*`FearInoculum_Resolve/` is the DaVinci Resolve working project (audio/edit), separate from asset production.*

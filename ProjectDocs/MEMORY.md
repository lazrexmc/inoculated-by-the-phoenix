# MEMORY — Durable decisions & facts

*Append-only-ish. Record decisions that should survive across sessions. Last updated: 2026-06-30.*

## Canon & source-of-truth
- **`Treatment.md` is the single canonical story/canon document.** (Converted from `.docx` to
  Markdown on 2026-06-23; the old `.docx` was then deleted — **Markdown is the only format kept**,
  generate a `.docx`/PDF from the `.md` on demand if a Word/print copy is ever needed.) The Asset
  Spec is the build bible and cites the treatment as its canon source.
- **Album plays in FULL sequence — no transpositions (v5 restructure, 2026-06-23).** Order:
  Fear Inoculum → Pneuma → **Invincible (III)** → **Descending (IV)** → Culling Voices → Chocolate
  Chip Trip → 7empest. *Invincible* now holds the Eagle's whole arc (maturation, the witnessing
  flight, the troll march, the freeze/realization, and the Phoenix's rise that **spares** the Tree);
  *Descending* is repurposed as "the Phoenix's Flight" — a post-rise elegy over the falling world,
  with the Dire Reveille as the Phoenix's unheeded call. Culling Voices / 7empest unchanged in essence.
- **Timecodes live ONLY in the treatment.** The Asset Spec references scenes by act/beat. Don't
  restate or invent mm:ss cues anywhere but the treatment.
- **All timecodes must be verified against the master audio** before storyboarding (masters vary
  CD vs streaming). The *Invincible* climax (march ~9:44 → freeze ~10:49 → Phoenix eruption ~10:52)
  is the priority.
- **Version numbers are cosmetic** to the owner (Lance). Keep filename, in-doc label, and the
  Asset Spec's canon citation in agreement; don't deliberate over the number itself.

- **Per-act files + the bidirectional sync rule (2026-06-24).** `ProjectDocs/Acts/Act_*.md` are
  per-act working files (Story + lyrics + canon flags) so an LLM can work one act without the whole
  treatment. They are **derived views**; the **Treatment is the source of truth**. **Treatment ↔
  per-act files ↔ `mastershotlist.md` must never drift** — change one, update the others; each act's
  Story stays a *verbatim* copy of its Treatment section (audited at 1.000 similarity). NOTE:
  write/regenerate `Act_II_Pneuma.md` via a **script** (file→file) — its Pneuma lyrics trip an output
  content-filter when typed (see `pneuma-lyrics-filter` in project memory).

## Production approach
- **Build order follows reuse/difficulty, not narrative order** (Asset Spec §9): bootstrap →
  Tier-1 foundations → 30-second style test → Tier-2 hero → Tier-3 populations → Tier-4 sims.
- **Do not start full production until the 30-second style test looks right** (Act I opening slice).
- **Claude produces the hero art** — the Asset Spec §5 "owner hand-authors the hero" assumption is
  **RETIRED (2026-06-29)**: Lance is a prompt-writer with no art/3D/UI training and can't hand-author;
  he directs by prompt. Claude brings the look up via (a) hero procedural shaders/geo in `bpy` (expose
  inputs as node groups so Python/the conductor can drive them) and (b) **prompt-driven gen-AI**
  (ComfyUI/SDXL, `genai/comfy_gen.py`). Never defer a "hero pass" to Lance.
- **Honor naming/scene conventions** (Asset Spec §3) in every script: prefixes (CHR_/ENV_/MAT_…),
  metric units (1 BU = 1 m), +Z up / -Y forward, apply transforms before export.

## Production state & tooling (2026-06-29)
- **HERO production underway; ACT I built end-to-end (2026-06-29).** `MAT_LiquidStarlight` is now hero,
  and Act I ("Fear Inoculum") is built as first-pass hero stills + a full-length animatic, canon-locked to
  the audited FI-001..025 shot list: `CHR_Egg`+`MAT_EggShell_Iridescent` (sealed), `ENV_Plateau`+
  `MAT_Plateau_Rock`, twin springs, Creator cradle, `FX_Shadow_Deceiver` (formless), `FX_InoculationGlow`,
  assembled by `blender/act1_scene.py`; FI-001 animated (`act1_genesis_anim.py`); full 10:21 cut via
  `build_act1_animatic.py`. Tier-1 foundations still hold. See `ProjectDocs/Acts/Act_I_BUILD_NOTES.md`.
- **Gen-AI pipeline ONLINE (the prompt lever):** ComfyUI at `F:\genai\ComfyUI` (torch 2.6+cu124, RTX 3080)
  + SDXL, driven by `genai/comfy_gen.py` (prompt→image). See `genai/README.md`.
- **All four DCCs located** (full paths in project memory `software-tooling-paths`): Blender 5.1.2
  (`E:\Software\blender.exe`), Houdini 21.0.729 (`E:\Software\Houdini 21.0.729\bin\hython.exe`), UE5 5.8
  (`E:\UE5\UE_5.8\…\UnrealEditor-Cmd.exe`), Resolve 21.0 (`F:\Software\Resolve.exe` / `fuscript.exe`). GPU RTX 3080.
- **Never write heavy output to C:** (system drive, chronically low) — use E:/F: (D: ok; G:/H: are USB).
  `uv`/torch caches redirected off C:; render scratch → `F:\…\_scratch`.
- **Music-sync pipeline** (`audio/`): the album **drives** the animation (§10). Demucs stem-separation
  (the Four Instruments) + librosa frame-mapped analysis (tempo→`NG_BioPulse` Rate, onsets→FX frames,
  RMS→amplitude), Python 3.12 venv on the RTX 3080. Act I separated + analyzed; next is WhisperX lyric
  forced-alignment on the vocals stem to auto-timecode the lyrics.

## Production state & tooling (2026-06-30) — LOOK LOCKED + pipeline proven + tool stack in
- **The LOOK is locked from owner reference images** — `ProjectDocs/Reference/ART_DIRECTION.md` (the look
  bible) + `Reference/images/` (six keeper frames + contact sheet). **Read it + `RUN_GUIDE.md` before
  generating.** Locked looks: First Light = the **album-lettering GOLD** through pure black on the chime
  (built in `blender/act1_first_light.py`); **Liquid Starlight = FLOWING self-luminous light, NOT a
  resin** (this corrects the earlier "resin flow" description of `MAT_LiquidStarlight`); the Egg = a
  **mosaic of faceted gem-scales in warm gold + ruby red + ivory white**, ancient Egyptian/Mesopotamian,
  lit from within, sealed (hero `_scratch/ref_egg_phoenix_v11.png`); Tree, Plateau/Eden, Phoenix.
- **The GOLD THROUGH-LINE (canon):** the universe's first photon and the Phoenix's fire are the **same
  gold** — one being's light struck at the start of the cycle and again at its rebirth.
- **`RUN_GUIDE.md` is the anti-repeat protocol** — before any generation/script, check the look bible,
  `_scratch/`, the script inventory, memory, and git, and report what exists *before* spending tokens.
- **The HYBRID gen-AI pipeline is the FINAL look layer and is PROVEN END-TO-END:** Blender bones →
  ControlNet composition-lock → film-grade still (Juggernaut) → SVD/Wan motion. Scripts in `genai/`:
  `comfy_gen`, `comfy_img2img`, `comfy_controlnet`, `comfy_svd`, `comfy_upscale`, `contact_sheet`, `dl_*`.
- **Free tool stack installed (ComfyUI 0.26 @ F:\genai\ComfyUI):** controlnet_aux (depth/canny/pose),
  IP-Adapter, RIFE/FILM, **Wan 2.2 5B** video, 4x-UltraSharp/RealESRGAN upscalers, ComfyUI-Manager;
  **OneTrainer** (`F:\genai\OneTrainer`, own venv) for LoRA training. **10GB VRAM is the binding
  constraint** (caps video length/res; VRAM upgrade being explored). Detailed pipeline facts live in the
  `.claude` project memory (`comfyui-pipeline`, `art-direction-references`, `production-approach`).
- **Egg coloration is now owner-locked** to warm gem-scale gold/red/white (foreshadows the Phoenix). This
  *updates* the older soft "Phoenix fire gold/white, red = corruption" lean — which was always a
  preference, not a hard lock; warm red+gold now reads as the One Being's fire, not corruption.

## Hard canon rules that have bitten before (keep front of mind)
- Phoenix fire reads gold/white; red = corruption/7empest — strong intent, held as a **preference, not a hard lock** (creativity first, filter second). Coloration canon to be firmed up once real images arrive; keep the palettes as separate material families so the distinction is easy to honor or relax.
- Egg stays sealed through Act I; the **only** hatch is *Pneuma*.
- The unmaking in *Invincible* is **local** (just the mob at the Tree); corruption survives for
  Culling Voices and 7empest.
- One creation-seam crack vs. the separate sphere seal-crack — never conflate them.
- *Culling Voices* = internal resolve; the literal gathering of corruption is in *7empest*.
- **Pneuma (II) has no real fracture** — it's the bird's coming-of-age (growth spine) + the unity peak; the old late-act fracture is softened to a looming, *unbroken* shadow. The real break lands in **early Invincible**, where the Eagle's growth also completes (growth carries unbroken across the Pneuma→Invincible seam).
- **The four instruments stage the image (production principle).** Each voice drives a visual layer, and animation is cut/energized to them: **Maynard (vocals) = the story/meaning**; **Adam (guitar) = the Bird/Phoenix and the life & energy in every object** (key the being's motion and the world's power to the guitar); **Justin (bass) = light & mood/temperature**; **Danny (drums) = the world & its weather** (sky, storm, darkness, lightning, impact). The world isn't just tempo-synced — it's *played* by the band. (Refines "everything alive pulses.")
- **One long wordless stretch bridges the climax.** The words end at Culling Voices **8:11** and do not return until 7empest's "keep it calm" (~1:35) — so CV's outro + all of **Chocolate Chip Trip** + 7empest's intro are continuous instrumental: the descent into and through the corruption. (All lyric-bearing acts — I–V, VII — are now beat-mapped to their lyrics; VI/CCT is an instrumental look-dev deferral. All timecodes still to be verified against the master.)
- **The corruption rises, then is sealed (CV → CCT → 7empest).** The wider world's corruption (everything Invincible left untouched) rises *of its own accord* to be faced — convening above the Tree across Culling Voices and Chocolate Chip Trip into one swirling mass. 7empest is **not** a fresh from-the-world gather; it's the Phoenix drawing that *present* mass in and compressing/sealing it into the sphere. (Resolves the "gathers twice" seam.)
- **Continuity between songs is the default, not a hard rule.** The film generally flows through each track (silent connective passages or hard cuts; the Pneuma→Invincible seam is deliberately continuous), but fades — out or in, even mid-song — are allowed wherever the moment calls for it.
- **Back-half dark through-line (IV→VII).** *Descending*'s last lyric, "call us all to arms and order," is **layered**: the Phoenix's plea to rouse-to-live AND the darkness's muster, which most of mankind answers — taking up arms unknowingly against the good (the dark muster gathers beneath the instrumental elegy). **Culling Voices** = the darkness **culling mankind through itself** (the voices/projection), never directly involved — consistent with the Deceiver being *a sense, not an actor*; the Phoenix **reckons while watching and does not fight** (to strike would feed the darkness). Its turning point: the darkness can't be beaten and mankind can't be saved by force — it must be **accepted and contained as the 7empest, forever**. Leads into 7empest's "a tempest must be just that."
- **Deceiver = voice, never body (canon); the 7empest ending.** The Deceiver stays a *sense* with no form throughout; at the 7empest climax (~10:31) it finds a single disembodied **voice** in a two-voice round with the Phoenix — still no body/face. The ending names the Phoenix's nature: not Good (would not kill), not Evil (would not protect), but the **Reckoner** (it lets it all try again). Two things are left **deliberately unanswered**: whether the Deceiver owns the 7empest, and whether the **Phoenix itself is the tempest**. The lyric "the tempest must will be just that" is *two overlapping voices* ("will be" + "must be") — NOT a transcription error; never 'fix' it.

## Open creative decisions
- **Act VI / Chocolate Chip Trip** (the psychedelic sphere interior) is a distinct look-dev problem
  (it deliberately abandons the act-palette system). It is **not yet a catalog asset** — to be
  specced when we reach it, intentionally not treated as a freebie.

## Session history pointer
See `CHATLOG.md` for what each working session did and why.

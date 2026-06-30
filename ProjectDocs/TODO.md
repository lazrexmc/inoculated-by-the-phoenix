# TODO — Inoculated by the Phoenix

*Last updated: 2026-06-29. Status: HERO production — `MAT_LiquidStarlight` is hero; **Act I built end-to-end as first-pass hero stills**; gen-AI prompt pipeline online. **Division of labor changed:** Claude produces the art, Lance directs by prompt (Asset Spec §5 "owner hand-authors hero" assumption RETIRED — see `user-role-and-art-pipeline` in project memory + the 2026-06-29 pivot CHATLOG entry).*

## Done 2026-06-29 (hero / Act I session)
- [x] **`MAT_LiquidStarlight` → HERO** (deep near-black-blue glassy cosmos, white cores + gold rims + bloom, resin flow) + `lookdev_swatch.py`.
- [x] **Audited Act I → FI-001..025** shot list + GAPS (canon-locked).
- [x] **Built Act I to first-pass hero:** `CHR_Egg`+`MAT_EggShell_Iridescent`, `ENV_Plateau`+`MAT_Plateau_Rock`, twin springs, Creator cradle, `FX_Shadow_Deceiver`, `FX_InoculationGlow`, `act1_scene.py` assembler; a hero still per beat + contact sheet.
- [x] **Gen-AI pipeline online:** ComfyUI (`F:\genai\ComfyUI`, torch 2.6+cu124, SDXL) + `genai/comfy_gen.py` prompt→image; verified. (Fixed torchaudio 2.11→2.6 ABI mismatch.)
- [ ] **Next:** FI-004 world-forming (`FX_Lightning` + `FX_CreationSeam_Crack` = the ONE crack); ENV_Cosmos star polish; full-act (~10.5 min) music-synced animation; **align Asset Spec §5 to the new division of labor.**

## Now / next
- [ ] **Owner manual review of each per-act file** (`ProjectDocs/Acts/Act_*.md`) — verbatim-synced to
      the Treatment (1.000); awaiting the owner's read. The Treatment↔acts↔shot-list **sync rule** is now in force.
- [x] **Blender + VS Code environment** ready — Blender 5.1.2 at `E:\Software`; scripts headless-tested
      (`--background --factory-startup --python`). All four DCC tool paths recorded in project memory.
- [x] **`bootstrap.py`** written + verified — units, collections, naming, default camera. (Build-order step 1.)
- [ ] **The 30-second style test** is now the active build gate (see below).

## Tier-1 foundations (highest reuse) — ✅ COMPLETE (2026-06-29, scripts in `blender/`)
- [x] `MAT_LiquidStarlight` (`NG_LiquidStarlight`) — first-pass scaffold; drivable inputs exposed. **Hero graph still owner-hand-authored (§5).**
- [x] `NG_BioPulse` — heartbeat driver; makes the starlight breathe (tempo-syncable from `audio/analysis`).
- [x] `FX_Feather` + `MAT_Feather_StateRange` — one feather, single `State` 0..1 (ash → starlight → ember).
- [x] `ENV_Tree` growth system (sprout → mid → mature → wounded → regrown) from one param set.
- [x] `CHR_OneBeing` proxy + `RIG_OneBeing` (22-bone, eaglet → Eagle → Phoenix). **Hero mesh = owner hand-sculpt; the proxy is a stand-in.**
> Previews in `blender/previews/` are bare **scaffolds** (flat emission, no bloom, proxy geo) — they prove the systems, not the final look. The look is solved at the style test.

## Pipeline tooling & music-sync (done 2026-06-29)
- [x] **Located all four DCCs** (paths in project memory `software-tooling-paths`): Blender 5.1.2,
      Houdini 21.0.729 (`hython`), UE5 5.8 (`UnrealEditor-Cmd`), Resolve 21.0 (`fuscript`). GPU RTX 3080.
- [x] **Output-drive policy:** never write heavy output to **C:** (use E:/F:; D: ok; G:/H: are USB).
      `uv`/torch caches redirected off C:; render scratch → `F:\…\_scratch`.
- [x] **Music-sync pipeline** (`audio/`): Demucs stems + librosa frame-mapped analysis (Python 3.12 venv).
      Act I (*Fear Inoculum*) separated into the Four Instruments + analyzed (tempo/onsets/RMS @ 24fps).
- [ ] **Lyric forced-alignment** on the isolated vocals stem (WhisperX — Windows/GPU, preferred over
      aeneas) to auto-generate the lyric→timecode map the owner sets by ear, and cross-check it.
- [ ] **bpy importer** for `audio/analysis/*.json` → drive `NG_BioPulse` Rate/Amplitude + place FX on onsets.

## Gate: the 30-second style test
- [ ] Build the Act I opening slice (Creation Sequence: opening chimes → first river reveal →
      sprout) using only the Tier-1 assets above. Must solve starlight, holographic dissolve,
      pulse, palette, and feather rendering in one contained sequence.
- [ ] **Owner hero pass** is part of passing the gate: hand-author the liquid-starlight hero graph +
      bloom/look-dev, and (optionally) drop a hand-sculpt over the `CHR_OneBeing` proxy. Scaffolds stand
      in until then.
- [ ] Wire the `audio/analysis` tempo/onset/RMS track into the test so the pulse/FX are *played by the album*.
- [ ] **Do not start full scene production until this looks right.**

## Later tiers (after the style test passes)
- [ ] Tier-2 hero: `CHR_Egg` + shell, `CHR_Creator_Cradle`, `ENV_Plateau`/terrain,
      `ENV_Water_System`, `CHR_Phoenix_FireLayers`, `FX_FirstLight/Speck`, `FX_InoculationGlow`.
- [ ] Tier-3 populations: `CHR_Mankind_Base` (+light-form shader), `CHR_Troll` distortions,
      `ENV_Cities_Empires`, `ENV_Cosmos`, `FX_Shadow_Deceiver`.
- [ ] Tier-4 climactic sims (Houdini-led): creation ripples, feather storm, time-freeze,
      7empest swirl/sphere/cracks, the collapse, the final-speck loop.

## Canon / docs tasks
- [ ] **Spec the Act VI / Chocolate Chip Trip interior** as its own look-dev asset entry and slot
      it into the build order — deliberately deferred, not a freebie. (Tracked in MEMORY.md.)
- [ ] **Continue the master shot list** (`mastershotlist.md`): Act I is drafted (v5-aligned); build
      Acts II–VII (Pneuma inherits the relocated hatch/exploration shots), then fill
      `Fear_Inoculum_ShotList.xlsx` from it.
- [x] **Cleaned the CCT (VI) → 7empest (VII) transition** (Audit #6): split into *rise* vs. *seal* —
      the wider world's corruption rises of its own accord and convenes across CV/CCT into one mass
      above the Tree; 7empest draws that *present* mass in and binds it (no more "gathers twice").
- [ ] **Firm up the Phoenix coloration canon** once real images arrive. The hard "gold/white, never
      red" rule was softened to a guiding preference (creativity first, filter second) so it doesn't
      restrict LLM/creative generation up front — revisit and decide the actual enforcement. (Audit #7.)
- [ ] **Two small canon-wording items** (later): scope "the Phoenix will not hesitate" (CV transition)
      against the 7empest reckoning; and clarify the Act I "first feather" vs. the Pneuma feather that
      "becomes the first speck," so a literal reader doesn't trip. (Audit #8.)
- [x] **Beat-mapped Culling Voices (V)** against its lyrics with timecodes: instrumental open → voices
      enter (1:27) → the culling (3:20–5:27) → 5:27 the guitar takes the song → 5:57–8:11 "Don't you
      dare" collapse → wordless reckoning to 10:05 → transition into CCT. All lyric-bearing acts (I–V,
      VII) are now beat-mapped; VI/CCT stays an instrumental look-dev deferral. Cues to verify vs. master.
- [x] **7empest ending (~9:44 → speck) beat-mapped:** the Reckoner crisis, the two-voice Phoenix /
      Deceiver round (voice never body), the "will be / must be" overlap, the Phoenix-as-tempest
      question. (7empest's earlier gathering/sealing beats remain story-level.)
- [ ] **Verify all timecodes against the master audio file** before storyboarding. Priority:
      the *Invincible* climax (march ~9:44 → freeze ~10:49 → Phoenix eruption ~10:52). Also confirm the
      long *Fear Inoculum* outro (8:37 "a long time coming" → 10:21) and the new Act I lyric cues
      (Bless 3:31–3:43, Exhale 3:56–4:15, Unveil→8:37). ✅ **Act I (*Fear Inoculum*) is now MASTER-VERIFIED** — full vocal map locked (Bless 3:31–3:43, Exhale/Enumerate 3:56–5:41, Forfeit 6:26–6:57, Exorcise 7:34–7:52, Unveil→"a long time coming" 8:11–8:37, outro to 10:21). Remaining priority: Acts II–VII cues + the Invincible climax.

## Done (2026-06-23, restructure session)
- [x] Restored full album order (dropped the Descending-before-Invincible transposition).
- [x] Rewrote **Invincible (Act III)** to hold the Eagle's full arc (maturation → witnessing flight
      → near-breaking → troll march → freeze/realization → dive → eruption → Tree spared).
- [x] Repurposed **Descending (Act IV)** as "the Phoenix's Flight" (elegy → Dire Reveille →
      instrumental soar fading into despair); reworked the lyric table to Phoenix/Mankind.
- [x] Propagated the change through the Asset Spec, README, CONTEXT, LLM_HANDOFF, MEMORY, and
      project memory; bumped canon to **v5** and renamed the treatment file.
- [x] Reframed **Pneuma (Act II)**: growth spine (bird's coming-of-age) + unity peak kept; the late
      "fracture" softened to a looming shadow (real break moved to early Invincible). Added the
      no-fades-between-songs visual rule; growth carries unbroken across the Pneuma→Invincible seam.
- [x] Developed the **back-half dark through-line**: Descending's "call to arms" layered (Phoenix's
      plea ∥ the darkness's muster, answered); Culling Voices = the darkness culling mankind through
      itself while the Phoenix reckons (does not fight) → realization: accept & contain the darkness
      as the 7empest, forever.

## Done (2026-06-23, docs consolidation session)
- [x] Reviewed both canon docs and gave feedback.
- [x] Resolved version sprawl: consolidated to a single canonical `Treatment_v4.docx`.
- [x] Removed duplicate/older treatment files (`v3_1` deleted by Claude; `v3` deleted by Lance).
- [x] Made the Asset Spec reference scenes by act/beat; removed all mm:ss timecodes; bumped its
      canon citation to v4.
- [x] Added a v4 revision entry to the treatment; aligned title/footer labels to v4.
- [x] Produced a paste-ready onboarding prompt for Codex/fresh LLM sessions (see LLM_HANDOFF.md).
- [x] Created ProjectDocs (CONTEXT, MEMORY, TODO, CHATLOG, LLM_HANDOFF).

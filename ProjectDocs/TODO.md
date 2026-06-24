# TODO — Inoculated by the Phoenix

*Last updated: 2026-06-23. Status: pre-production / docs phase. No assets built yet.*

## Now / next
- [ ] **Set up the Blender + VS Code environment** (Asset Spec §4): "Blender Development"
      extension (Jacques Lucke), `fake-bpy-module` for intellisense, Pylance override for
      `bpy.props` noise. Re-verify these tool details are current before relying on them.
- [ ] **Write `bootstrap.py`** — sets units, collections, naming, default camera. Every later
      script imports/assumes it. (Build order step 1.)

## Tier-1 foundations (highest reuse — build first)
- [ ] `MAT_LiquidStarlight` — the single most reused look; hand-authored master shader.
- [ ] `NG_BioPulse` — shared, tempo-syncable luminance/scale pulse for all living things.
- [ ] `FX_Feather` + `MAT_Feather_StateRange` — one feather, single 0–1 corruption/ignition driver.
- [ ] `ENV_Tree` growth system (Sprout → Mid → Mature → Wounded → Regrown), driven by parameters.
- [ ] `CHR_OneBeing` base mesh + `RIG_OneBeing` (eaglet → mature Eagle → Phoenix, shared topology).

## Gate: the 30-second style test
- [ ] Build the Act I opening slice (Creation Sequence: opening chimes → first river reveal →
      sprout) using only the Tier-1 assets above. Must solve starlight, holographic dissolve,
      pulse, palette, and feather rendering in one contained sequence.
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
- [ ] **Beat-map Culling Voices (V)** against its lyrics with timecodes, the way Invincible and
      Descending were done. (Framing is in the treatment; the timecoded beat sheet is still pending.)
- [x] **7empest ending (~9:44 → speck) beat-mapped:** the Reckoner crisis, the two-voice Phoenix /
      Deceiver round (voice never body), the "will be / must be" overlap, the Phoenix-as-tempest
      question. (7empest's earlier gathering/sealing beats remain story-level.)
- [ ] **Verify all timecodes against the master audio file** before storyboarding. Priority:
      the *Invincible* climax (march ~9:44 → freeze ~10:49 → Phoenix eruption ~10:52).

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

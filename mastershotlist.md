# INOCULATED BY THE PHOENIX — Master Shot List

*Working master shot list. Canon-locked to **Treatment v5**. This Markdown is the authoring source; the companion `Fear_Inoculum_ShotList.xlsx` is filled from it.*

*Last updated: 2026-06-24 · Status: **Act I drafted (v5-aligned)**; Acts II–VII to come.*

---

## How to use this document

- **One block per shot.** Fields map 1:1 to the Excel columns, so filling the spreadsheet is mechanical:
  **Shot #** (block title) · **TC In / TC Out** (`TC`) · **Beat** (section banner) · **Description** · **Camera** · **Key Assets** · **VFX / Software** · **Audio Cue** · **Director's Notes** (`Notes`).
- **Timecodes** are anchored to the album recording and must be verified frame-accurately against the master before storyboarding (per the Treatment's note). A leading `~` marks a **proposed/approximate** cue not yet locked.
- **Software shorthand:** H = Houdini · B = Blender · UE5 = Unreal Engine 5 · DR = DaVinci Resolve.
- **Canon wins.** When a shot and the Treatment (`Inoculated_by_the_Phoenix_Treatment_v5.md`) disagree, the Treatment is right; fix the shot.

---

## Act I — Fear Inoculum (10:21) — Creation

> **v5 note.** The Egg stays **sealed** through Act I — it never hatches here; the only hatch is *Pneuma*. Act I's back half is the **passive inoculation**: the shadow builds and lunges at the Tree, and the **Egg's light** (no will, no hatchling) drives it back, ending on a *false* peace. (The hatch + exploration that an earlier shotlist placed here have moved to the Pneuma list; see "Relocated" at the end of this act.)

### THE TEN CHIMES OF CREATION (0:00–0:53)

**FI-001 — Chime 1: First Light**
- **TC:** 0:00 → 0:05
- **Description:** Absolute black. A single point of pure white-gold light appears dead center on the Chime 1 strike. Expands outward in concentric ripple-waves, like a crack forming through nothingness.
- **Camera:** Locked, center frame. No movement.
- **Key Assets:** Point light source; void/black plate.
- **VFX/Software:** H — concentric wave propagation; custom "fabric of nothingness" shader.
- **Audio Cue:** Chime 1 @ 0:00.
- **Notes:** Hold pure black silence before the chime hits. One premature frame of light kills the moment.

**FI-002 — Chime 2: Universe Inhales**
- **TC:** 0:05 → 0:11
- **Description:** Ripples continue outward. On the strike, stars ignite in sequence — first one, then thousands, then uncountable. Galaxies begin to spiral.
- **Camera:** Slow pull-back revealing cosmic scale.
- **Key Assets:** Star particle system; galaxy spiral sims.
- **VFX/Software:** H — sequenced star ignition tied to the chime; galaxy formation sim.
- **Audio Cue:** Chime 2 @ 0:05.
- **Notes:** Time begins to flow with this chime — the first sense of motion in the film.

**FI-003 — Chime 3: Reality Forms**
- **TC:** 0:11 → 0:16
- **Description:** Particles, cosmic dust, energy strands weave themselves into the earliest structures of existence. The universe is thinking itself into being.
- **Camera:** Continued slow drift outward.
- **Key Assets:** Particle systems (dust, strands).
- **VFX/Software:** H — "reality-weaving" procedurals.
- **Audio Cue:** Chime 3 @ 0:11.
- **Notes:** Keep the pace meditative. Do not accelerate the camera yet.

**FI-004 — Chime 4: A World Forms**
- **TC:** 0:16 → 0:21
- **Description:** Camera dives toward a forming world — still a ball of swirling mist. Breaks through the outer atmosphere; a lightning crash @ 0:18–0:19 ignites a mythic spark; the world solidifies in the flash.
- **Camera:** Aggressive dive into the planet; holds wide on completion.
- **Key Assets:** Mist planet; lightning FX; solidification rig.
- **VFX/Software:** H — mist-to-solid transition synced exactly to the lightning frame.
- **Audio Cue:** Chime 4 @ 0:16; lightning @ 0:18–0:19.
- **Notes:** First time the camera moves with purpose. Lightning must hit on frame — sync is non-negotiable.

**FI-005 — Chime 5: Rivers of Mesopotamia**
- **TC:** 0:21 → 0:27
- **Description:** Flash fades to landscape. Rivers trace themselves across the terrain like veins of liquid starlight — vast, ancient, purposeful. Camera follows them upstream, shrinking back toward source springs.
- **Camera:** Reverse tracking along the river paths.
- **Key Assets:** Mythic Mesopotamian terrain; `MAT_LiquidStarlight` river shader.
- **VFX/Software:** H — procedural river-path generation; custom emission/refraction shader for liquid starlight.
- **Audio Cue:** Chime 5 @ 0:21.
- **Notes:** **ESTABLISH the liquid-starlight visual language here.** This look is the DNA of the entire film.

**FI-006 — Chime 6: Springs & Sprout**
- **TC:** 0:27 → 0:32
- **Description:** Two mythic springs glisten in a clearing. Where they meet, a sprout pushes up through the earth — small, weak, barely standing. Pulses gently. Fragile, sacred, alone.
- **Camera:** Slow push-in toward the sprout.
- **Key Assets:** Twin springs; sprout (early `ENV_Tree`); clearing terrain.
- **VFX/Software:** H — spring water sim; bioluminescent pulse rig (`NG_BioPulse`) on the sprout, reused on the Tree.
- **Audio Cue:** Chime 6 @ 0:27.
- **Notes:** Build the sprout as the **same asset** as the Tree — different growth/scale stages of one model.

**FI-007 — Chime 7: Plateau Forms, Oceans Birth**
- **TC:** 0:32 → 0:38
- **Description:** Soil and rock combine around the sprout. Streams carve new land. The plateau takes shape. Thunder @ 0:36–0:37 strikes behind the sprout; a great splash floods the scene; camera zooms out to reveal the birthing oceans surrounding the planet.
- **Camera:** Holds as the plateau forms; rapid zoom-out on the 0:36 thunder hit.
- **Key Assets:** Plateau geometry; ocean shader (matches the starlight rivers).
- **VFX/Software:** H — terrain-formation sim; ocean-birth splash; reuse `MAT_LiquidStarlight` on the oceans.
- **Audio Cue:** Chime 7 @ 0:32; thunder @ 0:36–0:37.
- **Notes:** Thunder is the cue. The splash and zoom-out must hit on the thunder frame, not a beat after.

**FI-008 — Chime 8: All Waters Are One**
- **TC:** 0:38 → 0:42
- **Description:** From an orbital view, oceans connect to rivers, to streams, to the springs at the sprout. Everything pulses together in unison — one living system.
- **Camera:** Orbital hold with a subtle camera pulse.
- **Key Assets:** Whole-planet view; full water network.
- **VFX/Software:** Synchronized pulse animation across all water bodies.
- **Audio Cue:** Chime 8 @ 0:38.
- **Notes:** Establishes "one breath" visually — every body of water on the same rhythm. This is the thesis statement.

**FI-009 — Chime 9: Return Begins**
- **TC:** 0:42 → 0:48
- **Description:** Camera reverses the journey — orbital ocean view back down to rivers, then streams.
- **Camera:** Slow descent — reverse path of FI-005.
- **Key Assets:** Reused water/terrain assets.
- **VFX/Software:** Match-move FI-005 reversed.
- **Audio Cue:** Chime 9 @ 0:42.
- **Notes:** The pan inward should feel inevitable, like returning home.

**FI-010 — Chime 10: Return to Plateau**
- **TC:** 0:48 → 0:53
- **Description:** Camera continues panning back to the springs and sprout. Lightning crashes @ 0:51. Conga-like drums begin @ 0:53–0:54.
- **Camera:** Final approach to the plateau, slowing to rest.
- **Key Assets:** Plateau hero approach shot.
- **VFX/Software:** Lightning strike @ 0:51 as punctuation.
- **Audio Cue:** Chime 10 @ 0:48; lightning @ 0:51; drums @ 0:53.
- **Notes:** Drums entering = "arrived." This shot ends as the drum loop begins.

### THE TREE OF LIFE REVEALED (0:53–1:02)

**FI-011 — Drums Establish: Tree Hero**
- **TC:** 0:53 → 1:02
- **Description:** Plateau hero shot. The sprout has grown — larger, stable, pulsing with purpose. Still fragile but unmistakably the Tree of Life nearing maturity.
- **Camera:** Slow orbit around the Tree.
- **Key Assets:** `ENV_Tree` (mid-stage growth).
- **VFX/Software:** Bioluminescent pulse rig synced to the drum loop.
- **Audio Cue:** Conga drums establish.
- **Notes:** Sync the Tree pulse to the drum tempo if technically possible — establishes the Tree as alive in time with the world.

### THE EGG MATERIALIZES (1:02–1:37)

**FI-012 — The Egg Materializes**
- **TC:** 1:02 → 1:15
- **Description:** A swirling distortion forms above the Tree. Colors fold into themselves — neon blues, purples, golds, greens. Iridescent, shifting. The Egg condenses from psychedelic energy. Simultaneously the indescribable Holding Device (the Creator) materializes. A single phoenix feather pulses **once** in the mist as the Egg forms.
- **Camera:** Tilt up from the Tree to the Egg forming above.
- **Key Assets:** Egg (`MAT_EggShell_Iridescent`); `CHR_Creator_Cradle` (neither mechanical nor organic — design phase); **FIRST FEATHER**.
- **VFX/Software:** H — particle convergence into egg shape; iridescent psychedelic shader; Holding Device needs its own design pass.
- **Audio Cue:** Drum loop continues.
- **Notes:** **CRITICAL — first feather appearance in the film.** Subtle, single pulse. Do not telegraph it; the audience won't understand until rewatch.

**FI-013 — Egg & Tree Breathe Together**
- **TC:** 1:15 → 1:37
- **Description:** Egg complete in the Holding Device. Pulses in rhythm with the Tree. Shell shifts color continuously, never settling. The plateau continues to evolve around them — more defined, more real.
- **Camera:** Slow drift around the Egg + Tree system.
- **Key Assets:** Established Egg, Tree, plateau.
- **VFX/Software:** Synchronized pulse Egg ↔ Tree; ongoing plateau-expansion sim at the edges.
- **Audio Cue:** Drum loop.
- **Notes:** First time the two pulse together. Establish their connection — they are two halves of one cosmic organism.

### CREATION CULMINATES (1:37–2:00)

**FI-014 — Creation Culminates**
- **TC:** 1:37 → 2:00
- **Description:** Tree, Egg, Breath — all in place. Camera drifts slowly around the sacred plateau, which continues expanding outward at its edges as if creation is still arriving.
- **Camera:** Wide, low-angle reverent orbit.
- **Key Assets:** Full plateau at its established state.
- **VFX/Software:** Continued plateau expansion at the edges; ambient breath particles drifting through frame.
- **Audio Cue:** Drum loop builds.
- **Notes:** Hold the silence. The audience absorbs without words — this is the "beginning of everything" beat.

### MAYNARD ENTERS — THE COSMIC INHALE (2:00–2:58)

**FI-015 — "Immunity long overdue…"**
- **TC:** 2:00 → 2:30
- **Description:** Maynard's voice enters. Camera lingers on the Egg in its Holding Device. We admire its purity, mystery, color-shifting beauty.
- **Camera:** Slow push-in toward the Egg.
- **Key Assets:** Egg, Holding Device.
- **VFX/Software:** Continued shell-shader animation; subtle feather drift in the background.
- **Audio Cue:** "Immunity long overdue / Venom in mania."
- **Notes:** Lingering, no cuts. Let the audience fall in love with the Egg.

**FI-016 — "Venom in mania" — Plateau Admired**
- **TC:** 2:30 → 2:58
- **Description:** Camera continues lingering — the Tree, then the springs, then the harmonious whole. Egg, Tree, springs, plateau all working in concert for the benefit of each other.
- **Camera:** Slow tracking across the plateau elements.
- **Key Assets:** Tree, springs, full plateau.
- **VFX/Software:** Continued bioluminescent pulse work.
- **Audio Cue:** Continues into the pre-chorus.
- **Notes:** The cosmic inhale before the story begins. The world is whole. **Restraint is the visual.**

### THE FIRST SHADOW (2:58–3:42)

**FI-017 — "Now, contagion I exhale you"**
- **TC:** 2:58 → 3:12
- **Description:** Fog, mist, and dark clouds begin to consume the edges of the plateau. NOT a being. NOT a form. Just a sense — a ripple in the breath. The downfalls of choice, arriving as they were always meant to.
- **Camera:** Wide on the plateau; slow encroachment of fog at the edges.
- **Key Assets:** Plateau; fog/mist sims; atmospheric "shadow" presence (no defined form yet) — `FX_Shadow_Deceiver`.
- **VFX/Software:** H — volumetric fog/mist; subtle darkening of the plateau's ambient light.
- **Audio Cue:** "Now, contagion I exhale you."
- **Notes:** **No physical Deceiver yet.** The shadow is a feeling, not an entity. Restraint.

**FI-018 — "Deceiver says…" — Tree & Egg Feel It**
- **TC:** 3:12 → 3:42
- **Description:** The Tree pulses uneasily — its rhythm broken for the first time. The Egg flickers, hearing the world change around it. The world remains whole, but something has shifted.
- **Camera:** Close on the Tree; intercut with the Egg in the Holding Device.
- **Key Assets:** Tree (close detail), Egg (close detail).
- **VFX/Software:** Disrupted pulse animation; subtle desaturation creeping in at the frame edges.
- **Audio Cue:** "Deceiver says, he says you belong to me."
- **Notes:** First break in the established rhythm. The uneasy pulse should feel like a heart skipping a beat.

### THE EGG INOCULATES (3:42–10:21) — *v5 rework (Egg sealed; passive repel)*

**FI-019 — The Egg Pulses With Awareness**
- **TC:** 3:42 → 4:30
- **Description:** The Egg now pulses inside the Holding Device with a self-aware rhythm. It senses the tension in the world. It understands it is safe. It is grateful for the safety.
- **Camera:** Tight on the Egg, slow rotation.
- **Key Assets:** Egg, Holding Device.
- **VFX/Software:** Shell color-shift shader becomes "thinking" rather than passive — purposeful timing.
- **Audio Cue:** Building toward the instrumental.
- **Notes:** The Egg knows. Its pulses are different now — wary, purposeful. It **never** opens.

**FI-020 — The Inoculation (the light radiates)**
- **TC:** ~4:30 → ~6:00
- **Description:** The shadow presses inward — fog thickening at the plateau's edges, the Deceiver's whisper circling the Tree. The Egg's inner light intensifies. **Not by choice. Not by will.** It does not move; its purity simply radiates, and the darkness recoils from a light it cannot enter. The world is being protected before it is even born.
- **Camera:** Wide on the plateau; the encroaching dark held back by the glow around the Egg/Tree.
- **Key Assets:** Egg (`FX_InoculationGlow`); Tree; fog/mist (`FX_Shadow_Deceiver`).
- **VFX/Software:** B — emission/volumetric "inoculation glow" that pushes the fog back; H — fog reaction sim.
- **Audio Cue:** Instrumental builds.
- **Notes:** This is **the title made visible** — passive immunity. The Egg fights *nothing*; it merely exists, and the dark can't abide it.

**FI-021 — The Shadow Takes a Shape**
- **TC:** ~6:00 → ~7:30
- **Description:** The fog gathers at the plateau's edge and begins to take a shape — never fully resolved, never named, a darkness pretending to a form. It circles, testing the light, looking for a way in. The sealed Egg pulses steadily, radiant; the Tree holds.
- **Camera:** Wide, the shape looming small-to-large at the edge of frame; the Egg/Tree lit and calm at center.
- **Key Assets:** `FX_Shadow_Deceiver` (bolder, beginning to coalesce — still atmospheric, never a character); Egg; Tree.
- **VFX/Software:** H — volumetric "Deceiver" shader gaining density; ominous color shift at the edges.
- **Audio Cue:** Instrumental darkening.
- **Notes:** Same shader/energy as FI-017, just bolder. **Never resolve it into a character.**

**FI-022 — The Lunge at the Tree**
- **TC:** ~7:30 → ~8:45
- **Description:** The shape gathers itself and **lunges — straight at the Tree.** The Tree's pulse stutters; for one instant the light of the young world falters and the plateau dims.
- **Camera:** Wide of the plateau as the shadow strikes; whip-in to the Tree's faltering pulse.
- **Key Assets:** `FX_Shadow_Deceiver`; Tree (stutter pulse); plateau (dimming).
- **VFX/Software:** Deceiver "lunge" sim; Tree pulse disruption; momentary ambient-light drop.
- **Audio Cue:** Instrumental crescendo.
- **Notes:** This is the act's peril beat — make the Tree feel genuinely threatened, so the repel lands.

**FI-023 — The Egg's Light Answers**
- **TC:** ~8:45 → ~9:45
- **Description:** The Egg's light **flares outward** — without will, without moving. The darkness cannot abide it. The shape recoils and comes apart; the Deceiver retreats from the plateau, repelled by a light it cannot enter; the fog withdraws.
- **Camera:** Push to the Egg as it flares; pull wide as the fog is driven off the plateau.
- **Key Assets:** Egg (`FX_InoculationGlow` — peak flare); retreating fog (`FX_Shadow_Deceiver`).
- **VFX/Software:** B — emission burst from the sealed Egg (no crack, glow only); H — fog dissipation sim.
- **Audio Cue:** Instrumental peak → release.
- **Notes:** Critical: the Egg **does not crack** — the glow alone drives the dark back. Keep the shell whole and sealed in every frame.

**FI-024 — False Peace ("So it thinks")**
- **TC:** ~9:45 → 10:21
- **Description:** The Tree's pulse steadies. The world feels whole again — safe, sacred, untouched. The shadow is gone. *So it thinks.* One last feather drifts past in the foreground as the song settles.
- **Camera:** Settle to a wide on the calm plateau; slow, reverent.
- **Key Assets:** Tree (steady pulse); plateau; a single drifting feather.
- **VFX/Software:** Tree pulse returns to steady rhythm; ambient particles settle; one feather pass.
- **Audio Cue:** Final notes of the song.
- **Notes:** **END ON A FALSE PEACE.** The shadow was only *repelled, never destroyed,* and the Egg never opened — the only true awakening is still to come. This sets up Pneuma.

> **Relocated from the earlier shotlist (do not place in Act I):** the old hatch/exploration/confrontation shots (First Crack, The Hatching, Exploration, The Internal Struggle, Wordless Recognition, Who-To-Follow, the Bird's charge, the Banishment) move forward — the **hatch + exploration + recognition** to the **Pneuma** list, and the active **protective charge** to **Invincible** (the Phoenix's dive to save the Tree). Their production detail (camera/assets/notes) transfers almost verbatim; they just change acts.

---

## Act II — Pneuma (11:53) — Unity & Growth
*To come. Will inherit the relocated hatch + "First Discovery" exploration + wordless recognition (from the earlier Act I shotlist), plus mankind forming, the frisson peak, and the looming-but-unbroken shadow.*

## Act III — Invincible (~12:44) — Awareness & Crisis
*To come. The Eagle's maturation, the witnessing flight, the troll march, the freeze/realization, the dive + eruption (Tree spared), the Ponce de Leon reprise. The protective-charge payoff lands here.*

## Act IV — Descending (~13:38) — The Phoenix's Flight
*To come. Ocean-of-unknowing open, the descent, the layered Dire Reveille, the ~6:49 handoff to the instrumental elegy-flight.*

## Act V — Culling Voices (10:05) — Reckoning
*To come. The dim instrumental open (to 1:27), the voices, the culling, the 5:27 guitar-takeover, the 5:57–8:11 "Don't you dare" collapse, the wordless reckoning.*

## Act VI — Chocolate Chip Trip (4:48) — Inside the Sphere
*To come. Look-dev-led (the rise/interior of the corruption); deliberately deferred until specced.*

## Act VII — 7empest (15:43) — The Eternal Cycle
*To come. Keep-it-calm intro, the dual-address verse, the Blame (everyone vs. the Creator), the wordless guitar torrent + seal, the Crack and two-voice climax, the descent into the crack, the collapse, the speck.*

# INOCULATED BY THE PHOENIX — Asset Spec & Build Bible

**For: Blender asset production (Python-scripted + hand-authored), feeding a Blender → Unreal Engine 5 pipeline**
**Canon source of truth: Treatment v5**
**Purpose: a portable, self-contained reference you can carry into any VS Code / fresh-Claude session so the asset work never drifts off-canon.**

---

## 0. How to use this document

This is the bridge between the story (Treatment v5) and the build. Every asset the film needs is catalogued below with the **canon constraints** that govern it — the non-negotiable rules a model, shader, or rig must respect to stay true to the myth — plus a **build approach** (script it, hand-author it, or hybrid) and a **priority tier**.

When you open a fresh Claude session in VS Code, that Claude knows nothing about this project. Paste the primer in §1 first. Then paste the specific asset entry you're working on. That's enough for it to write canon-correct Blender Python.

---

## 1. Paste-this-first primer (for a context-free Claude session)

> I'm building a wordless feature-length animated film called *Inoculated by the Phoenix*, set entirely to Tool's album *Fear Inoculum*. It's a cosmological myth about a single cosmic being that moves through three phases across one eternal, repeating cycle: **the Egg** (pure potential), **the Bird/Eagle** (the witness — hatches already eagle-shaped, matures across the film), and **the Phoenix** (realization). The visual language is futurist-holographic with Mesopotamian imagery, bioluminescent light, and "liquid starlight." I'm producing assets in Blender, scripting with `bpy` in VS Code, and will assemble in Unreal Engine 5; heavy procedural/particle work goes to Houdini. I'll give you a specific asset spec with canon constraints — write me clean, idiomatic Blender Python (Blender 4.2+/5.x API) that respects those constraints. Don't invent lore; if a constraint is ambiguous, ask.

Keep that paragraph handy. It primes any session in ~150 words.

---

## 2. Global canon constraints (every asset obeys these)

These are the load-bearing rules. They override convenience. If a build choice violates one of these, it's wrong even if it looks good.

1. **One being across time.** The Egg, the Bird/Eagle, and the Phoenix are *the same entity* at different stages — not separate characters. They never coexist on screen (the only "echoes" of the being that appear out of phase are **feathers**). Build their geometry and rigs to share topology wherever possible so the transformations read as continuity, not swaps.
2. **The Bird is eagle-shaped from birth.** It hatches as a fragile *eaglet* and matures into the full mythical Eagle in *Invincible*. There is no moment where it changes species. "Bird" and "Eagle" are the same asset at different maturities/scales.
3. **The Egg never opens during *Fear Inoculum*.** It stays sealed and whole through Act I. Its shell can *intensify and radiate light* (the inoculation) but must never crack or hatch until the hatch in *Pneuma* (Act II). The shell needs a glow-driving parameter that is fully independent of any fracture/hatch state.
4. **The Creator = the Holding Device.** The cradle that holds the Egg is the primordial light/dot/awakening given physical form — the source of everything. It is *neither mechanical, organic, divine, nor technological*; it is the thing those concepts derive from. After the hatch it **dissolves into the world's ambient light** (rivers, Tree, feathers) rather than persisting as an object. Don't model it as a machine or a throne; model it as *contained light that holds a shape only as long as it needs to*.
5. **The speck and the Egg are one.** The single point of light at the opening chime is the same consciousness that later condenses into the Egg. The final feather of the film dissolves into that first speck, closing the loop. Any "first light" / "final speck" asset is the same asset.
6. **Liquid starlight is ONE material**, reused everywhere water-like or life-energy appears: springs, rivers, oceans, the Egg's interior glow, the Tree's pulse, and the base layer of the Phoenix's fire. Build it once as a master shader with exposed parameters; instance it, don't rebuild it.
7. **Everything alive pulses.** Tree, Egg, rivers, Phoenix, the 7empest sphere — all have a rhythmic luminance/scale pulse. Drive it from a shared, ideally tempo-syncable, control so the world can "breathe" together (Pneuma's thesis) and fall out of sync when corruption enters.
8. **Phoenix fire is gold and white. Never red.** Red is reserved *exclusively* for the 7empest / corruption. Keep these two palettes physically separate in your material library so they can never bleed.
9. **The crack is ONE wound in reality.** It first appears between the first and second chime of creation, reopens at the end of *Culling Voices*, and the Phoenix flies into it in *7empest*. The hairline fracture in the *sealed sphere* during 7empest is a **separate** thing (a seal failing) and must look different from the creation-seam.
10. **Trolls are corrupted humanity, not external monsters.** Faint traces of the human form remain visible beneath the stone/clay. They are built by *distorting the mankind base mesh*, not as a from-scratch creature.
11. **Feathers are soul-fragments and appear before the Phoenix exists.** One feather asset with a continuous **state range**: glowing/iridescent → muted → blackened/smoldering → ignited. State tracks the world's health.
12. **Holographic dissolve.** Object edges can dissolve into light particles. This is a global look principle — budget for it in shaders/geo-nodes on hero assets rather than treating it as a one-off effect.
13. **Color follows the act.** Palette desaturates from Act I→V, goes to pure chaos in Act VI, returns to black-and-gold in Act VII. Bake act-palette swatches into your material setup so lighting/grade stays on-canon per scene.

---

## 3. Scene & naming conventions (agree on these before the first script)

Set these once and make every script honor them, or assets won't compose later in UE5.

- **Units:** Metric, 1 Blender unit = 1 meter. Set `scene.unit_settings.scale_length = 1.0`.
- **Scale discipline:** Build hero assets at sane real-world-ish scale (Egg ≈ 1–2 m; juvenile Eagle wingspan ≈ 1.5 m; mature Eagle ≈ 4–6 m; Phoenix ≈ tens of m; Tree ≈ 30–60 m at maturity). **Do not** build galaxies at true scale — fake cosmic scale with camera/scene scaling and depth cues to avoid float-precision breakdown. Apply transforms (`object.transform_apply`) before export.
- **Orientation:** +Z up, -Y forward (Blender default), which maps cleanly to UE5 on FBX/USD import. Decide your forward axis now and keep it.
- **Naming prefixes:**
  - `CHR_` characters/beings · `ENV_` environment · `PROP_` props · `FX_` effects/sim proxies · `MAT_` materials · `RIG_` armatures · `GN_` geometry-node groups · `NG_` shader node groups.
  - Example: `CHR_Eagle_Mature`, `ENV_Tree_Stage3_Mature`, `MAT_LiquidStarlight`, `GN_Feather_Instancer`, `RIG_OneBeing`.
- **Collections:** Organize by category first, then by act where relevant: `CHR/`, `ENV/`, `FX/`, plus a `_StyleTest/` collection. Keep one master `.blend` per major asset, link/append into shot files later.
- **Versioning:** asset files carry a version suffix; never overwrite a known-good `.blend`.

---

## 4. Blender + VS Code setup (grounded, current as of mid-2026)

- **Live-execution workflow (recommended):** Install the **"Blender Development"** extension (Jacques Lucke) in VS Code. `Ctrl+Shift+P → Blender: Start`, point it at your Blender executable. It runs your code inside a live Blender, streams output to the VS Code terminal, and supports **breakpoints**. Enable `blender.addon.reloadOnSave` for reload-on-save.
- **Autocomplete:** The real `bpy` ships **no stub files**, so Pylance can't autocomplete it. Install **`fake-bpy-module`** (`pip install fake-bpy-module`) into your VS Code interpreter for `bpy`/`mathutils`/`gpu` intellisense. It's stubs only — runtime still happens in Blender.
- **Pylance noise:** Blender's `bpy.props` registration trips Pylance's type checks. Silence it in workspace settings:
  ```json
  "python.analysis.diagnosticSeverityOverrides": { "reportInvalidTypeForm": "none" }
  ```
- **Headless/batch generation:** For "generate N variants" scripts, run `blender --background --python your_script.py`. On Blender 4.2+ you can also register entry points with `bpy.utils.register_cli_command` and invoke with `--command`.
- **Standalone `bpy` (optional):** `pip install bpy` gives Blender-as-a-module, but it's version-locked to one exact Python (currently Python 3.13) and is heavyweight. Only worth it for fully headless pipeline tooling; for look-dev, prefer the live extension.
- **Avoid `sys.exit()` inside Blender scripts** — it can take Blender down. Return/raise instead.

---

## 5. Script it vs. hand-author it

A blunt heuristic for where Python pays off versus where you'll move faster by hand:

| Script it in Python (`bpy`) | Hand-author in Blender UI |
|---|---|
| Parametric assets with variants (Tree growth stages, feather state range, troll vice-distortions) | Hero shaders / look-dev (liquid starlight, Egg shell, Phoenix fire) |
| Batch operations (instancing 10,000 feathers, scattering a city) | One-off art-directed silhouettes and key poses |
| Repeatable scene setup (units, collections, naming, cameras) | Sculpt-level detail and final topology cleanup |
| Procedural placement (rivers along terrain, stars) | Tuning a single beautiful frame |
| Anything you'll regenerate after a canon tweak | Anything judged purely by eye, once |

**Important:** Geometry Nodes and shader node trees *are* scriptable via Python, but wiring complex node graphs in code is verbose and brittle. Best practice: **build the hero node graph by hand**, then script only the parts you need to parameterize or batch (expose inputs as a node group, drive those inputs from Python). Don't try to author the liquid-starlight shader graph line-by-line in `bpy`.

---

## 6. Asset catalog

Format per entry — **Canon constraints** (must-obey) · **Build** (approach) · **Reuse** · **First appears** · **Tier**.

> **Timecodes live in the Treatment, not here.** "First appears" names the act and beat only. For exact mm:ss cues, consult Treatment v5 — and verify against the master audio before storyboarding, per the Treatment's own note.

### 6.1 The beings (the one entity across time)

**`CHR_Egg`**
- *Canon:* Sealed and whole through Act I; never cracks before the *Pneuma* hatch. Iridescent color-shifting shell that never settles. Inoculation glow must intensify/radiate **independently of any fracture state**. Pulses in sync with the Tree.
- *Build:* Mesh by hand (simple ovoid, clean quad topology for later fracture). Shell look = `MAT_EggShell_Iridescent`. Inoculation glow = emission strength driver + volumetric halo. Keep a *separate* fracture/hatch shape-key or Cell-Fracture setup for the Pneuma hatch only.
- *Reuse:* Same object that the speck condenses into (§6.4 `FX_FirstLight`).
- *First appears:* Act I — *the Egg Materializes* (condensing above the Tree). *Tier 2.*

**`CHR_OneBeing` (shared base for Eaglet → Eagle → Phoenix)**
- *Canon:* One being, three readable stages. Eaglet and mature Eagle share topology (scale + proportion + plumage detail differ). Phoenix shares the *skeletal/wing structure* so the rise reads as the same body igniting, not a new creature. Eyes: "twin suns" at Phoenix stage.
- *Build:* Hand-sculpt/retopo the mature Eagle as the canonical mesh. Derive the eaglet via shape keys (shorter wings, downy proportions, oversized relative head/feet). Derive the Phoenix via the same skeleton with extended wing geo + fire layers. **One `RIG_OneBeing` armature** drives all three.
- *Reuse:* Everything. This is the protagonist.
- *First appears:* Eaglet at the *Pneuma* hatch; mature Eagle as *Invincible* opens (its maturation beat); Phoenix at the *Invincible* Rise (the realization/time-freeze). *Tier 1.*

**`CHR_Phoenix_FireLayers`**
- *Canon:* Gold/white fire, **never red**. Feathers of living flame; wings of molten gold. Fire base layer derives from the liquid-starlight material's energy, ignited.
- *Build:* Hybrid — geo for wing/body shells (from `CHR_OneBeing`) + Houdini/Blender sim or geo-nodes flame for the living-flame plumage. Keep flame palette locked to gold/white in `MAT_PhoenixFire`.
- *First appears:* Act III — the *Invincible* Rise. *Tier 2.*

**`CHR_Mankind_Base`**
- *Canon:* Rendered as **humanoid light-forms** early (Pneuma), becoming *more solid* as they corrupt. Born from the same breath as the Bird (visually echo the being's glow at birth).
- *Build:* One base humanoid mesh + rig. A "solidity" parameter (shader + maybe geo) ramps from translucent light-form → opaque as corruption rises. Crowd instancing via geo-nodes/particle for populations.
- *Reuse:* Source mesh for `CHR_Troll`.
- *First appears:* Act II — *Mankind Begins to Form* (Pneuma). *Tier 3.*

**`CHR_Troll` (distortions of `CHR_Mankind_Base`)**
- *Canon:* **Not external monsters** — the final form of accepted human corruption, with faint human traces visible beneath stone/clay. Limbs distort by vice: grasping hands (greed), swollen forms (gluttony), jagged edges (cruelty), hollowed eyes (envy). Skin cracks like dried clay.
- *Build:* Script-friendly — drive distortions as parameterized shape-key/displacement sets on the mankind base so you can generate a varied mob. `MAT_TrollStoneClay` with crack detail + faint subsurface "humanity" glow.
- *Canon (continuity):* The mob unmade at the Tree in *Invincible* is **local**; trollified humanity persists elsewhere (needed for *Culling Voices* and *7empest*). Build enough variety for both the doomed mob and the surviving population.
- *First appears:* Act III — the Troll March / *The Transformation Begins*. *Tier 3.*

**`CHR_Creator_Cradle` (the Holding Device)**
- *Canon:* The Creator itself — primordial light given form. Not mechanical/organic/divine/technological. Holds a cradle shape only while needed; **dissolves into ambient world-light after the hatch**. Materializes just after the Egg, above the Tree.
- *Build:* Volumetric/emissive "contained light" — geo-nodes + volume shader, minimal hard surface. Author a *dissolve-to-ambient* transition (drives the world's rivers/Tree/feather glow up as the cradle fades). Avoid any sci-fi/throne reading.
- *Reuse:* Conceptually identical light to `FX_FirstLight` / the speck.
- *First appears:* Act I — just after *the Egg Materializes*, above the Tree. *Tier 2.*

### 6.2 Environment

**`ENV_Tree` (growth-stage system: Sprout → Mid → Mature → Wounded → Regrown)**
- *Canon:* **One asset at stages**, not separate trees. The body of creation; source of all rivers; two halves of one organism with the Phoenix (Tree = body, Phoenix = breath). Pulses; bioluminescent. Dims as the world darkens, regrows brighter after the Phoenix.
- *Build:* Script-friendly — parameterize growth (trunk girth, branch count, canopy spread, luminance) so stages are one driver. Wounded stage = withered branches + dimmed pulse + crack detail. Bioluminescent pulse via `NG_BioPulse`.
- *First appears:* Sprout in Act I's Creation Sequence; matures across the film. *Tier 1.*

**`ENV_Plateau` + `ENV_Terrain_Mesopotamia`**
- *Canon:* Mythic Mesopotamian plateau, the sacred center; "continues to expand at the edges as if creation is still arriving." Futurist-holographic, not literal desert.
- *Build:* Sculpt/hand base + scriptable edge-expansion. Holographic dissolve at far edges.
- *First appears:* Act I — forming during the Creation Sequence. *Tier 2.*

**`ENV_Water_System` (springs, rivers, oceans)**
- *Canon:* All one connected system; all use **liquid starlight**; all pulse in unison ("all waters are one"). Starlight fades from water as mankind corrupts; returns with the Phoenix.
- *Build:* Geo for riverbeds/coastlines (scriptable along terrain); all share `MAT_LiquidStarlight`. Sim (flow/splash, ocean birth) → Houdini, proxied in Blender.
- *First appears:* Act I Creation Sequence — rivers, then springs, then oceans. *Tier 2.*

**`ENV_Cosmos` (void, first light, stars, galaxies)**
- *Canon:* The darkness *before* light. Chime-by-chime ignition of stars then galaxies. "First" = first-of-this-cycle (bootstrap; never assert an absolute pre-cycle beginning).
- *Build:* Fake scale (see §3). Particle/geo-nodes star fields; emissive galaxy cards/volumes. Ignition sequence driven by a timeline aligned to the ten chimes.
- *First appears:* Act I — the opening of the Creation Sequence (chime 1). *Tier 3.*

**`ENV_Cities_Empires`**
- *Canon:* Mankind's expansion into empire, then rot from within. Mesopotamian-futurist (Uruk/Akkad/Babylon as holographic myth, not historical reconstruction). Collapsing libraries, cuneiform drifting upward "like dying fireflies."
- *Build:* Modular kit (scriptable scatter/instancing). Decay as a parameter.
- *First appears:* Act III — the *Invincible* witnessing flight (and again across the *Descending* flight). *Tier 3.*

### 6.3 Effects & simulations (mostly Houdini; Blender for proxies/look)

These are flagged for **Houdini** where procedural/particle depth matters; build Blender proxies for layout and import sims via Alembic/VDB later.

| Asset | Canon constraint | Primary tool | Tier |
|---|---|---|---|
| `FX_CreationRipples` | Concentric waves writing physics into being; tied to chimes 1–3 | Houdini | 4 |
| `FX_Lightning` | Punctuates chimes 4, 7, 10; ignites solidification on-frame | Houdini/Blender | 4 |
| `FX_InoculationGlow` | Egg light radiates outward, passively repels shadow; no will, no hatch | Blender (shader/volume) | 2 |
| `FX_Shadow_Deceiver` | A *sense*, not a being; fog/mist/dark cloud; never resolves to a character (no body/face) — but finds one disembodied **voice** at the 7empest climax | Houdini volumetrics | 3 |
| `FX_FeatherStorm` | Every feather in the film converges on the Eagle at the realization (the *Invincible* freeze) | Houdini (instanced) | 4 |
| `FX_TimeFreeze` | World freezes at the *Invincible* realization beat; **Eagle + feathers stay outside the freeze** | Blender (anim/state) | 4 |
| `FX_7empest_Swirl` | Raw, *not-yet-sealed* corruption; pure chaos; **red palette**; glyphs flashing | Houdini | 4 |
| `FX_7empest_Sphere` | Sealed crystalline/faceted vessel of all corruption; troll faces, burning forests inside | Houdini + Blender | 4 |
| `FX_SealCrack` | Hairline fracture in the *sealed sphere* — distinct from the creation-seam | Blender | 4 |
| `FX_CreationSeam_Crack` | The ONE wound in reality; appears chime 1–2, reopens end of Culling Voices, entered in 7empest | Houdini/Blender | 4 |
| `FX_Collapse_Implosion` | Sphere implodes; stars blink out in reverse creation order; everything ends | Houdini | 4 |
| `FX_FirstLight / Speck` | Single point of light = nascent Egg; final feather dissolves into it; loops to chime 1 | Blender | 2 |

### 6.4 Motif assets

**`FX_Feather` (state-range asset)**
- *Canon:* Soul-fragments; appear before the Phoenix exists; never explained. Continuous state: **glowing/iridescent → muted → blackened/smoldering → ignited**. Final feather → first speck (loops the film).
- *Build:* One feather mesh/card + `MAT_Feather_StateRange` with a single 0–1 "corruption/ignition" parameter driving color/emission/char. `GN_Feather_Instancer` for drifting ambient feathers and the realization-beat storm.
- *Tier 1* (it's the connective tissue of the whole film — build early).

**`PROP_Glyphs_Cuneiform`**
- *Canon:* Cuneiform/proto-Hebrew/Akkadian/Sumerian sigils; drift like dying fireflies; flash unreadably fast inside the 7empest.
- *Build:* Scriptable instanced glyph library (cards/geo) with emissive drift.
- *Tier 3.*

---

## 7. Material / shader library (build once, expose parameters, instance)

| Material | Canon-critical parameters | Notes |
|---|---|---|
| `MAT_LiquidStarlight` | flow, emission, refraction, "starlight density" (fades with corruption) | The single most reused look. Build first, hand-authored. |
| `MAT_EggShell_Iridescent` | hue-shift speed, iridescence, **glow strength (independent of any crack)** | Never settles on a color. |
| `NG_BioPulse` | rate (tempo-syncable), amplitude, sync/desync | Shared luminance/scale pulse for all living things. |
| `MAT_PhoenixFire` | gold↔white range only | **Hard-locked away from red.** |
| `MAT_7empest_Corruption` | red palette, chaos/turbulence, glyph flicker | **The only place red lives.** |
| `MAT_TrollStoneClay` | crack density, dryness, faint human-subsurface glow | Humanity must remain faintly visible beneath. |
| `MAT_Feather_StateRange` | single 0–1 corruption/ignition driver | Drives the whole feather lifecycle. |
| `NG_HoloDissolve` | edge-dissolve threshold, particle size | Global look principle on hero edges. |
| `MAT_Mankind_LightForm` | solidity (translucent → opaque with corruption) | Born as light, solidifies as it falls. |

---

## 8. Rigs & shared topology

- **`RIG_OneBeing`:** one armature spanning eaglet → mature Eagle → Phoenix. Wing chains long enough for the Phoenix's extended span; eaglet uses a scaled/constrained subset. This is what makes the transformations read as *the same body remembering itself*, per canon #1–2.
- **`RIG_Mankind`:** one humanoid rig; `CHR_Troll` reuses it with distortion shape-keys, so a troll is visibly a corrupted human (canon #10).
- **Feathers:** no rig — instanced via geo-nodes, driven by the state parameter and (for the realization-beat storm) by a converging force field/curve.

---

## 9. Build order (the roadmap)

Follow difficulty/reuse, not narrative order (per your standing principle).

1. **Scene conventions + a tiny `bootstrap.py`** that sets units, collections, naming, and a default camera. Every later script imports/assumes it.
2. **Tier-1 foundations (highest reuse):** `MAT_LiquidStarlight`, `NG_BioPulse`, `FX_Feather` + `MAT_Feather_StateRange`, `ENV_Tree` growth system, `CHR_OneBeing` base + `RIG_OneBeing`.
3. **The 30-second style test.** Pull from the assets above — recommended slice: the opening chimes through the first river reveal and the sprout (Act I Creation Sequence). This forces you to solve the starlight look, the holographic dissolve, the pulse, the palette, and feather rendering in one contained sequence. **Do not start full scene production until this looks right.**
4. **Tier-2 hero assets:** `CHR_Egg` + shell, `CHR_Creator_Cradle`, `ENV_Plateau`/terrain, `ENV_Water_System`, `CHR_Phoenix_FireLayers`, `FX_FirstLight/Speck`, `FX_InoculationGlow`.
5. **Tier-3 populations:** `CHR_Mankind_Base` (+light-form shader), `CHR_Troll` distortions, `ENV_Cities_Empires`, `ENV_Cosmos`, `FX_Shadow_Deceiver`.
6. **Tier-4 climactic sims (Houdini-led):** creation ripples, feather storm, time-freeze, the 7empest swirl/sphere/cracks, the collapse, the final speck loop.

Then — and only then — a shot list becomes a real shooting plan against assets that exist.

---

## 10. Pipeline notes (Blender → UE5, with Houdini sims)

- **Export:** Static/rigged assets → FBX or USD into UE5. USD is increasingly the cleaner choice for a procedural-heavy pipeline; FBX remains reliable for rigged characters. Apply transforms, real-world scale, +Z up before export.
- **Sims:** Houdini → Alembic (`.abc`) for animated geo, VDB for volumes (fire, fog, the 7empest), into Blender for look or straight into UE5.
- **Shaders don't transfer 1:1.** Blender material node graphs won't import into UE5 — you'll rebuild hero looks as UE5 materials. So **document each material's intent and parameters** (this table in §7 is the start) rather than relying on the Blender graph surviving the trip.
- **Keep `MAT_PhoenixFire` (gold/white) and `MAT_7empest_Corruption` (red) as separate material families** in every tool, so the gold-never-red rule survives the pipeline.
- **Tempo-sync:** since the whole film is music-locked, consider driving `NG_BioPulse` and ignition sequences from a frame-mapped tempo track early, so "the world breathes with the album" is built in rather than retrofitted.
- **Instrument → visual layer (Treatment, "The Four Instruments"):** map each stem to what it drives — **guitar** → the being and the energy of objects; **bass** → lighting & mood; **drums** → environment & weather (sky, storm, lightning, impact); **vocals** → story beats. Stem-separate the master if possible so each layer can drive its own animation/FX (e.g., drums → `FX_Lightning`/environment, guitar → `CHR_OneBeing` motion + `NG_BioPulse`).

---

*Inoculated by the Phoenix — Asset Spec & Build Bible · Canon-locked to Treatment v5 · Personal non-commercial creative work.*

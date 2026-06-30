# Art Direction — the look bible (owner-sourced references)

> Source of truth for the **visual language** of *Inoculated by the Phoenix*. The Treatment owns story
> + timecodes; the Asset Spec owns build rules; **this owns palette, material mood, and reference DNA.**
> Established 2026-06-30 from a set of owner-supplied reference images ("none exact — building the
> general idea of the set"). Drop the actual reference files in `ProjectDocs/Reference/images/`.

## 0. The root palette — the *Fear Inoculum* album cover

The album cover **is** the film's color spine:
- **Antique brass-gold** — the "TOOL" / "FEAR INOCULUM" lettering. Warm, metallic, art-nouveau gold
  (~`#B8923A`–`#C9A24B`). **This gold = the One Being's light.**
- **Cool cyan-blue pinpoints** — the perforated, curved "wave/funnel" mesh of tiny blue luminous dots
  on near-black (~dots `#4F8FD0`, field `#0A0E14`). A **general cosmic-blue accent** (liquid starlight,
  distant starfields) — **NOT** the origin of first light (see canon decision).

### CANON DECISION — the first spec of light
**FI-001 "First Light" is a single point of TOOL-lettering gold, born through pure black on the opening
chime.** Only the **lettering color** (antique brass-gold) carries over from the cover. The background
is **absolute black**; the **chime brings the light through it** (sound births the first photon). There
is **NO blue, NO dotted mesh, NO perforated wave** in this shot — that field is general palette, not the
origin of first light. Pure black → one gold spark. This is locked.
*Built in* `blender/act1_first_light.py` — gold emissive spec on a true-black world + a compositor
fog-glow bloom and a 6-point "chime" starburst; `--frames` keys the ignition to the downbeat. (This
beat is Blender, not gen-AI: a point on black is too little content — SDXL invents mesh/flower/ring.)

### The gold through-line (the spine of the myth, in one color)
The **first photon of creation** and the **Phoenix's fire** are the **same gold**. One being's light,
struck at the beginning of the cycle (Egg/First Light) and again at its rebirth (Phoenix). Every
gold beat in the film — first light, the Egg's gold facets, the Phoenix — is the same hue answering
itself across the eternal cycle. Use it deliberately; don't dilute gold into generic "warm light."

## 1. The Phoenix (title creature)
Reference: fiery phoenix, wings spread, rising from dark cloud against a blazing sky.
- Raptor/eagle build (not a peacock); broad spread wings, fanned tail.
- **Gold-into-orange-into-red fire** — core is the *same brass-gold as first-light*, edges flare to
  orange/scarlet. Feathers read as both plumage and flame.
- Always **rising / ascendant**, emerging from darkness or smoke. Backlit, god-ray halo.
- It is the cycle's answer to the first photon: the light, now embodied and aflame.

## 2. The Egg (CHR_Egg)
References: 3D-printed dragon egg (faceted blue→green scales), psychedelic neon-swirl egg (magenta/
rainbow on black), rainbow-striped egg.
- **Faceted / scaled / patterned shell** — jewel-like, not smooth plastic. Think cut-gem or dragon
  scale tessellation catching light.
- **Iridescent, neon-on-dark** — saturated blue → violet → gold → green shift across the surface as
  it/the camera turns; lit against deep darkness so the color glows.
- SEALED every frame (canon). Glow ≠ crack. The shell is a living jewel, faintly lit from within.

## 3. Liquid Starlight (MAT_LiquidStarlight) — the shared water material
References: a **flowing luminous river** streaming through a dark mossy forest (THE key ref); glowing
bottle with rainbow-blue liquid + sparkle; glass bottle with a galaxy/starfield suspended inside.
- **NOT a resin.** This is the locked correction: liquid starlight is **thin, flowing, alive** —
  water-weight, not gel. A *river of liquid light* full of **countless tiny star-points moving in the
  current**, sparkling as it streams. NOT thick / glassy / viscous / set / syrupy / a solid glossy
  slab. (The glass-bottle refs were about the *glowing contents*, not a glassy container — don't make
  the liquid itself read as glass/resin.)
- **Luminous cyan-white base** with faint **rainbow filaments**; suspended star-points + fine sparkle;
  soft self-emission so it lights its banks. Flows, ripples, currents — it *moves*.
- Reads as a *living liquid made of starlight* — equal parts water, nebula, and light.
- **Shows best in the dark.** Its glow only reads against darkness, so starlight water lives in
  dark/bioluminescent settings (see §4), with a warm gold light somewhere behind (the through-line).
- This is ONE material everywhere water appears (springs, pools, rivers, the Tree's reflection).

## 4. The Plateau / Eden (ENV_Plateau)
References: lush green garden (cycad/sago palms, river, grasses, cattails, wildflowers); desert oasis
(palms, turquoise pools, vivid orange/pink/yellow flowers, sandstone hills).
- A **paradise** — warm, fertile, alive; soft golden hour key light, naturalistic but heightened.
- The twist that makes it ours: **its water is Liquid Starlight.** The pools/springs/river glow
  cyan-rainbow; the lush life grows around luminous water, not ordinary water.
- Two flavors blend: the **green-garden** lushness + the **oasis** turquoise-pool clarity.

## 5. The Tree of Life
Reference: rainbow willow — multicolored glowing foliage, prismatic, reflected in still water.
- **Prismatic glowing canopy** — every color, lit from within like fiber-optic foliage; willow-like
  cascading form reading as both tree and aurora.
- Stands in / over a **Liquid Starlight pool** that mirrors it. The reflection is half the shot.
- Trunk grounded and real (bark, roots) so the glowing canopy reads as miraculous, not cartoonish.

## How this drives the pipeline
These set the **prompt language** for the gen-AI hybrid (`genai/comfy_gen.py` + `comfy_img2img.py`)
and the **target** for the procedural Blender materials. Every Act I beat should trace its palette to
§0 (gold + cosmic-blue) and its element mood to §1–5 above. When a render drifts brighter/flatter/
more "toddler" than these, it's wrong — pull it back toward this bible.

## Look-dev keepers (the look, locked — `ProjectDocs/Reference/images/`)
The six elements rendered to target, 2026-06-30 (contact sheet: `00_contact_sheet.png`):
- `01_first_light.png` — FI-001, lettering-gold spec on pure black (Blender, `act1_first_light.py`)
- `02_liquid_starlight.png` — flowing self-luminous river (NOT resin)
- `03_egg.png` — sealed dragon-scale iridescence, lit from within
- `04_tree_of_life.png` — glowing canopy over a starlight pool, mirrored
- `05_plateau_eden.png` — lush Eden with a glowing liquid-starlight river
- `06_phoenix.png` — gold-into-fire raptor, rising
These are the **bar**: new Act I frames should match this quality/palette or they're not done. Owner
reference images (the source inspiration) can also live in this folder alongside the keepers.

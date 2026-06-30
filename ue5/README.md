# UE5 — assembly + Lumen render (`ue5/`)

Claude-driven, **headless** Unreal Engine 5.8, the same way we run Blender: drive it with Python, render
frames to disk, view the frames (no live viewport). UE5 is for what 2D gen-AI and Blender stills can't
give cheaply: **persistent 3D worlds, sustained camera moves, big crowds/sims, and Lumen "pop"** on hero
assets (glowing translucent jewels render spectacularly under real-time GI). It's also the film's
assembly engine — and can feed depth/canny "bones" to the gen-AI ControlNet pass.

## Layout
- **Engine:** `E:\UE5\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe` (UE 5.8.0).
- **Project (off C: per drive policy):** `F:\ue5\IBTP\IBTP.uproject` — Blueprint-only (no C++ compile),
  plugins: PythonScript, EditorScriptingUtilities, SequencerScripting, MovieRenderPipeline. Lumen + DX12.
- **DDC / shader cache → F:** set `UE-LocalDataCachePath=F:\ue5\ddc` in the environment when launching
  (UE writes many GB of shader cache; it must NOT land on C:).
- **Python scripts:** here in `ue5/` (version-controlled). Render output → `F:\…\_scratch\ue\`.

## Run a script headless
```
set UE-LocalDataCachePath=F:\ue5\ddc
"E:\UE5\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "F:\ue5\IBTP\IBTP.uproject" ^
  -run=pythonscript -script="F:\Inoculated by the Phoenix\ue5\hello.py" -unattended -nopause -nosplash -nullrhi -stdout
```
- `-nullrhi` skips shader compile (fast) for non-rendering scripts. Drop it for actual rendering (the
  first real render triggers a long one-time shader compile into the DDC).
- First launch is slow (project init + shader warmup). Subsequent runs are fast.

## Scripts (in this folder; copied to `F:\ue5\scripts\` for no-space launch paths)
- `hello.py` / `probe.py` — headless Python smoke tests (write a sentinel file).
- `build_scene.py` — build + save a test scene: level + sphere + lights + cine camera + Level Sequence
  (run with `-ExecutePythonScript`). `make_queue.py` — build + save a `MoviePipelineQueue` asset.
- `render.py` — render via the editor Movie-Render-Queue subsystem (PIE/NewProcess executor).

## Status (2026-06-30)
**Stood up and working:** headless Python; building levels, meshes, lights, cine-cameras, Level Sequences,
and Movie-Render-Queue assets — all via Python.
**Open (the wall): the headless MRQ RENDER doesn't emit a frame yet.** See `[[ue5-headless]]` in project
memory for the full play-by-play. Key gotchas already solved/learned:
- Editor-world ops (new_level/spawn) **need `-ExecutePythonScript`** (a real world), NOT the
  `-run=pythonscript` commandlet (access-violates — no world).
- Light components: `actor.get_component_by_class(unreal.PointLightComponent)`. MovieScene ops live on
  `unreal.MovieSceneSequenceExtensions`; binding id = `unreal.MovieSceneObjectBindingID(guid=binding.get_id())`.
- **Delete `/Game/<dir>` before recreating assets** (else `create_asset` returns None).
- **Run the command-line `-game` render from PowerShell, NOT Git Bash** — Git Bash mangles `/Game/...`
  and `/Script/...` args into `C:/Program Files/Git/...`.
- The `-game -MoviePipelineConfig=<queue>` render loads the executor only with the right module
  (`/Script/MovieRenderPipelineEditor.MoviePipelinePIEExecutor`) but still exits 3 — the next thing to
  resolve (try `UnrealEditor.exe` with slate/PIE viewport, or drop `-RenderOffscreen`).

UE5's payoff is **assembly / persistent worlds / Lumen / crowds** for the film — not blocking the egg,
which is being solved in Blender first (see `[[egg-look-status]]`).

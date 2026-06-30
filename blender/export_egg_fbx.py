r"""export_egg_fbx.py — export just the CHR_Egg mesh (UV-unwrapped) to FBX for UE import.

The gem material is authored in UE (Lumen); UE only needs clean egg geometry with a sane UV layout.

Run:
  "E:\Software\blender.exe" -b --factory-startup --python blender/export_egg_fbx.py -- --out F:/ue5/assets/Egg.fbx
"""
import bpy, sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import bootstrap
import tier2_chr_egg_gem as eggmod   # reuse build_egg() (importing only defines functions)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = argv[argv.index("--out") + 1] if "--out" in argv else "F:/ue5/assets/Egg.fbx"

    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bootstrap.set_units()
    egg = eggmod.build_egg(name="CHR_Egg")

    bpy.ops.object.select_all(action="DESELECT")
    egg.select_set(True); bpy.context.view_layer.objects.active = egg
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.02)   # radians (~66 deg)
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.shade_smooth()

    os.makedirs(os.path.dirname(out), exist_ok=True)
    bpy.ops.export_scene.fbx(
        filepath=out, use_selection=True, object_types={"MESH"},
        apply_unit_scale=True, global_scale=1.0, mesh_smooth_type="FACE",
        add_leaf_bones=False, bake_anim=False)
    print(f"[export-egg] wrote {out} (verts={len(egg.data.vertices)})")


if __name__ == "__main__":
    main()

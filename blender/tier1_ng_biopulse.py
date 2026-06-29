r"""
tier1_ng_biopulse.py — NG_BioPulse, the heartbeat driver (Asset Spec §6/§9, Tier-1).

The living pulse of the film: the slow breath that makes the liquid-starlight glow rise and
fall, the Tree's heartbeat, the throb under the Egg's shell. A reusable UTILITY node group
(scriptable per §5 — it is a driver, not a hero look) that outputs a single Float `Pulse`:

    Pulse = Baseline + Amplitude * (0.5 + 0.5*sin(TAU * Time * Rate)) ** Sharpness

Exposed inputs (all drivable from Python / synced to the music later):
    Time        seconds (drive from frame/fps for live playback)
    Rate        pulses per second  (0.2 Hz ~= one calm beat every 5 s)
    Amplitude   how far the glow swings above Baseline
    Baseline    the resting glow it never falls below
    Sharpness   1 = gentle breath  ->  6 = sharp throb (powers the peak)

Output: `Pulse` (Float). Plug it into MAT_LiquidStarlight's "Emission Strength" (or
"Starlight Density") and the look breathes. `apply_biopulse()` does exactly that.

Run (renders the mature Tree at a chosen phase; --time picks where in the beat):
  "E:\Software\blender.exe" --background --factory-startup --python blender/tier1_ng_biopulse.py -- --stage mature --time 1.25 --render peak.png
  "E:\Software\blender.exe" --background --factory-startup --python blender/tier1_ng_biopulse.py -- --stage mature --time 3.75 --render trough.png
"""
import bpy, sys, os, math

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import bootstrap
import tier1_env_tree as tree
import tier1_mat_liquid_starlight as starlight

TAU = 2.0 * math.pi

# defaults — a slow, calm heartbeat (one beat ~ every 5 s), glow swinging 1.0 -> 3.0
DEF = dict(Time=0.0, Rate=0.2, Amplitude=2.0, Baseline=1.0, Sharpness=2.5)


def pulse(t, rate=DEF["Rate"], amp=DEF["Amplitude"], base=DEF["Baseline"], sharp=DEF["Sharpness"]):
    """Pure-Python mirror of the node graph — for the waveform proof + unit checks."""
    s = 0.5 + 0.5 * math.sin(TAU * t * rate)
    return base + amp * (s ** sharp)


def _set(node_input, value):
    try:
        node_input.default_value = value
        return True
    except Exception:
        return False


def build_group():
    ng = bpy.data.node_groups.get("NG_BioPulse")
    if ng:
        return ng
    ng = bpy.data.node_groups.new("NG_BioPulse", "ShaderNodeTree")
    itf = ng.interface

    def add_in(nm, default):
        s = itf.new_socket(nm, in_out="INPUT", socket_type="NodeSocketFloat")
        s.default_value = default
        return s

    add_in("Time", DEF["Time"])
    add_in("Rate", DEF["Rate"])
    add_in("Amplitude", DEF["Amplitude"])
    add_in("Baseline", DEF["Baseline"])
    add_in("Sharpness", DEF["Sharpness"])
    itf.new_socket("Pulse", in_out="OUTPUT", socket_type="NodeSocketFloat")

    n, L = ng.nodes, ng.links
    gi = n.new("NodeGroupInput"); gi.location = (-900, 0)
    go = n.new("NodeGroupOutput"); go.location = (700, 0)

    def math_node(op, x=None, y=None, loc=(0, 0)):
        m = n.new("ShaderNodeMath"); m.operation = op; m.location = loc
        if x is not None: _set(m.inputs[0], x)
        if y is not None: _set(m.inputs[1], y)
        return m

    m_tr = math_node("MULTIPLY", loc=(-680, -40))            # Time * Rate
    m_ph = math_node("MULTIPLY", y=TAU, loc=(-500, -40))     # * TAU  -> phase
    m_sin = math_node("SINE", loc=(-320, -40))               # sin(phase)
    m_half = math_node("MULTIPLY", y=0.5, loc=(-150, -40))   # * 0.5
    m_bias = math_node("ADD", y=0.5, loc=(20, -40))          # + 0.5  -> 0..1
    m_pow = math_node("POWER", loc=(190, -40))               # ** Sharpness  (sharpen the peak)
    m_amp = math_node("MULTIPLY", loc=(360, -40))            # * Amplitude
    m_out = math_node("ADD", loc=(530, -40))                 # + Baseline -> Pulse

    L.new(gi.outputs["Time"], m_tr.inputs[0]); L.new(gi.outputs["Rate"], m_tr.inputs[1])
    L.new(m_tr.outputs[0], m_ph.inputs[0])
    L.new(m_ph.outputs[0], m_sin.inputs[0])
    L.new(m_sin.outputs[0], m_half.inputs[0])
    L.new(m_half.outputs[0], m_bias.inputs[0])
    L.new(m_bias.outputs[0], m_pow.inputs[0]); L.new(gi.outputs["Sharpness"], m_pow.inputs[1])
    L.new(m_pow.outputs[0], m_amp.inputs[0]); L.new(gi.outputs["Amplitude"], m_amp.inputs[1])
    L.new(m_amp.outputs[0], m_out.inputs[0]); L.new(gi.outputs["Baseline"], m_out.inputs[1])
    L.new(m_out.outputs[0], go.inputs["Pulse"])
    return ng


def add_time_driver(socket, fps):
    """Drive a Float socket from the timeline so the pulse plays live: Time = frame / fps."""
    fc = socket.driver_add("default_value")
    fc.driver.type = "SCRIPTED"
    fc.driver.expression = f"frame / {fps:.6f}"   # `frame` is provided by the driver namespace
    return fc


def apply_biopulse(obj, time=None, animate=False):
    """Insert NG_BioPulse into the object's MAT_LiquidStarlight and drive its Emission Strength."""
    mat = bpy.data.materials.get("MAT_LiquidStarlight") or starlight.build_material()
    if mat.name not in [m.name for m in obj.data.materials]:
        obj.data.materials.clear(); obj.data.materials.append(mat)
    nt = mat.node_tree
    grp = next((nd for nd in nt.nodes if nd.type == "GROUP" and nd.node_tree
                and nd.node_tree.name == "NG_LiquidStarlight"), None)
    if grp is None:                       # material was bare — rebuild it through starlight
        starlight.build_material()
        grp = next(nd for nd in nt.nodes if nd.type == "GROUP")

    pn = nt.nodes.new("ShaderNodeGroup"); pn.node_tree = build_group(); pn.location = (-260, -280)
    pn.label = "NG_BioPulse"
    nt.links.new(pn.outputs["Pulse"], grp.inputs["Emission Strength"])
    if time is not None:
        _set(pn.inputs["Time"], time)
    if animate:
        add_time_driver(pn.inputs["Time"], bpy.context.scene.render.fps)
    return mat, pn


def main():
    argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []

    def opt(flag, default=None):
        return argv[argv.index(flag)+1] if flag in argv else default

    stage = opt("--stage", "mature")
    png = opt("--render")
    time = float(opt("--time")) if "--time" in argv else None
    animate = "--animate" in argv

    # waveform proof (pure-Python mirror): one calm beat, sampled across 5 s
    print("[biopulse] waveform (Rate=%.2f Hz, Amp=%.1f, Base=%.1f, Sharp=%.1f):"
          % (DEF["Rate"], DEF["Amplitude"], DEF["Baseline"], DEF["Sharpness"]))
    for i in range(11):
        t = i * 0.5
        v = pulse(t)
        bar = "#" * int(round((v - DEF["Baseline"]) / DEF["Amplitude"] * 40))
        print(f"   t={t:4.1f}s  pulse={v:4.2f}  {bar}")

    tree.clear_scene()
    bootstrap.set_units(); bootstrap.ensure_collections()
    obj, p = tree.build_tree(stage)
    starlight.build_material()
    obj.data.materials.clear(); obj.data.materials.append(bpy.data.materials["MAT_LiquidStarlight"])
    mat, pn = apply_biopulse(obj, time=time, animate=animate)
    where = f"Time={time:.2f}s" if time is not None else ("driven (frame/fps)" if animate else "static")
    print(f"[biopulse] NG_BioPulse -> MAT_LiquidStarlight Emission Strength on {obj.name} ({where})")
    if png:
        tree.render(obj, p, png)
        print(f"[biopulse] rendered -> {png}")


if __name__ == "__main__":
    main()

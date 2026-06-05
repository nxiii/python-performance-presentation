import json
import math
import pathlib
import matplotlib.pyplot as plt


ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "inmemory_bench.json").read_text())
OUT = ROOT / "charts" / "inmemory.png"

TIER_COLOR = {
    "arrow":     "#1f77b4",
    "pandas":    "#5fa8d3",
    "py_dense":  "#e1b73b",
    "py_object": "#d62728",
    "py_set":    "#7f7f7f",
    "parquet":   "#2ca02c",
}
TIER_DARK_INSIDE = {"pandas", "py_dense"}

rows = sorted(DATA["results"], key=lambda r: r["time_ms"])
names  = [r["name"] for r in rows]
times  = [r["time_ms"] for r in rows]
mems   = [r["mem_mb"]  for r in rows]
tiers  = [r["tier"] for r in rows]
colors = [TIER_COLOR[t] for t in tiers]


fig, (ax_t, ax_m) = plt.subplots(1, 2, figsize=(13, 6), sharey=True)
fig.subplots_adjust(left=0.21, right=0.97, top=0.82, bottom=0.04, wspace=0.06)


def declutter(ax):
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="x", which="both",
                   bottom=False, top=False, labelbottom=False, labeltop=False)
    ax.tick_params(axis="y", left=False)
    ax.minorticks_off()


def log_pos(v, lo, hi):
    return (math.log(v) - math.log(lo)) / (math.log(hi) - math.log(lo))


def place_label(ax, x_data, y, text, tier, *, inside, mirrored):
    if inside:
        anchor = x_data * 0.95
        ha = ("left" if mirrored else "right")
        color = "#222" if tier in TIER_DARK_INSIDE else "white"
        weight = "bold"
    else:
        anchor = x_data * 1.12
        ha = ("right" if mirrored else "left")
        color = "#222"
        weight = "normal"
    ax.text(anchor, y, text, va="center", ha=ha,
            fontsize=9, color=color, fontweight=weight)

ax_t.barh(names, times, color=colors, edgecolor="none")
ax_t.set_xscale("log")
ax_t.invert_yaxis()
xlo_t, xhi_t = min(times) * 0.65, max(times) * 1.8
ax_t.set_xlim(xlo_t, xhi_t)
declutter(ax_t)
fastest_t = min(times)
for i, (v, tier) in enumerate(zip(times, tiers)):
    ratio = v / fastest_t
    txt = f"{v:.2f} ms" if ratio < 2 else f"{v:.1f} ms  ({ratio:.0f}×)"
    inside = log_pos(v, xlo_t, xhi_t) > 0.55
    place_label(ax_t, v, i, txt, tier, inside=inside, mirrored=False)

ax_m.barh(names, mems, color=colors, edgecolor="none")
ax_m.set_xscale("log")
ax_m.invert_xaxis()
xlo_m, xhi_m = min(mems) * 0.65, max(mems) * 1.8
ax_m.set_xlim(xhi_m, xlo_m)
declutter(ax_m)
ax_m.tick_params(axis="y", labelleft=False, labelright=False)
baseline_m = min(mems)
for i, (v, tier) in enumerate(zip(mems, tiers)):
    ratio = v / baseline_m
    txt = f"{v:.0f} MB" if ratio < 1.3 else f"{v:.0f} MB  ({ratio:.0f}×)"
    inside = log_pos(v, xlo_m, xhi_m) > 0.55
    place_label(ax_m, v, i, txt, tier, inside=inside, mirrored=True)

fig.suptitle("When data is in memory, the container is the cost",
             fontsize=14, fontweight="bold", y=0.95)
fig.text(0.5, 0.88,
         "min + max + sum + count over 2 M int64 values  ·  "
         "wall time (left)   ·   memory (right)",
         ha="center", fontsize=10, color="#555")

fig.savefig(OUT, dpi=130)
print(f"wrote {OUT}")

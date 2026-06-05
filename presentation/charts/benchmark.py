import json
import pathlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "benchmarks.json").read_text())
OUT = ROOT / "charts" / "benchmark.png"

COLORS = {
    "pyarrow":    "#1f77b4",
    "java_arrow": "#9467bd",
    "spark":      "#d62728",
}
LABELS = {
    "pyarrow":    "Python + pyarrow.compute",
    "java_arrow": "Java + arrow-dataset (JNI)",
    "spark":      "Java + Spark 3.5",
}

OPS = [
    ("Stats (min/max/sum/count)",      "stats",       ["pyarrow", "java_arrow", "spark"]),
    ("Add column (amount * quantity)", "add_column",  ["pyarrow", "spark"]),
    ("Drop column (customer_id)",      "drop_column", ["pyarrow", "spark"]),
]

LAYOUTS = ["one_file", "many_files"]
COL_TINT = {"one_file": "#eef3fa", "many_files": "#fbeeec"}
COL_TEXT = {"one_file": "#1f4d7a", "many_files": "#9a342a"}


def col_header(layout_key):
    ds = DATA["datasets"][layout_key]
    files = ds["files"]
    size = ds["size_mb"]
    if files == 1:
        return f"1 file  ·  ~{size} MB"
    return f"{files} files  ·  ~{size} MB total"


fig, axes = plt.subplots(
    3, 2, figsize=(13, 7.5), sharey="row",
)
fig.subplots_adjust(
    left=0.16, right=0.97, top=0.86, bottom=0.07,
    hspace=0.55, wspace=0.32,
)

for col, layout in enumerate(LAYOUTS):
    for row, (op_title, op_key, runtimes) in enumerate(OPS):
        ax = axes[row, col]
        ax.set_facecolor(COL_TINT[layout])

        op = DATA[layout][op_key]
        names, values, colors = [], [], []
        for r in runtimes:
            v = op.get(r)
            if v is None:
                continue
            names.append(LABELS[r])
            values.append(v)
            colors.append(COLORS[r])

        ax.set_title(op_title, loc="left", fontsize=11, fontweight="bold")

        if not values:
            ax.text(0.5, 0.5, "(no measurement)",
                    transform=ax.transAxes, ha="center", va="center",
                    fontsize=11, color="#888")
            ax.set_xticks([])
            ax.set_yticks([])
            continue

        bars = ax.barh(names, values, color=colors, edgecolor="black",
                       linewidth=0.6)
        ax.invert_yaxis()
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(
            lambda v, _: f"{int(v)}"
        ))

        fastest = min(values)
        for bar, v in zip(bars, values):
            ratio = v / fastest
            label = f"{v:.0f} ms" if ratio < 1.1 else f"{v:.0f} ms  ({ratio:.1f}×)"
            ax.text(
                v + max(values) * 0.01,
                bar.get_y() + bar.get_height() / 2,
                label,
                va="center", fontsize=9,
            )
        ax.set_xlim(0, max(values) * 1.30)

    axes[-1, col].set_xlabel("milliseconds (warm run)")

left_x  = (axes[0, 0].get_position().x0 + axes[0, 0].get_position().x1) / 2
right_x = (axes[0, 1].get_position().x0 + axes[0, 1].get_position().x1) / 2
fig.text(left_x,  0.91, col_header("one_file"),
         ha="center", va="bottom", fontsize=15, fontweight="bold",
         color=COL_TEXT["one_file"])
fig.text(right_x, 0.91, col_header("many_files"),
         ha="center", va="bottom", fontsize=15, fontweight="bold",
         color=COL_TEXT["many_files"])

divider_x = (axes[0, 0].get_position().x1 + axes[0, 1].get_position().x0) / 2
fig.add_artist(plt.Line2D(
    [divider_x, divider_x], [0.04, 0.93],
    transform=fig.transFigure, color="#cccccc", linewidth=1.0,
))

fig.suptitle(
    "pyarrow.compute vs Spark — same 2 M rows, two on-disk layouts",
    fontsize=13, fontweight="bold", y=0.975,
)

fig.savefig(OUT, dpi=130)
print(f"wrote {OUT}")

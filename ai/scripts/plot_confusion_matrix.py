import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

CM_PATH = Path("ai/models/audio/eval_test/confusion_matrix.npy")
LABELS_PATH = Path("ai/models/audio/labels.json")
METRICS_PATH = Path("ai/models/audio/eval_test/metrics_overall.json")# optional
OUT_DIR = CM_PATH.parent# save PNGs next to the .npy

OUT_COUNTS_PNG = OUT_DIR / "confusion_matrix_counts.png"
OUT_ROWPNG     = OUT_DIR / "confusion_matrix_rownorm.png"

# Load data 
cm = np.load(CM_PATH)
labels = json.load(open(LABELS_PATH))
assert cm.shape[0] == cm.shape[1] == len(labels), "CM/labels size mismatch"

title_extra = ""
if METRICS_PATH.exists():
    m = json.load(open(METRICS_PATH))
    bits = []
    if "accuracy" in m and m["accuracy"] is not None:
        bits.append(f"acc={m['accuracy']:.3f}")
    if "macro/f1" in m and m["macro/f1"] is not None:
        bits.append(f"macro-F1={m['macro/f1']:.3f}")
    if bits:
        title_extra = " (" + ", ".join(bits) + ")"

def render_and_save(cm_plot, labels, normalize_tag, out_png, show_counts_under=False):
    n = len(labels)
    side = max(6, min(14, 0.65 * n + 3))  # scale figure size with #classes
    fig, ax = plt.subplots(figsize=(side, side))
    im = ax.imshow(cm_plot, interpolation="nearest")
    ax.set_xticks(range(n)); ax.set_yticks(range(n))
    ax.set_xticklabels(labels, rotation=45, ha="right"); ax.set_yticklabels(labels)
    ax.set_xlabel("Predicted"); ax.set_ylabel("True")
    ax.set_title(f"Confusion Matrix – {normalize_tag}{title_extra}")

    vmax = cm_plot.max() if cm_plot.size else 0.0
    thresh = vmax / 2.0
    for i in range(n):
        for j in range(n):
            if show_counts_under:
                txt = f"{cm_plot[i,j]:.2f}\n({int(cm[i,j])})"
            else:
                txt = f"{int(cm_plot[i,j])}"
            ax.text(j, i, txt,
                    ha="center", va="center",
                    color="white" if cm_plot[i,j] > thresh else "black",
                    fontsize=8)

    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    plt.tight_layout()
    plt.savefig(out_png, dpi=220)
    plt.close(fig)
    print("Saved:", out_png)

# Raw counts
render_and_save(cm.astype(float), labels, "Counts", OUT_COUNTS_PNG, show_counts_under=False)

# Row-normalized (per true class)
row_sums = cm.sum(axis=1, keepdims=True).clip(min=1e-12)
cm_row = (cm / row_sums).astype(float)
render_and_save(cm_row, labels, "Row-normalized", OUT_ROWPNG, show_counts_under=True)

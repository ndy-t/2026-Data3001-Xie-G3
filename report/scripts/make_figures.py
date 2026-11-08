"""
Generate the supplementary report figures from SAVED project outputs only.

No model is trained or re-evaluated here. Inputs (read-only):
  models/final_test_comparison.csv              (notebook 08, cell 39)
  data/processed/report_test_predictions.parquet (notebook 08, cells 39/49)
  data/processed/modelling_dataset_final.parquet (notebook 08, cells 8/25)
  data/processed/gulf_stream_trajectories.parquet (drogue-status check only)

Outputs: report/figures/generated/*.pdf|png and a check log printed to stdout.

Run from the repository root:
    python report/scripts/make_figures.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "report" / "figures" / "generated"
OUT.mkdir(parents=True, exist_ok=True)

# Validated colours (dataviz reference palette); baselines neutral grey.
C_BASE = "#9A9A9A"
C_CURRENT = "#2A78D6"
C_HISTORY = "#199E70"
INK = "#222222"

plt.rcParams.update({
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#555555",
    "axes.labelcolor": INK,
    "text.color": INK,
    "savefig.dpi": 300,
})

MODEL_ORDER = [
    "Constant Velocity", "Mean-flow Advection",
    "Ridge Current", "Ridge History",
    "Elastic Net Current", "Elastic Net History",
    "RF Current", "RF History",
    "ET Current", "ET History",
    "GB Current", "GB History",
]


def colour_for(name):
    if name in ("Constant Velocity", "Mean-flow Advection"):
        return C_BASE
    return C_CURRENT if name.endswith("Current") else C_HISTORY


def save(fig, stem):
    fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(OUT / f"{stem}.png", bbox_inches="tight")
    plt.close(fig)
    print(f"saved {stem}.pdf/.png")


# ---------------------------------------------------------------------------
# Figure: held-out TEST model comparison
# ---------------------------------------------------------------------------
def test_comparison():
    res = pd.read_csv(ROOT / "models" / "final_test_comparison.csv")
    assert list(res["Model"]) == MODEL_ORDER, "unexpected model order/names"
    assert len(res) == 12
    res = res.set_index("Model").loc[MODEL_ORDER]

    print("\n[test] metrics (km), rounded to 3 dp:")
    print(res.round(3).to_string())
    cv = res.loc["Constant Velocity"]
    print("\n[test] % reduction vs Constant Velocity:")
    print((100 * (cv - res) / cv).round(1).to_string())

    fams = [("Ridge", "Ridge"), ("Elastic Net", "Elastic Net"),
            ("Random Forest", "RF"), ("Extra Trees", "ET"),
            ("Gradient Boosting", "GB")]
    gain = []
    for label, p in fams:
        c, h = res.loc[f"{p} Current"], res.loc[f"{p} History"]
        gain.append({
            "Family": label,
            "Median": 100 * (c["Median"] - h["Median"]) / c["Median"],
            "P90": 100 * (c["P90"] - h["P90"]) / c["P90"],
            "Mean": 100 * (c["Mean"] - h["Mean"]) / c["Mean"],
            "RMSE": 100 * (c["RMSE"] - h["RMSE"]) / c["RMSE"],
        })
    gain = pd.DataFrame(gain).set_index("Family")
    print("\n[test] % reduction History vs Current within family:")
    print(gain.round(1).to_string())

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(7.2, 3.9),
        gridspec_kw={"width_ratios": [1.55, 1]})

    y = np.arange(len(MODEL_ORDER))
    for i, name in enumerate(MODEL_ORDER):
        med, p90 = res.loc[name, "Median"], res.loc[name, "P90"]
        col = colour_for(name)
        ax1.plot([med, p90], [i, i], color=col, lw=2, alpha=0.45,
                 solid_capstyle="round", zorder=2)
        ax1.scatter(med, i, s=34, color=col, zorder=3, edgecolor="white",
                    linewidth=0.8, marker="o")
        ax1.scatter(p90, i, s=38, color=col, zorder=3, edgecolor="white",
                    linewidth=0.8, marker="D")
        ax1.text(p90 + 1.2, i, f"{med:.2f} | {p90:.2f}", va="center",
                 fontsize=7, color="#52514e")
    ax1.set_yticks(y)
    ax1.set_yticklabels(MODEL_ORDER)
    ax1.invert_yaxis()
    ax1.set_xlim(0, 92)
    ax1.set_xlabel("24-h great-circle position error (km)")
    ax1.axvline(res.loc["Constant Velocity", "Median"], color=C_BASE,
                lw=0.8, ls=":", zorder=1)
    ax1.grid(axis="x", color="#e6e6e6", lw=0.6)
    ax1.set_axisbelow(True)
    from matplotlib.lines import Line2D
    handles = [
        Line2D([], [], marker="o", ls="", color=INK, label="Median"),
        Line2D([], [], marker="D", ls="", color=INK, label="90th percentile"),
        Line2D([], [], lw=6, color=C_BASE, label="Physical baseline"),
        Line2D([], [], lw=6, color=C_CURRENT, label="Current-only"),
        Line2D([], [], lw=6, color=C_HISTORY, label="History-enhanced"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=5, frameon=False,
               fontsize=7, bbox_to_anchor=(0.5, -0.04))
    ax1.set_title("(a) Held-out test error (median | P90, km)", loc="left")

    yy = np.arange(len(gain))
    h = 0.36
    b1 = ax2.barh(yy - h / 2, gain["Median"], height=h, color=C_HISTORY,
                  label="Median", edgecolor="white", linewidth=1)
    b2 = ax2.barh(yy + h / 2, gain["P90"], height=h, color="#7FCDB0",
                  label="90th percentile", edgecolor="white", linewidth=1)
    for bars in (b1, b2):
        for bar in bars:
            ax2.text(bar.get_width() + 0.6,
                     bar.get_y() + bar.get_height() / 2,
                     f"{bar.get_width():.1f}%", va="center", fontsize=7,
                     color="#52514e")
    ax2.set_yticks(yy)
    ax2.set_yticklabels(gain.index)
    ax2.invert_yaxis()
    ax2.set_xlim(0, 40)
    ax2.set_ylim(len(gain) - 0.4, -1.1)
    ax2.set_xlabel("Error reduction, History vs Current (%)")
    ax2.grid(axis="x", color="#e6e6e6", lw=0.6)
    ax2.set_axisbelow(True)
    ax2.legend(frameon=False, loc="upper center", fontsize=7, ncol=2,
               bbox_to_anchor=(0.5, 1.0))
    ax2.set_title("(b) Gain from 24-h history (test)", loc="left")

    fig.tight_layout(w_pad=1.5, rect=(0, 0.05, 1, 1))
    save(fig, "fig_test_model_comparison")
    return res, gain


# ---------------------------------------------------------------------------
# Figure: spatial performance with documented colour clipping
# ---------------------------------------------------------------------------
def spatial():
    sp = pd.read_parquet(
        ROOT / "data" / "processed" / "report_test_predictions.parquet",
        columns=["trajectory_id", "lon_t", "lat_t",
                 "Constant Velocity_error", "GB History_error"])
    GRID = 1.0
    sp["lon_grid"] = np.floor(sp["lon_t"] / GRID) * GRID
    sp["lat_grid"] = np.floor(sp["lat_t"] / GRID) * GRID
    sp["gb_error"] = sp["GB History_error"]
    sp["improvement"] = sp["Constant Velocity_error"] - sp["GB History_error"]

    g = (sp.groupby(["lat_grid", "lon_grid"])
         .agg(mean_gb_error=("gb_error", "mean"),
              mean_improvement=("improvement", "mean"),
              n_forecasts=("gb_error", "size"),
              n_drifters=("trajectory_id", "nunique"))
         .reset_index())
    valid = g[(g.n_forecasts >= 100) & (g.n_drifters >= 3)].copy()

    n_cells, n_fc = len(valid), int(valid.n_forecasts.sum())
    print(f"\n[spatial] total cells {len(g)}, eligible {n_cells}, "
          f"forecasts {n_fc} ({100 * n_fc / len(sp):.1f}%)")
    assert len(g) == 198 and n_cells == 145 and n_fc == 73214, \
        "spatial replication does not match notebook cell 60"
    top = valid.sort_values("mean_gb_error", ascending=False).head(10)
    print(top.round(3).to_string(index=False))
    assert abs(top.iloc[0].mean_gb_error - 32.162) < 5e-3

    imp = valid.mean_improvement
    print(f"[spatial] improvement: min {imp.min():.3f}, max {imp.max():.3f}, "
          f"median {imp.median():.3f}; cells with negative mean improvement: "
          f"{int((imp < 0).sum())}")
    assert imp.min() > 0, "sequential scale assumes all cells positive"
    clip = float(np.ceil(np.percentile(imp, 98)))
    n_clip = int((imp > clip).sum())
    clipped = valid.loc[imp > clip,
                        ["lat_grid", "lon_grid", "mean_improvement",
                         "n_forecasts", "n_drifters"]]
    print(f"[spatial] colour cap {clip:.0f} km (98th pct of gain, "
          f"rounded up); clipped cells: {n_clip}")
    print(clipped.round(3).to_string(index=False))
    dr = valid.n_drifters
    print(f"[spatial] distinct drifters per eligible cell: min {dr.min()}, "
          f"median {dr.median():.0f}, max {dr.max()}")

    lon_edges = np.arange(-80, -59, GRID)
    lat_edges = np.arange(30, 46, GRID)

    def to_grid(col):
        return (valid.pivot(index="lat_grid", columns="lon_grid", values=col)
                .reindex(index=lat_edges[:-1], columns=lon_edges[:-1])
                .to_numpy())

    fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.75), sharey=True)
    nodata = "#E9E9E9"
    m1 = axes[0].pcolormesh(lon_edges, lat_edges, to_grid("mean_gb_error"),
                            cmap="YlOrRd", shading="flat",
                            edgecolors="white", linewidth=0.3)
    cb = fig.colorbar(m1, ax=axes[0], orientation="horizontal", pad=0.2,
                      fraction=0.06)
    cb.set_label("Mean GB History error (km)")
    axes[0].set_title("(a) GB History error", loc="left")

    m2 = axes[1].pcolormesh(
        lon_edges, lat_edges, to_grid("mean_improvement"), cmap="Blues",
        vmin=0, vmax=clip, shading="flat", edgecolors="white",
        linewidth=0.3)
    cb = fig.colorbar(m2, ax=axes[1], orientation="horizontal", pad=0.2,
                      fraction=0.06, extend="max")
    cb.set_label(f"Mean reduction vs CV (km), capped at {clip:.0f}")
    axes[1].set_title("(b) Improvement over CV", loc="left")

    m3 = axes[2].pcolormesh(lon_edges, lat_edges, to_grid("n_drifters"),
                            cmap="Purples", shading="flat",
                            edgecolors="white", linewidth=0.3,
                            vmin=0, vmax=dr.max())
    cb = fig.colorbar(m3, ax=axes[2], orientation="horizontal", pad=0.2,
                      fraction=0.06)
    cb.set_label("Distinct test drifters per cell")
    axes[2].set_title("(c) Drifter support", loc="left")

    for ax in axes:
        ax.set_facecolor(nodata)
        ax.set_xlim(-80, -60)
        ax.set_ylim(30, 45)
        ax.set_aspect(1 / np.cos(np.radians(37.5)))
        ax.set_xticks([-80, -75, -70, -65, -60])
        ax.set_xticklabels(["80°W", "75°W", "70°W", "65°W", "60°W"])
        ax.tick_params(length=2)
    axes[0].set_yticks([30, 35, 40, 45])
    axes[0].set_yticklabels(["30°N", "35°N", "40°N", "45°N"])
    fig.tight_layout(w_pad=0.6)
    save(fig, "fig_spatial_performance_rescaled")
    return clip, n_clip, clipped, valid


# ---------------------------------------------------------------------------
# Figure: study region and sample coverage
# ---------------------------------------------------------------------------
def study_region():
    m = pd.read_parquet(
        ROOT / "data" / "processed" / "modelling_dataset_final.parquet",
        columns=["trajectory_id", "time", "lon_t", "lat_t", "split"])
    print(f"\n[cohort] samples {len(m)}, drifters {m.trajectory_id.nunique()}")
    summ = m.groupby("split").agg(samples=("time", "size"),
                                  drifters=("trajectory_id", "nunique"))
    print(summ.to_string())
    assert len(m) == 626679 and m.trajectory_id.nunique() == 517

    m["year"] = pd.to_datetime(m["time"]).dt.year
    by_year = (m.groupby(["year", "split"]).size().unstack(fill_value=0)
               [["train", "validation", "test"]])
    drifters_year = m.groupby("year").trajectory_id.nunique()
    print("[cohort] distinct drifters per year (all splits):")
    print(drifters_year.to_string())

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.9),
                                   gridspec_kw={"width_ratios": [1.05, 1]})
    hb = ax1.hexbin(m.lon_t, m.lat_t, gridsize=(40, 22),
                    extent=(-80, -60, 30, 45), cmap="Blues",
                    norm=LogNorm(), mincnt=1, linewidths=0.1)
    cb = fig.colorbar(hb, ax=ax1, fraction=0.04, pad=0.02)
    cb.set_label("Forecast origins per bin")
    ax1.plot([-80, -60, -60, -80, -80], [30, 30, 45, 45, 30], color=INK,
             lw=1)
    ax1.set_xlim(-81, -59)
    ax1.set_ylim(29.5, 45.5)
    ax1.set_aspect(1 / np.cos(np.radians(37.5)))
    ax1.set_facecolor("#F4F4F2")
    ax1.set_xticks([-80, -75, -70, -65, -60])
    ax1.set_xticklabels(["80°W", "75°W", "70°W", "65°W", "60°W"])
    ax1.set_yticks([30, 35, 40, 45])
    ax1.set_yticklabels(["30°N", "35°N", "40°N", "45°N"])
    ax1.set_title("(a) Forecast-origin density (log scale)", loc="left")

    cols = {"train": "#9FC3EE", "validation": C_CURRENT, "test": C_HISTORY}
    bottom = np.zeros(len(by_year))
    for s in ["train", "validation", "test"]:
        ax2.bar(by_year.index, by_year[s] / 1000, bottom=bottom,
                color=cols[s], label=s.capitalize(), width=0.8,
                edgecolor="white", linewidth=0.6)
        bottom += by_year[s].to_numpy() / 1000
    ax2.set_ylabel("Forecast origins (thousands)")
    ax2.set_xticks(by_year.index[::3])
    ax2.grid(axis="y", color="#e6e6e6", lw=0.6)
    ax2.set_axisbelow(True)
    ax2.set_ylim(0, 62)
    ax2.legend(frameon=False, fontsize=7, loc="upper center", ncol=3,
               bbox_to_anchor=(0.5, 1.02))
    ax2.set_title("(b) Origins per year by partition", loc="left")
    fig.tight_layout(w_pad=1.2)
    save(fig, "fig_study_region_coverage")
    return summ, by_year, drifters_year


# ---------------------------------------------------------------------------
# Descriptive check: drogue status at forecast origins (not used in models)
# ---------------------------------------------------------------------------
def drogue_check():
    src = pd.read_parquet(
        ROOT / "data" / "processed" / "gulf_stream_trajectories.parquet",
        columns=["trajectory_id", "time", "drogue_status"])
    src = src.drop_duplicates(["trajectory_id", "time"])
    m = pd.read_parquet(
        ROOT / "data" / "processed" / "modelling_dataset_final.parquet",
        columns=["trajectory_id", "time", "split"])
    j = m.merge(src, on=["trajectory_id", "time"], how="left",
                validate="many_to_one")
    print("\n[drogue] status at forecast origins by split (share):")
    tab = (j.groupby("split")["drogue_status"]
           .value_counts(normalize=True, dropna=False).unstack())
    print(tab.round(4).to_string())
    print("[drogue] counts:")
    print(j.groupby("split")["drogue_status"].value_counts(dropna=False)
          .unstack().to_string())
    und = j.loc[j.drogue_status == False]  # noqa: E712
    print("[drogue] drifters with >=1 undrogued origin, by split:")
    print(und.groupby("split").trajectory_id.nunique().to_string())



# ===========================================================================
# Readability re-plots of existing notebook figures (revision 2).
# Each function recomputes the plotted summary from saved outputs and asserts
# agreement with the values printed in notebook 08 before plotting.
# ===========================================================================
PRED = ROOT / "data" / "processed" / "report_test_predictions.parquet"
REGIMES = ["Low", "Medium", "High"]

# Model colours as used in notebook 08 (cells 46/51), kept for continuity.
MODEL_COLOURS = {
    "Constant Velocity": "#D97706",
    "Mean-flow Advection": "#8C5A1E",
    "Ridge History": "#9333EA",
    "Elastic Net History": "#C026D3",
    "RF History": "#DC2626",
    "ET History": "#0891B2",
    "GB Current": "#2563EB",
    "GB History": "#059669",
}
PROFILE_COLOURS = {
    "Constant Velocity": "#7F7F7F", "Mean-flow Advection": "#D97706",
    "Ridge History": "#9333EA", "GB Current": "#2563EB",
    "RF History": "#DC2626", "GB History": "#059669",
}
PROFILE_MARKERS = {
    "Constant Velocity": "o", "Mean-flow Advection": "s",
    "Ridge History": "^", "GB Current": "v",
    "RF History": "D", "GB History": "P",
}


def _close(a, b, tol=0.006):
    return np.allclose(np.asarray(a, float), np.asarray(b, float), atol=tol)


# --------------------------- trajectories ---------------------------------
def _select_tracks():
    """Replicates notebook cells 44/46: three test drifters with most
    forecasts; longest continuous hourly segment (by target time); 7 days."""
    cols = ["trajectory_id", "time", "lon_target", "lat_target"]
    models = list(MODEL_COLOURS)
    for m in models:
        cols += [f"{m}_lon", f"{m}_lat", f"{m}_error"]
    pr = pd.read_parquet(PRED, columns=cols)
    pr["time"] = pd.to_datetime(pr["time"], utc=True)
    pr["target_time"] = pr["time"] + pd.Timedelta(hours=24)
    counts = pr.groupby("trajectory_id").size().sort_values(ascending=False)
    print("\n[traj] top drifter forecast counts:", counts.head(5).to_dict())
    assert counts.iloc[2] != counts.iloc[3], "tie in drifter selection"
    ids = counts.head(3).index.tolist()
    tracks = {}
    for i in ids:
        tr = pr[pr.trajectory_id == i].sort_values("target_time").copy()
        tr["seg"] = (tr["target_time"].diff().dt.total_seconds()
                     .fillna(3600).gt(3600).cumsum())
        longest = tr.groupby("seg").size().idxmax()
        tracks[i] = tr[tr.seg == longest].head(7 * 24).copy()
    # common extents per drifter over every model shown in any panel
    ext = {}
    for i, seg in tracks.items():
        lo = np.concatenate([seg.lon_target] + [seg[f"{m}_lon"] for m in models])
        la = np.concatenate([seg.lat_target] + [seg[f"{m}_lat"] for m in models])
        ml, mb = max(np.ptp(lo) * .08, .05), max(np.ptp(la) * .08, .05)
        ext[i] = ((lo.min() - ml, lo.max() + ml), (la.min() - mb, la.max() + mb))
    med = pd.DataFrame({m: [tracks[i][f"{m}_error"].median() for i in ids]
                        for m in models}, index=ids)
    print("[traj] window median errors (km):")
    print(med.round(1).to_string())
    # notebook figure (cell 44) panel labels
    assert _close(med.loc[ids, "Constant Velocity"], [11.2, 12.9, 12.2], .051)
    assert _close(med.loc[ids, "GB Current"], [8.6, 12.5, 12.6], .051)
    assert _close(med.loc[ids, "GB History"], [3.9, 7.0, 8.2], .051)
    return ids, tracks, ext


def _traj_grid(ids, tracks, ext, models, stem, short):
    fig, axes = plt.subplots(3, len(models), figsize=(7.0, 7.9))
    for r, i in enumerate(ids):
        seg = tracks[i]
        (x0, x1), (y0, y1) = ext[i]
        for c, m in enumerate(models):
            ax = axes[r, c]
            ax.plot(seg.lon_target, seg.lat_target, color=INK, lw=2.0,
                    zorder=3, solid_capstyle="round")
            ax.plot(seg[f"{m}_lon"], seg[f"{m}_lat"], color=MODEL_COLOURS[m],
                    lw=1.1, ls=(0, (3, 1.6)), zorder=4)
            ax.scatter(seg.lon_target.iloc[0], seg.lat_target.iloc[0],
                       s=22, color=INK, zorder=5)
            ax.scatter(seg.lon_target.iloc[-1], seg.lat_target.iloc[-1],
                       s=55, marker="*", color=INK, zorder=5)
            ax.set_xlim(x0, x1)
            ax.set_ylim(y0, y1)
            ax.set_aspect(1 / np.cos(np.radians(seg.lat_target.mean())),
                          adjustable="box")
            ax.text(0.03, 0.97, f"median {seg[f'{m}_error'].median():.1f} km",
                    transform=ax.transAxes, va="top", fontsize=7.5,
                    bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.2))
            ax.tick_params(labelsize=6.5, length=2)
            ax.locator_params(nbins=3)
            ax.grid(color="#eeeeee", lw=0.5)
            for sp in ("top", "right"):
                ax.spines[sp].set_visible(True)
            if r == 0:
                ax.set_title(short.get(m, m), fontsize=9,
                             color=MODEL_COLOURS[m], fontweight="bold")
            if c == 0:
                ax.set_ylabel(f"Drifter {chr(65 + r)}\nlatitude (°)",
                              fontsize=7.5)
            if r == 2:
                ax.set_xlabel("longitude (°)", fontsize=7.5)
    from matplotlib.lines import Line2D
    fig.legend(handles=[
        Line2D([], [], color=INK, lw=2, label="Observed position at target time"),
        Line2D([], [], color="#666666", lw=1.1, ls=(0, (3, 1.6)),
               label="Rolling 24-h forecast endpoint (model colour)"),
        Line2D([], [], color=INK, marker="o", ls="", ms=4, label="Start"),
        Line2D([], [], color=INK, marker="*", ls="", ms=7, label="End")],
        loc="lower center", ncol=4, frameon=False, fontsize=7.5,
        bbox_to_anchor=(0.5, -0.005))
    fig.tight_layout(rect=(0, 0.035, 1, 1), h_pad=0.6, w_pad=0.4)
    save(fig, stem)


def trajectories():
    ids, tracks, ext = _select_tracks()
    print("[traj] drifter A/B/C =", ids)
    short = {"Constant Velocity": "Constant Velocity",
             "Mean-flow Advection": "Mean-flow Advection"}
    _traj_grid(ids, tracks, ext,
               ["Constant Velocity", "GB Current", "GB History"],
               "fig_traj_cv_gb", short)
    _traj_grid(ids, tracks, ext,
               ["Mean-flow Advection", "Ridge History", "Elastic Net History"],
               "fig_traj_mf_linear", short)
    _traj_grid(ids, tracks, ext,
               ["RF History", "ET History", "GB History"],
               "fig_traj_trees", short)
    return ids


# --------------------------- heatmaps -------------------------------------
def _heat(ax, mat, cmap, fmt, title, cbar_label, xlabel, ylabel, fig,
          vmin=None, vmax=None):
    im = ax.imshow(mat, cmap=cmap, vmin=vmin, vmax=vmax, aspect="equal")
    lo, hi = im.norm.vmin, im.norm.vmax
    for (r, c), v in np.ndenumerate(mat):
        frac = (v - lo) / (hi - lo) if hi > lo else 0
        ax.text(c, r, fmt.format(v), ha="center", va="center", fontsize=9,
                color="white" if frac > 0.6 else INK, fontweight="bold")
    ax.set_xticks(range(3))
    ax.set_xticklabels(REGIMES, fontsize=8)
    ax.set_yticks(range(3))
    ax.set_yticklabels(REGIMES, fontsize=8)
    ax.set_xlabel(xlabel, fontsize=8.5)
    ax.set_ylabel(ylabel, fontsize=8.5)
    ax.set_title(title, fontsize=9, loc="left")
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0)
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label(cbar_label, fontsize=7.5)
    cb.ax.tick_params(labelsize=7)


def joint_speed_turning():
    pr = pd.read_parquet(PRED, columns=["trajectory_id", "Speed_group",
                                        "Turning_group", "GB Current_error",
                                        "GB History_error"])
    j = pr[pr.Turning_group.astype(str) != "Undefined"].copy()
    j["S"] = j.Speed_group.astype(str)
    j["TR"] = j.Turning_group.astype(str)
    j["gain"] = j["GB Current_error"] - j["GB History_error"]
    cnt = pd.crosstab(j.S, j.TR).reindex(index=REGIMES, columns=REGIMES)
    pct = cnt.div(cnt.sum(axis=1), axis=0) * 100
    med = j.groupby(["S", "TR"])["GB History_error"].median().unstack() \
        .reindex(index=REGIMES, columns=REGIMES)
    gain = j.groupby(["S", "TR"])["gain"].mean().unstack() \
        .reindex(index=REGIMES, columns=REGIMES)
    print("\n[joint] counts\n", cnt.to_string())
    print("[joint] GBH median\n", med.round(2).to_string())
    print("[joint] mean gain\n", gain.round(2).to_string())
    assert (cnt.to_numpy() == np.array([[946, 8263, 15288], [5225, 10394, 8427],
                                        [24399, 5775, 3816]])).all()
    assert _close(med, [[7.36, 5.57, 5.44], [8.48, 8.68, 7.26],
                        [16.06, 15.94, 10.47]])
    assert _close(gain, [[2.00, 2.36, 2.76], [3.26, 3.23, 4.65],
                         [4.11, 3.63, 7.03]])
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.75))
    _heat(axes[0], pct.to_numpy(), "Blues", "{:.1f}",
          "(a) Turning mix within speed (%)", "Row share (%)",
          "Turning regime", "Speed regime", fig, 0, 75)
    _heat(axes[1], med.to_numpy(), "YlOrRd", "{:.1f}",
          "(b) GB History median error", "Median error (km)",
          "Turning regime", "", fig)
    _heat(axes[2], gain.to_numpy(), "Greens", "{:.2f}",
          "(c) Mean benefit of history", "Mean reduction (km)",
          "Turning regime", "", fig, 0, None)
    fig.tight_layout(w_pad=0.8)
    save(fig, "fig_joint_speed_turning")


def _sst_test():
    src = pd.read_parquet(
        ROOT / "data" / "processed" / "gulf_stream_trajectories.parquet",
        columns=["trajectory_id", "time", "sst"]).drop_duplicates(
        ["trajectory_id", "time"])
    m = pd.read_parquet(
        ROOT / "data" / "processed" / "modelling_dataset_final.parquet",
        columns=["sample_id", "trajectory_id", "time", "split"])
    m = m.merge(src, on=["trajectory_id", "time"], how="left",
                validate="many_to_one")
    m["sst_c"] = m["sst"] - 273.15
    lo, hi = m.loc[(m.split == "train") & m.sst_c.notna(), "sst_c"] \
        .quantile([1 / 3, 2 / 3])
    print(f"\n[sst] thresholds {lo:.2f}, {hi:.2f}")
    assert round(lo, 2) == 26.93 and round(hi, 2) == 28.06
    pr = pd.read_parquet(PRED, columns=["sample_id", "trajectory_id",
                                        "Speed_group", "Constant Velocity_error",
                                        "GB Current_error", "GB History_error"])
    t = pr.merge(m[["sample_id", "sst_c"]], on="sample_id", how="left",
                 validate="one_to_one")
    t["SST"] = pd.cut(t.sst_c, [-np.inf, lo, hi, np.inf], labels=REGIMES)
    t["gain"] = t["GB Current_error"] - t["GB History_error"]
    return t


def sst_figures():
    t = _sst_test()
    s = t.dropna(subset=["SST"]).copy()
    s["SST"] = s["SST"].astype(str)
    print("[sst] regime counts", s.SST.value_counts().reindex(REGIMES).to_dict())
    assert s.SST.value_counts().reindex(REGIMES).tolist() == [28147, 21205, 28493]
    models = ["Constant Velocity", "GB Current", "GB History"]
    col = {"Constant Velocity": "#7F7F7F", "GB Current": C_CURRENT,
           "GB History": C_HISTORY}
    mk = {"Constant Velocity": "o", "GB Current": "v", "GB History": "P"}
    stats = {m: s.groupby("SST")[f"{m}_error"].agg(
        ["median", lambda x: x.quantile(.9)]).reindex(REGIMES) for m in models}
    gain = s.groupby("SST")["gain"].mean().reindex(REGIMES)
    print("[sst] medians", {m: stats[m]["median"].round(3).tolist() for m in models})
    assert _close(stats["GB History"]["median"], [9.981, 9.278, 8.279], .001)
    assert _close(stats["Constant Velocity"].iloc[:, 1], [47.712, 38.313, 36.837], .001)
    assert _close(gain, [4.093, 3.492, 3.387], .001)

    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.5))
    for m in models:
        axes[0].plot(REGIMES, stats[m]["median"], marker=mk[m], color=col[m],
                     lw=1.8, ms=5, label=m)
        axes[1].plot(REGIMES, stats[m].iloc[:, 1], marker=mk[m], color=col[m],
                     lw=1.8, ms=5, label=m)
    axes[0].set_title("(a) Median error", loc="left")
    axes[1].set_title("(b) 90th-percentile error", loc="left")
    axes[0].set_ylabel("Position error (km)")
    b = axes[2].bar(REGIMES, gain, color=C_HISTORY, width=0.6,
                    edgecolor="white")
    for bar in b:
        axes[2].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + .05,
                     f"{bar.get_height():.2f}", ha="center", fontsize=7.5)
    axes[2].set_ylim(0, 5)
    axes[2].set_title("(c) Mean benefit of history", loc="left")
    axes[2].set_ylabel("Mean reduction (km)")
    for ax in axes:
        ax.set_xlabel("SST regime")
        ax.grid(axis="y", color="#e6e6e6", lw=0.6)
        ax.set_axisbelow(True)
    fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center",
               ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.08, 1, 1), w_pad=1.0)
    save(fig, "fig_sst_regimes")

    ss = s.dropna(subset=["Speed_group"]).copy()
    ss["S"] = ss.Speed_group.astype(str)
    cnt = pd.crosstab(ss.SST, ss.S).reindex(index=REGIMES, columns=REGIMES)
    pct = cnt.div(cnt.sum(axis=1), axis=0) * 100
    med = ss.groupby(["SST", "S"])["GB History_error"].median().unstack() \
        .reindex(index=REGIMES, columns=REGIMES)
    g2 = ss.groupby(["SST", "S"])["gain"].mean().unstack() \
        .reindex(index=REGIMES, columns=REGIMES)
    assert (cnt.to_numpy() == np.array([[6855, 9048, 12244], [6085, 6615, 8505],
                                        [10202, 6883, 11408]])).all()
    assert _close(med, [[6.44, 8.61, 15.03], [5.53, 7.87, 15.77],
                        [4.81, 7.57, 14.96]])
    assert _close(g2, [[2.12, 3.63, 5.53], [2.90, 3.58, 3.85],
                       [2.77, 4.14, 3.48]])
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.75))
    _heat(axes[0], pct.to_numpy(), "Blues", "{:.1f}",
          "(d) Speed mix within SST (%)", "Row share (%)",
          "Speed regime", "SST regime", fig, 0, 75)
    _heat(axes[1], med.to_numpy(), "YlOrRd", "{:.1f}",
          "(e) GB History median error", "Median error (km)",
          "Speed regime", "", fig)
    _heat(axes[2], g2.to_numpy(), "Greens", "{:.2f}",
          "(f) Mean benefit of history", "Mean reduction (km)",
          "Speed regime", "", fig, 0, None)
    fig.tight_layout(w_pad=0.8)
    save(fig, "fig_sst_speed")


# --------------------------- profiles / bootstrap / temporal --------------
def motion_profiles():
    mo = pd.read_csv(ROOT / "models" / "motion_conditioned_test_errors.csv")
    models = list(PROFILE_COLOURS)
    fig, axes = plt.subplots(2, 3, figsize=(7.2, 4.9), sharey="row")
    for c, d in enumerate(["Speed", "Acceleration", "Turning"]):
        for r, metric in enumerate(["Median", "P90"]):
            ax = axes[r, c]
            for m in models:
                v = mo[(mo.Descriptor == d) & (mo.Model == m)] \
                    .set_index("Regime").reindex(REGIMES)[metric]
                ax.plot(REGIMES, v, color=PROFILE_COLOURS[m],
                        marker=PROFILE_MARKERS[m], ms=4.5, lw=1.6, label=m)
            ax.grid(color="#e9e9e9", lw=0.6)
            ax.set_axisbelow(True)
            if r == 0:
                ax.set_title(d, fontsize=9.5)
            if r == 1:
                ax.set_xlabel(f"{d} regime")
        axes[0, 0].set_ylabel("Median error (km)")
        axes[1, 0].set_ylabel("90th-percentile error (km)")
    fig.legend(*axes[0, 0].get_legend_handles_labels(), loc="lower center",
               ncol=6, frameon=False, fontsize=7.5, bbox_to_anchor=(0.5, -0.01))
    fig.tight_layout(rect=(0, 0.05, 1, 1), h_pad=0.8)
    save(fig, "fig_motion_profiles")


def bootstrap_forest():
    b = pd.read_csv(ROOT / "models" / "history_gain_cluster_bootstrap.csv")
    fig, ax = plt.subplots(figsize=(6.2, 3.3))
    y = np.arange(len(b))
    ax.errorbar(b["Mean Gain (km)"], y,
                xerr=[b["Mean Gain (km)"] - b["CI Lower"],
                      b["CI Upper"] - b["Mean Gain (km)"]],
                fmt="o", color=C_HISTORY, ecolor="#7FA79A", capsize=3,
                ms=5, lw=1.4)
    for yi, (_, r) in zip(y, b.iterrows()):
        ax.text(9.6, yi, f"{r['Mean Gain (km)']:.2f} [{r['CI Lower']:.2f}, "
                f"{r['CI Upper']:.2f}]   n={int(r['Samples']):,}, "
                f"{int(r['Drifters'])} dr.", va="center", fontsize=6.8,
                color="#52514e")
    ax.axvline(0, color=INK, lw=0.8)
    ax.axvline(3.652, color=C_CURRENT, lw=1, ls=":")
    ax.text(3.75, len(b) - 0.35, "overall mean 3.65 km [3.14, 4.14]",
            color=C_CURRENT, fontsize=7, va="bottom")
    ax.set_yticks(y)
    ax.set_yticklabels([r.replace(" Speed / ", " speed / ")
                        .replace(" Turning", " turning") for r in b.Regime],
                       fontsize=7.5)
    ax.set_ylim(len(b) - 0.3, -0.6)
    ax.set_xlim(0, 9.5)
    ax.set_xlabel("Mean reduction in 24-h error, GB Current $-$ GB History (km)")
    ax.grid(axis="x", color="#e9e9e9", lw=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout()
    save(fig, "fig_bootstrap_regimes")


def temporal():
    pr = pd.read_parquet(PRED, columns=["trajectory_id", "time",
                                        "Constant Velocity_error",
                                        "GB Current_error", "GB History_error"])
    pr["year"] = pd.to_datetime(pr.time).dt.year
    yr = pr.groupby("year").agg(
        n=("time", "size"), d=("trajectory_id", "nunique"),
        cv=("Constant Velocity_error", "median"),
        gc=("GB Current_error", "median"), gh=("GB History_error", "median"))
    print("\n[temporal]\n", yr.round(3).to_string())
    assert _close(yr.loc[[2007, 2009, 2013], "gh"], [8.257, 16.030, 6.524], .001)
    assert (yr.gh < yr.gc).all() and (yr.gc < yr.cv).all()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.0, 3.9), sharex=True,
                                 gridspec_kw={"height_ratios": [1.6, 1]})
    for c, lab, col, mk in [("cv", "Constant Velocity", "#7F7F7F", "o"),
                            ("gc", "GB Current", C_CURRENT, "v"),
                            ("gh", "GB History", C_HISTORY, "P")]:
        a1.plot(yr.index, yr[c], color=col, marker=mk, ms=4.5, lw=1.6,
                label=lab)
    a1.set_ylabel("Median error (km)")
    a1.legend(frameon=False, ncol=3, fontsize=7.5, loc="upper right")
    a1.grid(color="#e9e9e9", lw=0.6)
    a2.bar(yr.index, yr.n / 1000, color="#B8C4D6", edgecolor="white")
    for x, (n, d) in zip(yr.index, zip(yr.n, yr.d)):
        a2.text(x, n / 1000 + 0.2, f"{d}", ha="center", fontsize=7,
                color="#52514e")
    a2.set_ylabel("Test forecasts\n(thousands)")
    a2.set_ylim(0, 14)
    a2.set_xticks(yr.index)
    a2.tick_params(axis="x", labelsize=7, rotation=45)
    a2.text(0.995, 0.97, "numbers above bars: distinct test drifters",
            transform=a2.transAxes, fontsize=7, color="#52514e", va="top",
            ha="right")
    fig.tight_layout(h_pad=0.4)
    save(fig, "fig_temporal")


if __name__ == "__main__":
    import sys
    stages = sys.argv[1:] or ["all"]
    run = lambda k: "all" in stages or k in stages  # noqa: E731
    if run("test"):
        test_comparison()
    if run("spatial"):
        spatial()
    if run("region"):
        study_region()
    if run("drogue"):
        drogue_check()
    if run("traj"):
        trajectories()
    if run("joint"):
        joint_speed_turning()
    if run("sst"):
        sst_figures()
    if run("motion"):
        motion_profiles()
    if run("boot"):
        bootstrap_forest()
    if run("temporal"):
        temporal()

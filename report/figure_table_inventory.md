# Figure and table inventory

"Copied" means the file is an unmodified copy of `image/report/<file>`, and the original is untouched. "Generated" means the file was produced by `report/scripts/make_figures.py` from saved outputs only, with no retraining or re-evaluation.

## Figures

All "generated" figures recompute their plotted values from saved outputs and **assert agreement with the values printed in notebook 08** before plotting (see `scripts/make_figures.py`). They were re-plotted only to improve legibility at A4; the original PNGs in `image/report/` are untouched.

| No. | Report file | Origin | Source data / notebook cell | Location | Notes |
|---|---|---|---|---|---|
| 1 | `figures/generated/fig_study_region_coverage.pdf` | Generated | `modelling_dataset_final.parquet` | §2 | New figure |
| 2 | TikZ in `sections/03_framework.tex` | Drawn | none | §3 | Schematic; contains no data |
| 3 | `figures/generated/fig_test_model_comparison.pdf` | Generated | `final_test_comparison.csv` (cell 39) | §5.1 | New **test-set** comparison |
| 4 | `figures/generated/fig_traj_cv_gb.pdf` | Re-plot of cell 44 | `report_test_predictions.parquet` | §5.2 | Same drifters and windows; panel medians asserted equal to the notebook figure (11.2/8.6/3.9, 12.9/12.5/7.0, 12.2/12.6/8.2 km). Axes fixed per drifter across Figs 4, 12 and 13 |
| 5 | `figures/report_geographic_forecast_cases.png` | Copied | cell 41 | §5.2 | Caption warns that the legend errors refer to the "Typical" panel only |
| 6 | `figures/generated/fig_motion_profiles.pdf` | Re-plot of cell 51 | `motion_conditioned_test_errors.csv` | §6.1 | Median and P90 in one 2×3 figure; distinct markers per model |
| 7 | `figures/generated/fig_joint_speed_turning.pdf` | Re-plot of cell 53 | `report_test_predictions.parquet` | §6.2 | Counts, medians and mean gains asserted equal to the notebook |
| 8a | `figures/generated/fig_bootstrap_regimes.pdf` | Re-plot of cell 55 | `history_gain_cluster_bootstrap.csv` | §6.3 | Adds per-regime values, cases and drifters |
| 8b | `figures/report_high_speed_turning_bootstrap_contrast.png` | Copied | cell 57 | §6.3 | Bootstrap replicates are not saved, so this figure cannot be re-plotted without re-running the bootstrap |
| 9 | `figures/generated/fig_spatial_performance_rescaled.pdf` | Re-plot of cell 60 | `report_test_predictions.parquet` | §7.1 | Scale capped at 18 km (3 cells exceed it, listed in the caption); drifter-support panel added |
| 10 | `figures/generated/fig_temporal.pdf` | Re-plot of cell 63 | `report_test_predictions.parquet` | §7.2 | Adds drifter counts per year |
| 11 | `figures/generated/fig_sst_regimes.pdf` + `fig_sst_speed.pdf` | Re-plot of cells 68, 70 | `report_test_predictions.parquet` + SST from `gulf_stream_trajectories.parquet` | §7.3 | Thresholds, counts and matrices asserted equal to the notebook |
| 12 | `figures/generated/fig_traj_mf_linear.pdf` | Re-plot of cell 46 | `report_test_predictions.parquet` | App. A.3 | Mean-flow, Ridge History, Elastic Net History |
| 13 | `figures/generated/fig_traj_trees.pdf` | Re-plot of cell 46 | `report_test_predictions.parquet` | App. A.3 | RF, ET, GB History |

**Copied into `report/figures/` but no longer used** (kept for comparison; originals in `image/report/`): `report_individual_trajectory_overlays.png`, `report_trajectory_*.png`, `report_motion_regime_*_errors.png`, `report_joint_speed_turning_analysis.png`, `report_history_gain_bootstrap_ci.png`, `report_temporal_forecast_performance.png`, `report_sst_*.png`, `report_spatial_forecast_performance.png`, `report_expanded_model_comparison.png` (validation medians; duplicated by Table 4) and `report_regional_trajectory_overlays.png` (too dense at A4).

**Deliberately excluded:** `image/report/report_ridge_comparison.png`, `report_six_model_comparison.png` and `report_history_gain.png`, which show validation results from before the geometric target refinement, and all top-level `image/*.png` and poster figures (earlier region and sample).

## Tables

| No. | Content | Source |
|---|---|---|
| 1 | Cohort and drifter-disjoint partitions, with undrogued share | cells 6, 8; drogue share from a report-time check (`make_figures.py`) |
| 2 | Predictor definitions (9 current + 16 history) | cells 7, 11 |
| 3 | Hyperparameter grids and selected configurations | cells 27–34 |
| 4 | Validation median and test mean/median/P90/RMSE for 12 methods | cells 36, 39; `final_*_comparison.csv` |
| 5 | Motion-regime counts and errors (CV, MF, GBC, GBH) | `motion_conditioned_test_errors.csv` (cell 51) |
| 6 | Four-period temporal summary | cell 63 |
| 7 | SST feature ablation (validation) | cell 74 |
| 8 | Proposal success criteria and status | README success criteria vs. evidence |
| 9 | Joint-regime bootstrap benefits with 95% intervals (appendix) | `history_gain_cluster_bootstrap.csv` (cell 55) |
| — | Reproducibility map (appendix, non-floating) | notebook cells and artefacts |

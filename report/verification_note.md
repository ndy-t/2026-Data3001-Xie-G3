# Verification note — DATA3001 final report

Prepared 8 November 2026. Primary source: `notebook/08_reoprt_part_1.ipynb` (the file name really is spelled "reoprt"). It has 79 cells, the execution counts are monotonic, and its outputs were saved. No notebook, dataset, model or original figure was modified or re-run. New artefacts live only under `report/`.

## 1. How numbers were checked

1. **Automated corpus check.** Every decimal number in `report/sections/*.tex` and `report/appendix/*.tex` was matched against all numbers that appear in notebook outputs, `models/*.csv`, `data/processed/*.csv` and the figure-script log, including rounded forms. Unmatched values were reviewed by hand. They were TikZ/layout coordinates, figure widths, or derived values recomputed below.
2. **Table-level checks against full-precision sources.**
   - Table 4 (validation and test) was checked against `models/final_test_comparison.csv` and `models/final_validation_comparison.csv`. This check found one error, which was corrected: the Elastic Net History validation median is 10.49 (source 10.4949…), not 10.50.
   - Table 5 (motion regimes) was checked cell by cell against `models/motion_conditioned_test_errors.csv`. All cells match.
   - Table 6 (periods) was recomputed from `data/processed/report_test_predictions.parquet`. All cells match. The 2019–2022 CV median is 15.7146 and is reported as 15.71; the notebook prints 15.715.
   - Table 9 (bootstrap) was checked against `models/history_gain_cluster_bootstrap.csv`. All rows match.
3. **Rounding-boundary values.** Wherever a notebook printout ends in 5 at the third decimal, the full-precision value was looked up before rounding. Example: the High-speed Low/Medium-turning gain is 4.0152, reported as 4.02.

## 2. Source of key claims

| Claim in report | Value | Source |
|---|---|---|
| Eligible origins / drifters | 632,770 / 519 | cell 4 output |
| Valid samples / drifters / retained | 626,679 / 517 / 99.04% | cell 6 |
| Split (cases, drifters) | train 455,662/361; val 88,471/78; test 82,546/78 | cell 8 |
| Motion descriptor summary (median speed 0.308, mean 0.408, max 2.60; turning median 9.42; 471 undefined) | — | cell 7 (626,679 − 626,208 = 471) |
| Mean-flow grid cells; fallback share | 224; 0.73% of hourly steps (val) | cells 10, 19 |
| Single-step vs stepwise mean-flow (val median) | 22.663 → 22.368 | cell 19 |
| Geometric check (median, P99, max; >1 km) | 0.021, 1.536, 2.981 km; 1,961 | cell 23 |
| Post-refit reconstruction max | 4.96e-9 m | cell 25 |
| Tuning grids and selected configurations | Table 3 | cells 27–34 |
| Training times (GB/ET/RF History, selected config) | 6.4 / 40.7 / 172.8 s | cells 31, 33, 34 |
| Test metrics, all models | Table 4 | cell 39; `final_test_comparison.csv` |
| % reductions (e.g. 41.9% median, 30.2% P90 vs CV; 29.3% history gain for GB) | derived | `make_figures.py` log |
| Motion thresholds | 0.2387/0.3985 m/s; 1.546e-5/2.331e-5 m/s²; 6.696/13.984 °/h | cell 49; `motion_group_thresholds.csv` |
| Joint counts, medians, mean benefits | Fig. 7 | cell 53 |
| Overall bootstrap gain | 3.652 [3.141, 4.141] | cell 55 |
| High-speed contrast | 7.032 vs 4.015; diff 3.017 [1.212, 5.248] | cell 57 |
| Spatial: 145/198 cells, 73,214 forecasts (88.7%) | — | cell 60; reproduced by `make_figures.py` (asserted) |
| Spatial improvement min/median/max; 3 clipped cells; drifters per cell 3–16 (median 6; 79% ≤ 10) | 0.295 / 6.209 / 42.025 km | `make_figures.py` log; report-time check |
| Yearly and period results | Table 6, Fig. 10 | cell 63 |
| SST thresholds, coverage, regime metrics | 26.93/28.06 °C; 77,845/82,546 | cells 66, 68 |
| SST × speed matrices | Fig. 11b | cell 70 |
| SST ablation (validation) | Table 7; mean gain 0.0192 km; 50.1% improved | cell 74 |

## 3. New report-time checks (not in the notebook)

These were computed from saved outputs with `report/scripts/make_figures.py` or with one-off read-only queries. They are labelled as report-time checks in the text.

- **Drogue status at forecast origins** (`drogue_status == False`): train 48.23%, validation 53.59%, test 46.01%, overall 48.69% (305,137 / 626,679). Drifters with at least one undrogued origin: 191 / 46 / 36. The models neither filtered nor used drogue status.
- **Share of test forecasts where GB History beat GB Current**: 71.43% (no ties).
- **Bootstrap sample**: 78 drifters and 82,533 cases. The single drifter with undefined turning also has forecasts with defined turning.
- **Default early stopping**: scikit-learn documents `HistGradientBoostingRegressor(early_stopping='auto')` as enabling early stopping when n > 10,000, using `validation_fraction=0.1`. The notebook did not override this default.

## 3b. Revision 2 checks (8 November 2026)

- **Validation-to-test shift**, computed from `final_validation_comparison.csv` and `final_test_comparison.csv`: median errors rise by 3.1% (GB Current) to 10.5% (Ridge/Elastic Net History). CV rises 5.6%, the History variants 8.2–10.5% and the Current variants 3.1–6.8%. The report now states that composition differences and validation optimism from model selection both remain possible.
- **Gradient Boosting early stopping**: the report now states that the internal validation split is random at row level (not drifter-grouped), that it lies wholly inside the training drifters, and that it therefore does not contaminate the external validation or test sets.
- **Regenerated figures (4, 6, 7, 8a, 10, 11, 12, 13)**: each function in `scripts/make_figures.py` asserts agreement with notebook outputs before plotting (trajectory panel medians, joint-regime counts/medians/gains, SST thresholds/counts/medians/P90/gains, SST × speed matrices, yearly medians). All assertions passed.
- **Practical-significance text**: the area ratios (9.23/15.89)² = 0.34 and (28.55/40.90)² = 0.49 are a geometric illustration only and are labelled as such. New references Breivik et al. (2011) and van Sebille et al. (2020) were verified via Crossref.

## 4. References

Every DOI in `references.bib` was resolved through the Crossref API (`api.crossref.org/works/<doi>`). The NOAA dataset DOI was resolved through DataCite (`api.datacite.org`). Authors, year, title, journal, volume, issue and pages were copied from the returned metadata. Pedregosa et al. (2011, JMLR) and Efron & Tibshirani (1993) have no DOI and are standard references. One DOI proposed from memory during drafting resolved to an unrelated article and was discarded; this is mentioned in the AI reflection.

## 5. Unresolved issues for the group

1. **Industry partner / client name.** The intro lecture slides (`intro.pdf`) are image-only and could not be machine-read. The report therefore uses the placeholder "Industry partner: [name to be confirmed]" and does not name the client. Insert the correct name and affiliation, and if you wish add one or two sentences on why the question matters to that client. The rubric's "Motivation" criterion asks for this.
2. **Author names and zIDs** are placeholders in `main.tex`.
3. **Error against lead time.** The course brief for project 3.2.4 asks for error against lead time on common axes. Only a 24 h horizon was modelled. This is disclosed as a limitation and a plan deviation, not resolved.
4. **Repository README.** `README.md` was rewritten in revision 2 (at the group's request) to document the final workflow. It distinguishes outputs reproducible from saved files, from saved models and from raw NOAA data, and states that a clean end-to-end re-run has **not** been verified. Notebook 08, `models/`, `report/` and the large processed parquet files are not in Git, so a fresh clone cannot reproduce the results until these are committed or shared. Package versions are not pinned.
5. **Drogue status.** Almost half the cohort is undrogued. If time permits, a drogue-stratified error table from `report_test_predictions.parquet` would strengthen the report. It would need no retraining.
6. **Hard-coded plotting extents.** Several notebook plotting cells hard-code the 80–60°W, 30–45°N box, so the region is only partly parameterised (success criterion 6).
7. **Earlier results.** The poster and `image/*.png` (top level) used a different box (80–50°W, 25–45°N), sample definition and metrics. They are not used in the report, and the report states that they are superseded.
8. **Existing-figure caveat.** In `report_geographic_forecast_cases.png` the shared legend shows errors for the "Typical" panel only. The report caption says so, and the figure itself was not altered.

## 6. Page count

The compiled `report/main.pdf` is 25 A4 pages in total (after revision 2), including the references, the AI reflection and the appendix. This is within the 30-page limit.

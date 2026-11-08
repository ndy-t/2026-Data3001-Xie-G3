# Forecasting Surface Drifter Trajectories in the Gulf Stream

**DATA3001 — Data Science and Decisions in Practice**  
**UNSW Sydney · Term 3, 2026 · Group 2026-Data3001-Xie-G3**

## 1. Research question and objectives

This project investigates whether recent movement history improves **24-hour position forecasts** for surface drifters in the Gulf Stream, beyond what can be predicted from their current velocity or the regional mean flow.

> **Primary research question:** Can the preceding 24 hours of a drifter's observed motion improve its next-day position forecast, when evaluated on drifters not used for model training?

Our objectives are to:

1. Build and evaluate 24-hour position forecasts using physically meaningful baselines and statistical learning models.
2. Compare **current-only** and **history-enhanced** models on identical held-out forecast cases to isolate the value of recent motion history.
3. Characterise forecast errors across speed, turning, acceleration, geography, time and sea-surface temperature.
4. Quantify uncertainty in the improvement attributable to history and interpret the implications for ocean observations.

## 2. Scientific motivation

The Gulf Stream is a strong western boundary current with sharp velocity gradients, meanders and energetic eddies. These characteristics make it an important setting for studying the predictability of drifting instruments.

Surface drifters are also **ocean-observing platforms**: their positions determine where measurements of currents and sea-surface temperature are collected. In a warming climate, sustained ocean observations are essential for interpreting changes in upper-ocean conditions and circulation. Uncertainty about where a drifter will travel therefore translates into uncertainty about **where future observations will be available**, especially near dynamically complex currents and eddies.

Our analysis examines how forecast errors vary with recent motion and location. This helps identify circumstances in which the spatial distribution of future drifter observations is easier or harder to anticipate. Forecast difficulty is not, by itself, a measure of intrinsic ocean predictability or evidence of climate-driven change; the contribution is to the interpretation and planning of Lagrangian observations.

## 3. Data and study region

We use the **NOAA Global Drifter Program (GDP) hourly dataset, version 2.01**, accessed through CloudDrift. The dataset provides hourly interpolated positions, eastward and northward velocities, sea-surface temperature and drifter metadata.

| Setting | Final study design |
| --- | --- |
| Region | 80°W–60°W, 30°N–45°N |
| Forecast-origin season | July–September |
| Years | 2007–2022 |
| Forecast horizon | 24 hours |
| Input history | 25 hourly observations, from `t−24` through `t` |
| Eligible origins | Valid observations inside the region and seasonal window, with the required history and future target |
| Forecast cases | 626,679 from 517 distinct drifters |

The input history and future target may extend beyond the geographic or seasonal selection boundaries. Forecast cases are defined by the **origin** at time `t`, not by requiring the entire track to remain inside the box.

Core variables include `id`, `time`, `lat`, `lon`, `ve`, `vn`, `sst` and `drogue_status`. Recent speed, turning and acceleration are derived from the observed motion history.

## 4. Forecasting and evaluation

### 4.1 Baselines and learned corrections

Two physical benchmarks are used:

- **Constant Velocity (CV):** extrapolates the current velocity over 24 hours.
- **Mean-flow Advection:** uses the estimated regional mean-flow field.

We evaluate five learning families: **Ridge, Elastic Net, Random Forest, Extra Trees and Gradient Boosting**. Each has a **current-only** version and a **history-enhanced** version. Learned models correct the displacement predicted by CV rather than directly predicting unrestricted latitude and longitude. Geographic predictions are constructed using spherical/geodesic displacement calculations.

The controlled comparison between current-only and history-enhanced versions tests whether recent trajectory information adds value beyond the current state.

### 4.2 Held-out design and metrics

Drifters are assigned to **disjoint training, validation and test sets**, so observations from a given drifter do not cross the outer partitions.

| Partition | Drifters | Forecast cases |
| --- | ---: | ---: |
| Training | 361 | 455,662 |
| Validation | 78 | 88,471 |
| Test | 78 | 82,546 |

Model selection uses validation performance; the final comparison is reported on the held-out test drifters. All methods are evaluated on the same test forecast cases. The primary metric is **great-circle distance error** in kilometres, summarised by the median and 90th percentile. Drifter-cluster bootstrap intervals account for repeated forecast cases from the same drifter when assessing selected history gains.

## 5. Main findings

| Model | Test median error | Test 90th-percentile error |
| --- | ---: | ---: |
| Constant Velocity | 15.89 km | 40.90 km |
| Mean-flow Advection | 24.28 km | — |
| Gradient Boosting, history-enhanced | **9.23 km** | **28.55 km** |

History-enhanced Gradient Boosting reduces median 24-hour error by approximately **41.9%** relative to Constant Velocity. History-enhanced Random Forest and Extra Trees achieve similar median errors (9.25 km and 9.33 km, respectively).

The paired mean error improvement from adding history to Gradient Boosting is **3.65 km**, with a **95% drifter-cluster bootstrap interval of [3.14, 4.14] km**. The benefit varies by motion regime and is particularly pronounced in the exploratory high-speed, high-turning subgroup. Spatial and temporal analyses further describe where and when forecasts are more challenging. Sea-surface temperature adds little predictive value in the tested feature-ablation comparison.

These results show that recent motion history improves **retrospective 24-hour forecast accuracy** in this study region. They do not establish real-time operational forecasting skill: the processed GDP hourly velocity estimates can use satellite observations from both before and after the nominal forecast time. Results are also specific to the selected region, months and evaluation design.

## 6. Project materials

| Location | Contents |
| --- | --- |
| [`notebook/01_gulf_stream_data_coverage.ipynb`](notebook/01_gulf_stream_data_coverage.ipynb) | GDP data access and initial regional extraction |
| [`notebook/08_reoprt_part_1.ipynb`](notebook/08_reoprt_part_1.ipynb) | Final modelling, evaluation and diagnostic analyses |
| [`report/`](report/) | Final report, LaTeX sources, figures and references |
| [`report/main.pdf`](report/main.pdf) | Final written report |

The final notebook is the reference implementation for the study definitions and reported results. The report provides the full methods, additional figures, uncertainty analysis and discussion.

## 7. References

- Aksamit, N. O., Sapsis, T. P., & Haller, G. (2020). Machine-learning mesoscale and submesoscale surface dynamics from Lagrangian ocean drifter trajectories. *Journal of Physical Oceanography, 50*(5), 1179–1196. https://doi.org/10.1175/JPO-D-19-0238.1
- Elipot, S., Lumpkin, R., Perez, R. C., Lilly, J. M., Early, J. J., & Sykulski, A. M. (2016). A global surface drifter data set at hourly resolution. *Journal of Geophysical Research: Oceans, 121*, 2937–2966. https://doi.org/10.1002/2016JC011716
- Elipot, S., Sykulski, A., Lumpkin, R., Centurioni, L., & Pazos, M. (2022). Hourly location, current velocity, and temperature collected from Global Drifter Program drifters world-wide, version 2.01. *NOAA National Centers for Environmental Information*. https://doi.org/10.25921/x46c-3620
- Grossi, M. D., Jegelka, S., Lermusiaux, P. F. J., & Özgökmen, T. M. (2025). Surface drifter trajectory prediction in the Gulf of Mexico using neural networks. *Ocean Modelling, 196*, 102543. https://doi.org/10.1016/j.ocemod.2025.102543

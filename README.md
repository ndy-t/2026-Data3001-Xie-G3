# Forecasting Surface Drifter Trajectories in the Gulf Stream

## Research proposal

### 1. Research questions and objectives

The main objective is to use the preceding 24 hours of a surface drifter's trajectory to predict its position 24 hours after the forecast origin. We will compare these forecasts with two physical baselines to assess whether recent history provides useful predictive information. Forecast origins will be restricted to the Gulf Stream region during July–September of 2007–2022.

The primary research question is:

> Does using the preceding 24 hours of trajectory history improve 24-hour position forecasts for drifters currently inside the Gulf Stream region, compared with constant present velocity and regional mean-flow advection?

The project has four objectives:

1. Build a forecasting model that uses the previous 24 hours of positions and velocities, together with the current state, to predict the position at `t + 24 hours`.
2. Compare its forecasts with the two physical baselines on identical test cases from drifters held out of training and model selection.
3. Compare learned models with and without historical features to distinguish the contribution of history from differences between modelling methods.
4. Produce a reproducible pipeline and report forecast errors, predicted and observed locations, and variation in performance within July–September, across locations, and by data quality and drogue status.

The initial study fixes both the history window and forecast horizon at 24 hours. Other horizons, history lengths, and more complex models are optional extensions.

### 2. Data, region, and data description

#### Study region

The initial region of interest is the following Gulf Stream box:

| Boundary | Value |
| --- | ---: |
| Western longitude | 80°W (`-80`) |
| Eastern longitude | 60°W (`-60`) |
| Southern latitude | 30°N |
| Northern latitude | 45°N |

This box captures the Gulf Stream along the east coast of the United States and its northeastward extension into the North Atlantic. This box defines eligible forecast origins; historical inputs and future target positions may lie outside it. The initial comparison will use these boundaries, while all code will accept the region as parameters rather than hard-coded constants.

#### Dataset

The project uses the NOAA Global Drifter Program hourly dataset, version 2.01. It contains quality-controlled, interpolated hourly locations, surface velocities, sea-surface temperatures, uncertainty estimates, and drifter metadata. The global CloudDrift representation contains 19,396 trajectories and 197,214,787 hourly observations.

This is one NOAA dataset, not two separate datasets. In its CloudDrift/Xarray representation, variables are organised along two linked dimensions:

- **Trajectory dimension (`traj`)**: one entry per drifter, including `id`, `rowsize`, deployment information, start and end dates, location system, and drogue-loss date.
- **Observation dimension (`obs`)**: many hourly entries per drifter, including `time`, `lat`, `lon`, eastward velocity `ve`, northward velocity `vn`, sea-surface temperature `sst`, uncertainty estimates, quality flags, and `drogue_status`.

The hourly product provides records at one-hour intervals after interpolation and quality control; this is not necessarily the interval between raw satellite fixes. The main inputs will be positions and velocities. SST is an optional extension, while uncertainty and drogue status will support quality checks and diagnostic evaluation. Relevant variables are:

| Variable | Meaning | Unit or type |
| --- | --- | --- |
| `id` | Unique drifter identifier | integer |
| `time` | Observation time | UTC datetime |
| `lat`, `lon` | Position | degrees |
| `ve`, `vn` | Eastward and northward velocity | m/s |
| `sst` | Fitted sea-surface temperature | K |
| `drogue_status` | Whether the drogue is present | boolean |

### 3. Importance and significance

Accurate surface-trajectory forecasts support search and rescue, oil-spill response, marine-debris tracking, fisheries management, and the interpretation of Lagrangian ocean observations. The Gulf Stream is an important test region because it is a fast, narrow western boundary current with strong spatial gradients, meanders, and eddies. These features create transport pathways that are economically and scientifically important while also making trajectories difficult to predict.

Over 24 hours, forecasts based on current velocity can accumulate errors as a drifter encounters curved flow, changing current speed, or an eddy. The preceding 24 hours may reveal motion patterns that help anticipate its next position. Comparison with physical baselines tests practical forecasting value, while a comparison of the same learned model with and without historical features tests the additional value of history.

### 4. Background and existing approaches

Elipot et al. (2016) developed the hourly GDP position and velocity product by fitting local trajectory models to irregular satellite fixes while accounting for location error. The resulting hourly resolution retains high-frequency motions that are not resolved safely by the older six-hourly product.

Several families of methods are relevant to this project:

- **Persistence or constant-velocity models** assume that the latest velocity continues unchanged. They are simple but can be difficult to beat at short lead times.
- **Mean-flow advection models** estimate a spatial, and optionally seasonal, climatological velocity field and integrate a particle through that field.
- **Statistical time-series models** use recent positions or velocities to extrapolate future motion.
- **Machine-learning sequence models** learn nonlinear relationships in recent drifter motion. Aksamit et al. (2020), for example, combined recurrent learning with a reduced physical drifter model. More recent work by Grossi et al. (2025) found that simple neural networks did not consistently beat autoregressive baselines on observed Gulf of Mexico trajectories, while a spatiotemporal graph model showed more promise. This supports using strong baselines and held-out trajectories rather than assuming that a more complex model will automatically perform better.

The initial learned models will be a simple regularised linear regression and a gradient-boosted regression model, using features derived from the previous 24 hours of motion. Each will also be fitted without historical features as a controlled comparison. Additional horizons, SST, alternative history lengths, and neural networks will be considered only after the primary 24-hour forecasting comparison is complete.

### 5. Proposed method

#### 5.1 Cohort construction and quality control

1. Define eligible forecast-origin times as 1 July at 00:00 UTC through 30 September at 23:00 UTC in each year from 2007 to 2022.
2. Select a forecast origin only when the drifter is inside the Gulf Stream box (`80°W–60°W`, `30°N–45°N`) at that time. A drifter currently outside the box is not eligible merely because it enters the region later.
3. Retrieve the preceding 24 hours of observations, the current observation, and the target at exactly 24 hours after each origin. Retain required observations outside the geographic box and seasonal window. For example, a 30 September origin may have its target on 1 October, and a 1 July origin may use June history. Complete trajectories may be retrieved for convenience.
4. Sort by drifter ID and time, remove duplicate drifter–time records, and check hourly timestamp continuity. Reject samples with missing or invalid positions or velocities in the required input window, or a missing or invalid target position. Examine dataset quality flags and uncertainty estimates, and document all quality exclusions.
5. Match targets by drifter ID and exact timestamp rather than by row offset. Direct endpoint prediction requires valid inputs and the target position; a complete observed path between the origin and target is not required.
6. Audit the existing extracts for missing boundary observations and retrieve these from the source dataset where necessary. Report eligible sample counts, distinct drifter counts, and sample losses by filtering reason.

#### 5.2 Input history and prediction target

At forecast origin `t`, use the 24 preceding hourly records at `t - 24 hours, ..., t - 1 hour`, together with the current position and velocity at `t`. This gives 25 timestamps spanning a full 24 hours when both endpoints are included. No input timestamp may be later than `t`.

| Component | Time | Role |
| --- | --- | --- |
| Historical observations | `t - 24 hours` through `t - 1 hour` | Previous positions and velocities |
| Current state | `t` | Forecast origin and latest position and velocity |
| Prediction target | `t + 24 hours` | Observed future position used for training or evaluation |

The learned models will directly predict eastward and northward displacement from the origin, then convert the displacement back to geographic coordinates using a documented geographic transformation. They will not recursively generate 24 one-hour predictions.

Current-state features will include the latest position and velocity, time within the July–September window, and local mean-flow velocity estimated from training data. Historical features will summarise relative positions, velocity means and variability, velocity trends, acceleration, and turning over the fixed 24-hour window. SST is not required for the primary comparison.

#### 5.3 Physical baselines and learned models

The two primary baselines are:

1. **Constant present velocity:** extrapolate the latest eastward and northward velocities for 24 hours to obtain a future position. This baseline assumes velocity remains constant, rather than assuming the drifter stays at its current position.
2. **Regional mean-flow advection:** estimate a spatial July–September mean-velocity field using training drifters only, then numerically advect a particle from the forecast origin for 24 hours. Extend training-data coverage beyond the selection box where available. If the predicted path enters an unsupported area, use the origin velocity for the unsupported integration steps and report fallback use. Choose field resolution and other baseline settings using training and validation data only.

Fit a regularised linear model and a gradient-boosted model to the same 24-hour displacement targets. For each model, compare a current-state-only version with a version that adds the historical features. Beating a physical baseline alone would not establish that history caused the improvement; the comparison within each model class addresses that question.

All methods will use identical eligible forecast origins and targets for evaluation, including requiring the same valid history even when a baseline does not use it.

#### 5.4 Validation and evaluation

Partition data into training, validation, and test sets by drifter ID, using a reproducible split fixed before model fitting. The same drifter must remain in one partition across all years and processed files. Report distinct drifter and sample counts for each partition.

Estimate preprocessing parameters, any data-derived quality thresholds, and the mean-flow field from training data only. Tune model and baseline settings on validation data, then freeze the design before final test evaluation. Do not use test data to choose features, thresholds, or hyperparameters.

For every method, report median and 90th-percentile great-circle distance error in kilometres on the same test cases. Compare history-based forecasts against both physical baselines and their corresponding current-state-only model. Account for repeated forecasts from the same drifter using paired bootstrap resampling at the drifter level when estimating uncertainty in performance differences.

Include maps showing recent history, the forecast origin, predicted 24-hour locations, and the actual target for a small, reproducibly selected set of test examples. Report diagnostic results by month within July–September, location, data quality, and drogue status where sufficient drifters are available. These are within-window comparisons, not evidence of performance across seasons.

### 6. Preliminary research

The analyses in [03_preliminary_analysis.ipynb](notebook/03_preliminary_analysis.ipynb) examine data completeness, forecast-horizon feasibility, and a simple prediction benchmark. The existing preliminary results below describe four processed files containing **July–September observations from 2007–2022**. They support feasibility assessment but do not yet evaluate the final 24-hour-history sample definition or held-out design in Section 5. Required observations outside the extract boundaries must still be audited and supplemented where necessary.

#### 6.1 Data completeness

The existing extract contains **2,482,661 hourly observations**. No missing or non-finite values were found in longitude, latitude, or either velocity component, and there were no duplicate trajectory–time records. SST missingness varies by period:

| Study period | Hourly observations | Unique trajectory IDs within period | Missing SST |
| --- | ---: | ---: | ---: |
| 2007–2010 | 616,023 | 251 | 3.05% |
| 2011–2014 | 640,974 | 320 | 6.15% |
| 2015–2018 | 587,026 | 231 | 3.30% |
| 2019–2022 | 638,638 | 240 | 0.40% |

Position and velocity are therefore available for the initial models. SST can be tested as an additional predictor, with missing values handled using training data only. Completeness alone does not establish measurement accuracy.

#### 6.2 Availability of future observations

![Percentage of origins with an exact future observation, by study period and forecast lead time](image/forecast_horizon_availability.png)

Future observations were matched using the same trajectory ID and an exact timestamp offset, rather than a row shift. Across the four periods, availability is **99.92–99.94% at 1 hour**, **98.28–98.60% at 24 hours**, and **90.20–91.27% at 168 hours**. The 24-hour result supports the chosen prediction horizon; the other horizons provide exploratory context only. These percentages measure endpoint availability, not the availability or quality of a complete 24-hour input history. The final usable sample count must be recalculated after enforcing the history and forecast-origin requirements and checking boundary coverage. A complete observed future path between the origin and target is not required.

#### 6.3 A 24-hour constant-velocity benchmark

![Median, mean, and 90th-percentile 24-hour constant-velocity position errors for four study periods](image/constant_velocity_24h_error.png)

The baseline extrapolates the latest eastward and northward velocities for 24 hours and compares the predicted position with the exact future observation using great-circle distance. Median error ranges from **12.45 to 13.66 km**, while the 90th percentile reaches **29.70–33.34 km**. The larger upper-tail errors motivate reporting more than an average and testing whether recent trajectory history improves difficult forecasts. These results use all available 24-hour pairs and provide an exploratory benchmark, not a held-out model evaluation.

### Expected deliverables

- Parameterised code for selecting forecast origins by geographic box and July–September study window, while retaining required history and targets across boundaries.
- A documented dataset of 24-hour-history inputs and 24-hour-ahead targets, including quality checks and drifter-ID partitions.
- Implementations of constant-velocity and mean-flow advection baselines.
- Linear and gradient-boosted forecasting models, each with and without historical features.
- Held-out evaluation with distance-error summaries, uncertainty estimates, and maps of predicted and observed locations.
- A final report explaining whether historical information improves prediction, where it helps or fails, and the study's limitations.

### Success criteria

The project will be considered successful if:

1. The pipeline produces valid samples using the full preceding 24 hours and current state to predict the position 24 hours ahead, with clear documentation of sample exclusions.
2. Both physical baselines and the initial learned models are implemented, including documented mean-flow fallback handling.
3. The comparison is completed on identical held-out cases, with preprocessing and model selection respecting the drifter-ID partitions.
4. Evaluation quantifies the value of historical features through comparisons with both physical baselines and the same learned models without history, reporting median and 90th-percentile distance errors and uncertainty that accounts for repeated forecasts.
5. Predicted and actual future positions are presented, and the geographic region can be changed without rewriting the analysis logic.

Success does not require history to improve prediction: a valid finding of little or no added value also answers the research question. Additional horizons and neural networks are not required for primary success.

Partial success: preprocessing and physical baselines are complete, but the initial learned-model comparisons remain incomplete.

Project failure: valid forecast samples cannot be produced, or the final comparison is compromised by held-out data being used in training, preprocessing estimation, or model selection.

### Limitations

1. This is a retrospective forecasting exercise. The GDP hourly dataset contains interpolated and smoothed positions and velocities that can incorporate observations after the forecast origin. Even timestamp-correct inputs therefore do not establish real-time operational performance.
2. Forecast origins are restricted to July–September of 2007–2022. Retaining boundary-crossing histories and targets does not justify generalisation to other seasons. Holding out drifters also does not separately test generalisation to future years.
3. Multiple forecasts from the same drifter are dependent. Drifter-level resampling addresses this clustering, but different drifters may also experience shared ocean conditions.
4. Sparse coverage, strong gradients, and mesoscale eddies may limit forecast performance. Mean-flow estimates use training data only and require the documented constant-velocity fallback in unsupported areas.
5. Drogue loss can introduce wind-driven slip; results will be examined by drogue status.
6. Requiring complete input history and valid target positions excludes some tracks. Report sample losses and coverage so this selection is visible.

### References

- Aksamit, N. O., Sapsis, T. P., & Haller, G. (2020). Machine-learning mesoscale and submesoscale surface dynamics from Lagrangian ocean drifter trajectories. *Journal of Physical Oceanography, 50*(5), 1179–1196. <https://doi.org/10.1175/JPO-D-19-0238.1>
- Elipot, S., Lumpkin, R., Perez, R. C., Lilly, J. M., Early, J. J., & Sykulski, A. M. (2016). A global surface drifter data set at hourly resolution. *Journal of Geophysical Research: Oceans, 121*, 2937–2966. <https://doi.org/10.1002/2016JC011716>
- Elipot, S., Sykulski, A., Lumpkin, R., Centurioni, L., & Pazos, M. (2022). A dataset of hourly sea surface temperature from drifting buoys. *Scientific Data, 9*, 567. <https://doi.org/10.1038/s41597-022-01670-2>
- Grossi, M. D., Jegelka, S., Lermusiaux, P. F. J., & Özgökmen, T. M. (2025). Surface drifter trajectory prediction in the Gulf of Mexico using neural networks. *Ocean Modelling, 196*, 102543. <https://doi.org/10.1016/j.ocemod.2025.102543>
- NOAA Global Drifter Program. Hourly location, current velocity, and temperature collected from Global Drifter Program drifters world-wide, version 2.01. <https://doi.org/10.25921/x46c-3620> (accessed 21 September 2026).

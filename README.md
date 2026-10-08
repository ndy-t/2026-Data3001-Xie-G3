# Motion Characteristics and 24-Hour Drifter Forecast Errors in the Gulf Stream

## Research proposal

### 1. Research questions and objectives

This project investigates which recent motion characteristics are associated with difficult 24-hour surface drifter position forecasts. We will use the preceding 24 hours of positions and velocities to describe speed, acceleration, heading, and turning, and compare forecast errors across these motion conditions on held-out drifters. Forecast origins will be restricted to the Gulf Stream region during July–September of 2007–2022.

The primary research question is:

How do 24-hour position forecast errors vary with a drifter's recent speed, acceleration, and turning, and under which motion conditions does trajectory history improve prediction beyond current-state information and physical baselines?

The project has four objectives:

1. Construct comparable 24-hour forecasts using constant present velocity, regional mean-flow advection, regularised linear regression, and gradient-boosted regression.
2. Quantify how median and upper-tail position errors vary with motion characteristics measured before the forecast, distinguishing speed, changes in velocity, and changes in direction.
3. Compare each learned model with and without historical features to identify conditions in which history provides additional predictive value, little benefit, or worse forecasts.
4. Produce a reproducible evaluation with uncertainty estimates and interpretable figures, reporting data coverage, dependence between forecasts, and the limits of any observed associations.

The working hypothesis is that greater recent acceleration and turning are associated with larger errors, especially for constant-velocity forecasts. Whether history reduces these errors is an open empirical question. Speed and absolute heading will provide context; their associations may reflect location or sampling differences. These are hypotheses to test, not established results.

Both the history window and forecast horizon remain fixed at 24 hours. Other horizons, history lengths, and more complex models are optional extensions.

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

An overall error score can conceal substantial differences between motion conditions. The proposed analysis will estimate which conditions have larger errors and whether the ranking of forecasting methods changes across them. This can guide subsequent feature development and identify situations requiring additional environmental information. Recent acceleration and turning may be useful indicators, but the study must test this association rather than assuming curved or fast trajectories are always harder to predict.

### 4. Related research, study value, and scope

#### 4.1 Existing research on drifter position prediction

Forecasting drifter motion from historical observations is an established research problem. The following studies provide direct precedents and help define an appropriate contribution for this project.

| Study | Approach and findings | Relevance to this project |
| --- | --- | --- |
| [Aksamit et al. (2020)](https://doi.org/10.1175/JPO-D-19-0238.1) | Combined a recurrent neural network using drifter motion history with a reduced Maxey–Riley physical model, evaluating trajectory predictions on Gulf of Mexico deployments. The hybrid approach improved upon the reduced physical model in their experiments. | Historical motion has already been used to improve drifter prediction. Their use of environmental information and different deployments prevents a direct numerical comparison with our trajectory-based setting. |
| [Grossi et al. (2025)](https://doi.org/10.1016/j.ocemod.2025.102543) | Predicted Gulf of Mexico drifter trajectories over 24-hour and five-day windows. Fully connected networks using velocity histories did not outperform autoregressive models; a model sharing spatial and temporal information between drifters showed better performance in many cases. | Added model complexity does not guarantee improvement. We need strong baselines and should examine whether any advantage is confined to particular motion conditions. |
| [Lin et al. (2026)](https://doi.org/10.3389/fmars.2026.1966411) | Compared kinematic and learned forecasts at approximately ten-minute horizons using one Taiwan Strait buoy. Constant velocity performed best overall; a secondary, retrospective analysis of trajectory geometry found limited, segment-specific benefits from learned corrections. | Geometry-dependent error analysis also has precedent. Our study will examine multiple held-out drifters, a 24-hour horizon, and motion groups defined from pre-forecast observations, while keeping these differences separate from any claim of general superiority. |

[Elipot et al. (2016)](https://doi.org/10.1002/2016JC011716) describe the hourly GDP product underlying our analysis. It estimates positions and velocities from irregular satellite fixes, so temporal interpolation and measurement uncertainty matter when deriving acceleration and turning.

#### 4.2 Intended contribution and research value

Our intended contribution is a reproducible assessment of how forecast difficulty varies with recent motion in the selected Gulf Stream data. Both historical-trajectory forecasting and geometry-based diagnostics have prior literature; we make no claim to introduce either idea or a new forecasting algorithm. This focused review motivates the study but does not establish that its exact combination of analyses has never been attempted.

The analysis will provide:

- **Evidence about difficult motion conditions:** error distributions across speed, acceleration, and turning groups, accompanied by sample counts and uncertainty rather than selected difficult examples alone.
- **A conditional assessment of history:** matched comparisons of learned models with and without historical features, showing where history helps, has little effect, or hurts relative to physical baselines.
- **A useful empirical result even without better average accuracy:** identifying stable or uncertain error patterns can guide model development and subsequent collection of wind, wave, or current information.

#### 4.3 Scope of the conclusions

Forecast difficulty is defined relative to the tested methods, data, and 24-hour horizon; it is not an estimate of an intrinsic limit on ocean predictability. Associations between acceleration, turning, and error do not establish that these variables cause model failure. Regional and seasonal selection, correlated forecasts, interpolated observations, and missing environmental forcing constrain interpretation. The [limitations](#limitations) below describe how these issues will be reported.

The initial learned models remain regularised linear regression and gradient-boosted regression, each fitted with and without historical features. A new neural architecture is not required to answer the focused research question.

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

Current-state features will include the latest position and velocity, time within the July–September window, and local mean-flow velocity estimated from training data. Historical features will summarise relative positions, velocity means and variability, velocity trends, acceleration, and turning over the fixed 24-hour window. Section 5.5 defines the motion descriptors used to analyse forecast difficulty. SST is not required for the primary comparison.

#### 5.3 Physical baselines and learned models

The two primary baselines are:

1. **Constant present velocity:** extrapolate the latest eastward and northward velocities for 24 hours to obtain a future position. This baseline assumes velocity remains constant, rather than assuming the drifter stays at its current position.
2. **Regional mean-flow advection:** estimate a spatial July–September mean-velocity field using training drifters only, then numerically advect a particle from the forecast origin for 24 hours. Extend training-data coverage beyond the selection box where available. If the predicted path enters an unsupported area, use the origin velocity for the unsupported integration steps and report fallback use. Choose field resolution and other baseline settings using training and validation data only.

Fit a regularised linear model and a gradient-boosted model to the same 24-hour displacement targets. For each model, compare a current-state-only version with a version that adds the historical features. The comparison within each model class estimates the incremental predictive value of historical features; improvement over a physical baseline alone cannot isolate that value.

All methods will use identical eligible forecast origins and targets for evaluation, including requiring the same valid history even when a baseline does not use it.

#### 5.4 Validation and evaluation

Partition data into training, validation, and test sets by drifter ID, using a reproducible split fixed before model fitting. The same drifter must remain in one partition across all years and processed files. Report distinct drifter and sample counts for each partition.

Estimate preprocessing parameters, any data-derived quality thresholds, and the mean-flow field from training data only. Tune model and baseline settings on validation data, then freeze the models, motion-group definitions, primary comparisons, and diagnostic analysis plan before final test evaluation. Do not use test data to choose features, thresholds, or hyperparameters.

For every method, report median and 90th-percentile great-circle distance error in kilometres on the same test cases. Compare history-based forecasts against both physical baselines and their corresponding current-state-only model. Account for repeated forecasts from the same drifter using paired bootstrap resampling at the drifter level when estimating uncertainty in performance differences.

Include maps showing recent history, the forecast origin, predicted 24-hour locations, and the actual target for a small, reproducibly selected set of test examples. Report diagnostic results by month within July–September, location, data quality, and drogue status where sufficient drifters are available. These are within-window comparisons, not evidence of performance across seasons.

#### 5.5 Motion characteristics and forecast difficulty

For each held-out forecast, define position error as the great-circle distance in kilometres between the predicted and observed position at `t + 24 hours`. This per-forecast evaluation error, rather than the model's training loss, is the outcome for the difficulty analysis. Report median and 90th-percentile errors for each method and motion group.

All primary motion descriptors use only the 25 input timestamps from `t - 24 hours` through `t`. Let `v_j = (ve_j, vn_j)`, `s_j = norm(v_j)`, and `delta_t = 3600 seconds` between consecutive valid input records, where `norm` is the Euclidean vector magnitude.

| Descriptor | Definition from the input window | Interpretation |
| --- | --- | --- |
| Speed | Current speed and the mean and standard deviation of `s_j` over the input window, in m/s | Separates fast motion from variable motion. |
| Acceleration magnitude | `a_j = norm(v_j - v_(j-1)) / delta_t`; summarise by the window mean and maximum, in m/s² | Captures changes in velocity, including both speed changes and turning. Also summarise absolute speed change per second to help distinguish these effects. |
| Heading | `theta_j = atan2(vn_j, ve_j)`; retain current heading as sine/cosine components | Absolute direction of motion, with zero pointing east and positive angles counterclockwise; it is different from turning. |
| Turning rate | Wrap each consecutive heading difference into `[-pi, pi]` using `atan2(sin(delta_theta), cos(delta_theta))`; summarise its absolute rate over the window, in degrees/hour | Captures changes in direction without treating a crossing of the angular boundary as a large turn. |

Heading and turning are unreliable near zero speed. Fix a documented low-speed threshold using development data before test evaluation, flag affected angles as undefined, and report those cases as a separate low-speed group. Any imputation required by a learned model must use training data only. Do not use future acceleration or future turns to define the primary groups; any future-path explanation in example plots must be labelled retrospective.

The analysis will proceed as follows:

1. **Define groups before testing.** Use training-set tertiles of mean speed, mean acceleration magnitude, and mean absolute turning rate for the primary low/medium/high comparisons. Define exploratory heading sectors and minimum distinct-drifter counts before inspecting test errors. Disclose cut points, low-speed exclusions from angular summaries, and sparse groups.
2. **Compare errors and model gains.** On identical test cases, plot error distributions across the groups and a speed-by-turning heatmap. Report sample and distinct-drifter counts in every group. Compare history-based models with their current-state-only counterparts and both physical baselines using mean paired distance-error reductions, defined for each case as `comparison error - history-model error`; positive reductions indicate an improvement.
3. **Account for repeated observations.** Use paired bootstrap resampling of entire drifter IDs to obtain 95% confidence intervals for group summaries and error reductions. Retain all sampled forecasts from each resampled drifter across methods. Include a sensitivity analysis that weights drifters equally so long tracks do not determine the conclusions alone; label sparsely supported results exploratory.
4. **Check competing explanations.** Repeat acceleration and turning comparisons within speed bands where coverage permits. Examine location, month, drogue status, data quality, and mean-flow fallback use as possible explanations of apparent differences. Report associations and uncertainty, without treating correlated kinematic descriptors as independent causal drivers.

Primary outputs are error-versus-motion plots and a table showing where historical features help or fail. Future-motion case studies, finer subgroups, and feature ablations are secondary analyses and will be labelled accordingly. No motion condition will be declared difficult before the held-out results are available.

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
- Error plots by motion condition, a speed-by-turning heatmap, and paired model comparisons with sample and distinct-drifter counts.
- A report connecting the results to prior research and explaining which recent motion conditions are associated with larger errors, where historical information helps or fails, and the limits of those conclusions.

### Success criteria

The project will be considered successful if:

1. The pipeline produces valid samples using the full preceding 24 hours and current state to predict the position 24 hours ahead, with clear documentation of sample exclusions.
2. Both physical baselines and the initial learned models are implemented, including documented mean-flow fallback handling.
3. The comparison is completed on identical held-out cases, with preprocessing and model selection respecting the drifter-ID partitions.
4. Evaluation quantifies the value of historical features through comparisons with both physical baselines and the same learned models without history, reporting median and 90th-percentile distance errors and uncertainty that accounts for repeated forecasts.
5. The predefined motion-group analysis is completed, with error distributions, paired model gains, sample counts, and uncertainty reported for speed, acceleration, and turning. Sparse groups and secondary analyses are identified explicitly.
6. Predicted and actual future positions are presented, and the geographic region can be changed without rewriting the analysis logic.

Success does not require history to improve prediction or acceleration and turning to show a clear association with error. A well-supported null or uncertain result also answers the research question. Additional horizons and neural networks are not required for primary success.

Partial success: preprocessing and physical baselines are complete, but the learned-model comparisons, evaluation by motion condition, or uncertainty assessment remain incomplete.

Project failure: valid forecast samples cannot be produced, or the final comparison is compromised by held-out data being used in training, preprocessing estimation, or model selection.

### Limitations

1. This is a retrospective forecasting exercise. The GDP hourly dataset contains interpolated and smoothed positions and velocities that can incorporate observations after the forecast origin. Even timestamp-correct inputs therefore do not establish real-time operational performance.
2. Forecast origins are restricted to July–September of 2007–2022. Retaining boundary-crossing histories and targets does not justify generalisation to other seasons. Holding out drifters also does not separately test generalisation to future years.
3. Multiple forecasts from the same drifter are dependent. Drifter-level resampling addresses this clustering, but different drifters may also experience shared ocean conditions.
4. Sparse coverage, strong gradients, and mesoscale eddies may limit forecast performance. Mean-flow estimates use training data only and require the documented constant-velocity fallback in unsupported areas.
5. Drogue loss can introduce wind-driven slip; results will be examined by drogue status.
6. Requiring complete input history and valid target positions excludes some tracks. Report sample losses and coverage so this selection is visible.
7. Acceleration is derived from velocity differences, and heading and turning can be unstable at low speeds. Interpolation, measurement noise, and smoothing can therefore change the apparent motion regimes. Report the low-speed rule and check sensitivity to the descriptor definitions using development data.
8. Speed, acceleration, turning, location, and environmental forcing can be correlated. The primary models do not incorporate resolved wind, wave, or evolving current fields, so larger errors cannot be attributed uniquely to a kinematic variable or interpreted causally.
9. The number of independent drifters in extreme-motion groups may be small even when the number of hourly records is large. Freeze primary group definitions before testing, report uncertainty, and treat additional subgroup searches as exploratory. Results apply to the tested models and sample, not to every drifter forecasting method.

### References

- Aksamit, N. O., Sapsis, T. P., & Haller, G. (2020). Machine-learning mesoscale and submesoscale surface dynamics from Lagrangian ocean drifter trajectories. *Journal of Physical Oceanography, 50*(5), 1179–1196. <https://doi.org/10.1175/JPO-D-19-0238.1>
- Elipot, S., Lumpkin, R., Perez, R. C., Lilly, J. M., Early, J. J., & Sykulski, A. M. (2016). A global surface drifter data set at hourly resolution. *Journal of Geophysical Research: Oceans, 121*, 2937–2966. <https://doi.org/10.1002/2016JC011716>
- Elipot, S., Sykulski, A., Lumpkin, R., Centurioni, L., & Pazos, M. (2022). A dataset of hourly sea surface temperature from drifting buoys. *Scientific Data, 9*, 567. <https://doi.org/10.1038/s41597-022-01670-2>
- Grossi, M. D., Jegelka, S., Lermusiaux, P. F. J., & Özgökmen, T. M. (2025). Surface drifter trajectory prediction in the Gulf of Mexico using neural networks. *Ocean Modelling, 196*, 102543. <https://doi.org/10.1016/j.ocemod.2025.102543>
- Lin, G., Xu, X., Yu, C., & Wang, Z. (2026). [Leakage-controlled benchmarking of kinematic and machine-learning models for ten-minute buoy drift forecasts](https://doi.org/10.3389/fmars.2026.1966411). *Frontiers in Marine Science, 13*, 1966411.
- NOAA Global Drifter Program. Hourly location, current velocity, and temperature collected from Global Drifter Program drifters world-wide, version 2.01. <https://doi.org/10.25921/x46c-3620> (accessed 21 September 2026).

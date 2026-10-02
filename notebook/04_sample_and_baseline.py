import glob
import pandas as pd
import numpy as np

# Load the four pre‑processed parquet datasets
file_paths = glob.glob("../data/processed/gulf_stream_q3_*.parquet")
print("Detected data files:", file_paths)

keep_columns = [
    "trajectory_id",
    "time",
    "lon",
    "lat",
    "ve",
    "vn",
    "drogue_status",
    "in_region"
]

data_frame_list = []
for file_path in file_paths:
    df_part = pd.read_parquet(file_path, columns=keep_columns)
    data_frame_list.append(df_part)

df_raw = pd.concat(data_frame_list, ignore_index=True)

print(f"\nMerge complete! Total observations: {df_raw.shape[0]}")
print(f"Number of unique drifters: {df_raw['trajectory_id'].nunique()}")
print("\nFirst 5 rows preview:")
print(df_raw.head())

# --------------------------
# Build 24‑hour forecast samples
# --------------------------
import matplotlib.pyplot as plt

# Ensure time column is datetime type
df_raw["time"] = pd.to_datetime(df_raw["time"])

sample_list = []
forecast_hours = 24

# Process each drifter trajectory separately
for traj_id, group in df_raw.groupby("trajectory_id"):
    group = group.sort_values("time").reset_index(drop=True)
    n_points = len(group)

    for i in range(n_points - forecast_hours):
        current = group.iloc[i]
        future = group.iloc[i + forecast_hours]

        sample = {
            "trajectory_id": traj_id,
            "time_current": current["time"],
            "lon_current": current["lon"],
            "lat_current": current["lat"],
            "ve_current": current["ve"],
            "vn_current": current["vn"],
            "lon_true_24h": future["lon"],
            "lat_true_24h": future["lat"]
        }
        sample_list.append(sample)

samples_df = pd.DataFrame(sample_list)
print(f"\nTotal constructed forecast samples: {len(samples_df)}")

# Save samples locally, DO NOT push this file to GitHub
samples_df.to_parquet("../data/processed/forecast_samples.parquet", index=False)
print("Samples saved locally to ../data/processed/forecast_samples.parquet")

# --------------------------
# Persistence Baseline Model
# Persistence: assume position does not change over 24h
# --------------------------
samples_df["lon_pred_persistence"] = samples_df["lon_current"]
samples_df["lat_pred_persistence"] = samples_df["lat_current"]

# Calculate absolute position errors (degrees)
samples_df["lon_error"] = samples_df["lon_pred_persistence"] - samples_df["lon_true_24h"]
samples_df["lat_error"] = samples_df["lat_pred_persistence"] - samples_df["lat_true_24h"]

samples_df["pos_error_deg"] = np.sqrt(samples_df["lon_error"] ** 2 + samples_df["lat_error"] ** 2)

# Summary metrics
mean_pos_error = samples_df["pos_error_deg"].mean()
median_pos_error = samples_df["pos_error_deg"].median()

print("\n======== Persistence Baseline Result (24‑hour forecast) ========")
print(f"Mean position error (degrees):   {mean_pos_error:.4f}")
print(f"Median position error (degrees): {median_pos_error:.4f}")

# Plot error histogram and save to image folder
plt.figure(figsize=(8, 5))
plt.hist(samples_df["pos_error_deg"], bins=80, range=(0, 2.0), alpha=0.7)
plt.title("Persistence Baseline: 24‑h Position Error Distribution")
plt.xlabel("Position Error (degrees)")
plt.ylabel("Count")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("../image/persistence_24h_error.png", dpi=150)
plt.close()
print("\nError plot saved to ../image/persistence_24h_error.png")

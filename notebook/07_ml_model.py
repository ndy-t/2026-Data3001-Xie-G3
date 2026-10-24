import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


data_dir = Path("../data/processed")
periods = ["2007_2010", "2011_2014", "2015_2018", "2019_2022"]
dfs = []

for period in periods:
    fp = data_dir / f"gulf_stream_q3_{period}.parquet"
    dfp = pd.read_parquet(fp)
    dfp["study_period"] = period.replace("_", "-")
    dfs.append(dfp)
df_raw = pd.concat(dfs, ignore_index=True)


df_raw = df_raw.sort_values(["trajectory_id", "time"]).reset_index(drop=True)
df_raw["lon_next24"] = df_raw.groupby("trajectory_id")["lon"].shift(-1)
df_raw["lat_next24"] = df_raw.groupby("trajectory_id")["lat"].shift(-1)
df_raw["d_lon"] = df_raw.groupby("trajectory_id")["lon"].diff()
df_raw["d_lat"] = df_raw.groupby("trajectory_id")["lat"].diff()

sample_df = df_raw.dropna(subset=["lon_next24", "lat_next24"]).copy()
print(f"Loaded total forecast samples: {len(sample_df)}")


err_per = np.sqrt((sample_df["lon"] - sample_df["lon_next24"]) ** 2 + (sample_df["lat"] - sample_df["lat_next24"]) ** 2)
mean_err_per = np.mean(err_per)
median_err_per = np.median(err_per)


adv_sample = sample_df.dropna(subset=["d_lon","d_lat"]).copy()
adv_pred_lon = adv_sample["lon"] + adv_sample["d_lon"]
adv_pred_lat = adv_sample["lat"] + adv_sample["d_lat"]
err_adv = np.sqrt((adv_pred_lon - adv_sample["lon_next24"]) ** 2 + (adv_pred_lat - adv_sample["lat_next24"]) ** 2)
mean_err_adv = np.mean(err_adv)
median_err_adv = np.median(err_adv)


features = ["lon", "lat"]
X = sample_df[features]
y = sample_df[["lon_next24", "lat_next24"]]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, shuffle=True
)
print("\n======= Training Linear Regression =======")
lr = LinearRegression()
lr.fit(X_train, y_train)
y_pred_lr = lr.predict(X_test)
err_lr = np.sqrt(
    (y_pred_lr[:,0] - y_test["lon_next24"].values)**2
    + (y_pred_lr[:,1] - y_test["lat_next24"].values)**2
)
mean_err_lr = np.mean(err_lr)
median_err_lr = np.median(err_lr)


print("======= Model Summary =======")
print(f"Persistence:        mean={mean_err_per:.4f}, median={median_err_per:.4f}")
print(f"Constant Advection: mean={mean_err_adv:.4f}, median={median_err_adv:.4f}")
print(f"Linear Regression:  mean={mean_err_lr:.4f}, median={median_err_lr:.4f}")


plt.figure(figsize=(8,5))
names = ["Persistence", "Constant Advection", "Linear Regression"]
mean_errors = [mean_err_per, mean_err_adv, mean_err_lr]
plt.bar(names, mean_errors, color=["#4472C4","#5B9BD5","#70AD47"])
plt.ylabel("Mean position error (degrees)")
plt.title("24h Forecast Error Comparison (3 Models)")
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
out_img = Path("../image/three_model_comparison.png")
plt.savefig(out_img, dpi=300)
plt.close()
print(f"\nComparison figure saved to {out_img}")

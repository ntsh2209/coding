import pandas as pd
import numpy as np

def validate_basic_stats(df):
    stats = {
        "columns": list(df.columns),
        "null_counts": df.isnull().sum().to_dict(),
        "unique_counts": df.nunique().to_dict(),
        "data_types": df.dtypes.apply(str).to_dict(),
        "row_count": len(df)
    }
    return stats

def detect_price_volume_jumps(df, threshold=0.05):
    jump_records = []

    for sedol, group in df.groupby("sedol"):
        group = group.sort_values("date")
        group["price_change_pct"] = group["closePrice"].pct_change()
        group["vol_change_pct"] = group["vol"].pct_change()

        jumps = group[(group["price_change_pct"].abs() > threshold) |
                      (group["vol_change_pct"].abs() > threshold)]

        if not jumps.empty:
            for _, row in jumps.iterrows():
                jump_records.append({
                    "date": row["date"],
                    "sedol": sedol,
                    "price_change_pct": row["price_change_pct"],
                    "vol_change_pct": row["vol_change_pct"]
                })

    return pd.DataFrame(jump_records)

def compare_with_golden(df_raw, df_golden, threshold=0.05):
    df = df_raw.merge(df_golden, on=["date", "sedol"], suffixes=("", "_golden"))
    df["price_delta_pct"] = ((df["closePrice"] - df["closePrice_golden"]).abs() /
                             df["closePrice_golden"])

    df["is_large_delta"] = df["price_delta_pct"] > threshold

    delta_stats = {
        "max_delta_pct": df["price_delta_pct"].max(),
        "mean_delta_pct": df["price_delta_pct"].mean(),
        "95th_percentile": np.percentile(df["price_delta_pct"], 95),
        "num_deltas_gt_5pct": df["is_large_delta"].sum()
    }

    delta_rows = df[df["is_large_delta"]][["date", "sedol", "closePrice", "closePrice_golden", "price_delta_pct"]]

    return delta_stats, delta_rows

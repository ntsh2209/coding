import pandas as pd
from validator_simple import validate_basic_stats, detect_price_volume_jumps, compare_with_golden

df_raw = pd.read_csv("data/raw_data.csv")
df_golden = pd.read_csv("data/golden_data.csv")

# 1. Basic stats
stats = validate_basic_stats(df_raw)
print("🔍 Basic Stats:", stats)

# 2. Price/volume jumps
jumps = detect_price_volume_jumps(df_raw)
print("📈 Detected Jumps:\n", jumps)

# 3. Compare with golden
delta_stats, delta_rows = compare_with_golden(df_raw, df_golden)
print("📊 Golden Comparison Stats:", delta_stats)
print("⚠️  Rows with >5% delta:\n", delta_rows)

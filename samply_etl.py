quant_pipeline/
├── config/
│   └── params.toml
├── data/
│   ├── input/
│   │   └── sedols.csv
│   ├── output/
│   └── cache/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── logger.py
│   ├── dq.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── sedol_loader.py
│   │   ├── cache.py
│   │   ├── kdb_client.py
│   │   ├── parallel.py
│   │   └── dates.py
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── adjust_data.py
│   │   ├── calculate_metrics.py
│   │   └── postprocess.py
│   └── viz/
│       ├── __init__.py
│       ├── generate_plots.py
│       └── output_tables.py
├── tests/
│   └── test_placeholder.py
├── requirements.txt
├── README.md
└── .gitignore

# config/params.toml
[dates]
analysis_date = "2024-12-31"
start_date = "2024-01-01"
end_date = "2024-12-31"

[flags]
readFromCache = true

# requirements.txt
pandas
pykx
pyyaml
matplotlib
seaborn
plotly
toml

# src/main.py
from src.config import load_config
from src.logger import setup_logger
from src.utils.sedol_loader import load_sedol_csv
from src.utils.parallel import parallel_q_calls
from src.processing.adjust_data import adjust_missing_data
from src.processing.calculate_metrics import calculate_rolling_metrics
from src.viz.output_tables import save_output_tables
from src.viz.generate_plots import generate_all_plots
from src.dq import dq_checks


def main():
    config = load_config("config/params.toml")
    setup_logger()

    sedols = load_sedol_csv("data/input/sedols.csv")
    dq_checks(sedols)

    results = parallel_q_calls(sedols, config)
    data = adjust_missing_data(results)
    metrics = calculate_rolling_metrics(data, config)

    save_output_tables(metrics)
    generate_all_plots(metrics)


if __name__ == "__main__":
    main()

# src/logger.py
import logging

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

# src/config.py
import toml

def load_config(path):
    with open(path, 'r') as f:
        return toml.load(f)

# src/utils/sedol_loader.py
import pandas as pd

def load_sedol_csv(path):
    df = pd.read_csv(path)
    df.drop_duplicates(inplace=True)
    return df

# src/utils/parallel.py
import pandas as pd
from multiprocessing import Pool, cpu_count
from functools import partial
from src.utils.kdb_client import fetch_data_from_kdb

def split_dataframe(df, num_chunks):
    chunk_size = len(df) // num_chunks
    return [df.iloc[i:i + chunk_size].reset_index(drop=True) for i in range(0, len(df), chunk_size)]

def worker(chunk, config):
    return fetch_data_from_kdb(chunk, config)

def parallel_q_calls(df, config, num_chunks=20):
    chunks = split_dataframe(df, num_chunks)
    with Pool(min(num_chunks, cpu_count())) as pool:
        results = pool.map(partial(worker, config=config), chunks)
    return pd.concat(results, ignore_index=True)

# src/utils/kdb_client.py
import pykx as kx
import hashlib
import os
import pandas as pd
from src.utils.cache import load_from_cache, save_to_cache

# Example connection setup
q = kx.QConnection("localhost", 5000)

def get_cache_key(df, config):
    hash_input = df.to_csv(index=False) + str(config['dates'])
    return hashlib.md5(hash_input.encode()).hexdigest()

def fetch_data_from_kdb(df, config):
    if config['flags']['readFromCache']:
        key = get_cache_key(df, config)
        cached = load_from_cache(key)
        if cached is not None:
            return cached

    # Simulated Q call
    result = q("select from my_table where sedol in $", df['sedol'].tolist())
    pdf = result.py()

    key = get_cache_key(df, config)
    save_to_cache(pdf, key)
    return pdf

# src/utils/cache.py
import os
import pandas as pd

def get_cache_path(key):
    return f"data/cache/{key}.parquet"

def load_from_cache(key):
    path = get_cache_path(key)
    if os.path.exists(path):
        return pd.read_parquet(path)
    return None

def save_to_cache(df, key):
    path = get_cache_path(key)
    df.to_parquet(path)

# src/dq.py

def dq_checks(df):
    assert 'sedol' in df.columns, "Missing 'sedol' column"
    assert df['sedol'].notnull().all(), "Null values found in sedol"

# src/processing/adjust_data.py

def adjust_missing_data(df):
    df.fillna(method='ffill', inplace=True)
    return df

# src/processing/calculate_metrics.py
import pandas as pd

def calculate_rolling_metrics(df, config):
    df['rolling_avg'] = df['price'].rolling(window=5).mean()
    return df

# src/viz/output_tables.py
import pandas as pd

def save_output_tables(df):
    df.to_csv("data/output/final_output.csv", index=False)

# src/viz/generate_plots.py
import matplotlib.pyplot as plt

def generate_all_plots(df):
    plt.figure(figsize=(10, 5))
    df.groupby('date')['price'].mean().plot()
    plt.title("Average Price Over Time")
    plt.savefig("data/output/price_plot.png")
    plt.close()

# tests/test_placeholder.py
def test_example():
    assert True

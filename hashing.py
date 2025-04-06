import hashlib
import os
import pandas as pd
import pykx as kx

class KDBClientWithParquetCache:
    def __init__(self, q_connection: kx.QConnection, cache_dir: str = "./kdb_cache"):
        self.q = q_connection
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def _serialize_for_hashing(self, arg):
        """Serialize arg into a consistent string representation for hashing."""
        if isinstance(arg, pd.DataFrame):
            return arg.sort_index(axis=1).to_csv(index=False)
        return str(arg)

    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Create a unique hash key based on function name and all arguments (including DataFrame contents)."""
        serialized_parts = [func_name] + [self._serialize_for_hashing(arg) for arg in args]
        serialized_parts += [f"{k}={self._serialize_for_hashing(v)}" for k, v in sorted(kwargs.items())]
        joined = "|".join(serialized_parts)
        return hashlib.md5(joined.encode("utf-8")).hexdigest()

    def _get_cache_file_path(self, cache_key: str) -> str:
        return os.path.join(self.cache_dir, f"{cache_key}.parquet")

    def call_with_cache(self, func_name: str, *args, **kwargs) -> pd.DataFrame:
        """
        Calls the KDB function with caching and stores results as Parquet.
        
        Parameters:
            func_name (str): KDB function name
            *args: Positional arguments (e.g., DataFrames, scalars)
            **kwargs: Keyword arguments (used only for hashing)
        
        Returns:
            pd.DataFrame: The result from KDB or cache
        """
        cache_key = self._generate_cache_key(func_name, args, kwargs)
        cache_path = self._get_cache_file_path(cache_key)

        if os.path.exists(cache_path):
            print(f"Cache hit: loading from {cache_path}")
            return pd.read_parquet(cache_path)

        # Convert DataFrames to kx.Table for KDB call
        kdb_args = [kx.Table(arg) if isinstance(arg, pd.DataFrame) else arg for arg in args]

        result = self.q(func_name, *kdb_args)

        # Convert result to DataFrame
        df = result.py() if isinstance(result, (kx.Table, kx.Dictionary)) else pd.DataFrame()

        df.to_parquet(cache_path, index=False)
        print(f"Cache miss: called KDB function '{func_name}', saved to {cache_path}")
        return df

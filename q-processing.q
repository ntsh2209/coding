# src/pipeline/data_pipeline.py
import pandas as pd
from src.dq import dq_checks
from src.utils.sedol_loader import load_sedol_csv
from src.utils.kdb_client import run_q_script_with_data

def data_gathering_pipeline(sedol_csv_path: str, config: dict) -> pd.DataFrame:
    """
    Full pipeline to read SEDOLs, pass entire table to a Q script, and return output.

    Args:
        sedol_csv_path: Path to the CSV containing SEDOLs
        config: Parsed TOML config as a dictionary

    Returns:
        pd.DataFrame: Final output returned from Q after complete processing
    """
    # Step 1: Load SEDOL list
    sedol_df = load_sedol_csv(sedol_csv_path)
    dq_checks(sedol_df)

    # Step 2: Call Q script with entire DataFrame and config
    result_df = run_q_script_with_data(sedol_df, config)

    return result_df


# src/utils/kdb_client.py (append this function)
import pykx as kx
import pandas as pd
import json

q = kx.QConnection("localhost", 5000)  # Adjust host/port if needed


def run_q_script_with_data(sedol_df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Sends full SEDOL table to a Q script and returns final result.

    Args:
        sedol_df: DataFrame with SEDOLs and metadata
        config: Configuration dict with date parameters

    Returns:
        pd.DataFrame: Final result from Q script
    """
    # Convert pandas to kx table
    q_table = kx.toq(sedol_df)

    # Send to Q environment as variable
    q["sedolTable"] = q_table
    q["startDate"] = config["dates"]["start_date"]
    q["endDate"] = config["dates"]["end_date"]
    q["analysisDate"] = config["dates"]["analysis_date"]

    # Load and execute Q script (assumed to process sedolTable and return finalTable)
    q("\n\n\n\n\n\n\n\n\n")  # Optional: clear previous defs
    q("\")  # ensure clean load
    q("\l scripts/data_processing.q")

    # Get final table back from Q
    final_result = q["finalTable"]
    return final_result.py() if isinstance(final_result, kx.Table) else pd.DataFrame()


# Q file: scripts/data_processing.q (simple placeholder)
/ scripts/data_processing.q
parseDates:{ [sd;ed;ad] .z.p:(-1)#.z.p; };  / just demo for resetting timer

processSedolTable:{
  / placeholder function - implement logic here
  update price:100.0 + til count sedolTable from sedolTable
};

finalTable: processSedolTable sedolTable;

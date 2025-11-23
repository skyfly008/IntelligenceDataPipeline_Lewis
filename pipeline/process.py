"""Process raw telemetry and write engineered parquet file.

Creates `data/processed_telemetry.parquet`.
"""
from pathlib import Path
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_CSV = DATA_DIR / "raw_telemetry.csv"
PROCESSED_PARQUET = DATA_DIR / "processed_telemetry.parquet"


def main(input_path: Path = RAW_CSV, output_path: Path = PROCESSED_PARQUET):
    if not input_path.exists():
        raise FileNotFoundError(f"Raw telemetry not found at {input_path}. Run ingest first.")
    logging.info("Reading raw telemetry from %s", input_path)
    df = pd.read_csv(input_path)

    # Parse timestamp robustly
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Drop rows without timestamp
    missing_ts = df["timestamp"].isna().sum()
    if missing_ts:
        logging.warning("Dropping %d rows with invalid timestamp", missing_ts)
        df = df.dropna(subset=["timestamp"]).copy()

    # Sort and compute diffs grouped by flight
    df = df.sort_values(["flight_id", "timestamp"]).reset_index(drop=True)

    # Ensure numeric columns are numeric
    for col in ["speed", "altitude"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["speed_diff"] = df.groupby("flight_id")["speed"].diff().fillna(0)
    df["altitude_diff"] = df.groupby("flight_id")["altitude"].diff().fillna(0)

    # Fill any remaining numeric NaNs with 0 for downstream modeling
    df["speed_diff"] = df["speed_diff"].fillna(0)
    df["altitude_diff"] = df["altitude_diff"].fillna(0)

    # Write parquet
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    logging.info("Writing processed telemetry to %s", output_path)
    df.to_parquet(output_path, index=False)

def run_process(input_path: Path = RAW_CSV, output_path: Path = PROCESSED_PARQUET) -> Path:
    """Run processing end-to-end and return the output parquet Path."""
    main(input_path=input_path, output_path=output_path)
    return output_path


def _cli():
    import argparse

    parser = argparse.ArgumentParser(description="Process raw telemetry into engineered parquet")
    parser.add_argument("--input", "-i", type=str, default=str(RAW_CSV), help="Input CSV path")
    parser.add_argument("--output", "-o", type=str, default=str(PROCESSED_PARQUET), help="Output parquet path")
    args = parser.parse_args()
    run_process(input_path=Path(args.input), output_path=Path(args.output))


if __name__ == "__main__":
    _cli()

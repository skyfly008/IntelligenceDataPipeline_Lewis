import pandas as pd
from pathlib import Path
import pipeline.ingest as ingest
import pipeline.process as process


def test_process_creates_parquet_and_features(tmp_path: Path):
    csv = tmp_path / "raw_telemetry.csv"
    parquet = tmp_path / "processed_telemetry.parquet"
    ingest.main(output_path=csv, n_flights=3, points_per_flight=5)
    process.main(input_path=csv, output_path=parquet)
    assert parquet.exists()
    df = pd.read_parquet(parquet)
    # features exist
    assert "speed_diff" in df.columns
    assert "altitude_diff" in df.columns
    # check sorting: timestamps per flight_id must be non-decreasing
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    for fid, g in df.groupby("flight_id"):
        assert g["timestamp"].is_monotonic_increasing

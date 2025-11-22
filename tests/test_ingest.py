import pandas as pd
from pathlib import Path
import pipeline.ingest as ingest


def test_ingest_creates_csv(tmp_path: Path):
    out = tmp_path / "raw_telemetry.csv"
    ingest.main(output_path=out, n_flights=2, points_per_flight=10)
    assert out.exists()
    df = pd.read_csv(out)
    expected_cols = {"timestamp", "flight_id", "lat", "lon", "altitude", "speed", "heading", "status", "is_anomaly"}
    assert expected_cols.issubset(set(df.columns))
    # quick sanity: number of rows == 20
    assert df.shape[0] == 2 * 10

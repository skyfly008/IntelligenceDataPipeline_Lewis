import pandas as pd
from pathlib import Path
import pipeline.ingest as ingest
import pipeline.process as process
import pipeline.model as model


def test_model_writes_db_and_columns(tmp_path: Path):
    csv = tmp_path / "raw_telemetry.csv"
    parquet = tmp_path / "processed_telemetry.parquet"
    db = tmp_path / "intel.db"
    ingest.main(output_path=csv, n_flights=4, points_per_flight=10)
    process.main(input_path=csv, output_path=parquet)
    model.main(input_path=parquet, db_path=db, table_name="telemetry_anomalies", contamination=0.05)
    assert db.exists()
    # read table
    df = pd.read_sql_table("telemetry_anomalies", f"sqlite:///{db}")
    assert "model_is_anomaly" in df.columns
    assert "anomaly_score" in df.columns
    # model_is_anomaly should be 0/1
    vals = set(df["model_is_anomaly"].unique().tolist())
    assert vals.issubset({0, 1})

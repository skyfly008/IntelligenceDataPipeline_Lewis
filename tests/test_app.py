import importlib
from pathlib import Path
import pandas as pd
from fastapi.testclient import TestClient
import pipeline.ingest as ingest
import pipeline.process as process
import pipeline.model as model


def test_app_endpoints_empty_db(tmp_path: Path):
    # Import app module and patch DATA_DIR/DB_PATH to tmp_path
    import app.main as m
    m.DATA_DIR = tmp_path
    m.DB_PATH = tmp_path / "intel.db"

    client = TestClient(m.app)
    r = client.get("/api/anomalies")
    assert r.status_code == 200
    j = r.json()
    assert "anomalies" in j and isinstance(j["anomalies"], list)

    r2 = client.get("/")
    assert r2.status_code == 200
    assert "Telemetry Anomalies" in r2.text


def test_app_with_data(tmp_path: Path):
    csv = tmp_path / "raw_telemetry.csv"
    parquet = tmp_path / "processed_telemetry.parquet"
    db = tmp_path / "intel.db"

    ingest.main(output_path=csv, n_flights=3, points_per_flight=8)
    process.main(input_path=csv, output_path=parquet)
    model.main(input_path=parquet, db_path=db, table_name="telemetry_anomalies", contamination=0.05)

    import app.main as m
    m.DATA_DIR = tmp_path
    m.DB_PATH = db

    client = TestClient(m.app)
    r = client.get("/api/anomalies")
    assert r.status_code == 200
    j = r.json()
    assert "anomalies" in j
    # even if no anomalies were detected, response shape should be correct
    assert "count" in j

    r2 = client.get("/")
    assert r2.status_code == 200
    assert "Telemetry Anomalies" in r2.text

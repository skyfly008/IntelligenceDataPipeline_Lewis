"""Train an anomaly detection model and write scored results to SQLite.

Creates `data/intel.db` with table `telemetry_anomalies`.
"""
from pathlib import Path
import pandas as pd
import logging
from sklearn.ensemble import IsolationForest
from sqlalchemy import create_engine

logging.basicConfig(level=logging.INFO)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PROCESSED_PARQUET = DATA_DIR / "processed_telemetry.parquet"
SQLITE_DB = DATA_DIR / "intel.db"


def main(input_path: Path = PROCESSED_PARQUET, db_path: Path = SQLITE_DB, table_name: str = "telemetry_anomalies", contamination: float = 0.02):
    if not input_path.exists():
        raise FileNotFoundError(f"Processed data not found at {input_path}. Run process first.")
    logging.info("Reading processed telemetry from %s", input_path)
    df = pd.read_parquet(input_path)

    numeric_cols = [c for c in ["lat", "lon", "altitude", "speed", "heading", "speed_diff", "altitude_diff"] if c in df.columns]
    if not numeric_cols:
        raise ValueError("No numeric columns found for modeling.")

    X = df[numeric_cols].copy()
    # Fill NaNs with median
    X = X.fillna(X.median())

    logging.info("Training IsolationForest on %d rows and %d features", X.shape[0], X.shape[1])
    model = IsolationForest(n_estimators=100, contamination=contamination, random_state=42)
    model.fit(X)
    labels = model.predict(X)
    scores = model.decision_function(X)

    df = df.copy()
    df["model_label"] = labels
    df["anomaly_score"] = scores
    df["model_is_anomaly"] = (df["model_label"] == -1).astype(int)

    # Write to SQLite
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}")
    logging.info("Writing scored telemetry to %s (table: %s)", db_path, table_name)
    df.to_sql(table_name, engine, if_exists="replace", index=False)


def run_model(input_path: Path = PROCESSED_PARQUET, db_path: Path = SQLITE_DB, table_name: str = "telemetry_anomalies", contamination: float = 0.02) -> Path:
    """Train model on processed parquet and write scored results to SQLite. Returns the DB path."""
    main(input_path=input_path, db_path=db_path, table_name=table_name, contamination=contamination)
    return db_path


def _cli():
    import argparse

    parser = argparse.ArgumentParser(description="Train anomaly model and write to SQLite")
    parser.add_argument("--input", "-i", type=str, default=str(PROCESSED_PARQUET), help="Input parquet path")
    parser.add_argument("--db", "-d", type=str, default=str(SQLITE_DB), help="SQLite DB path")
    parser.add_argument(
        "--contamination",
        "-c",
        type=float,
        default=0.02,
        help="Contamination fraction for IsolationForest",
    )
    args = parser.parse_args()
    main(input_path=Path(args.input), db_path=Path(args.db), contamination=args.contamination)


if __name__ == "__main__":
    _cli()
 

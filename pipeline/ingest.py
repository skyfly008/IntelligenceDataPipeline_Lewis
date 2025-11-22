"""Generate synthetic aircraft telemetry and write to CSV.

Creates `data/raw_telemetry.csv`.
"""
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
import logging

logging.basicConfig(level=logging.INFO)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
RAW_CSV = DATA_DIR / "raw_telemetry.csv"


def generate_flight(flight_id: str, start_time: datetime, n_points: int, seed: int = None):
    rng = np.random.default_rng(seed)
    # base positions
    lat0 = 37.0 + rng.normal(0, 0.5)
    lon0 = -122.0 + rng.normal(0, 0.5)
    altitude0 = 30000 + rng.normal(0, 500)
    speed0 = 450 + rng.normal(0, 10)

    timestamps = [start_time + timedelta(seconds=10 * i) for i in range(n_points)]
    lats = lat0 + np.cumsum(rng.normal(0, 0.0015, size=n_points))
    lons = lon0 + np.cumsum(rng.normal(0, 0.0015, size=n_points))
    altitudes = altitude0 + np.cumsum(rng.normal(0, 5, size=n_points))
    speeds = speed0 + np.cumsum(rng.normal(0, 1.5, size=n_points))
    headings = (rng.uniform(0, 360, size=n_points)).round(1)

    df = pd.DataFrame({
        "timestamp": timestamps,
        "flight_id": [flight_id] * n_points,
        "lat": lats,
        "lon": lons,
        "altitude": altitudes,
        "speed": speeds,
        "heading": headings,
        "status": ["OK"] * n_points,
        "is_anomaly": [0] * n_points,
    })

    # Inject a few synthetic anomalies
    n_anom = max(1, n_points // 100)
    anom_idx = rng.choice(n_points, size=n_anom, replace=False)
    for i in anom_idx:
        if rng.random() < 0.6:
            # spike speed
            df.loc[i, "speed"] = df.loc[i, "speed"] * (1 + rng.uniform(1.5, 3.0))
            df.loc[i, "status"] = "SPEED_SPIKE"
        else:
            # altitude drop
            df.loc[i, "altitude"] = df.loc[i, "altitude"] - rng.uniform(5000, 15000)
            df.loc[i, "status"] = "ALT_DROP"
        df.loc[i, "is_anomaly"] = 1

    return df


def main(output_path: Path = RAW_CSV, n_flights: int = 5, points_per_flight: int = 200):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    logging.info("Generating synthetic telemetry")
    rows = []
    base_time = datetime.now(timezone.utc)
    for i in range(n_flights):
        flight_id = f"FLIGHT_{i+1:03d}"
        # staggering start times
        st = base_time + timedelta(minutes=5 * i)
        rows.append(generate_flight(flight_id, st, points_per_flight, seed=42 + i))

    df = pd.concat(rows, ignore_index=True)
    # Make deterministic ordering before saving
    df = df.sort_values(["flight_id", "timestamp"]).reset_index(drop=True)
    df.to_csv(output_path, index=False)
    logging.info("Wrote raw telemetry to %s", output_path)


def _cli():
    import argparse

    parser = argparse.ArgumentParser(description="Generate synthetic telemetry CSV")
    parser.add_argument("--num-flights", "-n", type=int, default=5, help="Number of flights to generate")
    parser.add_argument(
        "--points-per-flight",
        "-p",
        type=int,
        default=200,
        help="Number of telemetry points per flight",
    )
    parser.add_argument("--output", "-o", type=str, default=str(RAW_CSV), help="Output CSV path")
    args = parser.parse_args()
    main(output_path=Path(args.output), n_flights=args.num_flights, points_per_flight=args.points_per_flight)


if __name__ == "__main__":
    _cli()


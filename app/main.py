"""FastAPI web app exposing telemetry anomalies and a simple dashboard."""
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd
from sqlalchemy import create_engine, inspect
import logging

logging.basicConfig(level=logging.INFO)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "intel.db"
TABLE_NAME = "telemetry_anomalies"

app = FastAPI(title="Intel Data Pipeline")
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[0] / "templates"))

# mount static files
app.mount("/static", StaticFiles(directory=str(Path(__file__).resolve().parents[0] / "static")), name="static")


def get_engine():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
    return engine


@app.get("/api/anomalies")
def api_anomalies(limit: int = 100):
    engine = get_engine()
    inspector = inspect(engine)
    if TABLE_NAME not in inspector.get_table_names():
        return JSONResponse(content={"anomalies": [], "count": 0})

    df = pd.read_sql_table(TABLE_NAME, engine)
    if df.empty:
        return JSONResponse(content={"anomalies": [], "count": 0})

    if "anomaly_score" in df.columns:
        df = df.sort_values("anomaly_score", ascending=True)

    anomalies = df[df.get("model_is_anomaly", 0) == 1]
    # Convert timestamp to ISO strings for JSON
    if "timestamp" in anomalies.columns:
        anomalies = anomalies.copy()
        anomalies["timestamp"] = anomalies["timestamp"].astype(str)
    anomalies = anomalies.head(limit)
    return JSONResponse(content={"anomalies": anomalies.to_dict(orient="records"), "count": int(anomalies.shape[0])})


@app.get("/")
def index(request: Request, limit: int = 200):
    engine = get_engine()
    inspector = inspect(engine)
    rows = []
    total = 0
    n_anom = 0
    if TABLE_NAME in inspector.get_table_names():
        df = pd.read_sql_table(TABLE_NAME, engine)
        total = int(df.shape[0])
        if total > 0:
            n_anom = int(df.get("model_is_anomaly", pd.Series([])).sum())
            df = df.sort_values("anomaly_score", ascending=True) if "anomaly_score" in df.columns else df
            rows_df = df.head(limit).copy()
            if "timestamp" in rows_df.columns:
                rows_df["timestamp"] = rows_df["timestamp"].astype(str)
            rows = rows_df.to_dict(orient="records")

    pct = (n_anom / total * 100) if total else 0.0
    stats = {"total": total, "n_anomalies": n_anom, "anomaly_pct": round(pct, 3)}
    # Use the newer TemplateResponse signature: (request, template_name, context)
    return templates.TemplateResponse(request, "index.html", {"rows": rows, "stats": stats})

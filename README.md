# Intel Data Pipeline (Synthetic Telemetry)

This project simulates an intelligence-style telemetry pipeline, performs anomaly detection with an IsolationForest, writes results to SQLite, and exposes a small FastAPI dashboard.

Quick start (Windows / PowerShell):

1. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

3. Run the pipeline (or use the helper)

```powershell
python run_pipeline.py
# or run steps individually:
python pipeline\ingest.py
python pipeline\process.py
python pipeline\model.py
```

4. Run the FastAPI server

```powershell
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/` for the dashboard and `http://127.0.0.1:8000/api/anomalies` for JSON.

Files of interest:
- `pipeline/ingest.py` — generate synthetic `data/raw_telemetry.csv`
- `pipeline/process.py` — compute `speed_diff`, `altitude_diff` and write `data/processed_telemetry.parquet`
- `pipeline/model.py` — train IsolationForest and write `data/intel.db` table `telemetry_anomalies`
- `app/main.py` — FastAPI app and Jinja2 template at `app/templates/index.html`

Running tests
---------------

This project includes pytest tests under the `tests/` folder. To run them:

```powershell
python -m pip install -r requirements.txt
python -m pip install pytest
pytest -q
```

Docker (optional)
-----------------

Build the Docker image:

```powershell
docker build -t intel-data-pipeline .
```

Run the container (exposes port 8000):

```powershell
docker run --rm -p 8000:8000 intel-data-pipeline
```

# Intelligence Data Pipeline
Language: Python 3.11

Backend: FastAPI

Data: Pandas, SQLite, Parquet

ML: scikit-learn (IsolationForest)

Testing: pytest, FastAPI TestClient

CI/CD: GitHub Actions

Frontend: Jinja2 templates + CSS

# Intel-Style Telemetry Pipeline & Anomaly Detection

[![CI](https://github.com/skyfly008/IntelligenceDataPipeline_Lewis/actions/workflows/tests.yml/badge.svg)](https://github.com/<YOUR_USERNAME>/<REPO_NAME>/actions)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-green)](https://fastapi.tiangolo.com/)

A self-contained **intelligence-style data pipeline** that:

- Generates synthetic **aircraft telemetry**
- Performs **feature engineering** and **anomaly detection**
- Stores scored results in **SQLite**
- Exposes a **FastAPI** JSON API and an **HTML dashboard** for interactive analysis
- Includes **tests** and **GitHub Actions CI**

Designed to look and feel like the kind of telemetry / anomaly analysis tooling used in **defense, aerospace, and national security** environments.

---

## Features

- Synthetic multi-flight telemetry generator (lat, lon, altitude, speed, heading, status)
- Processing & feature engineering (`speed_diff`, `altitude_diff`, etc.)
- IsolationForest-based anomaly detection with configurable contamination
- Results stored in a local SQLite DB (`intel.db`, git-ignored)
- FastAPI backend:
  - `GET /` – HTML dashboard with anomaly highlighting
  - `GET /api/anomalies` – JSON list of detected anomalies
- Pytest-based tests for:
  - Ingestion
  - Processing
  - Modeling
  - API routes
- GitHub Actions CI to run tests on push/PR
- `.gitignore` configured to **exclude all data files** (`data/*.db`, `*.csv`, `*.parquet`)

---

## Architecture

```text
+-------------------+       +------------------+       +------------------------+
|  ingest.py        |       |  process.py      |       |  model.py              |
|  Generate         | ----> |  Clean &         | ----> |  Train IsolationForest |
|  raw_telemetry.csv|       |  Feature-Engineer|       |  Score anomalies       |
+-------------------+       +------------------+       +------------------------+
                                                                |
                                                                v
                                                        +----------------+
                                                        |  intel.db      |
                                                        |  telemetry_    |
                                                        |  anomalies     |
                                                        +----------------+
                                                                |
                                      +-------------------------+----------------------+
                                      |                                                |
                                      v                                                v
                            +-------------------+                           +---------------------+
                            |  FastAPI UI (/)   |                           | FastAPI JSON API    |
                            |  HTML Dashboard   |                           | /api/anomalies      |
                            +-------------------+                           +---------------------+



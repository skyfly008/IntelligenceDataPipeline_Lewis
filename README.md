# Intel-Style Telemetry Pipeline & Anomaly Detection

A self-contained, **intelligence-style data pipeline** that:

- Generates **synthetic aircraft telemetry** for multiple flights
- Performs **feature engineering** and **IsolationForest-based anomaly detection**
- Stores scored results in **SQLite**
- Exposes:
  - a **FastAPI JSON API** for anomalies
  - an **HTML dashboard** that highlights anomalous rows
- Includes **pytest tests** and **GitHub Actions CI**

Designed to resemble the kind of telemetry / anomaly tooling used in **defense, aerospace, and national security** environments — but running entirely on synthetic data.

>  **Data & Security:**  
> All telemetry is **fully synthetic**. No real-world or sensitive data is used.  
> `data/*.db`, `*.csv`, and `*.parquet` are **ignored by git** and generated at runtime.

---

## Project Overview

This project simulates an end-to-end pipeline you might see in a monitoring or intel setting:

1. **Ingest** – generate synthetic telemetry for multiple flights over time.
2. **Process** – clean and feature-engineer the data (speed/altitude deltas).
3. **Model** – train an **IsolationForest** to detect anomalous behavior.
4. **Serve** – expose the results through a **FastAPI** app with:
   - `/` → HTML dashboard
   - `/api/anomalies` → JSON API

It’s deliberately small but engineered with “real project” practices:
- clear package layout
- tests
- CI workflow
- Dockerfile
- environment-agnostic paths

---

## Features

- **Synthetic telemetry generator**
  - Multiple `flight_id` values
  - Columns like: `timestamp`, `flight_id`, `lat`, `lon`, `altitude`, `speed`, `heading`, `status`
- **Feature engineering**
  - Per-flight `speed_diff`, `altitude_diff`
  - Sorted time series per flight
- **Anomaly detection**
  - IsolationForest (configurable contamination)
  - Outputs `anomaly_score`, `model_label`, and `model_is_anomaly` flags
- **Storage**
  - SQLite database at `data/intel.db`
  - Table: `telemetry_anomalies`
- **FastAPI app**
  - `GET /` – HTML dashboard with summary stats and anomaly highlighting
  - `GET /api/anomalies?limit=100` – top-N most anomalous rows as JSON
- **Tests & CI**
  - `tests/` for ingest, process, model, and app
  - GitHub Actions workflow runs pipeline + tests on push/PR
- **Docker support**
  - Dockerfile for containerized deployment

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
                            +--------------------------------------+-------------------------------+
                            |                                                                      |
                            v                                                                      v
                  +----------------------------+                                   +----------------------------+
                  |  FastAPI UI (GET /)        |                                   | FastAPI JSON API           |
                  |  HTML Dashboard + Summary  |                                   | GET /api/anomalies         |
                  +----------------------------+                                   +----------------------------+

```
## Tech Stack
Language: Python 3.11
Backend: FastAPI (+ Starlette)
Data: Pandas, SQLite, Parquet (PyArrow)
ML: scikit-learn (IsolationForest)
Frontend: Jinja2 templates + basic CSS
Testing: pytest, FastAPI TestClient
CI/CD: GitHub Actions
Containerization: Docker (optional)


## Quick Start (Windows / PowerShell)
### 1. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

### 2. Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

### 3. Run the data pipeline (end-to-end)
python run_pipeline.py
### or step-by-step:
python pipeline\ingest.py
python pipeline\process.py
python pipeline\model.py

### 4. Launch the FastAPI app
uvicorn app.main:app --reload

Dashboard → http://127.0.0.1:8000/
JSON API → http://127.0.0.1:8000/api/anomalies

## Running Tests
Tests live under tests/ and cover:
  -test_ingest.py – synthetic data generation
  -test_process.py – feature engineering and ordering
  -test_model.py – anomaly model + DB table existence
  -test_app.py – FastAPI routes and responses (using TestClient)
### In your activated venv
python -m pip install -r requirements.txt
python -m pip install pytest
pytest -q


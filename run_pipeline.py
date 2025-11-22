"""Convenience script to run ingest -> process -> model sequentially."""
import subprocess
import sys
from pathlib import Path


def run(cmd):
    print(f"Running: {' '.join(cmd)}")
    r = subprocess.run(cmd, check=False)
    if r.returncode != 0:
        print(f"Command failed: {' '.join(cmd)} (exit {r.returncode})")
        sys.exit(r.returncode)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run the ingest->process->model pipeline")
    parser.add_argument("--num-flights", "-n", type=int, default=5)
    parser.add_argument("--points-per-flight", "-p", type=int, default=200)
    parser.add_argument("--contamination", "-c", type=float, default=0.02)
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    py = sys.executable
    run([
        py,
        str(root / "pipeline" / "ingest.py"),
        "--num-flights",
        str(args.num_flights),
        "--points-per-flight",
        str(args.points_per_flight),
    ])
    run([py, str(root / "pipeline" / "process.py")])
    run([py, str(root / "pipeline" / "model.py"), "--contamination", str(args.contamination)])
    print("Pipeline completed.")


if __name__ == '__main__':
    main()

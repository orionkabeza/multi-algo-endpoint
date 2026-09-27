import json
import os
import threading
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename

from algorithms import ALGORITHMS
from models import Analysis, SessionLocal, init_db, save_analysis
from visualizer import TIME_BUDGET_S, measure, render

MAX_POINTS = 2000
DATA_DIR = Path(__file__).parent / "data"

app = Flask(__name__)
init_db()  # Initialize the database when the app starts
benchmark_lock = threading.Lock()


def clean(value):
    return value.strip().strip("'\"").strip()


def parse_int(name, raw):
    try:
        return int(clean(raw).replace(",", "").replace("_", ""))
    except ValueError:
        raise ValueError(f"'{name}' must be a whole number, got {raw!r}")


@app.get("/")
def index():
    return jsonify(
        message="Time complexity visualizer",
        usage="/analyze?algo=linear_search&step=10&n_max=10000",
        algorithms=sorted(ALGORITHMS),
    )


@app.get("/algorithms")
def list_algorithms():
    return jsonify({name: {"complexity": entry[2], "max_n": entry[3]} for name, entry in ALGORITHMS.items()})


@app.get("/analyze")
def analyze():
    raw_algo = request.args.get("algo")
    raw_step = request.args.get("step")
    raw_n_max = request.args.get("n_max")
    missing = [k for k, v in (("algo", raw_algo), ("step", raw_step), ("n_max", raw_n_max)) if v is None]
    if missing:
        return jsonify(error=f"missing query parameter(s): {', '.join(missing)}"), 400

    algo = clean(raw_algo).lower()
    if algo not in ALGORITHMS:
        return jsonify(error=f"unknown algo {algo!r}", supported=sorted(ALGORITHMS)), 400

    try:
        step = parse_int("step", raw_step)
        n_max = parse_int("n_max", raw_n_max)
    except ValueError as e:
        return jsonify(error=str(e)), 400

    n_min = 0
    if step < 1:
        return jsonify(error="'step' must be at least 1"), 400
    max_n = ALGORITHMS[algo][3]
    if not 0 <= n_max <= max_n:
        return jsonify(error=f"'n_max' for {algo} must be between 0 and {max_n:,} "
                             "(a single run above that would take too long)"), 400
    if n_max // step + 1 > MAX_POINTS:
        return jsonify(error=f"too many points ({n_max // step + 1}); raise 'step' or lower 'n_max' (limit {MAX_POINTS})"), 400

    with benchmark_lock:
        points, truncated = measure(algo, n_min, n_max, step)
        path, image_b64 = render(algo, points)

    result = {
        "algo": algo,
        "complexity": ALGORITHMS[algo][2],
        "n_min": n_min,
        "n_max": n_max,
        "step": step,
        "truncated": truncated,
        "points": [{"n": n, "seconds": s} for n, s in points],
        "snapshot_path": str(path),
        "image_format": "png",
        "image_base64": image_b64,
    }
    if truncated:
        result["note"] = (f"Stopped at n={points[-1][0]} after the {TIME_BUDGET_S}s time budget; "
                          "use a smaller n_max or a larger step to cover the full range.")
    save_analysis(result)
    return jsonify(result)
    

@app.post("/save")
def save_json():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify(error="request body must be valid JSON (Content-Type: application/json)"), 400

    raw_name = request.args.get("name")
    if raw_name is not None:
        name = secure_filename(raw_name)
        if not name:
            return jsonify(error=f"invalid 'name' {raw_name!r}"), 400
        if not name.endswith(".json"):
            name += ".json"
    else:
        name = f"data_{datetime.now():%Y%m%d_%H%M%S_%f}.json"

    DATA_DIR.mkdir(exist_ok=True)
    path = DATA_DIR / name
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return jsonify(saved_path=str(path), filename=name, data=payload), 201

@app.post("/save_analysis")
def save_analysis_endpoint():
    result = request.get_json(silent=True)
    if result is None:
        return jsonify(error="request body must be valid JSON (Content-Type: application/json)"), 400
    try:
        analysis_id = save_analysis(result)
    except KeyError as e:
        return jsonify(error=f"missing field {e}"), 400
    return jsonify(id=analysis_id), 201


@app.get("/analyses")
def list_analyses():
    with SessionLocal() as session:
        rows = session.query(Analysis).order_by(Analysis.created_at.desc()).all()
        return jsonify([
            {"id": r.id, "algo": r.algo, "complexity": r.complexity, "created_at": r.created_at.isoformat()}
            for r in rows
        ])


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 8000)), debug=False)

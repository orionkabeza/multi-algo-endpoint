import base64
import io
import time
from datetime import datetime
from pathlib import Path

from matplotlib.figure import Figure   # no pyplot -> no GUI backend, thread-safe

from algorithms import ALGORITHMS

SNAPSHOT_DIR = Path(__file__).parent / "snapshots"
TIME_BUDGET_S = 30


def measure(algo, n_min, n_max, step, budget=TIME_BUDGET_S):
    setup, run = ALGORITHMS[algo][:2]
    points, truncated = [], False
    started = time.perf_counter()

    for n in range(n_min, n_max + 1, step):
        if time.perf_counter() - started > budget:
            truncated = True
            break
        best = None
        for _ in range(5):
            data = setup(n)                       # not timed
            t0 = time.perf_counter()
            run(data)
            elapsed = time.perf_counter() - t0
            best = elapsed if best is None else min(best, elapsed)
            if best > 0.01:                       # slow enough to be stable
                break
        points.append((n, best))
    return points, truncated


def render(algo, points):
    ns = [p[0] for p in points]
    secs = [p[1] for p in points]

    fig = Figure(figsize=(8, 5), dpi=100)
    ax = fig.subplots()
    ax.plot(ns, secs, "o-", markersize=3)
    ax.set_xlabel("Input size (n)")
    ax.set_ylabel("Running time (seconds)")
    ax.set_title(f"{algo} - {ALGORITHMS[algo][2]}")
    ax.grid(True, alpha=0.3)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    png = buf.getvalue()

    SNAPSHOT_DIR.mkdir(exist_ok=True)
    path = SNAPSHOT_DIR / f"{algo}_{datetime.now():%Y%m%d_%H%M%S_%f}.png"
    path.write_bytes(png)
    return path, base64.b64encode(png).decode("ascii")

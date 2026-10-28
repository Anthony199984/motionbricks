"""Genera las animaciones de jobs.json con kmd-generate en modo servidor (carga el modelo una vez)."""
import json
import subprocess
import sys
import time
from pathlib import Path

gen, motion, text, out = sys.argv[1:5]
import os
jobs = json.loads(Path(__file__).with_name("jobs.json").read_text())
shard, nshards = int(os.environ.get("SHARD", 0)), int(os.environ.get("NSHARDS", 1))
jobs = jobs[shard::nshards]
out = Path(out)
out.mkdir(parents=True, exist_ok=True)
t0 = time.time()
p = subprocess.Popen([gen, "--server", motion, text], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
report = []
for j in jobs:
    pf = out / f"{j['name']}.txt"
    pf.write_text(j["prompt"])
    t = time.time()
    line = "\t".join(["10", str(j.get("steps", 100)), str(j["seed"]), str(out / j["name"]), str(j["frames"]), str(pf)])
    p.stdin.write(line + "\n"); p.stdin.flush()
    resp = p.stdout.readline().strip()
    dt = time.time() - t
    print(f"{j['name']}: {resp} ({dt:.1f}s)", flush=True)
    report.append({"name": j["name"], "response": resp, "seconds": round(dt, 1), "frames": j["frames"]})
p.stdin.close(); p.wait()
(out / f"report_{shard}.json").write_text(json.dumps({"total_seconds": round(time.time() - t0, 1), "jobs": report}, indent=1))

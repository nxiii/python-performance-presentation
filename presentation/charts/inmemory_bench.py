import array
import json
import os
import pathlib
import sys
import tempfile
import time

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
from pympler import asizeof


ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "inmemory_bench.json"
N = 2_000_000


def bench(fn, repeat=3):
    fn()  # warmup
    times = []
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn()
        times.append((time.perf_counter() - t0) * 1000)
    return min(times)


def mem_mb(obj):
    return asizeof.asizeof(obj) / 1024 / 1024


rng = np.random.default_rng(42)
data = rng.integers(0, 10_000_000, N, dtype=np.int64)

results = []


def record(name, tier, fn, obj, note=""):
    print(f"... {name}", flush=True)
    t = bench(fn)
    m = mem_mb(obj) if obj is not None else None
    print(f"    {t:8.2f} ms   {m:6.1f} MB   {note}")
    results.append({"name": name, "tier": tier, "time_ms": round(t, 2),
                    "mem_mb": round(m, 1) if m is not None else None,
                    "note": note})


arrow_arr = pa.array(data)
record("PyArrow Int64Array", "arrow",
       lambda: (pc.min_max(arrow_arr), pc.sum(arrow_arr), pc.count(arrow_arr)),
       arrow_arr)

np_arr = data
record("NumPy int64 ndarray", "arrow",
       lambda: (np_arr.min(), np_arr.max(), int(np_arr.sum()), len(np_arr)),
       np_arr)

arr_arr = array.array("q", data.tolist())
record("array.array('q')", "py_dense",
       lambda: (min(arr_arr), max(arr_arr), sum(arr_arr), len(arr_arr)),
       arr_arr)

lst = data.tolist()
record("list[int]", "py_dense",
       lambda: (min(lst), max(lst), sum(lst), len(lst)),
       lst)

tpl = tuple(lst)
record("tuple[int]", "py_dense",
       lambda: (min(tpl), max(tpl), sum(tpl), len(tpl)),
       tpl)

records_lst = [{"q": int(v)} for v in lst]
record("list[dict] (records)", "py_object",
       lambda: (min(r["q"] for r in records_lst),
                max(r["q"] for r in records_lst),
                sum(r["q"] for r in records_lst),
                len(records_lst)),
       records_lst)

s = set(lst)
record("set[int]", "py_set",
       lambda: (min(s), max(s), sum(s), len(s)),
       s,
       note="(deduplicates — not equivalent to list stats)")

d = dict.fromkeys(lst)
record("dict[int, None]", "py_set",
       lambda: (min(d), max(d), sum(d), len(d)),
       d,
       note="(deduplicates — not equivalent to list stats)")

pd_series = pd.Series(data)
record("pandas Series (numpy)", "pandas",
       lambda: (pd_series.min(), pd_series.max(),
                int(pd_series.sum()), pd_series.count()),
       pd_series)

pd_pa_series = pd.Series(data, dtype="int64[pyarrow]")
record("pandas Series (arrow backend)", "pandas",
       lambda: (pd_pa_series.min(), pd_pa_series.max(),
                int(pd_pa_series.sum()), pd_pa_series.count()),
       pd_pa_series)

parq_path = tempfile.mktemp(suffix=".parquet")
pq.write_table(pa.table({"q": arrow_arr}), parq_path, compression="none")
parq_size_mb = os.path.getsize(parq_path) / 1024 / 1024

def parquet_uncompressed_stats():
    a = pq.read_table(parq_path, columns=["q"]).column("q")
    return pc.min_max(a), pc.sum(a), pc.count(a)

print("... PyArrow + parquet (uncompressed)", flush=True)
t = bench(parquet_uncompressed_stats)
print(f"    {t:8.2f} ms   {parq_size_mb:6.1f} MB on disk")
results.append({
    "name": "PyArrow + parquet (uncompressed)",
    "tier": "parquet",
    "time_ms": round(t, 2),
    "mem_mb": round(parq_size_mb, 1),
    "note": "(disk size, not RAM)",
})

OUT_JSON.write_text(json.dumps({"n": N, "results": results}, indent=2))
print(f"\nwrote {OUT_JSON}")

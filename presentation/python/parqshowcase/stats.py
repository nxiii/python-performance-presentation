import sys
import time
import pyarrow.parquet as pq
import pyarrow.compute as pc


def main():
    path, column = sys.argv[1], sys.argv[2]

    t0 = time.monotonic()
    arr = pq.read_table(path, columns=[column]).column(column)
    mm = pc.min_max(arr)
    s = pc.sum(arr)
    n = pc.count(arr)
    elapsed = (time.monotonic() - t0) * 1000

    print(f"column:  {column}")
    print(f"min:     {mm['min'].as_py()}")
    print(f"max:     {mm['max'].as_py()}")
    print(f"sum:     {s.as_py()}")
    print(f"count:   {n.as_py()}")
    print(f"elapsed: {round(elapsed, 1)}ms")


if __name__ == "__main__":
    main()

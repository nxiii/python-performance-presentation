import sys
import time
import pyarrow.parquet as pq


def main():
    src, dst, drop_col = sys.argv[1], sys.argv[2], sys.argv[3]

    t0 = time.monotonic()
    table = pq.read_table(src)
    out = table.drop_columns([drop_col])
    pq.write_table(out, dst, compression="zstd")
    elapsed = (time.monotonic() - t0) * 1000

    print(f"rows:    {out.num_rows}")
    print(f"dropped: {drop_col}")
    print(f"columns: {out.num_columns}")
    print(f"elapsed: {round(elapsed, 1)}ms")


if __name__ == "__main__":
    main()

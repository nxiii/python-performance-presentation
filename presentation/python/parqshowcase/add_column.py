import sys
import time
import pyarrow.parquet as pq
import pyarrow.compute as pc


def main():
    src, dst = sys.argv[1], sys.argv[2]

    t0 = time.monotonic()
    table = pq.read_table(src)
    total = pc.multiply(
        pc.cast(table["amount"], "float64"),
        pc.cast(table["quantity"], "float64"),
    )
    out = table.append_column("total", total)
    pq.write_table(out, dst, compression="zstd")
    elapsed = (time.monotonic() - t0) * 1000

    print(f"rows:    {out.num_rows}")
    print(f"columns: {out.num_columns}")
    print(f"added:   total = amount * quantity")
    print(f"elapsed: {round(elapsed, 1)}ms")


if __name__ == "__main__":
    main()

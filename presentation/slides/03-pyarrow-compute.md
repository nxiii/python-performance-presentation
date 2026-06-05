# What `pyarrow.compute` gives you

> `pyarrow.compute` is the Arrow project's C++ kernel library exposed to
> Python. The compute layer is the same code that powers Arrow's Java,
> R, Rust, and Go bindings — and it's what DuckDB, Polars, and Spark
> reach for when they need columnar primitives.

## Kernels & semantics

- **300+ kernels**: arithmetic, comparison, logic, casts, string ops
  (regex, slice, trim, case), temporal extraction (year/month/day-of-week),
  hashing, set operations.
- **Aggregations**: `sum`, `min_max`, `mean`, `stddev`, `quantile`,
  `count_distinct`, `value_counts`, `mode`, `tdigest`.
- **Null-safe by default**: every kernel propagates Arrow nulls without
  per-value branching.
- **Broadcasting**: scalar OP array, array OP array, no shape gymnastics.
- **Element-wise + reductive in one library**: no `.apply(lambda ...)`,
  no `.map_partitions(...)`.

## Zero-copy ergonomics

- `Table.append_column`, `drop_columns`, `select`, `slice`, `rename_columns`
  are O(1) metadata ops over shared Arrow buffers.
- Row-group-level filter & projection pushdown to Parquet through
  `pyarrow.dataset.dataset(...).to_table(filter=..., columns=...)`.
- `Table.combine_chunks()` lets you control when to materialise.
- Decimal, timestamp, dictionary-encoded, and nested types are first
  class — no `.to_pandas()` detour.

## When NOT to use it

- **Multi-machine joins / shuffles** → Spark or DuckDB's distributed mode.
- **Iterative ML / heavy linear algebra** → NumPy, JAX, PyTorch.
- **Sub-millisecond OLTP queries** → a real database.

For everything else on Parquet — `pip install pyarrow`, six lines, 38 ms.

## Appendix: outliers worth knowing

- **DuckDB** does aggregation _inside_ the Parquet scan (pushdown) and beats
  PyArrow at this benchmark (11 ms) — at the cost of speaking SQL.
- **Polars** uses Rust's own Parquet reader (20 ms) — another good option
  if you prefer a `.with_columns(...)` expression API.
- **pandas with `engine="pyarrow"` is still 7× slower** than direct
  `pc.*` calls — every `df["col"].mean()` copies Arrow → NumPy and back.
  That copy is the whole pandas tax.

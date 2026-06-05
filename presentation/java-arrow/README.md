# java-arrow

`arrow-dataset` via JNI — the same C++ Parquet decoder PyArrow uses, just
called from Java. The decode itself runs at native speed; the cost is the
Java code that iterates the materialised batches by vector type and the
ceremony required to make JNI work (shade plugin, `--add-opens`).

Only `Stats` is implemented here. `arrow-dataset` is a scanner — it doesn't
ship a Parquet writer for Java, so the add/drop column equivalents would
require pulling in `parquet-mr` as well. That's exactly the point.

## Build

```bash
mvn -q package
```

## Run

```bash
WARMUP=../../wip/dynamicgen/data_warmup/orders/orders_000000.parquet
TEST=../../wip/dynamicgen/data/orders/orders_000000.parquet

java --add-opens=java.base/java.nio=ALL-UNNAMED \
    -cp target/showcase-arrow-1.0.jar \
    parqshowcase.Stats \
    "$WARMUP" "$TEST" quantity
```

The warmup pass runs on `<warmup-path>` to amortise JIT compilation
and JNI dylib load; the timed pass reads `<test-path>` cold from disk.

The `--add-opens` flag is required on Java 17+. Without it, Netty's
off-heap buffer allocation throws `InaccessibleObjectException`.

package parqshowcase;

import java.nio.file.Paths;
import java.util.Optional;
import org.apache.arrow.dataset.file.FileFormat;
import org.apache.arrow.dataset.file.FileSystemDatasetFactory;
import org.apache.arrow.dataset.jni.NativeMemoryPool;
import org.apache.arrow.dataset.scanner.ScanOptions;
import org.apache.arrow.dataset.scanner.Scanner;
import org.apache.arrow.dataset.source.Dataset;
import org.apache.arrow.dataset.source.DatasetFactory;
import org.apache.arrow.memory.BufferAllocator;
import org.apache.arrow.memory.RootAllocator;
import org.apache.arrow.vector.BigIntVector;
import org.apache.arrow.vector.FieldVector;
import org.apache.arrow.vector.Float4Vector;
import org.apache.arrow.vector.Float8Vector;
import org.apache.arrow.vector.IntVector;
import org.apache.arrow.vector.VectorSchemaRoot;
import org.apache.arrow.vector.ipc.ArrowReader;

public class Stats {

    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("Usage: Stats <warmup-path> <test-path> <column>");
            System.exit(1);
        }

        String warmupPath = args[0];
        String testPath = args[1];
        String column = args[2];
        String warmupUri = Paths.get(warmupPath).toAbsolutePath().toUri().toString();
        String testUri = Paths.get(testPath).toAbsolutePath().toUri().toString();

        BufferAllocator allocator = new RootAllocator();

        for (int run = 0; run < 2; run++) {
            String uri = (run == 0) ? warmupUri : testUri;
            long t0 = System.nanoTime();

            ScanOptions options = new ScanOptions(
                32768, Optional.of(new String[] {column})
            );

            long longMin = Long.MAX_VALUE, longMax = Long.MIN_VALUE;
            long longSum = 0;
            double dblMin = Double.MAX_VALUE, dblMax = -Double.MAX_VALUE;
            double dblSum = 0;
            long count = 0;
            boolean isInt = false;

            try (
                DatasetFactory factory = new FileSystemDatasetFactory(
                    allocator, NativeMemoryPool.getDefault(),
                    FileFormat.PARQUET, uri
                );
                Dataset dataset = factory.finish();
                Scanner scanner = dataset.newScan(options);
                ArrowReader reader = scanner.scanBatches()
            ) {
                while (reader.loadNextBatch()) {
                    VectorSchemaRoot root = reader.getVectorSchemaRoot();
                    FieldVector vec = root.getVector(column);
                    int n = vec.getValueCount();

                    if (vec instanceof IntVector) {
                        IntVector iv = (IntVector) vec;
                        isInt = true;
                        for (int i = 0; i < n; i++) {
                            if (iv.isNull(i)) continue;
                            int v = iv.get(i);
                            if (v < longMin) longMin = v;
                            if (v > longMax) longMax = v;
                            longSum += v;
                            count++;
                        }
                    } else if (vec instanceof BigIntVector) {
                        BigIntVector bv = (BigIntVector) vec;
                        isInt = true;
                        for (int i = 0; i < n; i++) {
                            if (bv.isNull(i)) continue;
                            long v = bv.get(i);
                            if (v < longMin) longMin = v;
                            if (v > longMax) longMax = v;
                            longSum += v;
                            count++;
                        }
                    } else if (vec instanceof Float4Vector) {
                        Float4Vector fv = (Float4Vector) vec;
                        for (int i = 0; i < n; i++) {
                            if (fv.isNull(i)) continue;
                            float v = fv.get(i);
                            if (v < dblMin) dblMin = v;
                            if (v > dblMax) dblMax = v;
                            dblSum += v;
                            count++;
                        }
                    } else if (vec instanceof Float8Vector) {
                        Float8Vector dv = (Float8Vector) vec;
                        for (int i = 0; i < n; i++) {
                            if (dv.isNull(i)) continue;
                            double v = dv.get(i);
                            if (v < dblMin) dblMin = v;
                            if (v > dblMax) dblMax = v;
                            dblSum += v;
                            count++;
                        }
                    } else {
                        throw new UnsupportedOperationException(
                            "Unsupported vector type: " + vec.getClass().getName()
                        );
                    }
                }
            }

            String ms = Bench.fmtMs(System.nanoTime() - t0);

            if (run == 0) {
                System.out.println("warmup:  " + ms);
                continue;
            }

            System.out.println("column:  " + column);
            if (isInt) {
                System.out.println("min:     " + longMin);
                System.out.println("max:     " + longMax);
                System.out.println("sum:     " + longSum);
            } else {
                System.out.println("min:     " + dblMin);
                System.out.println("max:     " + dblMax);
                System.out.println("sum:     " + dblSum);
            }
            System.out.println("count:   " + count);
            System.out.println("elapsed: " + ms);
        }

        allocator.close();
    }
}

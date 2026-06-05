package parqshowcase;

import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import static org.apache.spark.sql.functions.*;

public class Stats {

    public static void main(String[] args) {
        if (args.length < 3) {
            System.err.println("Usage: Stats <warmup-path> <test-path> <column>");
            System.exit(1);
        }

        String warmupPath = args[0];
        String testPath = args[1];
        String column = args[2];

        SparkSession spark = SparkSession.builder()
            .appName("stats")
            .config("spark.ui.enabled", "false")
            .config("spark.sql.parquet.enableVectorizedReader", "true")
            .getOrCreate();
        spark.sparkContext().setLogLevel("ERROR");

        for (int run = 0; run < 2; run++) {
            String p = (run == 0) ? warmupPath : testPath;

            long t0 = System.nanoTime();

            Row r = spark.read().parquet(p).agg(
                min(col(column)),
                max(col(column)),
                sum(col(column)),
                count(col(column))
            ).first();

            String ms = Bench.fmtMs(System.nanoTime() - t0);

            if (run == 0) {
                System.out.println("warmup:  " + ms);
                continue;
            }

            System.out.println("column:  " + column);
            System.out.println("min:     " + r.get(0));
            System.out.println("max:     " + r.get(1));
            System.out.println("sum:     " + r.get(2));
            System.out.println("count:   " + r.get(3));
            System.out.println("elapsed: " + ms);
        }

        spark.stop();
    }
}

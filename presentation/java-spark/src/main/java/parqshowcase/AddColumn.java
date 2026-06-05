package parqshowcase;

import org.apache.spark.sql.SparkSession;
import static org.apache.spark.sql.functions.*;

public class AddColumn {

    public static void main(String[] args) {
        if (args.length < 3) {
            System.err.println("Usage: AddColumn <warmup-src> <test-src> <test-dst>");
            System.exit(1);
        }

        String warmupSrc = args[0];
        String testSrc = args[1];
        String testDst = args[2];

        SparkSession spark = SparkSession.builder()
            .appName("add-column")
            .config("spark.ui.enabled", "false")
            .config("spark.sql.parquet.enableVectorizedReader", "true")
            .getOrCreate();
        spark.sparkContext().setLogLevel("ERROR");

        for (int run = 0; run < 2; run++) {
            String src = (run == 0) ? warmupSrc : testSrc;
            String dst = (run == 0) ? testDst + "_warmup" : testDst;

            long t0 = System.nanoTime();

            spark.read().parquet(src)
                .withColumn("total", col("amount").multiply(col("quantity")))
                .write().mode("overwrite").parquet(dst);

            String ms = Bench.fmtMs(System.nanoTime() - t0);

            if (run == 0) {
                System.out.println("warmup:  " + ms);
                continue;
            }

            System.out.println("added:   total = amount * quantity");
            System.out.println("output:  " + dst);
            System.out.println("elapsed: " + ms);
        }

        spark.stop();
    }
}

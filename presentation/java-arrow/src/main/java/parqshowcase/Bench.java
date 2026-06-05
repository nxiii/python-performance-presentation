package parqshowcase;

import java.math.BigDecimal;
import java.math.RoundingMode;

final class Bench {
    private Bench() {}

    static String fmtMs(long nanos) {
        return BigDecimal.valueOf(nanos / 1_000_000.0)
            .setScale(1, RoundingMode.HALF_UP) + "ms";
    }
}

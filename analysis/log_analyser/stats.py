from log_analyser.config import OUT_DIR
import pandas as pd


def summarize(df: pd.DataFrame, save_csv: bool) -> pd.DataFrame:
    summary = (
        df.groupby(["location", "size"])
        .agg(
            transactions = ("latency_ms", "count"),
            lat_min_ms = ("latency_ms", "min"),
            lat_max_ms = ("latency_ms", "max"),
            lat_mean_ms = ("latency_ms", "mean"),
            lat_p50_ms = ("latency_ms", lambda x: x.quantile(0.50)),
            lat_p95_ms = ("latency_ms", lambda x: x.quantile(0.95)),
            lat_p99_ms = ("latency_ms", lambda x: x.quantile(0.99)),
            tput_min_kbs = ("throughput_kbs", "min"),
            tput_max_kbs = ("throughput_kbs", "max"),
            tput_mean_kbs = ("throughput_kbs", "mean"),
            rtput_min_kbs = ("throughput_real_kbs", "min"),
            rtput_max_kbs = ("throughput_real_kbs", "max"),
            rtput_mean_kbs = ("throughput_real_kbs", "mean"),
        )
        .round(2)
    )
 
    print("\nSUMMARY — per file")
    print(summary.to_string())
 
    if save_csv:
        summary.to_csv(OUT_DIR / "summary.csv", index=True)
 
    return summary
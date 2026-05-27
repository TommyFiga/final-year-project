from config import BENCHMARK_DIR
from log_analyser.charts import (
    plot_effective_throughput, 
    plot_latency_distribution, 
    plot_latency_percentiles,
    plot_latency_vs_throughput, 
    plot_throughput
)
from log_analyser.parser import load_logs
from log_analyser.stats import summarize


def main():
    print("Loading .log files")
    df = load_logs(BENCHMARK_DIR)

    if df is None or df.empty:
        print("Data frame is empty")
        return

    summarize(df, True)

    print("\n\nGenerating charts...")
    plot_latency_distribution(df)
    plot_latency_percentiles(df)
    plot_throughput(df)
    plot_effective_throughput(df)
    plot_latency_vs_throughput(df)

    print("All outputs saved to /output/")


if __name__ == "__main__":
    main()
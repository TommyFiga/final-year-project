from pathlib import Path

ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / "data"

LOGS_DIR = DATA_DIR / "logs"
BENCHMARK_DIR = LOGS_DIR / "benchmark"

OUT_DIR  = DATA_DIR / "output"
 
TIMESTAMP_FMT = "%Y/%m/%d %H:%M:%S.%f"

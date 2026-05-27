from log_analyser.config import TIMESTAMP_FMT
from datetime import datetime, timedelta
from pathlib import Path
import math
import pandas as pd
import re

_TIMESTAMP_REGEX = re.compile(r"^(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d+)")


def _parse_timestamp(line: str) -> datetime | None:
    timestamp_match = _TIMESTAMP_REGEX.match(line)
    return datetime.strptime(timestamp_match.group(1), TIMESTAMP_FMT) if timestamp_match else None
    

def _to_ms(delta: timedelta) -> float:
    return delta.total_seconds() * 1000


def parse_log_file(path: Path) -> list[dict]:
    records = []
 
    request_sent_at    = None
    header_received_at = None
    total_bytes        = None
 
    with open(path, encoding="utf-8", errors="replace") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
 
            if "REQUEST_SENT" in line:
                request_sent_at = _parse_timestamp(line)
                header_received_at = None
                total_bytes = None
 
            elif "HEADER_RECEIVED" in line and request_sent_at:
                header_received_at = _parse_timestamp(line)
                bytes_match = re.search(r"b=(\d+)", line)
                total_bytes = int(bytes_match.group(1)) if bytes_match else None
 
            elif "TRANSFER_COMPLETE" in line and request_sent_at and header_received_at:
                transfer_complete_at = _parse_timestamp(line)
                if transfer_complete_at is None:
                    continue
 
                latency_ms = _to_ms(transfer_complete_at - request_sent_at)
                transfer_ms = _to_ms(transfer_complete_at - header_received_at)
                transfer_s = transfer_ms / 1000
                
                throughput_bs = (total_bytes * 8)/ transfer_s if total_bytes and transfer_s > 0 else None
                throughput_kbs = throughput_bs / 1024 if throughput_bs is not None else None

                throughput_real_bs = math.floor(throughput_bs * 3 / 4) if throughput_bs else None
                throughput_real_kbs = throughput_real_bs / 1024 if throughput_real_bs else None

                records.append({
                    "timestamp":           request_sent_at,
                    "latency_ms":          round(latency_ms, 3),
                    "transfer_ms":         round(transfer_ms, 3),
                    "total_bytes":         total_bytes,
                    "throughput_bs":       round(throughput_bs, 3),
                    "throughput_kbs":      round(throughput_kbs, 3),
                    "throughput_real_bs":  round(throughput_real_bs, 3),
                    "throughput_real_kbs": round(throughput_real_kbs, 3)
                })
 
                request_sent_at = None
                header_received_at = None
                total_bytes = None
 
    return records
 
 
def load_logs(path: Path) -> pd.DataFrame | None:
    log_files = sorted(path.glob("*.log"))
 
    if not log_files:
        print(f"[!] No .log files found in {path}")
        return None
 
    all_records: list[dict] = []
    for path in log_files:
        records = parse_log_file(path)

        file = path.stem
        location, size = file.split("_", 1)
        
        for record in records:
            record["file"]     = file
            record["location"] = location
            record["size"]     = size
        
        all_records.extend(records)

    df = pd.DataFrame(all_records)
    df["location"] = pd.Categorical(df["location"], categories=["local", "cloud", "webapi"], ordered=True)
    df["size"] = pd.Categorical(df["size"], categories=["50kb", "100kb"], ordered=True)

    return df
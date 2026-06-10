from pathlib import Path

import pandas as pd

# Load raw data capture and remove redundant features
def load_traffic_capture(filepath: Path, label: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df = df.drop(columns=['No.', 'Protocol', 'Info'])
    df['Label'] = label
    return df

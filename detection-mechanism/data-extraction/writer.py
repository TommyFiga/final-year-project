from pathlib import Path
import pandas as pd

# Store dataset instances in a dataset file 
def store_dataset(dataset: pd.DataFrame, dataset_file: Path) -> None:
    dataset.to_csv(dataset_file)
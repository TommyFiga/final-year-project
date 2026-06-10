from .builder_a import extract_time_window_dataset_instances
from .builder_b import extract_packet_window_dataset_instances
from .loader import load_traffic_capture
from .summary import show_dataset_statistics
from .writer import store_dataset

import config as cfg
import pandas as pd


def main():
    time_window_dataframes = []
    packet_window_dataframes = []

    for label, dir in cfg.LABELED_DIRS.items():
        traffic_capture_files = sorted(dir.glob('*.csv'))

        if not traffic_capture_files:
            print(f'[WARNING]: no CSV files found in directory: {dir}')
            continue
        
        for filepath in traffic_capture_files:
            traffic_capture = load_traffic_capture(filepath, label)

            time_window_dataframe = extract_time_window_dataset_instances(traffic_capture)
            time_window_dataframes.append(time_window_dataframe)

            packet_window_dataframe = extract_packet_window_dataset_instances(traffic_capture)
            packet_window_dataframes.append(packet_window_dataframe)
    
    if not time_window_dataframes or not packet_window_dataframes:
        print(f'')
        return

    dataset_a = pd.concat(time_window_dataframes, ignore_index=True)
    store_dataset(dataset_a, cfg.DATASET_A)
    
    dataset_b = pd.concat(packet_window_dataframes, ignore_index=True)
    store_dataset(dataset_b, cfg.DATASET_B)

    show_dataset_statistics(dataset_a, cfg.DATASET_A.name)
    show_dataset_statistics(dataset_b, cfg.DATASET_B.name)


if __name__ == '__main__':
    main()

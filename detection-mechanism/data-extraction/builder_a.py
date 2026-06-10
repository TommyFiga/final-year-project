import config as cfg
import pandas as pd

# Time window size in seconds
WINDOW_SIZE = 10

def extract_time_window_dataset_instances(traffic_capture: pd.DataFrame) -> pd.DataFrame:
    dataset = []

    # Associate each packet timestamp to a time window index
    # ex.: 0 - 10s (0), 11 - 20s (1)
    traffic_capture['Window'] = (traffic_capture["Time"] // WINDOW_SIZE).astype(int)

    for _, window in traffic_capture.groupby('Window'):
        lengths = window['Length'].astype(int)

        sent_packets = window[window['Destination'] == cfg.TELEGRAM_IP]
        received_packets = window[window['Source'] == cfg.TELEGRAM_IP]

        dataset_row = {
            'total_packets': len(window),
            'total_bytes': lengths.sum(),

            'min_packet_size': lengths.min(),
            'max_packet_size': lengths.max(),
            'avg_packet_size': lengths.mean(),
            'std_dev_packet_size': lengths.std(),
            'packet_size_variance': lengths.var(),

            'packets_sent': len(sent_packets),
            'packets_received': len(received_packets),

            'bytes_sent': sent_packets['Length'].astype(int).sum(),
            'bytes_received': received_packets['Length'].astype(int).sum(),

            'packet_rate': len(window) / WINDOW_SIZE,
            'throughput': lengths.sum() / WINDOW_SIZE,

            'label': traffic_capture['Label'].iloc[0]
        }

        dataset.append(dataset_row)

    return pd.DataFrame(dataset)

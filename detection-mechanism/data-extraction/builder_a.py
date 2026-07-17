import config as cfg
import pandas as pd

# Time window size in seconds
WINDOW_SIZE = 10

def extract_time_window_dataset_instances(traffic_capture: pd.DataFrame) -> pd.DataFrame:
    dataset = []

    traffic_capture['Window'] = (traffic_capture['Time'].astype(float) // WINDOW_SIZE).astype(int)
    capture_end = traffic_capture['Time'].astype(float).max()

    for window_idx, window in traffic_capture.groupby('Window'):
        window_start = window_idx * WINDOW_SIZE
        window_end = window_start + WINDOW_SIZE

        # drop the last window if it doesn't span the full WINDOW_SIZE seconds
        if window_end > capture_end:
            continue
        
        lengths = window['Length'].astype(int)

        sent_packets = window[window['Destination'].isin(cfg.TELEGRAM_IPS)]
        received_packets = window[window['Source'].isin(cfg.TELEGRAM_IPS)]

        dataset_row = {
            'total_packets': len(window),

            'total_bytes': lengths.sum(),
            'min_packet_size': lengths.min(),
            'max_packet_size': lengths.max(),
            'avg_packet_size': lengths.mean(),
            'std_dev_packet_size': lengths.std() if len(lengths) > 1 else 0.0,
            'packet_size_variance': lengths.var() if len(lengths) > 1 else 0.0,

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

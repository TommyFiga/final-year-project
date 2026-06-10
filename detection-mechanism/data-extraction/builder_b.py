import config as cfg
import pandas as pd
import numpy as np

# Packet window size
WINDOW_SIZE = 50

def extract_packet_window_dataset_instances(traffic_capture: pd.DataFrame) -> pd.DataFrame:
    dataset = []

    for start in range(0, len(traffic_capture), WINDOW_SIZE):
        window = traffic_capture.iloc[start:start + WINDOW_SIZE]

        # each window frame should contain exactly 50 packets
        if len(window) < WINDOW_SIZE:
            continue
        
        # packets timestamps and lengths
        times = window['Time'].astype(float)
        lengths = window['Length'].astype(int)

        inter_packet_times = np.diff(times)

        sent_packets = window[window['Destination'] == cfg.TELEGRAM_IP]
        received_packets = window[window['Source'] == cfg.TELEGRAM_IP]

        dataset_row = {
            'duration': times.iloc[-1] - times.iloc[0],
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

            'avg_inter_packet_time':
                 inter_packet_times.mean() if len(inter_packet_times) > 0 else 0,

            'inter_packet_time_dev':
                inter_packet_times.std() if len(inter_packet_times) > 0 else 0,

            'label': traffic_capture['Label'].iloc[0]
        }

        dataset.append(dataset_row)
    
    return pd.DataFrame(dataset)

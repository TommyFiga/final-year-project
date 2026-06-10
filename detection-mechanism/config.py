from pathlib import Path


EVASION_LABEL = 'Evasion'
NORMAL_LABEL = 'Normal'

ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / 'data'

DATASETS_DIR = DATA_DIR / 'datasets'
DATASET_A = DATASETS_DIR / 'time_window.csv'
DATASET_B = DATASETS_DIR / 'packet_window.csv'

RAW_DIR = DATA_DIR / 'raw'
EVASION_TRAFFIC_DIR = RAW_DIR / 'evasion'
NORMAL_TRAFFIC_DIR = RAW_DIR / 'normal' 

LABELED_DIRS = {
    NORMAL_LABEL: NORMAL_TRAFFIC_DIR,
    EVASION_LABEL: EVASION_TRAFFIC_DIR
}

RESULTS_DIR = DATA_DIR / 'results'
METRICS_DIR = RESULTS_DIR / 'metrics'
PLOTS_DIR = RESULTS_DIR / 'plots'

TELEGRAM_IP = '149.154.167.99'
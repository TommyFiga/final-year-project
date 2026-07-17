from dataclasses import dataclass
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

import hyper_parameters as hp
import numpy as np
import pandas as pd


@dataclass
class PreprocessedDataset:
    name: str

    # Pre-Processed data
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    scaler: StandardScaler
    label_encoder: LabelEncoder
    feature_names: list[str]

    # Pre-Processed statistics
    feat_stats: pd.DataFrame
    scaled_feat_stats: pd.DataFrame
    feat_correlations: pd.DataFrame
    class_distribution: dict[str, dict[str, int]]
    per_class_feat_stats: pd.DataFrame


def preprocess_dataset(path: Path) -> PreprocessedDataset:
    # Load dataset from csv file
    dataset = pd.read_csv(path)
    df = dataset.copy()

    # Get feature matrix (X) and target vector (y)
    X = df.drop(columns=['label'])
    y = df['label']

    # Group by original string labels to keep Normal/Evasion readable in the report
    X_with_label = X.copy()
    X_with_label['label'] = y
    per_class_feat_stats = X_with_label.groupby('label').agg(['mean', 'std']).T

    # Encode labels (Normal/Evasion -> 0/1)
    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)

    # Ensure the positive class corresponds to Evasion (1)
    if list(encoder.classes_) == ['Evasion', 'Normal']:
        y_encoded = 1 - y_encoded

        # Keep classes_ consistent with the new encoding
        encoder.classes_ = np.array(['Normal', 'Evasion'])

    y_encoded = pd.Series(y_encoded, name='label')

    # Capture pre-scaling stats and correlations on the full feature set
    feat_stats = X.describe().T[['mean', 'std', 'min', 'max']]
    feat_correlations = X.corr()

    # Train/Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y_encoded,
        test_size=hp.TEST_SIZE,
        random_state=hp.RANDOM_STATE,
        stratify=y_encoded
    )

    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train), 
        columns=X_train.columns, 
        index=X_train.index
    )
    
    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test),
        columns=X_test.columns, 
        index=X_test.index
    )

    # Post-scaling stats
    scaled_feat_stats = X_train_scaled.describe().T[['mean', 'std', 'min', 'max']]

    # Class counts per split
    class_distribution = {
        'train': dict(y_train.value_counts().rename(index=dict(enumerate(encoder.classes_)))),
        'test': dict(y_test.value_counts().rename(index=dict(enumerate(encoder.classes_))))
    }

    _log_class_distribution(y_train, y_test, encoder)

    return PreprocessedDataset(
        name=path.name,
        X_train=X_train_scaled,
        X_test=X_test_scaled,
        y_train=y_train,
        y_test=y_test,
        scaler=scaler,
        label_encoder=encoder,
        feature_names=X.columns.to_list(),
        feat_stats=feat_stats,
        scaled_feat_stats=scaled_feat_stats,
        feat_correlations=feat_correlations,
        class_distribution=class_distribution,
        per_class_feat_stats=per_class_feat_stats
    )


def _log_class_distribution(y_train: pd.Series, y_test: pd.Series, label_encoder: LabelEncoder) -> None:
    total = len(y_train) + len(y_test)

    print(f'\nClass distribution  (total={total})')
    print(f'{'Split':<8}  {'Class':<10}  {'Count':>6}  {'%':>8}')

    for split_name, split in [('train', y_train), ('test', y_test)]:
        for encoded_label, count in sorted(split.value_counts().items()):
            class_name = label_encoder.inverse_transform([encoded_label])[0]
            percentage = count / len(split) * 100
            print(f'  {split_name:<8}  {class_name:<10}  {count:>6}  {percentage:>5.1f}%')

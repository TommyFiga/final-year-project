from .preprocessor import PreprocessedDataset
from .trainer import TrainingResults

from dataclasses import dataclass
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve
)

import hyper_parameters as hp
import numpy as np
import pandas as pd
import shap


@dataclass
class ModelMetrics:
    name: str

    y_proba: np.ndarray
    y_pred: np.ndarray
    y_true: np.ndarray

    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float
    pr_precision: np.ndarray
    pr_recall: np.ndarray

    tpr: np.ndarray
    fpr: np.ndarray
    conf_matrix: np.ndarray
    tn: int
    fp: int
    fn: int
    tp: int
    sensitivity: float
    specificity: float

    shap_values: np.ndarray

@dataclass 
class EvaluationResults:
    results: list[ModelMetrics]


def evaluate_models(training_result: TrainingResults, preprocessed_dataset: PreprocessedDataset) -> EvaluationResults:
    results: list[ModelMetrics] = []

    y_true = preprocessed_dataset.y_test
    X_test = preprocessed_dataset.X_test
    X_train = preprocessed_dataset.X_train

    for trained_model in training_result.trained_models:
        print('  [INFO] Evaluating model: ' + trained_model.name)
        classifier = trained_model.classifier

        y_pred = classifier.predict(X_test)
        y_proba_both = classifier.predict_proba(X_test)
        y_proba = y_proba_both[:, 1]

        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='binary')
        recall = recall_score(y_true, y_pred, average='binary')
        f1 = f1_score(y_true, y_pred, average='binary')
        roc_auc = roc_auc_score(y_true, y_proba)
        pr_precision, pr_recall, _ = precision_recall_curve(y_true, y_proba)
        
        fpr, tpr, _ = roc_curve(y_true, y_proba)
        conf_matrix = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = conf_matrix.ravel()

        conf_matrix_display = np.array([
            [tp, fn],
            [fp, tn]
        ])

        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    
        match trained_model.name:
            case 'Logistic Regression':
                explainer = shap.LinearExplainer(classifier, X_train)
                shap_values = explainer.shap_values(X_test)
            case 'Random Forest':
                explainer = shap.TreeExplainer(classifier)
                raw = explainer.shap_values(X_test)
                # Handle both list-of-arrays and single 3D array return formats
                shap_values = raw[1] if isinstance(raw, list) else raw[:, :, 1]
            case 'SVM':
                background = shap.sample(X_train, 100, random_state=hp.RANDOM_STATE)
                explainer = shap.KernelExplainer(classifier.predict_proba, background)
                shap_values = explainer.shap_values(X_test)[:, :, 1]
        
        # shap_values shape: (n_samples, n_features)
        feature_names = X_test.columns.tolist()

        # Per-sample, per-feature values as a DataFrame (easiest to inspect/export)
        shap_df = pd.DataFrame(shap_values, columns=feature_names, index=X_test.index)

        # Mean absolute SHAP value per feature (global importance ranking)
        mean_abs_shap = shap_df.abs().mean().sort_values(ascending=False)
        print(f'\n  [DEBUG] Mean |SHAP value| per feature for {trained_model.name}:')
        for feat, val in mean_abs_shap.items():
            print(f'    {feat}: {val:.4f}')

        metrics = ModelMetrics(
            name=trained_model.name,
            y_proba=y_proba,
            y_pred=y_pred,
            y_true=y_true,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1=f1,
            roc_auc=roc_auc,
            pr_precision=pr_precision,
            pr_recall=pr_recall,
            tpr=tpr,
            fpr=fpr,
            conf_matrix=conf_matrix_display,
            tn=tn,
            fp=fp,
            fn=fn,
            tp=tp,
            sensitivity=sensitivity,
            specificity=specificity,
            shap_values=shap_values
        )

        results.append(metrics)

    return EvaluationResults(
        results=results
    )

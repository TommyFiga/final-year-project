from .evaluator import EvaluationResults
from .preprocessor import PreprocessedDataset
from .trainer import TrainingResults
from .visualizer import (
    plot_evalutaion_metrics,
    plot_learning_curve,
    plot_shap_bar,
    plot_shap_beeswarm
)

import config as cfg


def generate_plot_report(
    preprocessed_dataset: PreprocessedDataset,
    training_results: TrainingResults,
    evaluation_results: EvaluationResults
) -> None:
    
    for model_metrics in evaluation_results.results:
        plot_evalutaion_metrics(preprocessed_dataset, model_metrics)
        plot_shap_bar(preprocessed_dataset, model_metrics)
        plot_shap_beeswarm(preprocessed_dataset, model_metrics)
    
    for trained_model in training_results.trained_models:
        plot_learning_curve(preprocessed_dataset, trained_model)


def generate_results_report(
    preprocessed_dataset: PreprocessedDataset,
    training_results: TrainingResults,
    evaluation_results: EvaluationResults
) -> None:
    
    dataset_name = preprocessed_dataset.name
    lines: list[str] = []

    print('  [INFO] Generating dataset report for dataset: ' + dataset_name)

    # Header
    lines += [
        '# Detection Mechanism — Results Report',
        f'**Dataset:** {dataset_name}  ',
        '',
    ]

    # 1. Preprocessing
    lines += ['## Preprocessing', '']

    # Class distribution for test and train splits
    lines += ['### Class Distribution', '']
    distribution = preprocessed_dataset.class_distribution
    lines += ['| Split | Normal | Evasion | Total |', '|---|---|---|---|']
    
    for split, counts in distribution.items():
        normal  = counts.get('Normal', 0)
        evasion = counts.get('Evasion', 0)
        lines.append(f'| {split.capitalize()} | {normal} | {evasion} | {normal + evasion} |')
    
    lines.append('')

    # Per-class feature stats - shows which features separate Normal from Evasion
    lines += ['### Feature Statistics by Class', '']
    lines.append(preprocessed_dataset.per_class_feat_stats.to_markdown(floatfmt='.4f'))
    lines.append('')


    # 2. Training
    lines += ['## Training', '']

    for trained_model in training_results.trained_models:
        lines += [
            f'### {trained_model.name}', 
            ''
        ]

        # Cross-validation scores - mean and std summarizes generalisation across folds
        lines += ['#### Cross-Validation Scores', '']
        lines += ['| Metric | Mean | Std | Per-Fold Scores |', '|---|---|---|---|']

        for metric, scores in trained_model.cross_val_scores.items():
            fold_scores = ', '.join(f'{s:.4f}' for s in scores)
            lines.append(
                f'| {metric.upper()} '
                f'| {scores.mean():.4f} '
                f'| {scores.std():.4f} '
                f'| {fold_scores} |'
            )

        lines.append('')

        # Fit and score times - mean and std reflects model complexity and inference cost
        lines += ['#### Timing', '']
        lines += ['| | Mean (s) | Std (s) |', '|---|---|---|']
        lines.append(f'| Fit time   | {trained_model.fit_time.mean():.4f} | {trained_model.fit_time.std():.4f} |')
        lines.append(f'| Score time | {trained_model.score_time.mean():.4f} | {trained_model.score_time.std():.4f} |')
        lines.append('---')
    lines.append('')
    
    # 3. Evaluation
    lines += ['## Evaluation', '']

    for model_metrics in evaluation_results.results:
        lines += [
            f'### {model_metrics.name}', 
            ''
        ]

        # Core metrics
        lines += ['#### Metrics', '']
        lines += ['| Metric | Value |', '|---|---|']
        lines += [
            f'| Accuracy    | {model_metrics.accuracy:.4f} |',
            f'| Precision   | {model_metrics.precision:.4f} |',
            f'| Recall      | {model_metrics.recall:.4f} |',
            f'| F1 Score    | {model_metrics.f1:.4f} |',
            f'| ROC-AUC     | {model_metrics.roc_auc:.4f} |',
            f'| Sensitivity | {model_metrics.sensitivity:.4f} |',
            f'| Specificity | {model_metrics.specificity:.4f} |',
        ]
        lines.append('')

        # Confusion Matrox breakdown
        lines += ['#### Confusion Matrix Breakdown', '']
        lines += ['| | Predicted Evasion | Predicted Normal |', '|---|---|---|']
        lines += [
            f'| **Actual Evasion**  | TP = {model_metrics.tp} | FN = {model_metrics.fn} |',
            f'| **Actual Normal** | FP = {model_metrics.fp} | TN = {model_metrics.tn} |',
        ]
        lines.append('---')
    lines.append('')

    # Save report 
    if dataset_name == 'time_window.csv':
        report_dir = cfg.DATASET_A_RESULT_DIR
    elif dataset_name == 'packet_window.csv':
        report_dir = cfg.DATASET_B_RESULT_DIR
    else:
        report_dir = cfg.RESULTS_DIR

    report_dir.mkdir(parents=True, exist_ok=True)

    filename = report_dir / f'results-report.md'
    filename.write_text('\n'.join(lines), encoding='utf-8')

    print(f'  [OK] Saved report -> {filename}')

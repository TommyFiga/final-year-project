from .evaluator import evaluate_models
from .preprocessor import preprocess_dataset
from .reporter import generate_plot_report, generate_results_report
from .trainer import train_models

import config as cfg


def main():
    datasets_paths = [cfg.DATASET_A, cfg.DATASET_B]

    for dataset in datasets_paths:
        print('\n[INFO] Preprocessing dataset ' + dataset.name)
        preprocessed_dataset = preprocess_dataset(dataset)

        print('\n\n[INFO] Training models for dataset: ' + dataset.name)
        training_results = train_models(preprocessed_dataset.X_train, preprocessed_dataset.y_train)

        print('\n\n[INFO] Evaluating models for dataset: ' + dataset.name)
        evaluation_results = evaluate_models(training_results, preprocessed_dataset)

        print('\n\n[INFO] Generating metrics and plot reports for dataset: ' + dataset.name)
        generate_plot_report(preprocessed_dataset, training_results, evaluation_results)
        generate_results_report(preprocessed_dataset, training_results, evaluation_results)

    print('[OK] Data analysis completed for both datasets')


if __name__ == '__main__':
    main()
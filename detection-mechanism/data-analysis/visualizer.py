from .evaluator import ModelMetrics
from .preprocessor import PreprocessedDataset
from .trainer import TrainedModel

from matplotlib.figure import Figure
from sklearn.preprocessing import LabelEncoder

import config as cfg
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import shap


# Plot custom theme variables
_BLUE_DARK    = '#1a3a5c'
_BLUE_MID     = '#2c6fad'
_BLUE_LIGHT   = '#89b4d9'
_BLUE_PALE    = '#d6e8f7'
_ACCENT       = '#f0a500'
_TEXT         = '#1a2a3a'

_CMAP = sns.light_palette(_BLUE_MID, as_cmap=True)

sns.set_theme(
    style='whitegrid',
    palette=[_BLUE_DARK, _BLUE_MID, _BLUE_LIGHT, _ACCENT],
    font_scale=0.95,
    rc={
        'axes.facecolor': _BLUE_PALE,
        'figure.facecolor': 'white',
        'axes.edgecolor': _BLUE_LIGHT,
        'grid.color': 'white',
        'text.color': _TEXT,
        'axes.labelcolor': _TEXT,
        'xtick.color': _TEXT,
        'ytick.color': _TEXT
    }
)


# Helper 
def _save_plot_image(fig: Figure, dataset_name: str, model_name: str, content: str) -> None:
    if dataset_name == 'time_window.csv':
        plots_dir = cfg.DATASET_A_PLOTS_DIR
    elif dataset_name == 'packet_window.csv':
        plots_dir = cfg.DATASET_B_PLOTS_DIR
    else:
        plots_dir = cfg.RESULTS_DIR
    
    plots_dir.mkdir(parents=True, exist_ok=True)
    
    normalized_model_name = model_name.lower().replace(' ', '-')
    filename = plots_dir / f'{content}-{normalized_model_name}.png'
    fig.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close(fig)

    print(f'  [OK] Saved plot: {filename}\n')


# Plot functions 
def plot_shap_beeswarm(preprocessed_dataset: PreprocessedDataset, model_metrics: ModelMetrics) -> None:
    fig = plt.figure(figsize=(14, 10))
    fig.suptitle(
        f'{model_metrics.name} - {preprocessed_dataset.name} - Feature Impact Distribution',
        fontsize=14,
        fontweight='bold',
        color=_TEXT,
        y=1.02
    )

    # Beeswarm — shows per-sample feature impact distribution across the test set
    shap.summary_plot(
        model_metrics.shap_values,
        preprocessed_dataset.X_test,
        feature_names=preprocessed_dataset.feature_names,
        plot_type='dot',
        show=False,
        color_bar=True
    )

    _save_plot_image(fig, preprocessed_dataset.name, model_metrics.name, 'shap-beeswarm')


def plot_shap_bar(preprocessed_dataset: PreprocessedDataset, model_metrics: ModelMetrics) -> None:
    fig = plt.figure(figsize=(14, 10))
    fig.suptitle(
        f'{model_metrics.name} - {preprocessed_dataset.name} - Mean Feature Importance',
        fontsize=14,
        fontweight='bold',
        color=_TEXT,
        y=1.02
    )

    # Bar — mean absolute SHAP values, global feature importance ranking
    shap.summary_plot(
        model_metrics.shap_values,
        preprocessed_dataset.X_test,
        feature_names=preprocessed_dataset.feature_names,
        plot_type='bar',
        show=False,
        color=_BLUE_MID
    )

    plt.gca().set_xlabel('mean(|SHAP value|)')

    _save_plot_image(fig, preprocessed_dataset.name, model_metrics.name, 'shap-bar')


def plot_learning_curve(preprocessed_dataset: PreprocessedDataset, trained_model: TrainedModel) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.suptitle(
        f'{trained_model.name} - {preprocessed_dataset.name}',
        fontsize=14,
        fontweight='bold',
        color=_TEXT,
        y=0.98
    )

    # Training score line and variance band
    print('  [INFO] Generating training score line and variance band for: ' + trained_model.name)
    ax.plot(trained_model.train_sizes, trained_model.train_mean, color=_BLUE_MID, lw=2, label='Training F1')
    ax.fill_between(
        trained_model.train_sizes,
        trained_model.train_mean - trained_model.train_std,
        trained_model.train_mean + trained_model.train_std,
        alpha=0.12,
        color=_BLUE_MID
    )

    # Validation score line and variance band
    print('  [INFO] Generating cross-validation score line and variance band for: ' + trained_model.name)
    ax.plot(trained_model.train_sizes, trained_model.val_mean, color=_ACCENT, lw=2, label='Cross-validation F1')
    ax.fill_between(
        trained_model.train_sizes,
        trained_model.val_mean - trained_model.val_std,
        trained_model.val_mean + trained_model.val_std,
        alpha=0.12,
        color=_ACCENT
    )

    ax.set_xlim([trained_model.train_sizes[0], trained_model.train_sizes[-1]])
    ax.set_ylim([0.0, 1.05])

    ax.set_title('Learning Curve', fontweight='bold', pad=10)
    ax.set_xlabel('Training Samples')
    ax.set_ylabel('F1 Score')
    ax.legend(fontsize=8, loc='lower right', framealpha=0.9)

    _save_plot_image(fig, preprocessed_dataset.name, trained_model.name, 'learning-curve')


def plot_evalutaion_metrics(preprocessed_dataset: PreprocessedDataset, model_metrics: ModelMetrics) -> None:
    fig = plt.figure(figsize=(14, 10))
    fig.suptitle(
        f'{model_metrics.name} - {preprocessed_dataset.name}',
        fontsize=14,
        fontweight='bold',
        color=_TEXT,
        y=0.98
    )

    gs = gridspec.GridSpec(
        nrows=2,
        ncols=2, 
        figure=fig,
        hspace=0.38,
        wspace=0.32
    )

    print('  [INFO] Generating confusion matrix for: ' + model_metrics.name)
    _plot_confusion_matrix(fig.add_subplot(gs[0, 0]), model_metrics.conf_matrix, preprocessed_dataset.label_encoder)
    
    print('  [INFO] Generating ROC curve for: ' + model_metrics.name)
    _plot_roc_curve(fig.add_subplot(gs[0, 1]), model_metrics.fpr, model_metrics.tpr, model_metrics.roc_auc)
    
    print('  [INFO] Generating precision-recall curve for: ' + model_metrics.name)
    _plot_precision_recall_curve(fig.add_subplot(gs[1, 0]), model_metrics.pr_precision, model_metrics.pr_recall)

    _save_plot_image(fig, preprocessed_dataset.name, model_metrics.name, 'evalution-metrics')
    

# Helper functions
def _plot_confusion_matrix(ax: plt.Axes, cm: np.ndarray, label_encoder: LabelEncoder) -> None:
    class_names = label_encoder.classes_

    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap=_CMAP,
        xticklabels=['Evasion', 'Normal'],
        yticklabels=['Evasion', 'Normal'],
        linewidths=0.5,
        linecolor='white',
        cbar_kws={'shrink':0.8},
        ax=ax
    )

    ax.xaxis.set_label_position('top')
    ax.xaxis.tick_top()
    
    ax.yaxis.set_label_position('left')
    ax.yaxis.tick_left()

    ax.set_title(label='Confusion Matrix', fontweight='bold', pad=10)
    ax.set_xlabel('Predicted Label')
    ax.set_ylabel('Actual Label')


def _plot_roc_curve(ax: plt.Axes, fpr: np.ndarray, tpr: np.ndarray, roc_auc:float) -> None:
    ax.plot(fpr, tpr, color=_BLUE_MID, lw=2, label=f'AUC = {roc_auc:.4f}')
    ax.plot([0, 1], [0, 1], color=_BLUE_LIGHT, lw=1, linestyle='--', label='Random classifier')

    ax.fill_between(fpr, tpr, alpha=0.10, color=_BLUE_MID)
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])

    ax.set_title('ROC Curve', fontweight='bold', pad=10)
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.legend(fontsize=8, loc='lower right', framealpha=0.9)


def _plot_precision_recall_curve(ax: plt.Axes, precision: np.ndarray, recall: np.ndarray) -> None:
    ax.plot(recall, precision, color=_BLUE_DARK, lw=2)

    ax.fill_between(recall, precision, alpha=0.10, color=_BLUE_DARK)
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])

    ax.set_title('Precision-Recall Curve', fontweight='bold', pad=10)
    ax.set_xlabel('Recall')
    ax.set_ylabel('Precision')

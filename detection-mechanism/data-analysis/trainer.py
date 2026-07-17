from dataclasses import dataclass
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_validate, learning_curve, StratifiedKFold, GridSearchCV
from sklearn.svm import SVC

import hyper_parameters as hp
import numpy as np
import pandas as pd


@dataclass
class TrainedModel:
    name: str
    classifier: BaseEstimator

    train_sizes: np.ndarray
    train_mean: np.ndarray
    train_std: np.ndarray
    val_mean: np.ndarray
    val_std: np.ndarray

    cross_val_scores: dict[str, np.ndarray]
    fit_time: np.ndarray
    score_time: np.ndarray

    hyper_parameters: dict

@dataclass
class TrainingResults:
    trained_models: list[TrainedModel]


def train_models(X_train: pd.DataFrame, y_train: pd.Series) -> TrainingResults:
    trained_models: list[TrainedModel] = []

    k_fold = StratifiedKFold(
        n_splits=hp.K_FOLDS_PARAMS['n_splits'], 
        shuffle=hp.K_FOLDS_PARAMS['shuffle'], 
        random_state=hp.RANDOM_STATE
    )

    models = [
        (
            'Logistic Regression', 
            LogisticRegression(
                class_weight=hp.LOGIC_REGRESSION_PARAMS['class_weight'],
                max_iter=hp.LOGIC_REGRESSION_PARAMS['max_iter'],
                random_state=hp.RANDOM_STATE
            ),
            hp.LOGIC_REGRESSION_GRID
        ),
        (
            'Random Forest', 
            RandomForestClassifier(
                class_weight=hp.RANDOM_FOREST_PARAMS['class_weight'],
                random_state=hp.RANDOM_STATE
            ),
            hp.RANDOM_FOREST_GRID
        ),
        (
            'SVM',
            SVC(
                class_weight=hp.SVM_PARAMS['class_weight'],
                probability=hp.SVM_PARAMS['probability'],
                random_state=hp.RANDOM_STATE
            ),
            hp.SVM_GRID
        )
    ]

    for name, classifier, param_grid in models:
        print('  [INFO] Search best params for model: ' + name)
        grid_search = GridSearchCV(
            estimator=classifier,
            param_grid=param_grid,
            scoring='f1',
            cv=k_fold,
            n_jobs=-1,
            refit=True
        )

        grid_search.fit(X_train, y_train)

        best_classifier = grid_search.best_estimator_

        print(f'  [INFO] Best estimator and params for {name}: {best_classifier} | {grid_search.best_params_}')
        print('  [INFO] Training model...\n')
        # Compute learning curve
        train_sizes, train_scores, val_scores = learning_curve(
            best_classifier,
            X_train,
            y_train,
            cv=k_fold,
            scoring='f1',
            n_jobs=-1,
            train_sizes=np.linspace(0.1, 1.0, 10)
        )

        # Summarise fold scores into mean and std bands
        train_mean = train_scores.mean(axis=1)
        train_std  = train_scores.std(axis=1)
        val_mean   = val_scores.mean(axis=1)
        val_std    = val_scores.std(axis=1)

        # Computre cross validation training
        scores = cross_validate(
            best_classifier,
            X=X_train,
            y=y_train,
            cv=k_fold,
            scoring=['f1', 'roc_auc'],
            n_jobs=-1
        )

        cross_val_scores = {
            'f1': scores[f'test_f1'],
            'roc_auc': scores[f'test_roc_auc']
        }
        
        best_classifier.fit(X_train, y_train)

        # Capture per-fold fit and score times for complexity reporting
        fit_time = scores['fit_time']
        score_time = scores['score_time']

        trained_model = TrainedModel(
            name=name,
            classifier=best_classifier,
            train_sizes=train_sizes,
            train_mean=train_mean,
            train_std=train_std,
            val_mean=val_mean,
            val_std=val_std,
            cross_val_scores=cross_val_scores,
            fit_time=fit_time,
            score_time=score_time,
            hyper_parameters=grid_search.best_params_
        )

        trained_models.append(trained_model)

    return TrainingResults(
        trained_models=trained_models
    )

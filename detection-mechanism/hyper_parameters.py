# Global random state
RANDOM_STATE = 42 #107 #719 #100

# Train/Test Split ratio 
TEST_SIZE = 0.2  

# Corss validation scroing parameters
CROSS_VALITADE_SCORING = ['f1', 'roc_auc'] 

# K-Folds parameters
K_FOLDS_PARAMS = {
    'n_splits': 10,
    'shuffle': True
}

# Logic Regression parameters
LOGIC_REGRESSION_PARAMS = {
    'class_weight': 'balanced',
    'max_iter': 1000
}

LOGIC_REGRESSION_GRID = {
    'C': [0.01, 0.1, 1, 10, 100],
    'solver': ['lbfgs', 'liblinear']
}

# Random Forest parameters
RANDOM_FOREST_PARAMS = {
    'class_weight': 'balanced',
}

RANDOM_FOREST_GRID = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 5, 10, 20],
    'min_samples_split': [2, 5, 10]
}

# SVM parameters
SVM_PARAMS = {
    'class_weight': 'balanced',
    'probability': True
}

SVM_GRID = {
    'C': [0.1, 1, 10, 100],
    'kernel': ['rbf', 'linear'],
    'gamma': ['scale', 'auto']
}

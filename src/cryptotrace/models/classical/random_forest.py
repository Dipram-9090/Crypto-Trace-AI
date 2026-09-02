"""
Random Forest Baseline Classifier.
"""
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, average_precision_score


class RandomForestBaseline:
    def __init__(self, n_estimators: int = 150, max_depth: int = 8, random_state: int = 42):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            class_weight="balanced",
            random_state=random_state
        )
        self.is_trained = False

    def train(self, X_train: pd.DataFrame, y_train: pd.Series):
        self.model.fit(X_train, y_train)
        self.is_trained = True

    def predict_proba(self, X: pd.DataFrame):
        return self.model.predict_proba(X)[:, 1]

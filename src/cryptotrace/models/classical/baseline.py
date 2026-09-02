"""
Logistic Regression Baseline Classifier.
"""
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, average_precision_score


class LogisticRegressionBaseline:
    def __init__(self, random_state: int = 42, max_iter: int = 1000):
        self.model = LogisticRegression(class_weight="balanced", random_state=random_state, max_iter=max_iter)
        self.is_trained = False

    def train(self, X_train: pd.DataFrame, y_train: pd.Series):
        self.model.fit(X_train, y_train)
        self.is_trained = True

    def predict_proba(self, X: pd.DataFrame):
        return self.model.predict_proba(X)[:, 1]

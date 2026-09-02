"""
Baseline models for benchmark evaluation.
"""
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, average_precision_score


class BaselineEvaluator:
    def __init__(self, random_state: int = 42):
        self.log_reg = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=random_state)
        self.rf = RandomForestClassifier(n_estimators=100, max_depth=8, class_weight="balanced", random_state=random_state)

    def fit_and_evaluate(self, X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series) -> pd.DataFrame:
        results = []

        self.log_reg.fit(X_train, y_train)
        lr_probs = self.log_reg.predict_proba(X_test)[:, 1]
        lr_preds = (lr_probs >= 0.5).astype(int)
        results.append({
            "Model": "Logistic Regression (Baseline)",
            "Precision": round(float(precision_score(y_test, lr_preds, zero_division=0)), 4),
            "Recall": round(float(recall_score(y_test, lr_preds, zero_division=0)), 4),
            "F1-Score": round(float(f1_score(y_test, lr_preds, zero_division=0)), 4),
            "PR-AUC": round(float(average_precision_score(y_test, lr_probs)), 4),
            "ROC-AUC": round(float(roc_auc_score(y_test, lr_probs)), 4)
        })

        self.rf.fit(X_train, y_train)
        rf_probs = self.rf.predict_proba(X_test)[:, 1]
        rf_preds = (rf_probs >= 0.5).astype(int)
        results.append({
            "Model": "Random Forest (Baseline)",
            "Precision": round(float(precision_score(y_test, rf_preds, zero_division=0)), 4),
            "Recall": round(float(recall_score(y_test, rf_preds, zero_division=0)), 4),
            "F1-Score": round(float(f1_score(y_test, rf_preds, zero_division=0)), 4),
            "PR-AUC": round(float(average_precision_score(y_test, rf_probs)), 4),
            "ROC-AUC": round(float(roc_auc_score(y_test, rf_probs)), 4)
        })

        return pd.DataFrame(results)

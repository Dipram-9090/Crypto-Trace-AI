"""
Unit tests for Behavioral Clustering and Ransomware models.
"""

import pandas as pd
import numpy as np
from src.cryptotrace.models.clustering import BehavioralClusterer
from src.cryptotrace.models.ransomware_model import RansomwareClassifier


def test_behavioral_clustering():
    np.random.seed(42)
    X = pd.DataFrame(np.random.randn(30, 6), columns=[f"feat_{i}" for i in range(6)])
    clusterer = BehavioralClusterer(eps=1.5, min_samples=3)
    labels, coords = clusterer.fit_predict(X)
    assert len(labels) == 30
    assert coords.shape == (30, 2)


def test_ransomware_model():
    df_heist = pd.DataFrame(
        {
            "length": [5, 10, 2, 8],
            "weight": [1.5, 4.0, 0.5, 3.2],
            "count": [3, 15, 1, 10],
            "looped": [0, 4, 0, 3],
            "neighbors": [4, 12, 2, 8],
            "income": [1000000, 50000000, 500000, 30000000],
            "is_ransomware": [0, 1, 0, 1],
        }
    )
    model = RansomwareClassifier(n_estimators=10, max_depth=3)
    metrics = model.train(df_heist)
    assert "pr_auc" in metrics

    probs = model.predict_ransomware_prob(df_heist)
    assert len(probs) == 4

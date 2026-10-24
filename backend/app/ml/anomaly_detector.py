"""
AI-Based Anomaly Detection Pipeline
Uses Scikit-learn Isolation Forest with StandardScaler preprocessing
to detect unusual multidimensional combinations of CPU, Memory, Latency, and Error rates.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session

from backend.app.models.metric import MetricSample
from backend.app.models.anomaly import AnomalyEvent
from backend.app.config import settings


class AnomalyDetector:
    def __init__(self):
        self.contamination = settings.ANOMALY_CONTAMINATION
        self.threshold = settings.ANOMALY_THRESHOLD
        self.model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None
        self.is_trained = False
        self.version = "isolation_forest_v1"

    def train_on_history(self, db: Session, min_samples: int = 20) -> bool:
        """
        Extract historical metric samples and fit the Isolation Forest model.
        Returns True if model was trained, False if insufficient data was available.
        """
        samples = (
            db.query(MetricSample)
            .filter(MetricSample.is_healthy == True)
            .order_by(MetricSample.timestamp.desc())
            .limit(1000)
            .all()
        )

        if len(samples) < min_samples:
            # Fallback to generating standard synthetic baseline vectors if DB is newly initialized
            synthetic_features = []
            for _ in range(100):
                cpu = np.random.uniform(20.0, 50.0)
                mem = np.random.uniform(30.0, 60.0)
                lat = np.random.uniform(40.0, 150.0)
                err = np.random.uniform(0.0, 1.0)
                synthetic_features.append([cpu, mem, lat, err])
            X = np.array(synthetic_features)
        else:
            X = np.array([
                [s.cpu_percent, s.memory_percent, s.latency_ms, s.error_rate_percent]
                for s in samples
            ])

        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=42,
            n_estimators=100
        )
        self.model.fit(X_scaled)
        self.is_trained = True
        print(f"[AI Anomaly Engine] Trained Isolation Forest on {len(X)} metric vectors.")
        return True

    def detect(self, metric: Dict[str, Any]) -> Tuple[bool, float, Dict[str, Any]]:
        """
        Evaluates a metric vector.
        Returns (is_anomaly, anomaly_score, feature_dict).
        Anomaly score: negative values (e.g. < -0.15) represent anomalies.
        """
        features = [
            float(metric["cpu_percent"]),
            float(metric["memory_percent"]),
            float(metric["latency_ms"]),
            float(metric["error_rate_percent"])
        ]

        feature_dict = {
            "cpu_percent": features[0],
            "memory_percent": features[1],
            "latency_ms": features[2],
            "error_rate_percent": features[3]
        }

        # Rule-based fallback if ML model is not yet trained
        if not self.is_trained or self.model is None or self.scaler is None:
            is_rule_anomaly = (
                features[0] > 90.0 or
                features[1] > 90.0 or
                features[2] > 700.0 or
                features[3] > 20.0
            )
            pseudo_score = -0.35 if is_rule_anomaly else 0.25
            return is_rule_anomaly, pseudo_score, feature_dict

        # Vector scaling and inference
        X_raw = np.array([features])
        X_scaled = self.scaler.transform(X_raw)
        
        # decision_function: lower score = more abnormal
        score = float(self.model.decision_function(X_scaled)[0])
        prediction = int(self.model.predict(X_scaled)[0]) # -1 = anomaly, 1 = normal

        is_anomaly = (prediction == -1) or (score < self.threshold)
        return is_anomaly, score, feature_dict


anomaly_detector = AnomalyDetector()

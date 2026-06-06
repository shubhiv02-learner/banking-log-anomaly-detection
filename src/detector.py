from pathlib import Path
import joblib
import numpy as np
import pandas as pd


class EnsembleDetector:

    def __init__(self):

        BASE_DIR = Path(__file__).resolve().parent.parent

        models_dir = BASE_DIR / "models"

        self.if_model = joblib.load(
            models_dir / "IsolationForestRaw.joblib"
        )
        self.ocsvm_model = joblib.load(
            models_dir / "OneClassSVMRaw.joblib"
        )

        self.scaler = joblib.load(
            models_dir / "ml_features_robust_scaler_Raw.joblib"
        )

        self.label_encoder = joblib.load(
            models_dir / "service_label_encoder_Raw.joblib"
        )

        self.feature_columns = [
            "service",
            "latency_ms_mean",
            "latency_ms_max",
            "latency_ms_std",
            "cpu_usage_mean",
            "cpu_usage_max",
            "memory_usage_mean",
            "queue_lag_mean",
            "queue_lag_max",
            "error_count_sum"
        ]

        print("✅ Detector initialized")

    def preprocess(self, window_df):

        df = window_df.copy()

        # encode service
        try:
            df["service"] = self.label_encoder.transform(
                df["service"]
            )
        except ValueError:
            df["service"] = -1

        # same transformations used during training
        df["latency_ms_max"] = np.log1p(
            df["latency_ms_max"]
        )

        df["error_count_sum"] = np.log1p(
            df["error_count_sum"]
        )

        X = df[self.feature_columns]

        X_scaled_numpy = self.scaler.transform(X)
        X_scaled = pd.DataFrame(
            X_scaled_numpy,
            columns=self.feature_columns
        )

        return X_scaled

    def score_window(self, window_df):
        #print("Scoring window:")
        
        X_scaled = self.preprocess(window_df)
        if_scores = -self.if_model.decision_function(
            X_scaled
        )

        ocsvm_scores = -self.ocsvm_model.decision_function(
            X_scaled
        )
        input("Press Enter to see the scores...")
        print(f"Isolation Forest score: {if_scores[0]:.4f}, One-Class SVM score: {ocsvm_scores[0]:.4f}")
        return {
            "if_score_raw": float(if_scores[0]),
            "ocsvm_score_raw": float(ocsvm_scores[0])
        }
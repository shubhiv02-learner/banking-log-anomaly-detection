#Read thresholds from config.py
#Use rolling MinMax normalization
#Use separate history for each metric
#Handle startup warm-up period
#Calculate ML Score
#Calculate Statistical Score
#Calculate Final Ensemble Score
#Assign Priority
#Return complete scoring output

from collections import deque

from config import (
    GLOBAL_THRESHOLD,
    CRITICAL_THRESHOLD,
    HIGH_THRESHOLD,
    MEDIUM_THRESHOLD,
    ROLLING_NORMALIZATION_WINDOW,
    NORMALIZATION_WARMUP_WINDOWS,
    ML_IF_WEIGHT,
    ML_OCSVM_WEIGHT,
    STAT_EWMA_WEIGHT,
    STAT_CUSUM_WEIGHT,
    STAT_PERSISTENCE_WEIGHT,
    STAT_INCIDENT_WEIGHT,
    FINAL_ML_WEIGHT,
    FINAL_STAT_WEIGHT
)


class RollingNormalizer:

    def __init__(self):

        self.history = deque(
            maxlen=ROLLING_NORMALIZATION_WINDOW
        )

    def normalize(self, value):

        value = float(value)

        self.history.append(value)

        # Warm-up period
        if len(self.history) < NORMALIZATION_WARMUP_WINDOWS:
            return 0.5

        min_val = min(self.history)
        max_val = max(self.history)

        if max_val == min_val:
            return 0.5

        return (
            (value - min_val)
            /
            (max_val - min_val)
        )


class EnsembleEngine:

    def __init__(self):

        self.if_normalizer = RollingNormalizer()

        self.ocsvm_normalizer = RollingNormalizer()

        self.ewma_normalizer = RollingNormalizer()

        self.cusum_normalizer = RollingNormalizer()

        self.persistence_normalizer = RollingNormalizer()

        self.incident_normalizer = RollingNormalizer()

    def get_priority(self, score):

        if score >= CRITICAL_THRESHOLD:
            return "Critical"

        elif score >= HIGH_THRESHOLD:
            return "High"

        elif score >= MEDIUM_THRESHOLD:
            return "Medium"

        return "Low"

    def predict(self,features):
        if_score = features["if_score"]
        ocsvm_score = features["ocsvm_score"]
        ewma = features["ewma"]
        cusum = features["cusum"]
        persistence = features["persistence"]
        incident_probability = features["incident_probability"]

        # -----------------------------
        # ML Normalization
        # -----------------------------
        
        if_norm = (self.if_normalizer.normalize(if_score))
        ocsvm_norm = (self.ocsvm_normalizer.normalize(ocsvm_score))

        ml_score = (
            ML_IF_WEIGHT * if_norm
            +
            ML_OCSVM_WEIGHT * ocsvm_norm
        )

        # -----------------------------
        # Statistical Normalization
        # -----------------------------

        ewma_norm = (
            self.ewma_normalizer.normalize(
                ewma
            )
        )

        cusum_norm = (
            self.cusum_normalizer.normalize(
                cusum
            )
        )

        persistence_norm = (
            self.persistence_normalizer.normalize(
                persistence
            )
        )

        incident_norm = (
            self.incident_normalizer.normalize(
                incident_probability
            )
        )

        statistical_score = (

            STAT_EWMA_WEIGHT * ewma_norm
            +
            STAT_CUSUM_WEIGHT * cusum_norm
            +
            STAT_PERSISTENCE_WEIGHT * persistence_norm
            +
            STAT_INCIDENT_WEIGHT * incident_norm

        )

        # -----------------------------
        # Final Ensemble Score
        # -----------------------------

        final_score = (
            FINAL_ML_WEIGHT * ml_score
            +
            FINAL_STAT_WEIGHT * statistical_score
        )

        prediction = (
            final_score >= GLOBAL_THRESHOLD
        )

        priority = (
            self.get_priority(
                final_score
            )
        )

        return {

                    "if_score_norm": round(if_norm, 4),
                    "ocsvm_score_norm": round(ocsvm_norm, 4),
                    "ewma_norm": round(ewma_norm, 4),
                    "cusum_norm": round(cusum_norm, 4),
                    "persistence_norm": round(persistence_norm, 4),
                    "incident_prob_norm": round(incident_norm, 4),
                    "ml_score": round(ml_score, 4),
                    "statistical_score": round(statistical_score, 4),
                    "final_score": round(final_score, 4),
                    "prediction": prediction,
                    "priority": priority
                }
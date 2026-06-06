#EWMA          -> Continuous
#Persistence   -> Continuous
#CUSUM         -> Daily Reset
#Incident Prob -> Daily Reset of maxima

from collections import defaultdict
from datetime import date

from kafka import record


class StreamMetrics:

    def __init__(self):

        self.state = defaultdict(
            lambda: {
                "ewma": 0.0,
                "cusum": 0.0,
                "persistence": 0,
                "last_date": None,
                "max_persistence": 1,
                "max_error_count": 1,
                "max_cpu_usage": 1
            }
        )

        self.alpha = 0.3
        self.cusum_k = 10

    def update(self, record):

        service = record["service"]
        current_date = record["timestamp"].date()
        latency_ms = record["latency_ms"]
        state = self.state[service]

        # -----------------
        # Daily CUSUM Reset
        # -----------------

        if (
            state["last_date"] is not None
            and current_date != state["last_date"]
        ):
            state["cusum"] = 0
            state["max_persistence"] = 1
            state["max_error_count"] = 1
            state["max_cpu_usage"] = 1

            state["last_date"] = current_date

        # -----------------
        # EWMA
        # -----------------

        if state["ewma"] == 0:
            state["ewma"] = latency_ms
        else:
            state["ewma"] = (
                self.alpha * latency_ms
                +
                (1 - self.alpha) * state["ewma"]
            )

        # -----------------
        # CUSUM
        # -----------------

        state["cusum"] = max(
            0,
            state["cusum"]
            +
            (latency_ms - self.cusum_k)
        )

        # -----------------
        # Alerts
        # -----------------

        ewma_alert = (
            state["ewma"] > 100
        )

        cusum_alert = (
            state["cusum"] > 200
        )

        combined_alert = (
            ewma_alert or cusum_alert
        )

        # -----------------
        # Persistence
        # -----------------

        if combined_alert:
            state["persistence"] += 1
        else:
            state["persistence"] = 0

        #Need to track max persistence, error count and cpu_usage for Normalization
        state["max_persistence"] = max(
            state["max_persistence"],
            state["persistence"])
        state["max_error_count"] = max(
            state["max_error_count"],
            record["error_count"])
        state["max_cpu_usage"] = max(
            state["max_cpu_usage"],
            record["cpu_usage"])
        
        persistence_norm = (state["persistence"]/state["max_persistence"])
        error_norm = (record["error_count"]/state["max_error_count"])
        cpu_norm = ( record["cpu_usage"]/state["max_cpu_usage"])
        incident_probability =(0.4 * persistence_norm)+(0.3 * error_norm)+(0.3 * cpu_norm)
        
        # -----------------
        # Output Record
        # -----------------
        #print(f"Service: {service}, EWMA: {state['ewma']:.2f}, CUSUM: {state['cusum']:.2f}, Persistence: {state['persistence']}, Incident Probability: {incident_probability:.2f}")
        record["ewma"] = state["ewma"]
        record["cusum"] = state["cusum"]
        record["persistence_score"] = state["persistence"]
        record["incident_probability"] = incident_probability
        #record["priority"] = self.get_priority(incident_probability)
        #Will show priority in the dashboard based on the ensemble model aggregated score, not the stream metrics score alone
        return record
    
    def get_priority(prob):

        if prob >= 0.7:
            return "Critical"
        elif prob >= 0.5:
            return "High"
        elif prob >= 0.3:
            return "Medium"
        return "Low"
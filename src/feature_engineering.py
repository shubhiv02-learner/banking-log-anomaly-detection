import pandas as pd


def create_window_features(records):

    df = pd.DataFrame(records)
    #print("Creating window features for service:")
    window_df = (
        df.groupby("service")
        .agg({
            "latency_ms": ["mean", "max", "std"],
            "cpu_usage": ["mean", "max"],
            "memory_usage": ["mean"],
            "queue_lag": ["mean", "max"],
            "error_count": ["sum"],
            "ewma": ["mean"],
            "cusum": ["max"],
            "persistence_score": ["mean"],
            "incident_probability": ["mean"]
        })
    )
    #print("Aggregation done for service:")

    window_df.columns = [
        "_".join(col)
        for col in window_df.columns
    ]
    #print("Column flattening done for service:")
    window_df = window_df.reset_index()
    window_df = window_df.fillna(0)
    print(window_df.head())
    #input("Press Enter to continue...")
    return window_df
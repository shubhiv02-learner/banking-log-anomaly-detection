import pandas as pd
import numpy as np

SERVICE_LATENCY_MAP = {
    "payment-api": 150,
    "auth-service": 80,
    "trading-engine": 100,
    "fraud-detection": 200,
    "notification-service": 70,
    "portfolio-service": 120,
    "investment-engine": 130
}
# ============================================================
# STEP 3 — EWMA DRIFT DETECTION
# ============================================================

def apply_ewma_detection(df, alpha=0.3):

    """
    Applies EWMA anomaly detection.

    EWMA helps detect gradual operational drift
    before systems cross critical thresholds.

    Parameters:
    -----------
    df : pandas.DataFrame
        Banking observability dataset

    alpha : float
        EWMA smoothing factor
        typically between 0 and 1, which dictates how quickly the average adapts to new data
        Higher the value it reacts faster to recent changes

    Returns:
    --------
    df : pandas.DataFrame
        Updated dataframe with EWMA metrics

    threshold : float
        Dynamic anomaly threshold
    """
    # Compute EWMA latency trend based on raw latency_ms (for plotting compatibility)
    df['ewma_latency'] = (round(df['latency_ms'].ewm(alpha=alpha).mean(),2))

    # Dynamic anomaly threshold for raw latency (for dashboard plotting purposes)
    raw_latency_plot_threshold = (df['ewma_latency'].mean()+ 2*df['ewma_latency'].std())

    # Calculate expected base latency for each service
    df['expected_base_latency'] = df['service'].map(SERVICE_LATENCY_MAP)

    # Calculate latency deviation from the expected base latency
    df['latency_deviation'] = df['latency_ms'] - df['expected_base_latency']
    df['latency_deviation'] = df['latency_deviation'].abs()
    # Compute EWMA latency deviation trend for actual anomaly detection
    df['ewma_latency_deviation_for_alert'] = (round(df['latency_deviation'].ewm(alpha=alpha).mean(),2))

    # Dynamic anomaly threshold based on deviation for alerting
    # The mean of ewma_latency_deviation_for_alert should ideally be close to 0 if the system is stable.
    deviation_alert_threshold = (
        df['ewma_latency_deviation_for_alert'].abs().mean()+2 * df['ewma_latency_deviation_for_alert'].std()
        )
    print(f"Raw Latency Plot Threshold (for dashboard): {raw_latency_plot_threshold}")
    print(f"Deviation Alert Threshold (for detection): {deviation_alert_threshold}")
    # Flag anomalous drift regions based on deviation
    df['ewma_alert'] = (
        (df['ewma_latency_deviation_for_alert'].abs() > deviation_alert_threshold)
    )

    print("EWMA detection completed.\n")
    print(f"Raw Latency Plot Threshold (for dashboard): {raw_latency_plot_threshold}")
    print(f"Deviation Alert Threshold (for detection): {deviation_alert_threshold}")
    return df, raw_latency_plot_threshold # Return the threshold for raw latency for dashboard compatibility


# ============================================================
# STEP 4 — CUSUM DETECTION
# ============================================================

def apply_cusum_detection(df):

    """
    Applies CUSUM detection.

    CUSUM identifies cumulative deviations
    from normal operational behavior.

    Useful for:
    - silent degradation
    - queue accumulation
    - sustained instability
    """
    # Ensure latency_deviation is available (compute if not already)
    if 'latency_deviation' not in df.columns:
        df['expected_base_latency'] = df['service'].map(SERVICE_LATENCY_MAP)
        df['latency_deviation'] = df['latency_ms'] - df['expected_base_latency']


    mu = df['latency_ms'].std()
    k = mu * 0.5
    print(f"CUSUM Smoothing Factor (k): {k}")
    h = mu*5 #ideally should be 5 or 6
    print(f"CUSUM Alert Threshold (for detection): {h}")

    # Target for deviation
    target = 0 # Ideally should be 0

    cusum_values = []
    current_cusum_sum = 0.0 # Initialize cumulative sum for each day
    # Convert timestamp to datetime if not already (good for plotting)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['logdate'] = df['timestamp'].dt.date # Add logdate column

    if not df.empty:
        prev_date = df['timestamp'].iloc[0].date()
    else:
        print("DataFrame is empty, cannot apply CUSUM detection.")
        return df

    for i in range(len(df)):
        current_date = df['logdate'].iloc[i]
        latency_dev = df['latency_deviation'].iloc[i]

        if current_date != prev_date:
            # Date has changed, reset the CUSUM sum for the new day
            current_cusum_sum = 0.0
            prev_date = current_date
          

        # Calculate CUSUM for the current point
        current_cusum_sum = round(max(0.0, current_cusum_sum + (latency_dev - target - k)), 2)
        cusum_values.append(current_cusum_sum)

    df['cusum'] = cusum_values

    # Alert threshold
    df['cusum_alert'] = (df['cusum'] > h)

    print("CUSUM detection completed.\n")

    return df


# ============================================================
# STEP 5 — PERSISTENCE SCORING
# ============================================================

def calculate_persistence_score(df):

    """
    Measures anomaly persistence duration.
    Persistent anomalies are treated as
    higher operational risks than isolated spikes.
    """

    # Combine anomaly signals
    df['combined_alert'] = ( df['ewma_alert'] | df['cusum_alert'])

    persistence = []
    count = 0

    for val in df['combined_alert']:
        if val:
            count += 1
        else:
            count = 0

        persistence.append(count)

    df['persistence_score'] = persistence
    print("Persistence scoring completed.\n")

    return df


# ==================================
# STEP 6 — CORRELATION ANALYSIS
# ==================================

def generate_correlation_analysis(df):

    correlation = df[
        [
            'latency_deviation',
            'error_count',
            'cpu_usage',
            'ewma_latency_deviation_for_alert',
            'cusum',
            'persistence_score',
            'incident_probability'
        ]
    ].corr().round(2)

    print("\nCorrelation Matrix:\n")

    custom_labels = ['Latency', 'Errors',  'CPU','EWMA','CUSUM','PS','IP']
    correlation.columns = custom_labels
    correlation.index = custom_labels
    print(correlation)
    print('\n\n')
    return correlation


# ============================================
# STEP 7 — BAYESIAN PRIORITIZATION
# ============================================

def apply_bayesian_prioritization(df):
    import pandas
    df['incident_probability'] = (round(

        0.4 * (df['persistence_score'] / df['persistence_score'].max())
        +
        0.3 * (df['error_count']/df['error_count'].max())
        +
        0.3 * (df['cpu_usage']/df['cpu_usage'].max()), 2)
    )

    df['priority'] = pandas.cut(df['incident_probability'], bins=[0, 0.3, 0.5, 0.7,1],
        labels=['Low','Medium','High','Critical'])

    df['priority'] = df['priority'].astype(str)
    return df

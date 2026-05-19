
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

    # Compute EWMA latency trend
    df['ewma_latency'] = (
        df['latency_ms']
        .ewm(alpha=alpha)
        .mean()
    )

    """
    e.g. Mean: 100 Std Dev: 10  Threshold: (100 + (2*10))= 120ms
    If the EWMA trend hits 125ms, the code flags it because it has moved significantly further than the usual "wiggle" room.
    """
    # Dynamic anomaly threshold
    threshold = (
        df['ewma_latency'].mean()
        +
        2 * df['ewma_latency'].std()
    )

    # Flag anomalous drift regions
    df['ewma_alert'] = (
        df['ewma_latency'] > threshold
    )

    print("EWMA detection completed.\n")

    return df, threshold


# ============================================================
# STEP 4 — CUSUM DETECTION
# ============================================================

def apply_cusum_detection(df, k=5):

    """
    Applies CUSUM detection.

    CUSUM identifies cumulative deviations
    from normal operational behavior.

    Useful for:
    - silent degradation
    - queue accumulation
    - sustained instability
    """

    target = df['latency_ms'].mean()

    cusum = [0]

    for x in df['latency_ms'][1:]:

        s = max(
            0,
            cusum[-1] + (x - target - k)
        )

        cusum.append(s)

    df['cusum'] = cusum

    # Alert threshold
    df['cusum_alert'] = (
        df['cusum'] > 50
    )

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
    df['combined_alert'] = (
        df['ewma_alert'] | df['cusum_alert']
    )

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
            'latency_ms',
            'error_count',
            'cpu_usage'
        ]
    ].corr()

    print("\nCorrelation Matrix:\n")
    print(correlation)

    return correlation


# ===========================================
# STEP 7 — BAYESIAN PRIORITIZATION
# ===========================================

def apply_bayesian_prioritization(df):
    import pandas 
    df['incident_probability'] = (

        0.4 * (
            df['persistence_score'] / df['persistence_score'].max()
        )

        +

        0.3 * (
            df['error_count']/df['error_count'].max()
        )

        +

        0.3 * (
            df['cpu_usage']/df['cpu_usage'].max()
        )
    )

    df['priority'] = pandas.cut(

        df['incident_probability'],

        bins=[0, 0.3, 0.6, 1],

        labels=[
            'Low',
            'Medium',
            'Critical'
        ]
    )

    return df

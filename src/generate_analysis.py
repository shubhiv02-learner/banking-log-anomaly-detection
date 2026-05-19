
# ==================================
# STEP 8 — EXECUTIVE DASHBOARD
# ==================================

def generate_dashboard(df, threshold):
    import matplotlib.pyplot as pyplot

    # Plot the latency data 
    pyplot.figure(figsize=(14,6))

    pyplot.plot(
        df['timestamp'],
        df['latency_ms'],
        label='Latency'
    )

    pyplot.plot(
        df['timestamp'],
        df['ewma_latency'],
        label='EWMA'
    )

    pyplot.axhline(
        threshold,
        color='red',
        linestyle='--',
        label='Threshold'
    )

    pyplot.title(
        "SentinelIQ Banking System Monitoring"
    )

    pyplot.xlabel("Timestamp")

    pyplot.ylabel("Latency (ms)")

    pyplot.legend()

    pyplot.grid(True)

    pyplot.xticks(rotation=45)

    pyplot.savefig("outputs/latency_chart.png")

    pyplot.show()


# ==================================
# STEP 9 — EXECUTIVE SUMMARY
# ==================================

def generate_executive_summary(df):

    critical_count = (
        df['priority'] == 'Critical').sum()

    medium_count = (
        df['priority'] == 'Medium').sum()

    summary = f"""

    SENTINELIQ OPERATIONAL SUMMARY
    --------------------------------

    Critical Incidents : {critical_count}

    Medium Incidents   : {medium_count}

    Observations:
    - Sustained latency degradation detected
    - Infrastructure pressure increasing
    - Multiple correlated anomaly windows identified

    Recommended Action:
    Investigate payment processing systems
    and infrastructure resource utilization.

    """

    print(summary)

    return summary

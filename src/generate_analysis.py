SERVICE_LATENCY_MAP = {
    "payment-api": 150,
    "auth-service": 80,
    "trading-engine": 100,
    "fraud-detection": 200,
    "notification-service": 70,
    "portfolio-service": 120,
    "investment-engine": 130
}
# ==================================
# STEP 8 — EXECUTIVE DASHBOARD
# ==================================

def generate_dashboard(df, threshold):
    import matplotlib.pyplot as pyplot
    import pandas as pd # Import pandas here for to_datetime

    # Convert timestamp to datetime if not already (good for plotting)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Plot the latency data
    pyplot.figure(figsize=(14,6))

    pyplot.plot(
        df['timestamp'],
        df['latency_deviation'],
        label='Adjusted Latency per service'
    )

    pyplot.plot(
        df['timestamp'],
        df['ewma_latency_deviation_for_alert'],
        label='EWMA'
    )

    critical_df = df[df['priority'] == 'Critical']
    high_df = df[df['priority'] == 'High']

    # Plot critical priority as scatter points on the latency axis
    pyplot.scatter(
        critical_df['timestamp'],
        critical_df['latency_deviation'], # Plot latency at critical priority
        color='purple',
        marker='X', # Use 'X' marker for critical priority
        s=100, # Size of the marker
        label='Critical Priority'
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

    pyplot.ylabel("Adjusted Latency per service(ms)")

    pyplot.legend()

    pyplot.grid(True)

    pyplot.xticks(rotation=45)

    pyplot.savefig("visualizations/latency_chart.png")

    pyplot.show()


# ==================================
# STEP 9 — EXECUTIVE SUMMARY
# ==================================

def generate_executive_summary(df):

    critical_count = (
        df['priority'] == 'Critical').sum()

    high_count = (
        df['priority'] == 'High').sum()
    medium_count = (
        df['priority'] == 'Medium').sum()


    summary = f"""

    SENTINELIQ OPERATIONAL SUMMARY
    --------------------------------
    Total Incidents : {len(df)}
    Critical Incidents : {critical_count}
    High Incidents   : {high_count}
    Medioum Incidents   : {medium_count}


    OBSERVATIONS
    ------------

    - Sustained latency degradation detected
    - Infrastructure pressure increasing
    - Multiple correlated anomaly windows identified

    Recommended Action:

    -----------------
    Investigate payment processing systems
    and infrastructure resource utilization.

    """
    print(summary)

    return summary


def write_pdf_report(file_path, content):
    from reportlab.platypus import SimpleDocTemplate
    from reportlab.lib.pagesizes import letter

    pdf = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=30
    )
    pdf.build(content)
    print(f"PDF generated successfully: {file_path}")

def generate_executive_summary_report(df):
    from reportlab.platypus import (Paragraph, Spacer, Image)
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.platypus.flowables import HRFlowable

    # ============================================================
    # PDF REPORT GENERATION
    # ============================================================

    pdf_file = "reports/banking_anomaly_report.pdf"

    styles = getSampleStyleSheet()
    content = []

    # ============================================================
    # TITLE
    # ============================================================

    content.append(Paragraph(
        "<b>SentinelIQ Banking Anomaly Detection Report</b>",
        styles['Title']
    ))

    content.append(Spacer(1, 20))

    # ============================================================
    # EXECUTIVE SUMMARY
    # ============================================================

    content.append(Paragraph(
        "<b>Executive Summary</b>",
        styles['Heading1']
    ))

    Total_count = len(df)
    critical_count = ( df['priority'] == 'Critical').sum()
    high_count = ( df['priority'] == 'High').sum()
    medium_count = ( df['priority'] == 'Medium').sum()

    content.append(Paragraph(
        "<b>SENTINELIQ OPERATIONAL SUMMARY</b>",
        styles['Heading2']
    ))
    summary = f"""

    \n\n

    Total Incidents : {Total_count}\n
    Critical Incidents : {critical_count}\n
    High Incidents   : {high_count}\n
    Medium Incidents   : {medium_count}\n\n

    """
    executive_summary_text = """
    This report provides an overview of simulated banking logs,
    observed anomalies, service failures, and system health metrics.

    Key findings include:

    • Increased authentication failures during peak traffic.
    • Elevated fraud detection alerts from payment-api.
    • Trading-engine latency spikes observed intermittently.
    • Isolation Forest identified suspicious transaction patterns.

    Overall system stability remained acceptable, though multiple
    high-severity anomalies require operational review.
    """
    summary = summary + executive_summary_text
    print(summary)
    content.append(Paragraph(summary, styles['BodyText']))

    content.append(Spacer(1, 15))

    # Horizontal line
    content.append(HRFlowable(width="100%", color=colors.grey))
    content.append(Spacer(1, 15))

    # ============================================================
    # PNG IMAGE / CHART
    # ============================================================

    content.append(Paragraph(
        "<b>Anomaly Trend Visualization</b>",
        styles['Heading2']
    ))

    # PNG image path
    image_path = "visualizations/latency_chart.png"

    # Add image
    img = Image(image_path, width=450, height=250)
    content.append(img)

    content.append(Spacer(1, 20))

    # ============================================================
    # SAMPLE TABLE (Commented out in original, keeping it that way)
    # ============================================================

    content.append(Paragraph(
        "<b>Service Error Summary</b>",
        styles['Heading2']
    ))
    """
    # Example table data
    service_data = [
        ["Service", "Error Count", "Severity"],
        ["payment-api", "42", "High"],
        ["auth-service", "31", "Medium"],
        ["fraud-detection", "15", "Critical"],
        ["trading-engine", "22", "High"]
    ]

    # Create table
    service_table = Table(service_data, colWidths=[180, 120, 120])

    # Table styling
    service_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]))

    content.append(service_table)

    content.append(Spacer(1, 25))
    """
    # ============================================================
    # ADDITIONAL INSIGHTS
    # ============================================================

    content.append(Paragraph(
        "<b>Observations</b>",
        styles['Heading1']
    ))

    observations = """
    The anomaly distribution indicates that most failures originated
    from authentication and payment processing systems.

    The fraud-detection service generated fewer events but showed
    higher severity anomalies.

    Further monitoring and alert correlation is recommended.
    """

    content.append(Paragraph(observations, styles['BodyText']))

    # ============================================================
    # BUILD PDF
    # ============================================================
    write_pdf_report(pdf_file, content)

    return

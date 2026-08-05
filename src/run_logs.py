import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logging_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

import pandas as pd

import generate_banking_logs_metrics as banking_utils
import generate_analysis as analysis_utils

df = pd.read_csv("data/banking_logs.csv")
logger.info("Loaded banking_logs.csv rows=%s", len(df))

logger.info("Applying EWMA detection")
df, threshold = banking_utils.apply_ewma_detection(df)

logger.info("Applying CUSUM detection")
df = banking_utils.apply_cusum_detection(df)

logger.info("Calculating persistence scores")
df = banking_utils.calculate_persistence_score(df)

logger.info("Applying Bayesian prioritization")
df = banking_utils.apply_bayesian_prioritization(df)

logger.info("Running correlation analysis")
correlation = banking_utils.generate_correlation_analysis(df)
logger.debug("Correlation matrix shape=%s", getattr(correlation, "shape", None))

logger.info("Generating monitoring dashboard")
analysis_utils.generate_dashboard(df, threshold)

logger.info("Generating executive summary")
summary = analysis_utils.generate_executive_summary(df)
analysis_utils.generate_executive_summary_report(df)

df.to_csv("outputs/sentineliq_results.csv", index=False)
logger.info("Wrote outputs/sentineliq_results.csv")

with open("outputs/executive_summary.txt", "w") as f:
    f.write(summary)
logger.info("Wrote outputs/executive_summary.txt")

logger.info("Offline pipeline completed")

import pandas as pd
import json

import generate_banking_logs_metrics as banking_utils
import generate_analysis as analysis_utils

# Load the banking_logs.csv file into a DataFrame
df = pd.read_csv('data/banking_logs.csv')

print("Loaded 'data/banking_logs.csv' into 'df'.")

# Display the first 5 rows of the DataFrame
print(df.head())

print("Applying EWMA Detection...\n")
df, threshold = banking_utils.apply_ewma_detection(df)

print("Applying CUSUM Detection...\n")
df = banking_utils.apply_cusum_detection(df)

print("Calculating Persistence Scores...\n")
df = banking_utils.calculate_persistence_score(df)

print("Applying Bayesian Prioritization...\n")
df = banking_utils.apply_bayesian_prioritization(df)

print("Running Correlation Analysis...\n")
correlation = banking_utils.generate_correlation_analysis(df)

# Display the first 5 rows of the DataFrame after metrics updation
print(df.head())

print("Generating Monitoring Dashboard...\n")
analysis_utils.generate_dashboard(df, threshold)

print("Generating Executive Summary...\n")
summary = analysis_utils.generate_executive_summary(df)
analysis_utils.generate_executive_summary_report(df)

# Save outputs
df.to_csv("outputs/sentineliq_results.csv",index=False )
print("Output with metrics saved to outputs/sentineliq_results.csv ")

with open('outputs/executive_summary.txt', 'w') as f:
      f.write(summary)
print("Executive summary saved to 'outputs/executive_summary.txt'")

print("\nPipeline Execution Completed.\n")

# SentryyIQ – Banking Anomaly Detection & Observability Platform

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-orange)
![Google Colab](https://img.shields.io/badge/Google-Colab-F9AB00)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-green)

---

# Overview

SentryyIQ is a hybrid statistical + machine learning anomaly detection framework designed for operational banking telemetry and observability monitoring.

The platform combines:

* rolling statistical intelligence,
* temporal anomaly analysis,
* unsupervised machine learning,
* and ensemble anomaly scoring

to identify abnormal operational behavior in simulated banking environments.

The project evaluates anomaly detection methodologies across:

* raw operational telemetry,
* rolling-window aggregation,
* engineered statistical feature spaces,
* and ensemble intelligence frameworks.

---

# Keywords

`Anomaly Detection` `Banking Telemetry` `Observability` `Isolation Forest` `One-Class SVM` `LOF` `Machine Learning` `Statistical Monitoring` `Rolling Window Analytics` `Operational Intelligence` `Incident Detection` `Ensemble Models` `Python` `Scikit-Learn` `Google Colab`

---

# Architecture Diagram

```text
                           ┌────────────────────┐
                           │ Banking Telemetry  │
                           │  Synthetic Logs    │
                           └─────────┬──────────┘
                                     │
                         ┌───────────▼───────────┐
                         │ Data Preprocessing    │
                         │ Cleaning & Encoding   │
                         └───────────┬───────────┘
                                     │
                 ┌───────────────────┼───────────────────┐
                 │                                       │
       ┌─────────▼─────────┐                 ┌───────────▼───────────┐
       │ Rolling Window     │                 │ Statistical Features  │
       │ Aggregation        │                 │ EWMA / CUSUM / Drift/ Prioritization │
       └─────────┬─────────┘                 └───────────┬───────────┘
                 │                                       │
                 └───────────────────┬───────────────────┘
                                     │
                      ┌──────────────▼──────────────┐
                      │ Feature Engineering Layer   │
                      └──────────────┬──────────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
┌─────────▼────────┐     ┌──────────▼─────────┐     ┌──────────▼──────────┐
│ Isolation Forest │     │ One-Class SVM      │     │ Local Outlier Factor │
└─────────┬────────┘     └──────────┬─────────┘     └──────────┬──────────┘
          │                          │                          │
          └──────────────────┬───────┴──────────────────────────┘
                             │
                ┌────────────▼────────────┐
                │ Ensemble Anomaly Score  │
                │ Weighted Aggregation    │
                └────────────┬────────────┘
                             │
                 ┌───────────▼───────────┐
                 │ Incident Prioritization│
                 │ Threshold Evaluation   │
                 └────────────────────────┘
```

---
Data Flow :

Kafka Record
      |
stream_metrics.py
      |
EWMA
CUSUM
Persistence
      |
Buffer
      |
5-Min Aggregation
      |
feature_engineering.py
      |
Incident Probability
Priority
      |
detector.py
      |
Final Ensemble

# Features

## Statistical Intelligence Layer

* Rolling-window aggregation
* EWMA trend monitoring
* CUSUM drift detection
* Temporal persistence analysis
* Statistical anomaly indicators

---

## Machine Learning Models

Implemented unsupervised anomaly detection models:

* Isolation Forest
* One-Class SVM
* Local Outlier Factor (LOF)

---

## Ensemble Intelligence

* Weighted anomaly score aggregation
* Percentile-based thresholding
* Adaptive anomaly prioritization

---

# Experimental Methodologies

| Methodology                    | Description                          |
| ------------------------------ | ------------------------------------ |
| Raw Operational Data           | Event-level anomaly detection        |
| Rolling Window Aggregation     | Temporal anomaly intelligence        |
| Statistical + Rolling Features | Engineered operational feature space |
| Weighted Ensemble Scoring      | Combined anomaly ranking             |

---

# Model Performance Summary

## Raw Operational Data

| Model            | Precision | Recall | F1   | ROC-AUC |
| ---------------- | --------- | ------ | ---- | ------- |
| Isolation Forest | 0.93      | 0.98   | 0.96 | 0.9892  |

---

## Raw Data + Rolling Window Aggregation

| Model            | Precision | Recall | F1     | ROC-AUC | PR-AUC |
| ---------------- | --------- | ------ | ------ | ------- | ------ |
| Isolation Forest | 1.0000    | 0.8105 | 0.8953 | 0.9594  | 0.8498 |
| One-Class SVM    | 0.1523    | 0.7053 | 0.2505 | 0.8698  | 0.5601 |
| LOF              | 0.0130    | 0.0947 | 0.0229 | 0.2798  | 0.0289 |

---

## Ensemble Model

### Configuration

* Isolation Forest Weight: 0.8
* One-Class SVM Weight: 0.2

| Metric    | Score  |
| --------- | ------ |
| Precision | 0.3333 |
| Recall    | 1.0000 |
| F1-Score  | 0.5000 |
| ROC-AUC   | 0.9967 |
| PR-AUC    | 0.5000 |

---

# Ensemble Score Distribution

| Metric          | Value  |
| --------------- | ------ |
| Minimum Score   | 0.1208 |
| Maximum Score   | 0.8659 |
| 95th Percentile | 0.4720 |
| 97th Percentile | 0.5117 |
| 99th Percentile | 0.6211 |

---

# Key Findings

* Isolation Forest consistently delivered the strongest anomaly detection performance.
* Raw operational telemetry preserved anomaly separability effectively.
* Rolling-window aggregation improved temporal anomaly awareness.
* One-Class SVM improved anomaly sensitivity but increased false positives.
* LOF struggled within transformed rolling statistical feature spaces.
* Weighted ensemble scoring improved anomaly coverage and operational sensitivity.

---

# Tech Stack

* Python
* Google Colab
* Pandas
* NumPy
* Scikit-learn
* Matplotlib
* Seaborn

---

# Project Structure

```text
banking-log-anomaly-detection/
│
├── notebooks/              # Google Colab notebooks. All logic in notebook
├── src/                    # Core anomaly detection modules to be added
├── data/                   # Generated telemetry datasets
├── reports/                # Evaluation reports and summaries
├── visualizations/         # ROC, PR curves and anomaly timelines
├── README.md
└── requirements.txt
```

---

# Current Progress

## Implemented

* Statistical anomaly framework
* Rolling-window feature engineering
* Unsupervised ML anomaly detection
* Ensemble scoring framework
* Comparative model evaluation

## In Progress

* ROC/PR curve visualizations
* Anomaly timeline visualization
* Threshold optimization
* Benchmarking framework

## Planned Enhancements

* Autoencoder anomaly detection
* Multi-layer anomaly intelligence
* Dynamic risk scoring
* Real-time streaming detection
* Production observability dashboard

---

# Future Vision

SentryyIQ is evolving toward a multi-layer anomaly intelligence platform combining:

* statistical observability,
* machine learning anomaly detection,
* temporal operational intelligence,
* adaptive anomaly prioritization,
* and production-grade monitoring capabilities.

---

# Installation

```bash
git clone https://github.com/shubhiv02-learner/banking-log-anomaly-detection.git
pip install -r requirements.txt
```

---

# Usage

Run the notebooks directly in Google Colab:

```python
# Open notebook
SentryyIQ.ipynb
```

---

# License

MIT License

---


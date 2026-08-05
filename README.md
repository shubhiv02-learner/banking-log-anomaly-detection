# SentryyIQ – AI-Powered Operations Intelligence & Incident Management Platform

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?logo=react)
![Apache Kafka](https://img.shields.io/badge/Apache-Kafka-231F20?logo=apachekafka)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql)
![Machine Learning](https://img.shields.io/badge/Machine-Learning-orange)
![Generative AI](https://img.shields.io/badge/Generative-AI-purple)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-green)

---

## AI-Powered Operations Intelligence for Modern Enterprise Systems

SentryyIQ is an end-to-end **AI-powered Operations Intelligence Platform** that transforms real-time operational telemetry into actionable insights through streaming analytics, statistical intelligence, machine learning, automated incident management, interactive operational dashboards, and an AI Operations Copilot.

Designed around an event-driven architecture, the platform continuously ingests telemetry from distributed services using Apache Kafka, performs configurable window-based feature engineering, applies statistical and machine learning models to detect anomalies, and automatically generates prioritized operational alerts and incidents.

Beyond anomaly detection, SentryyIQ enriches operational data with contextual intelligence and provides an AI-powered Operations Copilot capable of investigating incidents, retrieving enterprise knowledge, assisting with Root Cause Analysis (RCA), and supporting engineers throughout the incident lifecycle using natural language interactions.

The project demonstrates how **stream processing, statistical analytics, machine learning, workflow automation, and Generative AI** can be combined to reduce operational noise, accelerate incident response, and improve production support for enterprise applications.

---

# 🌐 Project Portfolio

The complete project portfolio includes:

- Solution architecture
- System workflows
- Interactive dashboards
- AI Operations Copilot demonstrations
- Technical documentation
- End-to-end implementation details
- Live product demonstrations

**Portfolio**

https://portfolio-iota-taupe-91.vercel.app/projects/sentryyiq

---

# 🎬 Live Demonstrations

The portfolio contains complete demonstrations covering:

### Part 1 – Event Processing & Intelligent Alert Generation

- Kafka-based telemetry ingestion
- Window aggregation
- Feature engineering
- Statistical anomaly detection
- Machine learning inference
- Ensemble scoring
- Alert generation
- Incident creation

### Part 2 – Operational Intelligence Dashboards

- Executive operations dashboard
- Alert monitoring
- Incident management
- Service health analytics
- Statistical intelligence
- Machine learning analytics
- Ensemble analytics
- Forensic investigation

### Part 3 – AI Operations Copilot

- Conversational incident investigation
- Root Cause Analysis (RCA)
- Runbook retrieval
- Architecture documentation lookup
- Error catalog search
- Incident assignment
- Resolution workflows
- Knowledge-assisted operational support

# Problem Statement

Modern enterprise applications generate massive volumes of telemetry across distributed services, infrastructure components, and business transactions. While observability platforms can collect logs and metrics, engineering teams still spend significant time manually correlating information across multiple systems before identifying the root cause of production issues.

Common operational challenges include:

- High volumes of operational telemetry and alerts resulting in alert fatigue.
- Limited correlation between metrics, logs, and business impact.
- Fragmented operational knowledge spread across dashboards, documentation, and runbooks.
- Manual Root Cause Analysis (RCA) requiring extensive investigation across multiple systems.
- Difficulty prioritizing incidents based on operational risk and business impact.
- Slow Mean Time to Detect (MTTD) and Mean Time to Resolve (MTTR).
- Heavy reliance on experienced engineers for troubleshooting complex production issues.
- Lack of intelligent automation across the incident management lifecycle.

Traditional monitoring solutions primarily report **what happened**, leaving engineers responsible for determining **why it happened**, **how severe it is**, and **what actions should be taken next**.

---

# Solution Overview

SentryyIQ addresses these challenges by combining **stream processing, statistical intelligence, machine learning, workflow automation, and Generative AI** into a unified Operations Intelligence Platform.

Rather than treating anomaly detection, incident management, and AI assistance as independent capabilities, SentryyIQ integrates them into a single end-to-end workflow that transforms raw telemetry into actionable operational intelligence.

The platform continuously ingests telemetry from distributed services through Apache Kafka, aggregates operational metrics over configurable processing windows, and performs feature engineering to prepare data for intelligent analysis.

Each processing window is evaluated using a combination of statistical models and machine learning algorithms to identify abnormal operational behaviour. Multiple detection techniques are combined using a weighted ensemble scoring framework that generates an overall incident probability and prioritizes operational risk.

Detected anomalies automatically generate alerts and incidents, which are enriched with contextual information and presented through interactive operational dashboards.

The platform further extends incident management through an AI Operations Copilot that retrieves operational knowledge, performs evidence-based Root Cause Analysis (RCA), assists with investigation, and guides engineers throughout the incident lifecycle using natural language interactions.

This architecture creates a closed operational intelligence loop:


Telemetry → Analytics → Intelligence → Incidents → AI Investigation → Resolution

# 🚀 Key Highlights

## ⚡ Event-Driven Architecture

Designed around an event-driven processing pipeline for continuous operational intelligence.

- Real-time telemetry ingestion using Apache Kafka
- Scalable producer-consumer architecture
- Configurable window-based stream processing
- Automated feature engineering pipeline
- Near real-time operational analytics



## 📊 Statistical Intelligence

Continuously analyzes operational behaviour using rolling statistical models to identify trends, sustained degradation, and abnormal system behaviour.

**Implemented Models**

- Exponentially Weighted Moving Average (EWMA)
- Cumulative Sum (CUSUM)
- Persistence Scoring
- Rolling Window Analytics
- Trend Analysis

---

## 🤖 Machine Learning Intelligence

Applies unsupervised anomaly detection models capable of identifying unknown operational patterns without requiring labelled training data.

**Implemented Models**

- Isolation Forest
- One-Class Support Vector Machine (One-Class SVM)

**Capabilities**

- Feature-based anomaly detection
- Outlier identification
- Multi-dimensional operational analysis
- Adaptive anomaly scoring

---

## 🧠 Ensemble Intelligence

Combines outputs from statistical analytics and machine learning models into a weighted ensemble engine to improve detection accuracy and operational confidence.

**Capabilities**

- Weighted ensemble scoring
- Incident probability calculation
- Risk prioritization
- Severity classification
- Confidence-based anomaly detection

---

## 🚨 Automated Alert & Incident Management

Transforms high-confidence anomalies into actionable operational incidents.

**Capabilities**

- Automatic alert generation
- Incident creation
- Severity assignment
- Priority classification
- Incident lifecycle management
- Evidence preservation
- Historical incident tracking

---

## 📈 Operational Intelligence Dashboards

Provides real-time visibility into platform health, operational risk, and incident status through interactive dashboards.

**Dashboard Modules**

- Executive Operations Dashboard
- Alert Monitoring Dashboard
- Incident Management Dashboard
- Service Health Dashboard
- Statistical Analytics Dashboard
- Machine Learning Analytics Dashboard
- Ensemble Intelligence Dashboard
- Window Metrics Dashboard
- Trend Analysis & Reporting
- Interactive Forensic Investigation

---

## 🤖 AI Operations Copilot

Extends traditional observability with an intelligent operations assistant capable of investigating incidents using live operational data and enterprise knowledge.

**Capabilities**

- Conversational incident investigation
- Root Cause Analysis (RCA)
- Incident summarization
- Runbook retrieval
- Architecture documentation lookup
- Error catalog search
- SLA guidance
- Incident assignment
- Resolution assistance
- Knowledge-assisted troubleshooting
- Evidence-based recommendations

---

## 🔄 Workflow Automation

Automates operational processes using event-driven workflows and AI orchestration.

**Capabilities**

- AI workflow orchestration using n8n
- Incident lifecycle automation
- Telegram notifications
- Email notifications
- API-driven integrations
- Operational workflow execution

---

## 🏗 Enterprise-Ready Platform

Built using a modular architecture that enables future expansion into a complete Enterprise AI Operations ecosystem.

**Future Direction**

- Enterprise Knowledge Intelligence integration
- Retrieval-Augmented Generation (RAG)
- Hybrid Search
- LangGraph multi-agent workflows
- Enterprise knowledge repositories
- Context engineering
- Intelligent decision support

# 🏗 System Architecture

SentryyIQ follows a modular, event-driven architecture that transforms raw operational telemetry into intelligent operational insights through streaming analytics, statistical intelligence, machine learning, automated incident management, and AI-assisted investigation.

The platform separates telemetry processing, anomaly detection, operational intelligence, visualization, and AI reasoning into independent components, allowing each layer to scale and evolve independently.

```
                          ┌────────────────────────────┐
                          │ Banking Microservices      │
                          │ Synthetic Telemetry        │
                          └─────────────┬──────────────┘
                                        │
                                        ▼
                          ┌────────────────────────────┐
                          │ Apache Kafka               │
                          │ Event Streaming Platform   │
                          └─────────────┬──────────────┘
                                        │
                                        ▼
                          ┌────────────────────────────┐
                          │ Telemetry Consumer         │
                          │ Window Aggregation         │
                          │ Feature Engineering        │
                          └─────────────┬──────────────┘
                                        │
                ┌───────────────────────┼────────────────────────┐
                │                       │                        │
                ▼                       ▼                        ▼
      ┌────────────────┐      ┌────────────────┐      ┌────────────────┐
      │ Statistical     │      │ Machine        │      │ Ensemble       │
      │ Intelligence    │      │ Learning       │      │ Scoring Engine │
      │ EWMA            │      │ IsolationForest│      │ Incident Score │
      │ CUSUM           │      │ One-Class SVM  │      │ Risk Ranking   │
      │ Persistence     │      └────────────────┘      └────────────────┘
      └────────────────┘
                │
                ▼
      ┌────────────────────────────┐
      │ Alert Generation Engine    │
      └─────────────┬──────────────┘
                    ▼
      ┌────────────────────────────┐
      │ Incident Management        │
      │ Prioritization             │
      │ Assignment                 │
      │ Lifecycle Tracking         │
      └─────────────┬──────────────┘
                    ▼
      ┌────────────────────────────┐
      │ PostgreSQL                 │
      │ Operational Repository     │
      └───────┬──────────┬─────────┘
              │          │
              ▼          ▼
  ┌────────────────┐   ┌────────────────────┐
  │ React Dashboard│   │ AI Operations      │
  │ Operational UI │   │ Copilot (n8n + LLM)│
  └────────────────┘   └────────────────────┘
```

---

# 🔄 End-to-End Workflow

SentryyIQ processes operational telemetry through a sequence of intelligent processing stages, converting raw system events into actionable operational intelligence.

## Stage 1 — Telemetry Generation

Synthetic banking services continuously generate operational telemetry representing real-world production workloads.

The telemetry includes service performance, infrastructure metrics, operational events, and business transaction indicators.

Examples include:

- Request latency
- CPU utilization
- Memory consumption
- Queue lag
- Error rates
- Request throughput
- Service availability
- Regional information
- Correlation identifiers
- Timestamped operational events

---

## Stage 2 — Event Streaming

Operational telemetry is published to Apache Kafka, providing a scalable event streaming platform that decouples telemetry producers from downstream analytics.

Kafka enables:

- High-throughput ingestion
- Reliable message delivery
- Independent producers and consumers
- Near real-time processing
- Scalable stream analytics

---

## Stage 3 — Window Processing & Feature Engineering

Telemetry consumers aggregate incoming events into configurable processing windows.

During this stage, SentryyIQ derives statistical and operational features required for intelligent anomaly detection.

Generated features include:

- Average latency
- Maximum latency
- Error rate
- CPU statistics
- Memory statistics
- Queue metrics
- Rolling averages
- Statistical indicators
- Service-level operational metrics

---

## Stage 4 — Intelligent Anomaly Detection

Each processing window is evaluated using multiple analytical techniques.

### Statistical Intelligence

Operational behaviour is analyzed using:

- EWMA
- CUSUM
- Persistence Scoring
- Rolling trend analysis

These techniques detect sustained degradation, gradual drift, and abnormal behavioural patterns.

### Machine Learning

Feature vectors are evaluated using unsupervised learning models.

Implemented algorithms include:

- Isolation Forest
- One-Class Support Vector Machine (One-Class SVM)

The models identify anomalous operational behaviour without requiring labelled training datasets.

---

## Stage 5 — Ensemble Intelligence

Outputs from statistical models and machine learning algorithms are combined into a weighted ensemble scoring engine.

The ensemble produces:

- Incident probability
- Risk score
- Severity classification
- Operational confidence
- Alert priority

This approach improves anomaly detection accuracy while reducing false positives.

---

## Stage 6 — Alert & Incident Generation

When configured thresholds are exceeded, the platform automatically:

- Creates operational alerts
- Generates incidents
- Assigns severity levels
- Preserves investigation evidence
- Stores operational context
- Initiates incident lifecycle management

---

## Stage 7 — Operational Intelligence

Processed operational data is stored in PostgreSQL and exposed through interactive dashboards.

Operational teams gain real-time visibility into:

- Service health
- Alert status
- Incident trends
- Statistical analytics
- Machine learning analytics
- Ensemble intelligence
- Operational KPIs
- Historical analysis

---

## Stage 8 — AI Operations Copilot

The AI Operations Copilot extends operational intelligence by combining live operational data with enterprise knowledge.

Using workflow orchestration through n8n and Large Language Models, the Copilot assists engineers by:

- Investigating incidents
- Performing Root Cause Analysis (RCA)
- Retrieving runbooks
- Searching architecture documentation
- Explaining operational anomalies
- Supporting incident assignment
- Guiding incident resolution
- Providing evidence-based recommendations

The Copilot enables engineers to interact with operational intelligence using natural language, significantly reducing investigation effort and improving operational decision-making.

---

# 🧩 Platform Architecture Principles

SentryyIQ is designed around a set of architectural principles that promote scalability, modularity, and extensibility.

- **Event-Driven Processing** – Decoupled telemetry ingestion and analytics using Apache Kafka.
- **Modular Intelligence** – Statistical models, machine learning, dashboards, and AI components evolve independently.
- **Configurable Processing** – Window sizes, thresholds, and analytics are configurable.
- **Evidence-Based AI** – AI recommendations are grounded in live operational data and enterprise knowledge.
- **Scalable Design** – Components communicate through APIs and event streams, enabling horizontal scaling.
- **Enterprise Integration** – Designed for integration with workflow automation, knowledge platforms, and future enterprise AI capabilities.
# 🧩 Platform Modules

SentryyIQ is built as a collection of independent, loosely coupled modules, each responsible for a specific stage of the operational intelligence lifecycle. This modular architecture enables scalability, maintainability, and future extensibility while allowing individual components to evolve independently.

---

# 📡 Telemetry Generation

The platform simulates operational telemetry from distributed banking services to emulate real-world production environments. Each service continuously publishes operational metrics and business events, creating realistic workloads for anomaly detection and operational analysis.

**Capabilities**

- Synthetic banking transaction simulation
- Multi-service telemetry generation
- Regional workload simulation
- Configurable event generation
- Business and infrastructure metrics
- Correlation ID propagation
- Timestamped event streams

**Sample Services**

- Payment API
- Authentication Service
- Trading Engine
- Fraud Detection
- Notification Service

---

# 🌊 Event Streaming

Apache Kafka serves as the event streaming backbone, enabling scalable and reliable telemetry ingestion while decoupling producers from downstream processing components.

**Capabilities**

- Real-time event ingestion
- High-throughput message streaming
- Producer-consumer architecture
- Fault-tolerant message delivery
- Near real-time processing
- Scalable event distribution

---

# ⚙️ Telemetry Processing & Feature Engineering

Incoming telemetry is consumed from Kafka and aggregated into configurable processing windows. During this stage, operational metrics are transformed into statistical features that support downstream anomaly detection.

**Capabilities**

- Window-based aggregation
- Feature engineering
- Rolling statistics
- Service-level metrics
- Regional aggregation
- Configurable processing windows
- Operational KPI generation

**Generated Features**

- Average latency
- Maximum latency
- Error rate
- CPU utilization
- Memory utilization
- Queue lag
- Request throughput
- Service availability
- Rolling averages
- Statistical indicators

---

# 📊 Statistical Intelligence Engine

The Statistical Intelligence Engine continuously evaluates operational behaviour using rolling statistical models designed to identify degradation, drift, and sustained abnormal patterns that traditional threshold-based monitoring may overlook.

**Implemented Models**

- Exponentially Weighted Moving Average (EWMA)
- Cumulative Sum (CUSUM)
- Persistence Scoring

**Capabilities**

- Trend detection
- Operational drift analysis
- Persistent anomaly detection
- Rolling statistical analytics
- Adaptive baseline comparison

---

# 🤖 Machine Learning Engine

The Machine Learning Engine complements statistical analytics by applying unsupervised learning techniques capable of identifying unknown operational anomalies without requiring labelled datasets.

**Implemented Models**

- Isolation Forest
- One-Class Support Vector Machine (One-Class SVM)

**Capabilities**

- Unsupervised anomaly detection
- Multi-dimensional feature analysis
- Outlier detection
- Behavioural pattern recognition
- Adaptive anomaly scoring

---

# 🧠 Ensemble Intelligence Engine

Rather than relying on a single detection algorithm, SentryyIQ combines outputs from multiple analytical models into a weighted ensemble scoring framework that produces a unified operational risk assessment.

**Capabilities**

- Weighted ensemble scoring
- Incident probability calculation
- Operational confidence scoring
- Risk prioritization
- Severity classification
- False-positive reduction

---

# 🚨 Alert & Incident Management

High-confidence anomalies automatically initiate the incident management workflow, transforming analytical outputs into actionable operational events.

**Capabilities**

- Automatic alert generation
- Incident creation
- Severity assignment
- Priority classification
- Incident lifecycle management
- Historical incident tracking
- Evidence preservation
- Operational audit trail

---

# 🗄 Operational Data Repository

Processed telemetry, alerts, incidents, analytical results, and operational context are persisted within PostgreSQL to support dashboards, AI investigations, and historical analysis.

**Stores**

- Window metrics
- Statistical results
- Machine learning predictions
- Ensemble scores
- Alerts
- Incidents
- Historical telemetry
- Operational metadata

---

# 📈 Operational Intelligence Dashboards

Interactive dashboards provide engineering teams with real-time visibility into operational health, system performance, and incident status.

**Dashboard Modules**

### Executive Dashboard

- Overall platform health
- Active incidents
- Alert summary
- Operational KPIs

### Alert Dashboard

- Active alerts
- Severity distribution
- Alert history
- Alert investigation

### Incident Dashboard

- Incident lifecycle
- Priority analysis
- Incident trends
- Resolution tracking

### Service Health Dashboard

- Service availability
- Latency monitoring
- Error trends
- Regional health

### Analytics Dashboard

- Statistical model outputs
- Machine learning predictions
- Ensemble intelligence
- Trend analysis

### Forensic Investigation

- Window metrics
- Historical telemetry
- Event correlation
- Operational drill-down

---

# 🤖 AI Operations Copilot

The AI Operations Copilot extends traditional observability by combining live operational intelligence with workflow automation and Large Language Models to provide conversational operational assistance.

The Copilot retrieves operational data, investigates incidents, accesses enterprise documentation, and assists engineers throughout the complete incident lifecycle.

**Capabilities**

- Conversational incident investigation
- Root Cause Analysis (RCA)
- Incident summarization
- Operational health queries
- Alert investigation
- Runbook retrieval
- Architecture documentation lookup
- Error catalogue search
- SLA guidance
- Incident assignment
- Resolution assistance
- Incident closure support
- Evidence-based operational recommendations

---

# 🔄 Workflow Automation

Operational workflows are orchestrated using n8n, enabling intelligent automation across the incident management lifecycle.

**Capabilities**

- AI workflow orchestration
- Telegram integration
- Email notifications
- Incident assignment workflows
- Resolution workflows
- Automated status updates
- API integrations
- Event-driven automation

---

# 🔌 Platform APIs

REST APIs expose operational intelligence for dashboards, workflow automation, and AI integrations.

**API Categories**

- Window Metrics
- Alerts
- Incidents
- Incident Details
- Operational Analytics
- AI Operations
- User Management
- Configuration

# 📊 Operational Intelligence Center

SentryyIQ provides a centralized Operational Intelligence Center that enables engineering teams to monitor platform health, investigate anomalies, manage incidents, and analyze operational telemetry from a single interface.

Unlike traditional monitoring dashboards that only display infrastructure metrics, SentryyIQ combines statistical analytics, machine learning predictions, ensemble intelligence, and incident management into an integrated operational workspace.

---

# 🏠 Executive Dashboard

The Executive Dashboard provides a consolidated operational view of the platform, allowing engineers to quickly assess system health and identify critical issues.

### Key Features

- Platform health summary
- Active incidents
- Active alerts
- Service status overview
- Critical event notifications
- Recent operational activity
- Incident trend visualization
- Quick navigation to investigation workflows

---

# 🚨 Alert Management

The Alert Management workspace provides complete visibility into anomalies detected by the analytics pipeline.

### Capabilities

- View active alerts
- Alert severity classification
- Alert status tracking
- Service association
- Region identification
- Alert timestamps
- Investigation entry point
- Historical alert review

Each alert serves as the starting point for detailed operational investigation.

---

# 🎫 Incident Management

Automatically generated alerts are converted into operational incidents that can be tracked throughout their lifecycle.

### Capabilities

- Incident listing
- Severity classification
- Priority tracking
- Current status
- Service ownership
- Incident timestamps
- Operational history
- Investigation access

This workspace enables production support teams to monitor and manage ongoing operational issues.

---

# 🔍 Alert Investigation

Selecting an alert opens a dedicated investigation workspace containing the evidence used during anomaly detection.

The investigation interface provides multiple analytical perspectives through dedicated tabs.

### Overview

Displays the operational context of the detected anomaly including:

- Service
- Region
- Severity
- Risk score
- Alert metadata
- Detection summary

---

### Summary

Provides a concise explanation of the detected anomaly including:

- Root observations
- Statistical findings
- Operational indicators
- AI-generated investigation summary

---

### Records

Displays the underlying telemetry records contributing to the anomaly.

Information includes:

- Window metrics
- Operational events
- Aggregated telemetry
- Processing timestamps

---

### Telemetry Details

Provides detailed operational evidence supporting the alert.

Includes:

- Feature values
- Error codes
- Performance metrics
- Infrastructure indicators
- Statistical outputs
- Processing metadata

---

# 📄 Incident Investigation

Each incident includes a dedicated investigation workspace that consolidates all operational evidence.

### Investigation Views

#### Overview

High-level incident summary including operational impact and affected services.

#### Summary

Incident narrative describing the detected issue and investigation findings.

#### Telemetry Details

Complete operational payload associated with the incident including processed analytical results and supporting evidence.

This enables engineers to investigate incidents without manually correlating information across multiple systems.

---

# 📈 Operational Analytics

The Operational Analytics workspace enables engineers to analyze system behaviour across multiple analytical layers, providing complete visibility into how incidents are detected and prioritized.

Instead of presenting only final anomaly scores, SentryyIQ visualizes the complete analytical pipeline—from raw operational telemetry through statistical intelligence and machine learning to the final incident probability.

---

## 📡 Raw Telemetry Analytics

Interactive time-series charts display operational behaviour captured from monitored services.

### Metrics

- CPU Utilization
- Memory Utilization
- Queue Lag
- Response Latency

These charts enable engineers to identify performance degradation, workload spikes, and infrastructure bottlenecks before they evolve into operational incidents.

---

## 📊 Statistical Intelligence Analytics

Statistical models continuously evaluate operational behaviour using rolling analytical windows.

Visualized metrics include: Rolling statistical trends

- EWMA
- CUSUM
- Persistence Score

These visualizations help identify gradual degradation, sustained anomalies, and operational drift that traditional threshold monitoring may not detect.

---

## 🤖 Machine Learning Analytics

Displays anomaly predictions generated by the machine learning engine.

Implemented models include:

- Isolation Forest
- One-Class Support Vector Machine (One-Class SVM)

The dashboard visualizes prediction trends over time, enabling engineers to compare behavioural changes across successive processing windows.

---

## 🧠 Ensemble Intelligence

Outputs from statistical models and machine learning algorithms are combined to produce an overall operational risk assessment.

Available metrics include:

- Ensemble Score
- Incident Probability

These metrics represent the final intelligence used for automated alert generation and incident creation.

---

## 📉 Normalized Trend Visualization

To enable meaningful comparison between metrics with different value ranges, analytical charts use normalized values for visualization.

This allows engineers to correlate infrastructure metrics, statistical indicators, machine learning predictions, and incident probability on a common timeline.

---

## 🔢 Actual Metric Values

While charts display normalized trends for comparative analysis, the dashboard also presents the corresponding raw values for every analytical metric.

This enables engineers to:

- Interpret actual operational measurements
- Validate analytical results
- Compare normalized and original values
- Investigate anomalous behaviour with full numerical context

---

## 🎯 Investigation Benefits

The analytics workspace enables engineers to:

- Correlate telemetry with anomaly scores
- Understand why alerts were generated
- Validate machine learning predictions
- Observe statistical model behaviour
- Compare multiple analytical techniques
- Investigate operational degradation over time

# 📊 Operational Investigation Workflow

The dashboard supports a structured investigation workflow that guides engineers from anomaly detection to incident analysis.

```
Operational Alert
        │
        ▼
Alert Investigation
        │
        ▼
Operational Summary
        │
        ▼
Telemetry Records
        │
        ▼
Telemetry Details
        │
        ▼
Incident Investigation
        │
        ▼
AI Operations Copilot
```

This workflow minimizes context switching by providing all relevant operational evidence within a single investigation experience.

---

# 🎯 Dashboard Highlights

- Executive operational overview
- Real-time alert monitoring
- Incident lifecycle management
- Interactive investigation workspaces
- Time-series operational analytics
- Service and regional performance monitoring
- Detailed telemetry inspection
- Statistical and machine learning evidence
- End-to-end incident investigation support

# 🤖 AI Operations Copilot

The AI Operations Copilot transforms traditional observability into an intelligent, conversational operational experience.

Rather than requiring engineers to manually navigate dashboards, correlate telemetry, and search documentation, the Copilot enables natural language interaction with operational data, incident records, and enterprise knowledge.

Built using **n8n workflow automation**, **Google Gemini**, and enterprise knowledge sources, the Copilot acts as an intelligent operational assistant capable of investigating incidents, retrieving contextual information, and supporting engineers throughout the complete incident lifecycle.

---

# 🎯 Objectives

The AI Operations Copilot is designed to:

- Accelerate incident investigation
- Reduce Mean Time to Detect (MTTD)
- Reduce Mean Time to Resolve (MTTR)
- Minimize manual correlation across operational systems
- Provide evidence-based operational recommendations
- Improve knowledge accessibility
- Standardize incident investigation workflows

---

# 🧠 Conversational Operations

Engineers interact with the platform using natural language rather than navigating multiple dashboards or documentation repositories.

Example queries include:

- Show active incidents
- List critical alerts
- Investigate incident **INC-2026-001**
- Why was this alert generated?
- Show telemetry for the affected service
- Display statistical analysis
- Explain the anomaly
- Show machine learning predictions
- What is the incident probability?
- Recommend next investigation steps

---

# 🔍 Intelligent Incident Investigation

The Copilot retrieves operational context directly from the SentryyIQ platform to provide comprehensive incident analysis.

### Investigation Workflow

- Retrieve incident details
- Load associated alert information
- Access processed telemetry
- Analyze statistical indicators
- Review machine learning predictions
- Evaluate ensemble scoring
- Generate investigation summary
- Recommend next actions

This enables engineers to perform complete investigations without manually correlating information across multiple systems.

---

# 📚 Enterprise Knowledge Assistance

The Copilot augments live operational intelligence with enterprise knowledge to provide contextual guidance during investigations.

Knowledge sources include:

- Operational runbooks
- Architecture documentation
- Error catalogues
- Service documentation
- Standard operating procedures
- SLA guidelines

This allows engineers to access operational knowledge without leaving the investigation workflow.

---

# 🧩 AI Workflow Orchestration

The Copilot is orchestrated using **n8n**, enabling modular and extensible AI workflows.

Current workflow capabilities include:

- User request processing
- Intent identification
- Operational data retrieval
- Knowledge retrieval
- Prompt construction
- LLM interaction
- Response generation
- Telegram delivery

The modular workflow design allows additional enterprise integrations and AI capabilities to be incorporated with minimal changes.

---

# 📱 Telegram Integration

The AI Operations Copilot is accessible through Telegram, allowing engineers to investigate incidents and retrieve operational intelligence from any location.

Supported interactions include:

- Incident lookup
- Alert lookup
- Investigation summaries
- Operational guidance
- Knowledge retrieval
- Conversational assistance

---

# 🔗 Context-Aware Intelligence

Unlike generic AI assistants, the Copilot combines multiple sources of contextual information before generating responses.

Context includes:

- Live incident records
- Alert metadata
- Window metrics
- Statistical analytics
- Machine learning predictions
- Ensemble intelligence
- Enterprise documentation
- Historical operational information

This enables responses that are grounded in operational evidence rather than generic AI reasoning.

---

# ⚙️ Technology Stack

| Component | Technology |
|-----------|------------|
| Workflow Automation | n8n |
| Large Language Model | Google Gemini |
| Backend Services | FastAPI |
| Operational Data | PostgreSQL |
| Knowledge Sources | Google Docs |
| Communication | Telegram Bot |
| APIs | REST APIs |

---

# 🚀 Future Enhancements

The AI Operations Copilot has been designed to evolve into a broader Enterprise AI Operations platform.

Planned capabilities include:

- Retrieval-Augmented Generation (RAG)
- Enterprise Knowledge Intelligence integration
- Hybrid semantic search
- LangGraph multi-agent workflows
- Context-aware reasoning
- Predictive operational recommendations
- Cross-system incident correlation
- Enterprise collaboration platform integration

# 🧠 Intelligence Engine

The Intelligence Engine is the analytical core of SentryyIQ, transforming aggregated operational telemetry into actionable operational intelligence.

Rather than relying solely on static thresholds, the platform combines statistical analytics, machine learning, and ensemble intelligence to detect abnormal operational behaviour, prioritize incidents, and reduce false positives.

The multi-layered analytical approach enables SentryyIQ to identify both sudden anomalies and gradual performance degradation while providing confidence-based operational risk assessment.

---

# 📊 Operational Feature Engineering

Before analytical models are executed, incoming telemetry is aggregated into configurable processing windows where operational metrics are transformed into meaningful analytical features.

### Feature Categories

#### Infrastructure Metrics

- CPU Utilization
- Memory Utilization
- Queue Lag

#### Performance Metrics

- Average Response Time
- Maximum Response Time
- Request Throughput
- Error Rate

#### Operational Context

- Service Name
- Region
- Processing Window
- Timestamp
- Correlation Information

These engineered features provide a consistent analytical foundation for both statistical and machine learning models.

---

# 📈 Statistical Intelligence

Statistical analytics continuously monitor operational behaviour using rolling processing windows.

Unlike traditional threshold monitoring, statistical models identify evolving behavioural changes that may indicate emerging production issues.

## Implemented Models

### Exponentially Weighted Moving Average (EWMA)

EWMA smooths short-term fluctuations while giving greater importance to recent observations.

**Purpose**

- Trend monitoring
- Performance degradation detection
- Operational baseline comparison

---

### Cumulative Sum (CUSUM)

CUSUM detects small but persistent deviations from expected operational behaviour.

**Purpose**

- Drift detection
- Sustained anomaly identification
- Early warning indicators

---

### Persistence Scoring

Measures whether abnormal behaviour continues across consecutive processing windows.

**Purpose**

- Reduce transient noise
- Identify recurring anomalies
- Improve alert confidence

---

# 🤖 Machine Learning Intelligence

Machine learning models complement statistical analytics by detecting multidimensional behavioural anomalies that cannot be identified using simple statistical rules.

The platform uses unsupervised learning techniques, allowing anomaly detection without requiring labelled training datasets.

---

## Isolation Forest

Isolation Forest identifies anomalous observations based on how easily they can be isolated within the feature space.

**Strengths**

- High-dimensional analysis
- Fast inference
- Effective outlier detection
- Production-friendly performance

---

## One-Class Support Vector Machine

One-Class SVM learns the boundary of normal operational behaviour and classifies observations outside that boundary as anomalous.

**Strengths**

- Behavioural modelling
- Unknown anomaly detection
- Non-linear pattern recognition

---

# 🧩 Ensemble Intelligence

Rather than relying on a single analytical model, SentryyIQ combines outputs from multiple analytical engines to produce a unified operational risk assessment.

The ensemble approach improves detection accuracy while reducing false positives.

### Ensemble Inputs

- EWMA
- CUSUM
- Persistence Score
- Isolation Forest
- One-Class SVM

### Ensemble Outputs

- Ensemble Score
- Incident Probability
- Confidence Score
- Operational Risk
- Recommended Severity

---

# 🎯 Incident Probability

The Intelligence Engine calculates an overall incident probability by combining statistical indicators and machine learning predictions.

This probability represents the likelihood that the current operational behaviour requires engineering attention.

The resulting score is used to:

- Generate alerts
- Prioritize incidents
- Recommend severity
- Support operational decision making

---

# 🚨 Alert Decision Engine

The Alert Decision Engine evaluates ensemble outputs against configurable operational policies.

When analytical thresholds are satisfied, the platform automatically:

- Generates operational alerts
- Assigns severity
- Creates incidents
- Preserves operational evidence
- Stores analytical results

This ensures that operational teams receive meaningful alerts rather than isolated metric deviations.

---

# 📉 Trend Analysis

Historical analytical results are retained to support long-term operational analysis.

Engineers can visualize trends for:

- CPU utilization
- Memory utilization
- Queue lag
- Statistical scores
- Machine learning predictions
- Ensemble scores
- Incident probability

For visualization purposes, trend charts are normalized to enable comparison across metrics with different value ranges.

The dashboard simultaneously displays the corresponding raw metric values, allowing engineers to correlate normalized trends with actual operational measurements.

---

# 🎯 Intelligence Engine Benefits

The Intelligence Engine enables engineering teams to:

- Detect operational anomalies earlier
- Reduce false-positive alerts
- Identify gradual performance degradation
- Prioritize incidents based on operational risk
- Combine statistical and machine learning insights
- Improve operational confidence
- Accelerate Root Cause Analysis (RCA)
- Support evidence-based incident management

---

# 💡 Design Principles

The analytical framework has been designed around the following principles:

- **Multi-Layer Intelligence** — Combine statistical and machine learning techniques for improved accuracy.
- **Explainable Analytics** — Preserve intermediate analytical outputs to support investigation and transparency.
- **Configurable Processing** — Allow analytical thresholds and processing windows to be tuned for different operational environments.
- **Evidence-Based Decisions** — Generate alerts using analytical evidence rather than individual metric thresholds.
- **Scalable Architecture** — Enable future integration of additional statistical models, machine learning algorithms, and predictive analytics without disrupting the existing processing pipeline.
# 🛠 Technology Stack

SentryyIQ combines modern backend technologies, real-time event streaming, statistical analytics, machine learning, workflow automation, and Generative AI to deliver an end-to-end Operations Intelligence Platform.

---

## Backend

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| API Framework | FastAPI |
| ORM | SQLAlchemy |
| Data Validation | Pydantic |
| ASGI Server | Uvicorn |

---

## Frontend

| Component | Technology |
|-----------|------------|
| Framework | React |
| Build Tool | Vite |
| Language | TypeScript |
| Styling | CSS |

---

## Event Streaming

| Component | Technology |
|-----------|------------|
| Event Broker | Apache Kafka |
| Producer | Banking Telemetry Generator |
| Consumer | Telemetry Processing Engine |

---

## Database

| Component | Technology |
|-----------|------------|
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic *(if used)* |

---

## Statistical Intelligence

| Model | Purpose |
|--------|---------|
| EWMA | Trend Detection |
| CUSUM | Drift Detection |
| Persistence Score | Sustained Anomaly Detection |

---

## Machine Learning

| Model | Purpose |
|--------|---------|
| Isolation Forest | Unsupervised Anomaly Detection |
| One-Class SVM | Behavioural Anomaly Detection |

---

## AI & Workflow Automation

| Component | Technology |
|-----------|------------|
| Workflow Automation | n8n |
| Large Language Model | Google Gemini |
| Knowledge Sources | Google Docs |
| Communication | Telegram Bot |
| Notification | Email |

---

## Development & Deployment

| Component | Technology |
|-----------|------------|
| Version Control | Git |
| Repository | GitHub |
| Backend Hosting | Render |
| Frontend Hosting | Vercel |
| Containerization | Docker *(where applicable)* |

---

# 📂 Repository Structure

```
## Root

- `backend/` — FastAPI app: DB models, CRUD, notifications, and RAG pipeline
- `frontend/` — Vite/React (TanStack) dashboard UI and Vercel deploy config
- `consumer/` — Kafka (or stream) consumer that pulls logs for detection
- `producer/` — Log/telemetry producer that publishes banking events
- `src/` — Core ML/detection library (ensemble, features, enrichment, metrics)
- `scripts/` — Data generation and preprocessing utilities
- `notebooks/` — Exploratory notebooks plus mirrored data/models/outputs
- `docs/` — Architecture docs, guides, presentations, and screen recordings
- `data/` — Raw and processed banking log datasets
- `models/` — Trained joblib/pkl models, scalers, encoders, ensemble configs
- `n8n/` — n8n workflow exports (incident notification & assignment)
- `outputs/` — Analysis artifacts (charts, CSVs, PDF reports)
- `reports/` — Generated anomaly report PDFs
- `logs/` — Runtime application logs (consumer, producer, uvicorn)
- `temp/` — Scratch/working copies of data and experimental scripts
- `config.py` — Root project configuration
- `logging_config.py` — Shared logging setup
- `requirements.txt` — Python dependencies
- `README.md` — Project overview and architecture


[Check details here :](docs/FOLDER_STRUCTURE.md)
 
```

> *The structure above represents the major modules. Refer to the repository for the latest implementation.*

---

# 🚀 Getting Started

## Clone the Repository

```bash
git clone https://github.com/shubhiv02-learner/banking-log-anomaly-detection
cd banking-log-anomaly-detection
```

---

## Backend Setup

Create a virtual environment.

```bash
python -m venv .venv
```

Activate the environment.

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

## Frontend Setup

```bash
cd frontend
npm install
```

Run the development server.

```bash
npm run dev
```

---

## Environment Configuration

Configure the required environment variables before starting the application.

Typical configuration includes:

- Database connection
- Kafka broker
- API configuration
- Gemini API Key
- Telegram Bot Token
- Google API credentials
- Email configuration

Refer to the project documentation for the complete configuration guide.

---

# ▶ Running the Platform

Start the backend.

```bash
uvicorn backend.main:app --reload

or
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

```

Start the frontend.

```bash
npm run dev
```

Start Kafka and PostgreSQL before launching the platform.

---

# 🔌 REST APIs

SentryyIQ exposes REST APIs used by the dashboard and AI Operations Copilot.

### Operational Analytics

- Window Metrics
- Recent Metrics
- Statistical Analytics
- Machine Learning Results

### Alert Management

- List Alerts
- Alert Details

### Incident Management

- List Incidents
- Incident Details
- Assign Incident
- Resolve Incident
- Close Incident

### AI Operations

- Copilot Queries
- Investigation APIs
- Knowledge Retrieval

---

# 📖 Documentation

Detailed technical documentation is available through the project portfolio.

Documentation includes:

- Architecture Overview
- System Design
- End-to-End Workflow
- Dashboard Walkthrough
- AI Operations Copilot
- API Documentation
- Deployment Guide

🌐 **Project Portfolio**

https://portfolio-iota-taupe-91.vercel.app/projects/sentryyiq

---

# 🎥 Demonstrations

The project portfolio contains complete demonstrations of the implemented platform.

### Part 1 — Kafka Streaming & Intelligent Alert Generation

- Event ingestion
- Window aggregation
- Statistical analytics
- Machine learning
- Ensemble scoring
- Alert generation
- Incident creation

---

### Part 2 — Operations Console

- Executive Dashboard
- Alert Management
- Incident Management
- Operational Analytics
- Investigation Workflow

---

### Part 3 — AI Operations Copilot

- Conversational investigation
- Root Cause Analysis
- Knowledge retrieval
- Incident lifecycle
- Operational assistance

---

# 🗺 Roadmap

The platform is designed to evolve into a broader Enterprise AI Operations ecosystem.

Planned enhancements include:

- Retrieval-Augmented Generation (RAG)
- Enterprise Knowledge Intelligence integration
- Hybrid Search
- LangGraph-based multi-agent workflows
- Enterprise collaboration integrations
- Predictive analytics
- Knowledge Graph support
- Context-aware operational reasoning

---

# 📄 License

This project is licensed under the MIT License.

---

# 🤝 Connect

If you're interested in discussing enterprise AI, observability, Operations Intelligence, or Generative AI applications, feel free to connect through the project portfolio or GitHub.

🌐 **Portfolio**

https://portfolio-iota-taupe-91.vercel.app/projects/sentryyiq

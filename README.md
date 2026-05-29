# 🌦️ Weather Intelligence Monitoring System

## Overview

A production-style backend system that continuously monitors real-time weather data for multiple cities and converts raw readings into meaningful, structured **weather intelligence events** using statistical and contextual analysis.

Built using **FastAPI** and **SQLAlchemy**, the system demonstrates real-world backend engineering concepts including event-driven architecture, anomaly detection, and data pipeline design.

---

## Monitored Cities

- Ottawa, Ontario, Canada  
- Toronto, Ontario, Canada  
- Vancouver, British Columbia, Canada  

---

## Key Features

### 📡 Real-Time Data Pipeline
- Automated weather polling service
- Continuous ingestion of live weather data
- Fault-tolerant background processing

### 🧹 Data Deduplication
- Prevents redundant weather entries using tolerance-based matching
- Ensures clean and efficient storage

### 🧠 Intelligent Event Detection
Transforms raw readings into actionable events using:

- Historical trend analysis
- Statistical anomaly detection (mean, standard deviation, z-score)
- City-specific behavioral baselines
- Cross-city comparisons

---

## Event Types

- 🌡️ Temperature Anomaly Detection  
- 🌬️ Wind Speed Spike Detection  
- 🌦️ Weather Condition Changes  
- 🌧️ Heavy Precipitation Alerts  
- 🌍 Cross-City Temperature Differences  

Each event includes:
- event type  
- city  
- timestamp  
- human-readable explanation  

---

## Architecture

```text
Weather API → Polling Service → Deduplication → Database → Event Engine → Event Storage

---

## Cursor AI Setup (Rules, Agent, Skills)

This project uses Cursor’s rule, agent, and skill system to enforce a structured, production-like architecture for a weather monitoring and event detection system.

---

# 1. Rules

## 1.1 polling_and_logging_rules.mdc

### Purpose
This rule defines how the system continuously collects weather data and ensures the polling pipeline remains stable, fault-tolerant, and consistent.

### What it enforces
- Strict separation of polling logic from event detection
- Async polling loop structure per city
- Safe retry mechanism with bounded retries
- Standardized logging format across the system
- Failure isolation so one city cannot crash the system
- Proper ordering of pipeline steps:
  fetch → deduplicate → save → detect → store events

### Why it exists
Weather polling systems run continuously and are prone to API and database failures. This rule ensures the system remains stable, predictable, and recoverable under failure conditions.

---

## 1.2 event_detection_rules.mdc

### Purpose
This rule defines how weather events are detected using statistical methods and ensures correctness of anomaly detection logic.

### What it enforces
- Use of rolling averages and standard deviation for anomaly detection
- Proper z-score-based thresholding for temperature and wind anomalies
- Independent logic for each event type
- Safe handling of insufficient historical data
- Strict separation between event logic and database/polling layers
- Consistent event output structure

### Why it exists
Event detection must remain statistically correct and consistent. Without strict rules, the system could generate noisy or misleading alerts.

---

# 2. Agent

## event_detection_reviewer

### Purpose
This agent acts as a domain expert reviewer for all event detection logic.

### What it does
- Reviews whether event detection logic is statistically correct
- Evaluates if thresholds are too sensitive or too strict
- Detects over-triggering or under-triggering of events
- Validates z-score usage and statistical correctness
- Ensures event logic reflects realistic weather behavior

### Why it exists
Event detection systems are highly sensitive to threshold tuning. This agent provides an automated review layer that ensures event logic remains balanced, realistic, and production-safe.

---

# 3. Skill

## weather_data_analysis.py

### Purpose
This skill provides a queryable data analysis tool over stored weather readings and detected events.

### What it does
- Queries stored weather readings from the database
- Retrieves recent event history
- Computes per-city statistics (average, min, max temperatures)
- Performs cross-city comparisons
- Summarizes event frequency over a time window
- Returns structured analytical output

### Why it exists
Cursor needs a way to interact with real stored data. This skill transforms raw database records into meaningful insights, enabling validation of system behavior and detection logic performance.

---

# Summary

Together, these components create a structured AI-assisted system:

- Rules enforce system behavior constraints
- Agent validates correctness of event logic
- Skill provides data-level introspection and analysis

This ensures the system is not only functional but also verifiable, maintainable, and analytically observable.
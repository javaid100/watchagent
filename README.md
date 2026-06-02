# 🌦️ WatchAgent – Intelligent Weather Monitoring & Event Detection System

## 📌 Overview

WatchAgent is a production-style weather monitoring platform that continuously collects real-time weather data from multiple Canadian cities, stores historical observations, detects significant weather events using statistical analysis, and exposes the results through a REST API.

The system is designed to demonstrate:

* Real-time weather data collection
* Historical weather storage
* Reading deduplication
* Statistical anomaly detection
* Event persistence
* REST API access
* Automated testing
* CI/CD integration
* Dockerized deployment
* Cursor AI development workflow

---

# 🚀 Features

### Weather Collection

* Polls weather data from Open-Meteo API
* Supports:

  * Toronto
  * Ottawa
  * Vancouver

### Data Storage

Stores:

* Temperature
* Apparent Temperature
* Wind Speed
* Precipitation
* Weather Code

### Event Detection

Detects:

* Temperature anomalies
* Wind spikes
* Weather condition changes
* Heavy precipitation
* Cross-city temperature gaps

### API Access

Provides endpoints for:

* Health monitoring
* Reading retrieval
* Event retrieval

### Reliability

* Duplicate reading prevention
* Structured logging
* Retry mechanism
* Error isolation per city
* Persistent PostgreSQL storage

---

# 🏗️ System Architecture

## High-Level Architecture

```text
                    ┌──────────────────────┐
                    │   Open-Meteo API     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Weather Service     │
                    │ weather_service.py   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Polling Service      │
                    │ polling_service.py   │
                    └──────────┬───────────┘
                               │
          ┌────────────────────┴──────────────────┐
          │                                       │
          ▼                                       ▼

┌──────────────────────┐           ┌──────────────────────┐
│ Deduplication Layer  │           │ Event Detection      │
│ pipeline.py          │           │ pipeline.py          │
└──────────┬───────────┘           └──────────┬───────────┘
           │                                  │
           └──────────────┬───────────────────┘
                          │
                          ▼

                 ┌──────────────────┐
                 │ PostgreSQL       │
                 │ Readings Table   │
                 │ Events Table     │
                 └────────┬─────────┘
                          │
                          ▼

                 ┌──────────────────┐
                 │ FastAPI API      │
                 │ main.py          │
                 └────────┬─────────┘
                          │
                          ▼

                  API Consumers
             (curl / Postman / UI)
```

---

# 📂 Project Structure

```text
watchagent/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── app/
│   ├── api/
│   ├── core/
│   ├── database/
│   ├── services/
│   ├── utils/
│   └── logs/
│
├── tests/
│
├── .cursor/
│   ├── agents/
│   ├── rules/
│   └── skills/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── .env
```

---

# ⚙️ Technology Choices & Justification

| Technology     | Purpose                 | Why It Was Chosen                            |
| -------------- | ----------------------- | -------------------------------------------- |
| Python 3.11    | Core Language           | Mature ecosystem and excellent async support |
| FastAPI        | REST API Framework      | High performance, automatic documentation    |
| SQLAlchemy     | ORM                     | Clean database abstraction                   |
| PostgreSQL     | Database                | Reliable and production-ready                |
| Docker         | Containerization        | Reproducible deployments                     |
| Docker Compose | Service Orchestration   | Simplifies multi-container setup             |
| Pytest         | Testing                 | Industry-standard testing framework          |
| GitHub Actions | CI/CD                   | Automated validation on every commit         |
| Open-Meteo API | Weather Source          | Free, reliable, no API key required          |
| Cursor         | AI Development Workflow | Enforces project-specific coding standards   |

---

# 🗄️ Database Design

## Readings Table

Stores raw weather observations.

| Field                | Description             |
| -------------------- | ----------------------- |
| id                   | Primary Key             |
| city                 | City Name               |
| temperature          | Current Temperature     |
| apparent_temperature | Feels Like Temperature  |
| precipitation        | Current Precipitation   |
| wind_speed           | Wind Speed              |
| weather_code         | Open-Meteo Weather Code |
| timestamp            | Reading Timestamp       |

---

## Events Table

Stores detected weather events.

| Field       | Description                      |
| ----------- | -------------------------------- |
| id          | Primary Key                      |
| city        | City Name                        |
| event_type  | Event Category                   |
| description | Human Readable Event Description |
| timestamp   | Event Timestamp                  |

---

# 🧠 Event Detection Design

## Design Goals

The event engine was designed to:

* Detect meaningful weather changes
* Avoid excessive alert generation
* Remain statistically defensible
* Produce explainable events
* Be deterministic and testable

---

## 1. Temperature Anomaly Detection

### Logic

Uses:

* Historical average
* Standard deviation
* Z-score

Formula:

```text
z = | (value - mean) / std |
```

Trigger:

```text
z >= 2
```

Severity:

```text
2 ≤ z < 3  → MEDIUM
z ≥ 3      → HIGH
```

### Why This Approach?

A fixed threshold such as "above 30°C" behaves differently in different cities and seasons.

Using a Z-score allows the system to detect statistically unusual temperatures relative to recent local conditions.

This makes anomaly detection adaptive and more realistic.

---

## 2. Wind Spike Detection

### Logic

Uses:

* Wind history only
* Independent mean
* Independent standard deviation
* Independent z-score

### Why This Approach?

Wind patterns differ significantly from temperature trends.

Maintaining a separate statistical baseline prevents false positives.

---

## 3. Weather Change Detection

### Logic

Triggers when:

```text
weather_code changes
```

Example:

```text
Clear Sky → Thunderstorm
```

### Why This Approach?

Weather condition transitions may be operationally important even when temperature remains unchanged.

---

## 4. Heavy Precipitation Detection

### Logic

Triggers when:

```text
precipitation > 2 mm
```

OR

```text
weather_code indicates precipitation
```

### Why This Approach?

Captures impactful rain, snow, and storm conditions.

---

## 5. Cross-City Temperature Gap

### Logic

Triggers when:

```text
Temperature Difference ≥ 8°C
```

Example:

```text
Toronto is 10°C warmer than Ottawa
```

### Why This Approach?

Provides regional intelligence rather than city-isolated monitoring.

Large temperature differences often indicate noteworthy weather patterns.

---

# 🔄 Deduplication Strategy

Before saving a reading:

1. Retrieve latest reading for the city
2. Compare all weather attributes
3. Skip storage if values are effectively identical

Compared Fields:

* temperature
* apparent_temperature
* precipitation
* wind_speed
* weather_code

Tolerance:

```python
0.01
```

### Why Deduplicate?

Weather APIs frequently return identical observations.

Without deduplication:

* Storage grows unnecessarily
* Historical averages become biased
* Event generation becomes noisy

---

# 📝 Logging Strategy

The application uses structured logging.

Format:

```text
[EVENT_TYPE] key=value key=value
```

Examples:

```text
[POLL_CYCLE_START]

[READING_SAVED] city=toronto id=10

[DUPLICATE_SKIPPED] city=ottawa

[EVENT_DETECTION_DONE] city=vancouver events=2

[POLL_FAILURE] city=toronto error=timeout
```

Benefits:

* Easy debugging
* Searchable logs
* Production-friendly monitoring

---

# 🐳 Docker Setup

## Clone Repository

```bash
git clone <repository-url>
cd watchagent
```

---

## Create Environment File

Create `.env`

```env
POSTGRES_USER=watchagent
POSTGRES_PASSWORD=watchagentpassword
POSTGRES_DB=watchagent
POSTGRES_HOST=db
POSTGRES_PORT=5432

API_PORT=8000
POLL_INTERVAL_SECONDS=300
```

---

## Build and Start

```bash
docker compose up --build
```

Run in background:

```bash
docker compose up -d --build
```

---

## Verify Containers

```bash
docker ps
```

---

## Stop Containers

```bash
docker compose down
```

---

# 💻 Running Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run application:

```bash
uvicorn app.main:app --reload
```

API available at:

```text
http://localhost:8000
```

---

# 📖 API Reference

## Health Check

### Request

```bash
curl http://localhost:8000/health
```

### Example Response

```json
{
  "status": "ok",
  "readings_stored": 120,
  "events_stored": 8
}
```

---

## Get Readings

### Request

```bash
curl "http://localhost:8000/readings?city=toronto&limit=10"
```

### Example Response

```json
{
  "readings": [...]
}
```

---

## Get Events

### Request

```bash
curl "http://localhost:8000/events?city=toronto&limit=10"
```

### Example Response

```json
{
  "events": [...]
}
```

---

# 🧪 Running Tests

Run all tests:

```bash
pytest -v
```

Or:

```bash
python tests/run_tests.py
```

---

## Test Coverage

### API Tests

* Health endpoint
* Readings endpoint
* Events endpoint

### Deduplication Tests

* Duplicate reading validation

### Event Detection Tests

* Temperature anomaly detection
* Insufficient history handling

---

# 🔄 Continuous Integration

GitHub Actions automatically validates:

* Dependency installation
* Test execution
* Build verification

Location:

```text
.github/workflows/ci.yml
```

Pipeline runs on:

* Push
* Pull Request

A merge is only accepted when all tests pass successfully.

---

# 🤖 Cursor Setup

This project includes a dedicated Cursor configuration tailored specifically to WatchAgent.

The purpose is to keep AI-generated code aligned with architecture decisions, engineering standards, and project goals.

---

# 📜 Cursor Rules

## event_detection_rules.mdc

### Purpose

Enforces statistical correctness and event-detection consistency.

### Key Requirements

* Z-score anomaly detection
* Separate helper functions per event type
* Minimum history validation
* Safe standard deviation handling
* No database writes inside event logic
* Deterministic and testable event generation

---

## polling_and_logging_rules.mdc

### Purpose

Enforces polling architecture and operational consistency.

### Key Requirements

* Polling handles orchestration only
* Deduplication before persistence
* Event detection after save
* Structured logging
* Proper exception handling
* Resilient long-running polling

---

# 👨‍🔬 Cursor Agent

## event_detection_reviewer.md

### Purpose

Acts as a senior weather data scientist reviewing event logic.

### Responsibilities

* Validate statistical correctness
* Review anomaly thresholds
* Identify over-trigger risks
* Identify under-trigger risks
* Evaluate event quality

### Required Output Format

```text
EVENT REVIEW SUMMARY

POTENTIAL OVER-TRIGGER RISKS

POTENTIAL UNDER-TRIGGER RISKS

STATISTICAL ISSUES

RECOMMENDED FIXES
```

### Why This Agent Exists

The project's most important component is event detection.

This agent provides focused expert review rather than generic code review.

---

# 📊 Cursor Skill

## weather_data_analysis.py

### Purpose

Performs historical weather analysis across the entire dataset.

### Capabilities

* City temperature trends
* Event frequency analysis
* Cross-city comparisons
* Multi-day reporting
* Dataset-wide insights

### Example Usage

```python
analyze_weather_data(days=7)
```

### Example Output

```json
{
  "status": "success",
  "total_readings": 420,
  "total_events": 31,
  "city_statistics": {},
  "cross_city_comparison": {},
  "event_summary": {}
}
```

### Why This Skill Exists

Unlike API endpoints that return raw records, this skill provides analytical insights spanning the entire dataset and multiple cities.

This enables higher-level reasoning and reporting.

---

# 🎯 Engineering Decisions

1. Statistical anomaly detection instead of fixed thresholds.
2. Explicit deduplication before event processing.
3. Independent event helper functions.
4. Structured logging for production troubleshooting.
5. PostgreSQL persistence for historical analytics.
6. Dockerized deployment for reproducibility.
7. GitHub Actions CI for automated validation.
8. Cursor rules, agent, and skill designed specifically for this codebase.

---

# 🔮 Future Enhancements

Potential improvements include:

* Dynamic anomaly thresholds
* Additional Canadian cities
* Forecast integration
* Email notifications
* SMS alerts
* Dashboard visualization
* Severity scoring
* Time-series analytics
* Prometheus monitoring
* Grafana dashboards

---

# ✅ Conclusion

WatchAgent demonstrates a complete weather monitoring pipeline combining real-time data collection, persistent storage, statistical event detection, automated testing, Docker deployment, CI/CD automation, and Cursor-assisted engineering practices.

The project emphasizes clean architecture, explainable event detection, reliability, maintainability, and production-oriented software engineering principles.

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy.orm import Session
from collections import defaultdict
from datetime import datetime, timedelta
import statistics

from app.database.init_db import SessionLocal
from app.database.models import Reading, Event, CityEnum


# =========================================================
# DATA ANALYSIS SKILL
# =========================================================
def analyze_weather_data(question: str = None, days: int = 1):
    """
    Cursor Skill:
    Analyzes stored weather readings and events from database.

    Supports:
    - per-city temperature trends
    - cross-city comparisons
    - event frequency analysis
    - time-window summaries
    """

    db: Session = SessionLocal()

    try:
        since_time = datetime.utcnow() - timedelta(days=days)
        readings = (db.query(Reading).filter(Reading.timestamp >= since_time).all())
        events = (db.query(Event).filter(Event.timestamp >= since_time).all())

        if not readings:
            return {"status": "empty", "message": "No readings found for the given time window"}

        # =====================================================
        # GROUP BY CITY
        # =====================================================
        city_data = defaultdict(list)

        for r in readings:
            city_data[r.city.value].append(r)

        # =====================================================
        # CITY STATISTICS
        # =====================================================
        city_stats = {}

        for city, items in city_data.items():
            temps = [r.temperature for r in items]
            winds = [r.wind_speed for r in items]

            city_stats[city] = {
                "count": len(items),
                "avg_temperature": round(statistics.mean(temps), 2),
                "max_temperature": max(temps),
                "min_temperature": min(temps),
                "avg_wind_speed": round(statistics.mean(winds), 2),
            }

        # =====================================================
        # CROSS CITY COMPARISON
        # =====================================================
        comparison = {}

        cities = list(city_stats.keys())
        if len(cities) > 1:
            for i in range(len(cities)):
                for j in range(i + 1, len(cities)):
                    c1, c2 = cities[i], cities[j]
                    temp_diff = abs(city_stats[c1]["avg_temperature"] - city_stats[c2]["avg_temperature"])
                    comparison[f"{c1}_vs_{c2}"] = {"temperature_difference": round(temp_diff, 2)}

        # =====================================================
        # EVENT ANALYSIS
        # =====================================================
        event_counts = defaultdict(int)

        for e in events:
            event_counts[e.event_type] += 1

        event_summary = dict(event_counts)

        # =====================================================
        # OUTPUT STRUCTURE
        # =====================================================
        result = {
            "status": "success",
            "time_window_days": days,
            "total_readings": len(readings),
            "total_events": len(events),
            "city_statistics": city_stats,
            "cross_city_comparison": comparison,
            "event_summary": event_summary
        }

        return result

    finally:
        db.close()


# =========================================================
# CLI TEST
# =========================================================
if __name__ == "__main__":
    output = analyze_weather_data(days=1)
    print(output)
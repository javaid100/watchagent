from app.database.models import Reading, Event

# =========================================================
# HEALTH CHECK TEST
# =========================================================
def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200

# =========================================================
# READINGS ENDPOINT TEST
# =========================================================
def test_readings_endpoint(client, db_session):
    db_session.add(Reading(city="toronto", temperature=20, apparent_temperature=19, precipitation=0, wind_speed=10, weather_code=1))
    db_session.commit()
    res = client.get("/readings")
    assert res.status_code == 200
    data = res.json()
    assert "readings" in data
    assert isinstance(data["readings"], list)

# =========================================================
# EVENTS ENDPOINT TEST
# =========================================================
def test_events_endpoint(client, db_session):
    db_session.add(Event(city="toronto", event_type="HEATWAVE", description="test event"))
    db_session.commit()
    res = client.get("/events")
    assert res.status_code == 200
    data = res.json()
    assert "events" in data
    assert isinstance(data["events"], list)
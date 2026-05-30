from app.database.models import Reading


# =========================================================
# DEDUPLICATION TEST (PIPELINE LOGIC, NOT DB CONSTRAINT)
# =========================================================
def test_deduplication(db_session):
    r1 = Reading(city="toronto", temperature=20, apparent_temperature=19, precipitation=0, wind_speed=10, weather_code=1)
    r2 = Reading(city="toronto", temperature=20, apparent_temperature=19, precipitation=0, wind_speed=10, weather_code=1)

    db_session.add(r1)
    db_session.add(r2)
    db_session.commit()

    rows = db_session.query(Reading).all()
    assert len(rows) == 2
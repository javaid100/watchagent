import httpx

CITY_COORDS = {
    "ottawa": {"lat": 45.42, "lon": -75.69},
    "toronto": {"lat": 43.70, "lon": -79.42},
    "vancouver": {"lat": 49.25, "lon": -123.12},
}

async def fetch_weather(city: str):
    coords = CITY_COORDS[city]

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={coords['lat']}&longitude={coords['lon']}"
        "&current=temperature_2m,apparent_temperature,precipitation,wind_speed_10m,weather_code"
        "&wind_speed_unit=kmh"
        "&timezone=auto"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

    current = data["current"]
    if not current:
        raise ValueError("No weather data received")

    return {
        "city": city,
        "temperature": current["temperature_2m"],
        "apparent_temperature": current["apparent_temperature"],
        "precipitation": current["precipitation"],
        "wind_speed": current["wind_speed_10m"],
        "weather_code": current["weather_code"],
    }

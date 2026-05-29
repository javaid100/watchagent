"""
Weather Codes Utility Layer
Converts raw weather API codes into semantic intelligence
for event detection, analytics, and alerting.
"""

# =========================================================
# CORE WEATHER CODE MAP
# =========================================================

WEATHER_CODE_MAP = {
    # Clear / sky
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",

    # Fog
    45: "Fog",
    48: "Depositing rime fog",

    # Drizzle
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",

    # Rain
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",

    # Snow
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",

    # Rain showers
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",

    # Thunderstorm
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


# =========================================================
# SEVERITY CLASSIFICATION
# =========================================================

WEATHER_SEVERITY = {
    # Safe / normal
    0: "LOW",
    1: "LOW",
    2: "LOW",
    3: "LOW",

    # Fog
    45: "LOW",
    48: "LOW",

    # Drizzle
    51: "LOW",
    53: "LOW",
    55: "MEDIUM",

    # Rain
    61: "LOW",
    63: "MEDIUM",
    65: "HIGH",

    # Snow
    71: "LOW",
    73: "MEDIUM",
    75: "HIGH",

    # Showers
    80: "MEDIUM",
    81: "MEDIUM",
    82: "HIGH",

    # Storms
    95: "HIGH",
    96: "VERY_HIGH",
    99: "CRITICAL",
}


# =========================================================
# PRECIPITATION CODES
# =========================================================

PRECIPITATION_CODES = {
    51, 53, 55,
    61, 63, 65,
    71, 73, 75,
    80, 81, 82,
    95, 96, 99,
}


# =========================================================
# STORM CODES
# =========================================================

STORM_CODES = {
    95, 96, 99
}


# =========================================================
# CORE FUNCTIONS
# =========================================================

def get_weather_description(code: int) -> str:
    """
    Convert weather code to human-readable description.
    """
    return WEATHER_CODE_MAP.get(code, "Unknown weather condition")


def get_weather_severity(code: int) -> str:
    """
    Returns severity level of weather condition.
    """
    return WEATHER_SEVERITY.get(code, "UNKNOWN")


def is_precipitation(code: int) -> bool:
    """
    Returns True if weather code indicates precipitation.
    """
    return code in PRECIPITATION_CODES


def is_storm(code: int) -> bool:
    """
    Returns True if weather code indicates storm conditions.
    """
    return code in STORM_CODES

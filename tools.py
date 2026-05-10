"""Simulated tool implementations for the Lab 08 Tool Use Pattern agent."""

from __future__ import annotations


WEATHER_DATA = {
    "islamabad": {"temp": 28, "condition": "Partly Cloudy", "humidity": 55},
    "karachi": {"temp": 34, "condition": "Hot and Sunny", "humidity": 70},
    "lahore": {"temp": 32, "condition": "Hazy", "humidity": 60},
    "london": {"temp": 16, "condition": "Overcast", "humidity": 80},
    "dubai": {"temp": 40, "condition": "Clear and Hot", "humidity": 45},
    "new york": {"temp": 22, "condition": "Sunny", "humidity": 50},
}


def get_weather(city: str, unit: str = "celsius") -> dict:
    """Return simulated current weather for a supported city."""

    data = WEATHER_DATA.get(city.lower().strip())
    if not data:
        return {
            "error": f"No weather data available for {city}.",
            "supported_cities": sorted(city.title() for city in WEATHER_DATA),
        }

    normalized_unit = unit.lower().strip()
    temp = data["temp"]
    symbol = "C"
    if normalized_unit == "fahrenheit":
        temp = round(temp * 9 / 5 + 32, 1)
        symbol = "F"

    return {
        "city": city.title(),
        "temperature": f"{temp} deg {symbol}",
        "condition": data["condition"],
        "humidity": f"{data['humidity']}%",
        "source": "Simulated lab dataset",
    }


RATES_TO_PKR = {
    "USD": 278.5,
    "GBP": 352.0,
    "EUR": 303.0,
    "AED": 75.8,
    "SAR": 74.3,
    "PKR": 1.0,
}


def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Convert an amount between supported currencies using simulated rates."""

    from_c = from_currency.upper().strip()
    to_c = to_currency.upper().strip()
    if from_c not in RATES_TO_PKR or to_c not in RATES_TO_PKR:
        return {
            "error": "Currency not supported.",
            "supported_currencies": sorted(RATES_TO_PKR),
        }

    pkr_amount = float(amount) * RATES_TO_PKR[from_c]
    converted = pkr_amount / RATES_TO_PKR[to_c]

    return {
        "original": f"{amount:g} {from_c}",
        "converted": f"{converted:,.2f} {to_c}",
        "rate": f"1 {from_c} = {RATES_TO_PKR[from_c] / RATES_TO_PKR[to_c]:.4f} {to_c}",
        "source": "Simulated lab exchange-rate table",
    }


FLIGHT_BASE_PKR = {
    ("islamabad", "karachi"): 8500,
    ("islamabad", "lahore"): 6000,
    ("islamabad", "dubai"): 35000,
    ("islamabad", "london"): 85000,
    ("karachi", "dubai"): 28000,
    ("lahore", "london"): 80000,
    ("lahore", "karachi"): 9500,
}


def estimate_flight_cost(origin: str, destination: str, passengers: int = 1) -> dict:
    """Estimate economy flight cost between supported cities in PKR."""

    normalized_origin = origin.lower().strip()
    normalized_destination = destination.lower().strip()
    key = (normalized_origin, normalized_destination)
    reverse_key = (normalized_destination, normalized_origin)
    base = FLIGHT_BASE_PKR.get(key) or FLIGHT_BASE_PKR.get(reverse_key)

    if not base:
        return {
            "error": f"Route {origin} to {destination} is not available in the estimator.",
            "supported_routes": [
                f"{start.title()} to {end.title()}" for start, end in sorted(FLIGHT_BASE_PKR)
            ],
        }

    safe_passengers = max(1, int(passengers))
    total = base * safe_passengers

    return {
        "route": f"{origin.title()} to {destination.title()}",
        "passengers": safe_passengers,
        "per_person": f"PKR {base:,}",
        "total_cost": f"PKR {total:,}",
        "note": "Economy class estimate. Actual prices may vary.",
        "source": "Simulated lab fare table",
    }


PRAYER_TIMES = {
    "islamabad": {
        "Fajr": "04:02 AM",
        "Dhuhr": "12:08 PM",
        "Asr": "04:55 PM",
        "Maghrib": "07:02 PM",
        "Isha": "08:30 PM",
    },
    "karachi": {
        "Fajr": "04:38 AM",
        "Dhuhr": "12:29 PM",
        "Asr": "05:03 PM",
        "Maghrib": "07:09 PM",
        "Isha": "08:28 PM",
    },
    "lahore": {
        "Fajr": "04:05 AM",
        "Dhuhr": "12:04 PM",
        "Asr": "04:50 PM",
        "Maghrib": "06:56 PM",
        "Isha": "08:23 PM",
    },
    "peshawar": {
        "Fajr": "04:00 AM",
        "Dhuhr": "12:11 PM",
        "Asr": "05:00 PM",
        "Maghrib": "07:08 PM",
        "Isha": "08:37 PM",
    },
    "quetta": {
        "Fajr": "04:29 AM",
        "Dhuhr": "12:33 PM",
        "Asr": "05:14 PM",
        "Maghrib": "07:22 PM",
        "Isha": "08:47 PM",
    },
}


def get_prayer_times(city: str, date: str) -> dict:
    """Return simulated daily prayer times for supported Pakistani cities."""

    data = PRAYER_TIMES.get(city.lower().strip())
    if not data:
        return {
            "error": f"No prayer time data available for {city}.",
            "supported_cities": sorted(city.title() for city in PRAYER_TIMES),
        }

    return {
        "city": city.title(),
        "date": date,
        **data,
        "calculation_note": "Simulated lab dataset for demonstration. Verify locally for worship use.",
        "source": "Simulated Pakistani prayer-time table",
    }

"""Tool schemas and registry for the Lab 08 Tool Use Pattern agent."""

from __future__ import annotations

from tools import convert_currency, estimate_flight_cost, get_weather


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": (
                "Get current weather for a city. Call this when the user asks "
                "about temperature, weather, humidity, or destination conditions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, for example Islamabad, Dubai, London.",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit. Default: celsius.",
                    },
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "convert_currency",
            "description": (
                "Convert an amount between currencies. Call this when the user asks "
                "about exchange rates, currency conversion, or costs in another currency."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "description": "Amount to convert."},
                    "from_currency": {
                        "type": "string",
                        "description": "Source currency code, for example PKR, USD, GBP.",
                    },
                    "to_currency": {
                        "type": "string",
                        "description": "Target currency code, for example PKR, USD, GBP.",
                    },
                },
                "required": ["amount", "from_currency", "to_currency"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "estimate_flight_cost",
            "description": (
                "Estimate economy flight cost between two cities in PKR. Call this "
                "when the user asks about flight prices, travel cost, or trip budget."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "Departure city."},
                    "destination": {"type": "string", "description": "Arrival city."},
                    "passengers": {
                        "type": "integer",
                        "description": "Number of passengers. Default: 1.",
                    },
                },
                "required": ["origin", "destination"],
            },
        },
    },
]


TOOL_FUNCTIONS = {
    "get_weather": get_weather,
    "convert_currency": convert_currency,
    "estimate_flight_cost": estimate_flight_cost,
}

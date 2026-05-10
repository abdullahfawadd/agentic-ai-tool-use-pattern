# Sample API Responses

These samples were generated in demo mode so the repository can document expected behavior without committing any API key. With `GROQ_API_KEY` configured, the same endpoints use Groq `llama-3.1-8b-instant` with native structured tool calls.

## GET /health

```json
{
  "status": "ok",
  "student": "M Abdullah Fawad",
  "model": "llama-3.1-8b-instant",
  "demo_mode": true,
  "tools": [
    "get_weather",
    "convert_currency",
    "estimate_flight_cost",
    "get_prayer_times"
  ]
}
```

## Single Tool Query

```json
{
  "query": "What is the current weather in Dubai?",
  "expected_tool": "get_weather",
  "expected_turn_count": 1
}
```

## Multi-Tool Query

```json
{
  "query": "I want to travel from Islamabad to London for 2 people. What will it cost in GBP, and what is the weather like there?",
  "expected_tools": [
    "estimate_flight_cost",
    "convert_currency",
    "get_weather"
  ]
}
```

## Prayer Times Query

```json
{
  "query": "What are the prayer times in Islamabad today?",
  "expected_tool": "get_prayer_times"
}
```

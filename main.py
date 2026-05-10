"""FastAPI implementation of the Tool Use Pattern for Lab 08."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from groq import Groq
from pydantic import BaseModel, Field

from schemas import TOOL_FUNCTIONS, TOOL_SCHEMAS


load_dotenv()

MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEMO_MODE = os.getenv("TOOL_USE_DEMO_MODE", "false").lower() in {"1", "true", "yes"}
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Lab 08 Tool Use Agent - Travel Assistant",
    version="1.0.0",
    description="FastAPI + Groq implementation of the Agentic AI Tool Use Pattern.",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

SYSTEM_PROMPT = """
You are a helpful travel planning assistant for Pakistani travellers.
You have access to registered tools for real-world data such as weather,
currency conversion, and travel costs.

Rules:
1. Always use tools for weather, currency, and flight data.
2. Use multiple tools when the query needs more than one data type.
3. Never invent tool data from training memory.
4. If a tool returns an error, explain it honestly and continue with what is known.
5. After all tool results are available, give a concise, friendly answer.
""".strip()


class PlanRequest(BaseModel):
    query: str = Field(..., examples=["Plan a trip from Islamabad to Dubai for 2 people."])
    max_turns: int = Field(default=5, ge=1, le=10)


class ToolCall(BaseModel):
    tool_name: str
    arguments: dict[str, Any]
    result: dict[str, Any]


class PlanResponse(BaseModel):
    answer: str
    tool_calls: list[ToolCall]
    turn_count: int
    model: str = MODEL


def execute_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute the registered Python function requested by the LLM."""

    func = TOOL_FUNCTIONS.get(name)
    if not func:
        return {"error": f"Unknown tool: {name}"}
    try:
        return func(**arguments)
    except TypeError as exc:
        return {"error": f"Invalid arguments for {name}: {exc}"}
    except Exception as exc:  # pragma: no cover - defensive mediation layer
        return {"error": f"Tool execution failed for {name}: {exc}"}


def _assistant_tool_message(message: Any) -> dict[str, Any]:
    """Convert a Groq SDK message object into the API message shape."""

    return {
        "role": "assistant",
        "content": message.content,
        "tool_calls": [tool_call.model_dump() for tool_call in message.tool_calls],
    }


def _parse_money(value: str) -> float:
    match = re.search(r"([\d,]+(?:\.\d+)?)", value)
    return float(match.group(1).replace(",", "")) if match else 0.0


def _demo_tool_plan(query: str) -> list[tuple[str, dict[str, Any]]]:
    """Small deterministic planner used only for screenshots without an API key."""

    text = query.lower()
    calls: list[tuple[str, dict[str, Any]]] = []
    cities = ["islamabad", "karachi", "lahore", "dubai", "london", "new york"]
    destination = next((city.title() for city in cities if f"to {city}" in text), None)
    mentioned_city = next((city.title() for city in cities if city in text), "Dubai")

    if any(word in text for word in ["flight", "cost", "budget", "travel"]):
        origin = "Islamabad"
        destination = destination or mentioned_city
        for city in cities:
            if f"from {city}" in text:
                origin = city.title()
        passengers_match = re.search(r"(\d+)\s*(people|persons|passengers|travellers|travelers)", text)
        passengers = int(passengers_match.group(1)) if passengers_match else 1
        calls.append(("estimate_flight_cost", {"origin": origin, "destination": destination, "passengers": passengers}))

    if any(word in text for word in ["gbp", "usd", "aed", "currency", "convert"]):
        calls.append(("convert_currency", {"amount": 170000, "from_currency": "PKR", "to_currency": "GBP"}))

    if any(word in text for word in ["weather", "temperature", "humidity"]):
        calls.append(("get_weather", {"city": destination or mentioned_city, "unit": "celsius"}))

    if (
        "get_prayer_times" in TOOL_FUNCTIONS
        and any(word in text for word in ["prayer", "namaz", "salah"])
    ):
        calls.append(("get_prayer_times", {"city": destination or mentioned_city, "date": "today"}))

    if not calls:
        calls.append(("get_weather", {"city": "Dubai", "unit": "celsius"}))
    return calls


def _run_demo_agent(query: str, max_turns: int) -> PlanResponse:
    """Return deterministic demo responses when explicitly enabled."""

    tool_log: list[ToolCall] = []
    for name, arguments in _demo_tool_plan(query)[:max_turns]:
        result = execute_tool(name, arguments)
        tool_log.append(ToolCall(tool_name=name, arguments=arguments, result=result))

    facts = []
    for call in tool_log:
        if call.tool_name == "get_weather" and "error" not in call.result:
            facts.append(
                f"{call.result['city']} weather is {call.result['temperature']}, "
                f"{call.result['condition']}, humidity {call.result['humidity']}."
            )
        elif call.tool_name == "estimate_flight_cost" and "error" not in call.result:
            facts.append(
                f"Flight estimate for {call.result['route']} is {call.result['total_cost']} "
                f"for {call.result['passengers']} passenger(s)."
            )
        elif call.tool_name == "convert_currency" and "error" not in call.result:
            facts.append(f"Currency conversion: {call.result['original']} = {call.result['converted']}.")
        elif call.tool_name == "get_prayer_times" and "error" not in call.result:
            facts.append(
                f"Prayer times for {call.result['city']} on {call.result['date']}: "
                f"Fajr {call.result['Fajr']}, Dhuhr {call.result['Dhuhr']}, "
                f"Asr {call.result['Asr']}, Maghrib {call.result['Maghrib']}, "
                f"Isha {call.result['Isha']}."
            )
        else:
            facts.append(str(call.result))

    if len(_demo_tool_plan(query)) > max_turns:
        facts.append("The max_turns safety limit stopped additional tool calls.")

    return PlanResponse(
        answer=" ".join(facts),
        tool_calls=tool_log,
        turn_count=len(tool_log),
        model=f"{MODEL} (demo mode)",
    )


def run_agent(query: str, max_turns: int) -> PlanResponse:
    """Run the open-ended Tool Use dispatch loop."""

    if DEMO_MODE:
        return _run_demo_agent(query, max_turns)
    if client is None:
        raise HTTPException(
            status_code=503,
            detail="GROQ_API_KEY is not configured. Add a rotated key to .env or enable TOOL_USE_DEMO_MODE=true.",
        )

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ]
    tool_log: list[ToolCall] = []

    for turn in range(max_turns):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
            temperature=0.2,
            max_tokens=1024,
        )
        message = response.choices[0].message

        if not message.tool_calls:
            return PlanResponse(
                answer=message.content or "No final response generated.",
                tool_calls=tool_log,
                turn_count=turn,
            )

        messages.append(_assistant_tool_message(message))

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            try:
                arguments = json.loads(tool_call.function.arguments or "{}")
            except json.JSONDecodeError:
                arguments = {}
            result = execute_tool(name, arguments)
            tool_log.append(ToolCall(tool_name=name, arguments=arguments, result=result))
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                }
            )

    final_response = client.chat.completions.create(
        model=MODEL,
        messages=messages
        + [
            {
                "role": "user",
                "content": "The max_turns limit was reached. Give the best final answer using the tool results above.",
            }
        ],
        temperature=0.2,
        max_tokens=1024,
    )
    return PlanResponse(
        answer=final_response.choices[0].message.content or "No final response generated.",
        tool_calls=tool_log,
        turn_count=len(tool_log),
    )


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "student": "M Abdullah Fawad",
        "model": MODEL,
        "demo_mode": DEMO_MODE,
        "tools": list(TOOL_FUNCTIONS.keys()),
    }


@app.post("/plan", response_model=PlanResponse)
def plan(req: PlanRequest) -> PlanResponse:
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="query cannot be empty")
    return run_agent(req.query.strip(), req.max_turns)

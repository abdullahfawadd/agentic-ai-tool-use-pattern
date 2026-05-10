const form = document.querySelector("#queryForm");
const queryInput = document.querySelector("#query");
const maxTurnsInput = document.querySelector("#maxTurns");
const conversation = document.querySelector("#conversation");
const toolList = document.querySelector("#toolList");
const turnCount = document.querySelector("#turnCount");
const traceSummary = document.querySelector("#traceSummary");
const registeredTools = document.querySelector("#registeredTools");
const modelName = document.querySelector("#modelName");
const modeName = document.querySelector("#modeName");
const toolCount = document.querySelector("#toolCount");
const lastRun = document.querySelector("#lastRun");
const runtimePill = document.querySelector("#runtimePill");
const submitButton = document.querySelector(".run-button");

function addMessage(role, content) {
  const article = document.createElement("article");
  article.className = `message ${role}`;

  const avatar = document.createElement("span");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "You" : "AI";

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  const meta = document.createElement("p");
  meta.className = "message-meta";
  meta.textContent = role === "user" ? "Your query" : "Agent answer";

  const text = document.createElement("p");
  text.textContent = content;

  bubble.append(meta, text);
  article.append(avatar, bubble);
  conversation.append(article);
  conversation.scrollTop = conversation.scrollHeight;
  return text;
}

function summarizeResult(call) {
  const result = call.result || {};
  if (result.error) return result.error;
  if (call.tool_name === "estimate_flight_cost") {
    return `${result.route}: ${result.total_cost} for ${result.passengers} passenger(s).`;
  }
  if (call.tool_name === "get_weather") {
    return `${result.city}: ${result.temperature}, ${result.condition}, humidity ${result.humidity}.`;
  }
  if (call.tool_name === "convert_currency") {
    return `${result.original} = ${result.converted}.`;
  }
  if (call.tool_name === "get_prayer_times") {
    return `${result.city}: Fajr ${result.Fajr}, Dhuhr ${result.Dhuhr}, Asr ${result.Asr}, Maghrib ${result.Maghrib}, Isha ${result.Isha}.`;
  }
  return JSON.stringify(result);
}

function makeDetails(label, data, open = false) {
  const details = document.createElement("details");
  details.open = open;

  const summary = document.createElement("summary");
  summary.textContent = label;

  const pre = document.createElement("pre");
  pre.textContent = JSON.stringify(data, null, 2);

  details.append(summary, pre);
  return details;
}

function renderTools(calls, count) {
  turnCount.textContent = `${count} turn${count === 1 ? "" : "s"}`;
  toolList.innerHTML = "";

  traceSummary.innerHTML = "";
  const dot = document.createElement("span");
  dot.className = "trace-dot";
  const text = document.createElement("span");
  text.textContent = calls.length
    ? `${calls.length} tool call${calls.length === 1 ? "" : "s"} executed`
    : "No tool calls executed";
  traceSummary.append(dot, text);

  if (!calls.length) {
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.innerHTML = "<strong>No tool calls</strong><span>The model answered without requesting a tool.</span>";
    toolList.append(empty);
    return;
  }

  calls.forEach((call, index) => {
    const card = document.createElement("article");
    card.className = "tool-card";

    const header = document.createElement("div");
    header.className = "tool-card-header";

    const titleWrap = document.createElement("div");
    titleWrap.className = "tool-title";

    const indexBadge = document.createElement("span");
    indexBadge.className = "tool-index";
    indexBadge.textContent = String(index + 1);

    const title = document.createElement("h3");
    title.textContent = call.tool_name;

    const status = document.createElement("span");
    status.className = "tool-status";
    status.textContent = call.result && call.result.error ? "ERROR" : "EXECUTED";

    titleWrap.append(indexBadge, title);
    header.append(titleWrap, status);

    const body = document.createElement("div");
    body.className = "tool-body";

    const resultLine = document.createElement("div");
    resultLine.className = "result-line";
    resultLine.textContent = summarizeResult(call);

    body.append(
      resultLine,
      makeDetails("Arguments", call.arguments),
      makeDetails("Result JSON", call.result, index === 0),
    );
    card.append(header, body);
    toolList.append(card);
  });
}

async function loadHealth() {
  try {
    const response = await fetch("/health");
    const health = await response.json();
    modelName.textContent = health.model;
    modeName.textContent = health.demo_mode ? "Demo mode" : "Live Groq";
    runtimePill.textContent = health.demo_mode ? "Demo mode" : "Live Groq";
    toolCount.textContent = String(health.tools.length);
    registeredTools.innerHTML = "";
    health.tools.forEach((tool) => {
      const item = document.createElement("span");
      item.textContent = tool;
      registeredTools.append(item);
    });
  } catch {
    modeName.textContent = "Offline";
    runtimePill.textContent = "Offline";
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = queryInput.value.trim();
  if (!query) return;

  submitButton.disabled = true;
  submitButton.textContent = "Running";
  lastRun.textContent = "Running";
  addMessage("user", query);
  const pendingMessage = addMessage("assistant", "Running the tool dispatch loop...");

  try {
    const response = await fetch("/plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query,
        max_turns: Number(maxTurnsInput.value || 5),
      }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Request failed.");
    }
    pendingMessage.textContent = data.answer;
    renderTools(data.tool_calls, data.turn_count);
    lastRun.textContent = `${data.turn_count} turn${data.turn_count === 1 ? "" : "s"}`;
  } catch (error) {
    pendingMessage.textContent = error.message;
    renderTools([], 0);
    lastRun.textContent = "Error";
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Run agent";
  }
});

document.querySelectorAll("[data-prompt]").forEach((button) => {
  button.addEventListener("click", () => {
    queryInput.value = button.dataset.prompt;
    queryInput.focus();
  });
});

loadHealth();

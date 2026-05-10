const form = document.querySelector("#queryForm");
const queryInput = document.querySelector("#query");
const maxTurnsInput = document.querySelector("#maxTurns");
const conversation = document.querySelector("#conversation");
const toolList = document.querySelector("#toolList");
const turnCount = document.querySelector("#turnCount");

function addMessage(role, content) {
  const article = document.createElement("article");
  article.className = `message ${role}`;
  const avatar = document.createElement("span");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "You" : "AI";
  const body = document.createElement("div");
  const meta = document.createElement("p");
  meta.className = "message-meta";
  meta.textContent = role === "user" ? "Your query" : "Agent answer";
  const text = document.createElement("p");
  text.textContent = content;
  body.append(meta, text);
  article.append(avatar, body);
  conversation.append(article);
  conversation.scrollTop = conversation.scrollHeight;
}

function renderTools(calls, count) {
  turnCount.textContent = `${count} turn${count === 1 ? "" : "s"}`;
  toolList.innerHTML = "";
  if (!calls.length) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = "No tools were needed for this query.";
    toolList.append(empty);
    return;
  }

  calls.forEach((call, index) => {
    const card = document.createElement("article");
    card.className = "tool-card";
    const title = document.createElement("h3");
    title.textContent = `${index + 1}. ${call.tool_name}`;
    const pre = document.createElement("pre");
    pre.textContent = JSON.stringify(
      { arguments: call.arguments, result: call.result },
      null,
      2,
    );
    card.append(title, pre);
    toolList.append(card);
  });
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = queryInput.value.trim();
  if (!query) return;

  addMessage("user", query);
  addMessage("assistant", "Running the tool dispatch loop...");
  const pendingMessage = conversation.lastElementChild.querySelector("p:last-child");

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
  } catch (error) {
    pendingMessage.textContent = error.message;
    renderTools([], 0);
  }
});

document.querySelectorAll("[data-prompt]").forEach((button) => {
  button.addEventListener("click", () => {
    queryInput.value = button.dataset.prompt;
    queryInput.focus();
  });
});

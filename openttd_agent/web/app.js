const statusEl = document.getElementById("status");
const feedEl = document.getElementById("feed");
const commandEl = document.getElementById("command");
const thoughtCountEl = document.getElementById("thoughtCount");
const eventCountEl = document.getElementById("eventCount");
const shotCountEl = document.getElementById("shotCount");
const lastUpdatedEl = document.getElementById("lastUpdated");
const apiKeyEl = document.getElementById("apiKey");
const apiStatusEl = document.getElementById("apiStatus");
const modelEl = document.getElementById("model");
const hostEl = document.getElementById("host");
const portEl = document.getElementById("port");

async function fetchState() {
  const response = await fetch("/api/state");
  const data = await response.json();
  render(data.memory, data.config);
}

function render(memory, config) {
  const now = new Date();
  statusEl.textContent = `Мыслей: ${memory.thoughts.length}, событий: ${memory.events.length}`;
  thoughtCountEl.textContent = memory.thoughts.length;
  eventCountEl.textContent = memory.events.length;
  shotCountEl.textContent = memory.events.filter((event) => event.type === "screenshot").length;
  lastUpdatedEl.textContent = now.toLocaleTimeString("ru-RU");
  updateConfigForm(config);

  feedEl.innerHTML = "";
  const feedItems = buildFeed(memory);
  feedItems.forEach((item) => feedEl.appendChild(item));
}

async function sendCommand() {
  const payload = { command: commandEl.value };
  await fetch("/api/command", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  commandEl.value = "";
  await fetchState();
}

async function runCycle() {
  const response = await fetch("/api/cycle", { method: "POST" });
  const data = await response.json();
  render(data.memory, data.config);
}

async function saveConfig() {
  const payload = {
    gemini_api_key: apiKeyEl.value,
    model: modelEl.value,
    openttd_host: hostEl.value,
    openttd_port: portEl.value,
  };
  const response = await fetch("/api/config", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  apiKeyEl.value = "";
  updateConfigForm(data.config);
  await fetchState();
}

async function checkApi() {
  const response = await fetch("/api/check_api", { method: "POST" });
  const result = await response.json();
  apiStatusEl.textContent = result.ok ? "API подключен" : result.message || "Ошибка API";
}

async function checkGame() {
  await fetch("/api/check_game", { method: "POST" });
  await fetchState();
}

async function takeShot() {
  await fetch("/api/screenshot", { method: "POST" });
  await fetchState();
}

function updateConfigForm(config) {
  if (!config) {
    return;
  }
  modelEl.value = config.model || "";
  hostEl.value = config.openttd_host || "";
  portEl.value = config.openttd_port || "";
  if (config.gemini_api_key_set) {
    apiStatusEl.textContent = `Ключ сохранён: ${config.gemini_api_key_masked}`;
  } else {
    apiStatusEl.textContent = "Ключ не задан";
  }
}

function buildFeed(memory) {
  const feed = [];
  const thoughts = memory.thoughts.map((thought) => ({
    type: "thought",
    role: thought.role,
    timestamp: thought.timestamp,
    content: thought.content,
  }));
  const events = memory.events.map((event) => ({
    type: "event",
    role: "event",
    timestamp: event.timestamp,
    content: event,
  }));
  const combined = thoughts.concat(events).sort((a, b) => {
    return String(a.timestamp).localeCompare(String(b.timestamp));
  });
  combined.reverse().slice(0, 80).forEach((item) => {
    const li = document.createElement("li");
    li.className = `chat-bubble role-${item.role}`;
    const meta = document.createElement("div");
    meta.className = "chat-meta";
    meta.textContent = `${item.timestamp || ""} · ${item.role}`;
    li.appendChild(meta);
    const body = document.createElement("div");
    if (item.type === "thought") {
      body.textContent = item.content;
    } else {
      body.textContent = JSON.stringify(item.content);
      if (item.content.type === "screenshot" && item.content.payload?.data_uri) {
        const img = document.createElement("img");
        img.src = item.content.payload.data_uri;
        img.alt = "OpenTTD screenshot";
        img.className = "chat-screenshot";
        li.appendChild(img);
      }
    }
    li.appendChild(body);
    feed.push(li);
  });
  return feed;
}

setInterval(fetchState, 4000);
fetchState();

document.getElementById("sendCommand").addEventListener("click", sendCommand);
document.getElementById("runCycle").addEventListener("click", runCycle);
document.getElementById("saveConfig").addEventListener("click", saveConfig);
document.getElementById("checkApi").addEventListener("click", checkApi);
document.getElementById("checkGame").addEventListener("click", checkGame);
document.getElementById("takeShot").addEventListener("click", takeShot);
document.getElementById("clearCommand").addEventListener("click", () => {
  commandEl.value = "";
});
document.getElementById("refreshState").addEventListener("click", fetchState);

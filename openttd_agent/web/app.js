const statusEl = document.getElementById("status");
const thoughtsEl = document.getElementById("thoughts");
const eventsEl = document.getElementById("events");
const commandEl = document.getElementById("command");
const thoughtCountEl = document.getElementById("thoughtCount");
const eventCountEl = document.getElementById("eventCount");
const lastUpdatedEl = document.getElementById("lastUpdated");

async function fetchState() {
  const response = await fetch("/api/state");
  const data = await response.json();
  render(data.memory);
}

function render(memory) {
  const now = new Date();
  statusEl.textContent = `Мыслей: ${memory.thoughts.length}, событий: ${memory.events.length}`;
  thoughtCountEl.textContent = memory.thoughts.length;
  eventCountEl.textContent = memory.events.length;
  lastUpdatedEl.textContent = now.toLocaleTimeString("ru-RU");

  thoughtsEl.innerHTML = "";
  memory.thoughts.slice().reverse().forEach((thought) => {
    const item = document.createElement("li");
    item.textContent = `${thought.timestamp} [${thought.role}] ${thought.content}`;
    thoughtsEl.appendChild(item);
  });

  eventsEl.innerHTML = "";
  memory.events.slice().reverse().forEach((event) => {
    const item = document.createElement("li");
    item.textContent = JSON.stringify(event);
    eventsEl.appendChild(item);
  });
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
  render(data.memory);
}

setInterval(fetchState, 4000);
fetchState();

document.getElementById("sendCommand").addEventListener("click", sendCommand);
document.getElementById("runCycle").addEventListener("click", runCycle);
document.getElementById("clearCommand").addEventListener("click", () => {
  commandEl.value = "";
});
document.getElementById("refreshState").addEventListener("click", fetchState);

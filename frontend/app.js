const API_BASE = "";

const thread = document.getElementById("thread");
const form = document.getElementById("composerForm");
const input = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const resetBtn = document.getElementById("resetBtn");
const statusDot = document.getElementById("statusDot");
const statusText = document.getElementById("statusText");

const SESSION_KEY = "seecs_helpdesk_session_id";

function getSessionId() {
  let id = localStorage.getItem(SESSION_KEY);
  if (!id) {
    id = crypto.randomUUID ? crypto.randomUUID() : String(Date.now()) + Math.random();
    localStorage.setItem(SESSION_KEY, id);
  }
  return id;
}

let sessionId = getSessionId();

function autoResize() {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 140) + "px";
}
input.addEventListener("input", autoResize);

function scrollToBottom() {
  thread.scrollTop = thread.scrollHeight;
}

function intentLabel(intent) {
  switch (intent) {
    case "document_qa": return "Answered from documents";
    case "help_request": return "Help request drafted";
    case "general_chat": return "General chat";
    default: return "";
  }
}

function intentThinkingLabel(intent) {
  switch (intent) {
    case "document_qa": return "Searching documents…";
    case "help_request": return "Drafting help request…";
    default: return "Thinking…";
  }
}

function addUserMessage(text) {
  const row = document.createElement("div");
  row.className = "msg-row user";
  row.innerHTML = `<div class="bubble"></div>`;
  row.querySelector(".bubble").textContent = text;
  thread.appendChild(row);
  scrollToBottom();
}

function addTypingIndicator() {
  const row = document.createElement("div");
  row.className = "msg-row assistant";
  row.id = "typingRow";
  row.innerHTML = `
    <div class="bubble">
      <span class="typing"><span></span><span></span><span></span></span>
    </div>`;
  thread.appendChild(row);
  scrollToBottom();
}

function removeTypingIndicator() {
  const row = document.getElementById("typingRow");
  if (row) row.remove();
}

function startAssistantMessage() {
  const row = document.createElement("div");
  row.className = "msg-row assistant";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  const text = document.createElement("div");
  text.className = "bubble-text";
  const cursor = document.createElement("span");
  cursor.className = "cursor";
  bubble.appendChild(text);
  bubble.appendChild(cursor);
  row.appendChild(bubble);

  const meta = document.createElement("div");
  meta.className = "msg-meta";
  row.appendChild(meta);

  thread.appendChild(row);
  scrollToBottom();

  return { row, bubble, text, cursor, meta, raw: "" };
}

function finishAssistantMessage(handle, data) {
  handle.cursor.remove();
  const html = marked.parse(handle.raw);
  handle.text.innerHTML = DOMPurify.sanitize(html);
  handle.text.classList.add("rendered");
  handle.meta.textContent = intentLabel(data.intent);

  if (data.sources && data.sources.length > 0) {
    const seen = new Set();
    const sourcesEl = document.createElement("div");
    sourcesEl.className = "sources";
    data.sources.forEach((s) => {
      const key = s.source + "|" + s.page;
      if (seen.has(key)) return;
      seen.add(key);
      const item = document.createElement("div");
      item.className = "source-item";
      item.textContent = s.page != null ? `${s.source} — page ${s.page + 1}` : s.source;
      sourcesEl.appendChild(item);
    });
    handle.row.appendChild(sourcesEl);
  }

  scrollToBottom();
}

function addErrorMessage(text) {
  const row = document.createElement("div");
  row.className = "msg-row assistant";
  row.innerHTML = `<div class="bubble error"></div>`;
  row.querySelector(".bubble").textContent = text;
  thread.appendChild(row);
  scrollToBottom();
}

async function sendMessage(message) {
  addUserMessage(message);
  addTypingIndicator();
  sendBtn.disabled = true;

  let handle = null;

  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId }),
    });

    if (!res.ok || !res.body) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || `Request failed (${res.status})`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split("\n\n");
      buffer = events.pop();

      for (const raw of events) {
        const line = raw.trim();
        if (!line.startsWith("data:")) continue;

        const payload = JSON.parse(line.slice(5).trim());

        if (payload.type === "intent") {
          removeTypingIndicator();
          handle = startAssistantMessage();
          handle.meta.textContent = intentThinkingLabel(payload.intent);
        } else if (payload.type === "token") {
          if (!handle) {
            removeTypingIndicator();
            handle = startAssistantMessage();
          }
          handle.raw += payload.content;
          handle.text.textContent += payload.content;
          scrollToBottom();
        } else if (payload.type === "done") {
          if (handle) finishAssistantMessage(handle, payload);
        } else if (payload.type === "error") {
          throw new Error(payload.message);
        }
      }
    }
  } catch (err) {
    removeTypingIndicator();
    if (handle) handle.row.remove();
    addErrorMessage(
      "Something went wrong reaching the helpdesk assistant. " +
      (err.message || "Please try again.")
    );
  } finally {
    sendBtn.disabled = false;
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const message = input.value.trim();
  if (!message) return;
  input.value = "";
  autoResize();
  sendMessage(message);
});

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    form.requestSubmit();
  }
});

resetBtn.addEventListener("click", async () => {
  try {
    await fetch(`${API_BASE}/reset/${sessionId}`, { method: "POST" });
  } catch (err) {
    // Non-fatal - a fresh session id below still isolates history.
  }
  localStorage.removeItem(SESSION_KEY);
  sessionId = getSessionId();
  thread.innerHTML = `
    <div class="intro">
      <p class="intro-lede">Ask about SEECS or NUST academic policy, handbooks, or forms.</p>
      <p class="intro-sub">If something isn't in the documents, I'll say so — and can draft a help request instead.</p>
    </div>`;
});

async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (res.ok) {
      statusDot.className = "status-dot online";
      statusText.textContent = "Online";
    } else {
      throw new Error();
    }
  } catch {
    statusDot.className = "status-dot offline";
    statusText.textContent = "Offline";
  }
}

checkHealth();

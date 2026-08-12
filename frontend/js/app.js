const API = {
  health: "/health",
  warmup: "/warmup",
  search: "/search",
  answer: "/search/answer",
  results: "/search/results",
  chatNew: "/conversation/new",
  chatEnd: "/conversation/end",
};

const ENDPOINTS = {
  full: API.search,
  answer: API.answer,
  results: API.results,
};

let currentMode = "full";
let chatActive = false;
let engineReady = false;
let loadingInterval = null;
let loadingStart = 0;

const chatPill = document.getElementById("chatPill");
const chatLabel = document.getElementById("chatLabel");
const startChatBtn = document.getElementById("startChatBtn");
const endChatBtn = document.getElementById("endChatBtn");
const chatMessages = document.getElementById("chatMessages");
const chatWelcome = document.getElementById("chatWelcome");
const questionInput = document.getElementById("questionInput");
const charCount = document.getElementById("charCount");
const submitBtn = document.getElementById("submitBtn");
const clearBtn = document.getElementById("clearBtn");
const loadingPanel = document.getElementById("loadingPanel");
const loadingTitle = document.getElementById("loadingTitle");
const elapsedTime = document.getElementById("elapsedTime");
const progressFill = document.getElementById("progressFill");
const systemStatus = document.getElementById("systemStatus");
const enginePill = document.getElementById("enginePill");
const engineLabel = document.getElementById("engineLabel");
const toast = document.getElementById("toast");

const fetchOpts = {
  credentials: "include",
  headers: { "Content-Type": "application/json" },
};

function showToast(message, type = "error") {
  toast.textContent = message;
  toast.className = `toast toast--${type}`;
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 4500);
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function setChatUI(active) {
  chatActive = active;

  chatPill.classList.toggle("chat-pill--active", active);
  chatPill.classList.toggle("chat-pill--idle", !active);
  chatLabel.textContent = active ? "Chat active" : "No active chat";

  startChatBtn.classList.toggle("hidden", active);
  endChatBtn.classList.toggle("hidden", !active);

  questionInput.disabled = !active;
  submitBtn.disabled = !active;
  clearBtn.disabled = !active;

  questionInput.placeholder = active
    ? "Ask a cybersecurity question…"
    : "Start a chat first, then ask your question…";

  if (!active) {
    chatWelcome.classList.remove("hidden");
  }
}

function setLoading(isLoading) {
  submitBtn.disabled = isLoading || !chatActive;
  submitBtn.querySelector(".btn__text").classList.toggle("hidden", isLoading);
  submitBtn.querySelector(".btn__loader").classList.toggle("hidden", !isLoading);
  loadingPanel.classList.toggle("hidden", !isLoading);

  if (isLoading) {
    loadingStart = performance.now();
    progressFill.style.width = "12%";
    loadingInterval = setInterval(() => {
      const elapsed = (performance.now() - loadingStart) / 1000;
      elapsedTime.textContent = `${elapsed.toFixed(1)}s`;
      progressFill.style.width = `${Math.min(90, 12 + elapsed * 8)}%`;
    }, 120);
  } else {
    clearInterval(loadingInterval);
    progressFill.style.width = "100%";
  }
}

function renderSourcesHtml(sources, sourcesOnly = false) {
  if (!sources?.length) {
    return '<p class="msg-sources__empty">No sources retrieved.</p>';
  }

  return sources
    .map(
      (item, i) => `
      <details class="msg-source" ${sourcesOnly ? "open" : ""}>
        <summary>#${i + 1} · ${escapeHtml(item.question)}</summary>
        ${sourcesOnly ? "" : `<p class="msg-source__answer">${escapeHtml(item.answer)}</p>`}
        <span class="msg-source__meta">ID ${item.id} · distance ${Number(item.distance).toFixed(4)}</span>
      </details>`
    )
    .join("");
}

function updateMessagesView() {
  document.querySelectorAll(".msg-group").forEach((group) => {
    const answerBlock = group.querySelector(".msg-answer-block");
    const sourcesBlock = group.querySelector(".msg-sources-block");

    if (answerBlock) {
      answerBlock.classList.toggle("hidden", currentMode === "results");
    }
    if (sourcesBlock) {
      sourcesBlock.classList.toggle("hidden", currentMode === "answer");
    }
  });
}

function appendMessage(question, data, elapsedSec, mode = currentMode) {
  chatWelcome.classList.add("hidden");

  const wrapper = document.createElement("div");
  wrapper.className = "msg-group reveal";
  wrapper.dataset.mode = mode;

  const showAnswer = mode === "full" || mode === "answer";
  const showSources = mode === "full" || mode === "results";
  const sourcesOnly = mode === "results";

  let assistantHtml = "";

  if (showAnswer && data.answer) {
    assistantHtml += `<div class="msg msg--assistant msg-answer-block ${sourcesOnly ? "hidden" : ""}"><div class="msg__bubble">${escapeHtml(data.answer)}</div><span class="msg__time">${elapsedSec.toFixed(1)}s</span></div>`;
  }

  if (showSources && data.retrieved_results) {
    assistantHtml += `<div class="msg-sources msg-sources-block ${mode === "answer" ? "hidden" : ""}">${renderSourcesHtml(data.retrieved_results, sourcesOnly)}</div>`;
  }

  wrapper.innerHTML = `
    <div class="msg msg--user">
      <div class="msg__bubble">${escapeHtml(question)}</div>
    </div>
    ${assistantHtml}
  `;

  chatMessages.appendChild(wrapper);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  updateMessagesView();
}

async function apiPost(url, body = null) {
  const response = await fetch(url, {
    ...fetchOpts,
    method: "POST",
    body: body ? JSON.stringify(body) : null,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    const detail = err.detail;
    const message = typeof detail === "string"
      ? detail
      : Array.isArray(detail)
        ? detail.map((item) => item.msg).join(", ")
        : err.message || `Request failed (${response.status})`;
    throw new Error(message);
  }

  return response.json();
}

async function startChat() {
  try {
    startChatBtn.disabled = true;
    await apiPost(API.chatNew);

    chatMessages.querySelectorAll(".msg-group").forEach((el) => el.remove());
    chatWelcome.classList.remove("hidden");
    chatWelcome.querySelector("h3").textContent = "Chat started";
    chatWelcome.querySelector("p").textContent = "Ask your first question below.";

    setChatUI(true);
    showToast("New chat started — context saved in MongoDB.", "info");
    questionInput.focus();
  } catch (error) {
    showToast(error.message);
  } finally {
    startChatBtn.disabled = false;
  }
}

async function endChat() {
  try {
    endChatBtn.disabled = true;
    await apiPost(API.chatEnd);

    setChatUI(false);
    questionInput.value = "";
    charCount.textContent = "0";
    chatMessages.querySelectorAll(".msg-group").forEach((el) => el.remove());
    chatWelcome.classList.remove("hidden");
    chatWelcome.querySelector("h3").textContent = "Chat ended";
    chatWelcome.querySelector("p").textContent = "Click Start Chat to begin a new session.";

    showToast("Chat ended and saved to MongoDB.", "info");
  } catch (error) {
    showToast(error.message);
  } finally {
    endChatBtn.disabled = false;
  }
}

async function submitQuestion() {
  const question = questionInput.value.trim();

  if (!chatActive) {
    showToast("Start a chat session first.", "info");
    return;
  }

  if (!question) {
    showToast("Type a question first.", "info");
    questionInput.focus();
    return;
  }

  if (!engineReady) {
    showToast("AI engine still loading — first load can take 1–2 minutes.", "info");
  }

  setLoading(true);
  loadingTitle.textContent =
    currentMode === "results"
      ? "Searching sources…"
      : engineReady
        ? "CYFEDIS is thinking…"
        : "Loading AI model (first time is slow)…";

  const startTime = performance.now();
  const modeUsed = currentMode;

  try {
    const data = await apiPost(ENDPOINTS[modeUsed], { question });
    const elapsed = (performance.now() - startTime) / 1000;

    appendMessage(question, data, elapsed, modeUsed);
    questionInput.value = "";
    charCount.textContent = "0";
  } catch (error) {
    showToast(error.message || "Something went wrong.");
  } finally {
    setLoading(false);
    questionInput.focus();
  }
}

async function warmupEngine() {
  enginePill.classList.remove("hidden");
  engineLabel.textContent = "Loading AI engine…";

  const poll = async () => {
    try {
      const response = await fetch(API.warmup);
      const data = await response.json();

      if (data.status === "ready") {
        engineReady = true;
        enginePill.classList.add("engine-pill--ready");
        engineLabel.textContent = "Engine ready";
        return;
      }

      engineLabel.textContent = "Loading AI engine…";
      setTimeout(poll, 3000);
    } catch {
      engineLabel.textContent = "Engine offline";
    }
  };

  poll();
}

async function checkHealth() {
  const label = systemStatus.querySelector(".status-label");

  try {
    const response = await fetch(API.health);
    const data = await response.json();

    systemStatus.classList.remove("header__status--ok", "header__status--degraded", "header__status--error");

    if (data.status === "ok") {
      systemStatus.classList.add("header__status--ok");
      label.textContent = "All systems operational";
    } else {
      systemStatus.classList.add("header__status--degraded");
      const mongoDown = data.services?.mongo?.status !== "ok";
      label.textContent = mongoDown
        ? "MongoDB offline — Start Chat disabled"
        : "Partial — degraded";
    }
  } catch {
    systemStatus.classList.add("header__status--error");
    label.textContent = "API offline";
  }
}

function setMode(mode) {
  currentMode = mode;
  document.querySelectorAll(".mode-tab").forEach((tab) => {
    const isActive = tab.dataset.mode === mode;
    tab.classList.toggle("active", isActive);
    tab.setAttribute("aria-selected", isActive);
  });
  updateMessagesView();
}

function clearInput() {
  questionInput.value = "";
  charCount.textContent = "0";
  questionInput.focus();
}

startChatBtn.addEventListener("click", startChat);
endChatBtn.addEventListener("click", endChat);
submitBtn.addEventListener("click", submitQuestion);
clearBtn.addEventListener("click", clearInput);

questionInput.addEventListener("input", () => {
  charCount.textContent = questionInput.value.length;
});

questionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    submitQuestion();
  }
});

document.querySelectorAll(".mode-tab").forEach((tab) => {
  tab.addEventListener("click", () => setMode(tab.dataset.mode));
});

document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    if (!chatActive) {
      showToast("Start a chat first.", "info");
      return;
    }
    questionInput.value = chip.dataset.question;
    charCount.textContent = questionInput.value.length;
    questionInput.focus();
  });
});

setChatUI(false);
checkHealth();
warmupEngine();
setInterval(checkHealth, 60000);

import { get, remove } from "./api.js";
import { assistantIcon, findAssistant, loadAssistants, renderAssistantCards, renderAssistantPicker } from "./assistants.js";
import { appendMessage, getConversation, getMessages, renderConversationMessages, sendChatMessage } from "./chat.js";

const state = { selectedAssistantId: "general", conversationId: null, busy: false, toastTimer: null, health: null };
const homeView = document.getElementById("home-view");
const chatView = document.getElementById("chat-view");
const messagesList = document.getElementById("messages-list");
const chatError = document.getElementById("chat-error");
const sidebar = document.getElementById("sidebar");
const mobileScrim = document.getElementById("mobile-scrim");

function showToast(message) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.classList.add("is-visible");
  clearTimeout(state.toastTimer);
  state.toastTimer = setTimeout(() => toast.classList.remove("is-visible"), 3000);
}

function selectAssistant(assistantId) {
  const assistant = findAssistant(assistantId);
  if (!assistant || !assistant.available) return;
  state.selectedAssistantId = assistantId;
  document.getElementById("selected-assistant-name").textContent = assistant.name;
  document.querySelector(".selected-assistant-wrap .mini-assistant-icon").textContent = assistantIcon(assistantId);
  document.getElementById("chat-composer-assistant").textContent = assistant.name;
  const picker = document.getElementById("assistant-picker");
  picker.hidden = true;
  picker.setAttribute("aria-hidden", "true");
}

function closeSidebar() {
  sidebar.classList.remove("is-open");
  mobileScrim.classList.remove("is-visible");
}

function showHome() {
  homeView.hidden = false;
  chatView.hidden = true;
  document.getElementById("topbar-title").textContent = "Home";
  closeSidebar();
}

function showChat() {
  homeView.hidden = true;
  chatView.hidden = false;
  document.getElementById("topbar-title").textContent = "Conversation";
  closeSidebar();
}

function resetConversation(assistantId = state.selectedAssistantId) {
  const assistant = findAssistant(assistantId);
  if (!assistant || !assistant.available) return;
  state.conversationId = null;
  state.selectedAssistantId = assistant.id;
  messagesList.replaceChildren();
  chatError.hidden = true;
  chatError.textContent = "";
  document.getElementById("chat-title").textContent = "New conversation";
  document.getElementById("chat-assistant-label").textContent = assistant.name.toUpperCase();
  document.getElementById("chat-assistant-icon").textContent = assistantIcon(assistant.id);
  document.getElementById("chat-composer-assistant").textContent = assistant.name;
  document.getElementById("chat-prompt").value = "";
  showChat();
  document.getElementById("chat-prompt").focus();
}

function setBusy(isBusy) {
  state.busy = isBusy;
  document.querySelectorAll(".chat-composer .send-button, #home-prompt-form .send-button").forEach((button) => {
    button.disabled = isBusy;
  });
}

async function submitMessage(message, sourceInput) {
  if (!message.trim() || state.busy) return;
  const assistant = findAssistant(state.selectedAssistantId);
  if (!assistant || !assistant.available) {
    showToast("Choose an available assistant before sending.");
    return;
  }
  if (sourceInput && sourceInput.id === "home-prompt") {
    state.conversationId = null;
    messagesList.replaceChildren();
  }
  if (sourceInput) sourceInput.value = "";
  showChat();
  if (messagesList.children.length === 0) {
    document.getElementById("chat-title").textContent = message.trim().slice(0, 54) || "New conversation";
    document.getElementById("chat-assistant-label").textContent = assistant.name.toUpperCase();
    document.getElementById("chat-assistant-icon").textContent = assistantIcon(assistant.id);
    document.getElementById("chat-composer-assistant").textContent = assistant.name;
  }
  chatError.hidden = true;
  appendMessage(messagesList, "user", message);
  const pending = appendMessage(messagesList, "assistant", "ROSE is thinking", { pending: true, id: "pending-message" });
  setBusy(true);
  try {
    const result = await sendChatMessage(state.selectedAssistantId, message, state.conversationId);
    state.conversationId = result.conversation_id;
    pending.remove();
    appendMessage(messagesList, "assistant", result.message);
    if (result.title) document.getElementById("chat-title").textContent = result.title;
    await refreshConversations();
  } catch (error) {
    pending.remove();
    if (error.conversationId) state.conversationId = error.conversationId;
    chatError.textContent = error.message;
    chatError.hidden = false;
  } finally {
    setBusy(false);
  }
}

function formatRelativeDate(value) {
  const date = new Date(value);
  if (Number.isNaN(date.valueOf())) return "";
  const days = Math.floor((Date.now() - date.valueOf()) / 86400000);
  if (days <= 0) return "Today";
  if (days === 1) return "Yesterday";
  if (days < 7) return days + " days ago";
  return date.toLocaleDateString([], { month: "short", day: "numeric" });
}

async function refreshConversations() {
  const list = document.getElementById("recent-conversations");
  try {
    const conversations = await get("/conversations?limit=5");
    list.replaceChildren();
    if (conversations.length === 0) {
      const empty = document.createElement("p");
      empty.className = "empty-state compact";
      empty.textContent = "No conversations yet. Start with a prompt above.";
      list.append(empty);
      return;
    }
    conversations.forEach((conversation) => {
      const row = document.createElement("button");
      row.type = "button";
      row.className = "conversation-row";
      row.addEventListener("click", () => openConversation(conversation.id));
      const icon = document.createElement("span");
      icon.className = "conversation-row-icon";
      icon.textContent = assistantIcon(conversation.assistant_id);
      icon.setAttribute("aria-hidden", "true");
      const copy = document.createElement("span");
      copy.className = "conversation-row-copy";
      const title = document.createElement("strong");
      title.textContent = conversation.title;
      const assistant = document.createElement("small");
      assistant.textContent = conversation.assistant_name;
      copy.append(title, assistant);
      const time = document.createElement("span");
      time.className = "conversation-row-time";
      time.textContent = formatRelativeDate(conversation.updated_at);
      row.append(icon, copy, time);
      list.append(row);
    });
  } catch (error) {
    list.replaceChildren();
    const empty = document.createElement("p");
    empty.className = "empty-state compact";
    empty.textContent = error.message;
    list.append(empty);
  }
}

async function openConversation(conversationId) {
  try {
    const [conversation, messages] = await Promise.all([
      getConversation(conversationId),
      getMessages(conversationId)
    ]);
    const assistant = findAssistant(conversation.assistant_id);
    if (!assistant || !assistant.available) {
      showToast("This conversation uses an assistant that is not available.");
      return;
    }
    state.conversationId = conversation.id;
    state.selectedAssistantId = assistant.id;
    document.getElementById("selected-assistant-name").textContent = assistant.name;
    document.querySelector(".selected-assistant-wrap .mini-assistant-icon").textContent = assistantIcon(assistant.id);
    document.getElementById("chat-title").textContent = conversation.title;
    document.getElementById("chat-assistant-label").textContent = assistant.name.toUpperCase();
    document.getElementById("chat-assistant-icon").textContent = assistantIcon(assistant.id);
    document.getElementById("chat-composer-assistant").textContent = assistant.name;
    chatError.hidden = true;
    renderConversationMessages(messagesList, messages);
    const historyDialog = document.getElementById("conversations-dialog");
    if (historyDialog.open) historyDialog.close();
    showChat();
  } catch (error) {
    showToast(error.message);
  }
}

async function refreshAllConversations() {
  const list = document.getElementById("all-conversations-list");
  list.replaceChildren();
  try {
    const conversations = await get("/conversations?limit=100");
    if (conversations.length === 0) {
      const empty = document.createElement("p");
      empty.className = "empty-state";
      empty.textContent = "No saved conversations yet.";
      list.append(empty);
      return;
    }
    conversations.forEach((conversation) => {
      const row = document.createElement("div");
      row.className = "history-entry";
      const openButton = document.createElement("button");
      openButton.className = "history-open";
      openButton.type = "button";
      openButton.addEventListener("click", () => openConversation(conversation.id));
      const icon = document.createElement("span");
      icon.className = "history-entry-icon";
      icon.textContent = assistantIcon(conversation.assistant_id);
      icon.setAttribute("aria-hidden", "true");
      const copy = document.createElement("span");
      copy.className = "history-entry-copy";
      const title = document.createElement("strong");
      title.textContent = conversation.title;
      const details = document.createElement("small");
      details.textContent = conversation.assistant_name + " · " + formatRelativeDate(conversation.updated_at);
      copy.append(title, details);
      openButton.append(icon, copy);

      const deleteButton = document.createElement("button");
      deleteButton.className = "delete-conversation";
      deleteButton.type = "button";
      deleteButton.textContent = "Delete";
      deleteButton.addEventListener("click", async () => {
        if (!window.confirm("Delete this conversation and its messages? This cannot be undone.")) return;
        try {
          await remove("/conversations/" + encodeURIComponent(conversation.id));
          if (state.conversationId === conversation.id) {
            state.conversationId = null;
            messagesList.replaceChildren();
            showHome();
          }
          await Promise.all([refreshAllConversations(), refreshConversations()]);
          showToast("Conversation deleted.");
        } catch (error) {
          showToast(error.message);
        }
      });
      row.append(openButton, deleteButton);
      list.append(row);
    });
  } catch (error) {
    const message = document.createElement("p");
    message.className = "empty-state";
    message.textContent = error.message;
    list.append(message);
  }
}

function renderSettingsStatus() {
  const list = document.getElementById("settings-status-list");
  if (!state.health) return;
  list.replaceChildren();
  [
    ["Backend", "Connected"],
    ["MySQL", state.health.database === "connected" ? "Connected" : "Not connected"],
    ["Gemini API key", state.health.ai_configured ? "Configured" : "Not configured"]
  ].forEach(([label, value]) => {
    const row = document.createElement("div");
    row.className = "settings-status-item";
    const name = document.createElement("span");
    name.textContent = label;
    const status = document.createElement("strong");
    status.textContent = value;
    row.append(name, status);
    list.append(row);
  });
}

async function updateHealth() {
  const pill = document.getElementById("connection-pill");
  try {
    state.health = await get("/health");
    pill.lastElementChild.textContent = state.health.database === "connected" ? "Services connected" : "Database not connected";
    pill.classList.toggle("is-good", state.health.database === "connected");
    pill.classList.toggle("is-warning", state.health.database !== "connected");
  } catch {
    pill.lastElementChild.textContent = "Backend unavailable";
    pill.classList.add("is-warning");
  }
  renderSettingsStatus();
}

function openDialog(dialogId) {
  const dialog = document.getElementById(dialogId);
  if (dialog && !dialog.open) dialog.showModal();
}

function setActiveNav(section) {
  document.querySelectorAll(".nav-item[data-section]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.section === section);
  });
}

function wireEvents() {
  document.getElementById("home-prompt-form").addEventListener("submit", (event) => {
    event.preventDefault();
    submitMessage(document.getElementById("home-prompt").value, document.getElementById("home-prompt"));
  });
  document.getElementById("chat-form").addEventListener("submit", (event) => {
    event.preventDefault();
    submitMessage(document.getElementById("chat-prompt").value, document.getElementById("chat-prompt"));
  });
  document.querySelectorAll(".suggestion-chip").forEach((button) => {
    button.addEventListener("click", () => {
      const prompt = document.getElementById("home-prompt");
      prompt.value = button.dataset.prompt;
      prompt.focus();
      prompt.setSelectionRange(prompt.value.length, prompt.value.length);
    });
  });
  document.getElementById("selected-assistant").addEventListener("click", () => {
    const picker = document.getElementById("assistant-picker");
    picker.hidden = !picker.hidden;
    picker.setAttribute("aria-hidden", String(picker.hidden));
    document.getElementById("selected-assistant").setAttribute("aria-expanded", String(!picker.hidden));
  });
  document.querySelectorAll("[data-section]").forEach((button) => {
    button.addEventListener("click", () => {
      setActiveNav(button.dataset.section);
      if (button.dataset.section === "conversations") {
        closeSidebar();
        openDialog("conversations-dialog");
        refreshAllConversations();
        return;
      }
      showHome();
      if (button.dataset.section === "crew") document.getElementById("crew-section").scrollIntoView({ behavior: "smooth" });
      if (button.dataset.section === "activity") {
        document.getElementById("activity-section").scrollIntoView({ behavior: "smooth" });
      }
    });
  });
  document.querySelectorAll("[data-planned]").forEach((button) => {
    button.addEventListener("click", () => showToast(button.dataset.planned + " is planned for a future ROSE release."));
  });
  document.querySelectorAll("[data-view='home']").forEach((button) => button.addEventListener("click", showHome));
  document.querySelectorAll("[data-close-dialog]").forEach((button) => {
    button.addEventListener("click", () => button.closest("dialog").close());
  });
  document.querySelectorAll("dialog").forEach((dialog) => {
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) dialog.close();
    });
  });
  document.getElementById("new-chat-button").addEventListener("click", () => resetConversation());
  document.getElementById("mobile-new-chat").addEventListener("click", () => resetConversation());
  document.getElementById("home-new-chat").addEventListener("click", () => resetConversation());
  document.getElementById("chat-new-chat").addEventListener("click", () => resetConversation());
  document.getElementById("back-to-home").addEventListener("click", showHome);
  document.getElementById("view-all-conversations").addEventListener("click", () => {
    openDialog("conversations-dialog");
    refreshAllConversations();
  });
  document.getElementById("menu-button").addEventListener("click", () => {
    sidebar.classList.add("is-open");
    mobileScrim.classList.add("is-visible");
  });
  mobileScrim.addEventListener("click", closeSidebar);
  document.getElementById("about-button").addEventListener("click", () => openDialog("about-dialog"));
  document.getElementById("team-button").addEventListener("click", () => openDialog("team-dialog"));
  ["settings-button", "topbar-settings"].forEach((id) => {
    document.getElementById(id).addEventListener("click", () => {
      renderSettingsStatus();
      openDialog("settings-dialog");
    });
  });
  document.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      resetConversation();
    }
    if (event.key === "Escape") closeSidebar();
    if (event.key === "Enter" && event.target.matches("#home-prompt, #chat-prompt") && !event.shiftKey) {
      event.preventDefault();
      event.target.form.requestSubmit();
    }
  });
}

async function initialize() {
  wireEvents();
  try {
    await loadAssistants();
    renderAssistantCards((id) => {
      selectAssistant(id);
      document.getElementById("home-prompt").focus();
    });
    renderAssistantPicker(selectAssistant);
    selectAssistant(state.selectedAssistantId);
  } catch (error) {
    document.getElementById("assistant-count").textContent = "Could not load assistants";
    showToast(error.message);
  }
  await Promise.all([refreshConversations(), updateHealth()]);
}

initialize();

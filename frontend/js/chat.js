import { get, post } from "./api.js";

export function sendChatMessage(assistantId, message, conversationId) {
  return post("/chat", {
    assistant_id: assistantId,
    message,
    conversation_id: conversationId || null
  });
}

export function getConversation(conversationId) {
  return get("/conversations/" + encodeURIComponent(conversationId));
}

export function getMessages(conversationId) {
  return get("/conversations/" + encodeURIComponent(conversationId) + "/messages");
}

export function appendMessage(container, role, content, options = {}) {
  const row = document.createElement("article");
  row.className = "message-row " + (role === "user" ? "user-message" : "assistant-message");
  if (options.pending) row.classList.add("is-pending");
  if (options.id) row.id = options.id;
  const avatar = document.createElement("span");
  avatar.className = "message-avatar";
  avatar.setAttribute("aria-hidden", "true");
  avatar.textContent = role === "user" ? "F" : "R";
  const body = document.createElement("div");
  body.className = "message-body";
  const meta = document.createElement("p");
  meta.className = "message-meta";
  const name = document.createElement("strong");
  name.textContent = role === "user" ? "You" : "ROSE";
  const time = document.createElement("time");
  time.textContent = options.time || "just now";
  meta.append(name, time);
  const bubble = document.createElement("div");
  bubble.className = "message-bubble";
  bubble.textContent = content;
  if (options.pending) {
    const dots = document.createElement("span");
    dots.className = "typing-dots";
    dots.setAttribute("aria-label", "Assistant is responding");
    for (let index = 0; index < 3; index += 1) dots.append(document.createElement("i"));
    bubble.append(dots);
  }
  body.append(meta, bubble);
  row.append(avatar, body);
  container.append(row);
  container.scrollTop = container.scrollHeight;
  return row;
}

export function renderConversationMessages(container, messages) {
  container.replaceChildren();
  messages.forEach((message) => {
    const timestamp = message.created_at ? new Date(message.created_at) : null;
    const time = timestamp && !Number.isNaN(timestamp.valueOf())
      ? timestamp.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })
      : "";
    appendMessage(container, message.role, message.content, { time });
  });
}

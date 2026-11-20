import { get } from "./api.js";

const iconById = { general: "✦", coding: "{ }", research: "⌕", document: "▤" };
let assistantList = [];

export async function loadAssistants() {
  assistantList = await get("/assistants");
  return assistantList;
}

export function findAssistant(assistantId) {
  return assistantList.find((assistant) => assistant.id === assistantId);
}

export function assistantIcon(assistantId) {
  return iconById[assistantId] || "✦";
}

export function renderAssistantCards(onSelect) {
  const grid = document.getElementById("assistant-grid");
  const count = document.getElementById("assistant-count");
  if (!grid || assistantList.length === 0) return;

  grid.replaceChildren();
  count.textContent = assistantList.filter((item) => item.available).length + " ready to help";
  assistantList.forEach((assistant) => {
    const card = document.createElement("article");
    card.className = "assistant-card" + (assistant.available ? " is-available" : "");
    const head = document.createElement("div");
    head.className = "assistant-card-head";
    const icon = document.createElement("span");
    icon.className = "assistant-icon";
    icon.setAttribute("aria-hidden", "true");
    icon.textContent = iconById[assistant.id] || "✦";
    const status = document.createElement("span");
    status.className = "availability" + (assistant.available ? "" : " is-planned");
    status.textContent = assistant.available ? "Available" : "Planned";
    head.append(icon, status);

    const title = document.createElement("h3");
    title.textContent = assistant.name;
    const description = document.createElement("p");
    description.textContent = assistant.description;
    const footer = document.createElement("div");
    footer.className = "assistant-card-footer";
    const capability = document.createElement("small");
    capability.textContent = assistant.available ? "Ready for a conversation" : "Coming in a future release";
    const button = document.createElement("button");
    button.className = "try-button";
    button.type = "button";
    button.textContent = assistant.available ? "Try it →" : "Planned";
    if (assistant.available) {
      button.addEventListener("click", () => onSelect(assistant.id));
    } else {
      button.disabled = true;
      button.title = assistant.name + " is planned and is not available yet.";
    }
    footer.append(capability, button);
    card.append(head, title, description, footer);
    grid.append(card);
  });
}

export function renderAssistantPicker(onSelect) {
  const picker = document.getElementById("assistant-picker");
  if (!picker) return;
  picker.replaceChildren();
  assistantList.filter((assistant) => assistant.available).forEach((assistant) => {
    const button = document.createElement("button");
    button.className = "picker-option";
    button.type = "button";
    const icon = document.createElement("span");
    icon.className = "mini-assistant-icon";
    icon.textContent = iconById[assistant.id] || "✦";
    const name = document.createElement("span");
    name.textContent = assistant.name;
    const label = document.createElement("small");
    label.textContent = "Available";
    button.append(icon, name, label);
    button.addEventListener("click", () => onSelect(assistant.id));
    picker.append(button);
  });
}

const isSeparatePreview = window.location.port === "5500";
const API_BASE = isSeparatePreview ? "http://127.0.0.1:8000/api" : "/api";

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(API_BASE + path, {
      ...options,
      headers: { "Content-Type": "application/json", ...(options.headers || {}) }
    });
  } catch {
    throw new Error("ROSE could not reach FastAPI. Start the backend and try again.");
  }

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = body.detail;
    const message = typeof detail === "string"
      ? detail
      : (detail && detail.message) || "The request could not be completed.";
    const error = new Error(message);
    error.status = response.status;
    error.conversationId = detail && detail.conversation_id;
    throw error;
  }
  return body;
}

export function get(path) {
  return request(path);
}

export function post(path, data) {
  return request(path, { method: "POST", body: JSON.stringify(data) });
}

export function remove(path) {
  return request(path, { method: "DELETE" });
}

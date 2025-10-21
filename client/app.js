/**
 * Main application JavaScript
 */

const WS_URL = "ws://localhost:8080/ws";

let ws = null;
let username = "";
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;

// DOM elements
const loginForm = document.getElementById("loginForm");
const chatContainer = document.getElementById("chatContainer");
const usernameInput = document.getElementById("usernameInput");
const tokenInput = document.getElementById("tokenInput");
const connectBtn = document.getElementById("connectBtn");
const messagesDiv = document.getElementById("messages");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const statusDiv = document.getElementById("status");
const errorDiv = document.getElementById("error");

// WebSocket connection
function connect() {
  username = usernameInput.value.trim();
  const token = tokenInput.value.trim();

  if (!username) {
    showError("Veuillez entrer un pseudo");
    return;
  }

  if (!token) {
    showError("Veuillez entrer un token d'authentification");
    return;
  }

  if (token.length < 8) {
    showError("Le token doit contenir au moins 8 caractères");
    return;
  }

  hideError();
  updateStatus("connecting", "Connexion en cours...");
  connectBtn.disabled = true;

  // Connection with token in query parameter
  ws = new WebSocket(`${WS_URL}?token=${encodeURIComponent(token)}`);

  ws.onopen = () => {
    console.log("✅ WebSocket connected");
    updateStatus("connected", `Connecté en tant que ${username}`);
    reconnectAttempts = 0;

    // Show chat interface
    loginForm.style.display = "none";
    chatContainer.classList.add("active");
    messageInput.focus();
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      handleMessage(data);
    } catch (error) {
      console.error("Error parsing message:", error);
    }
  };

  ws.onerror = (error) => {
    console.error("❌ WebSocket error:", error);
  };

  ws.onclose = (event) => {
    console.log("WebSocket closed:", event.code, event.reason);
    updateStatus("disconnected", "Déconnecté");

    // If auth error (code 1008), show error
    if (event.code === 1008) {
      showError("Authentification échouée : token invalide");
      chatContainer.classList.remove("active");
      loginForm.style.display = "block";
      connectBtn.disabled = false;
      return;
    }

    // Attempt reconnection
    if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
      reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 10000);
      updateStatus("connecting", `Reconnexion dans ${delay / 1000}s...`);
      setTimeout(connect, delay);
    } else {
      showError("Impossible de se reconnecter. Rechargez la page.");
      chatContainer.classList.remove("active");
      loginForm.style.display = "block";
      connectBtn.disabled = false;
    }
  };
}

// Send message
function sendMessage() {
  const text = messageInput.value.trim();

  if (!text) return;
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    showError("Non connecté au serveur");
    return;
  }

  ws.send(
    JSON.stringify({
      type: "message",
      username: username,
      text: text,
    })
  );

  messageInput.value = "";
  messageInput.focus();
}

// Handle received messages
function handleMessage(data) {
  switch (data.type) {
    case "message":
      addUserMessage(data.username, data.text, data.timestamp);
      break;
    case "user_joined":
      addSystemMessage(`${data.username} a rejoint le chat`);
      break;
    case "user_left":
      addSystemMessage(`${data.username} a quitté le chat`);
      break;
    default:
      console.log("Unknown message type:", data.type);
  }
}

// Display messages
function addUserMessage(username, text, timestamp) {
  const messageDiv = document.createElement("div");
  messageDiv.className = "message user";

  const time = new Date(timestamp).toLocaleTimeString("fr-FR", {
    hour: "2-digit",
    minute: "2-digit",
  });

  messageDiv.innerHTML = `
    <div class="username">${escapeHtml(username)}</div>
    <div class="text">${escapeHtml(text)}</div>
    <div class="timestamp">${time}</div>
  `;

  messagesDiv.appendChild(messageDiv);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function addSystemMessage(text) {
  const messageDiv = document.createElement("div");
  messageDiv.className = "message system";
  messageDiv.textContent = text;

  messagesDiv.appendChild(messageDiv);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Utilities
function updateStatus(state, text) {
  statusDiv.className = `status ${state}`;
  statusDiv.textContent = text;
}

function showError(message) {
  errorDiv.textContent = message;
  errorDiv.style.display = "block";
}

function hideError() {
  errorDiv.style.display = "none";
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Event listeners
connectBtn.addEventListener("click", connect);

usernameInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") connect();
});

tokenInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") connect();
});

sendBtn.addEventListener("click", sendMessage);

messageInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

// Handle disconnection
window.addEventListener("beforeunload", () => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.close();
  }
});

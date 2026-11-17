// Dynamically populate the model dropdown on page load
window.onload = async () => {
  try {
    const res = await fetch("/models");
    const data = await res.json();
    const select = document.getElementById("model-select");

    data.models.forEach(model => {
      const opt = document.createElement("option");
      opt.value = model;
      opt.innerText = model;
      select.appendChild(opt);
    });
  } catch (error) {
    alert("Failed to load models.");
  }
};

// Initialize the selected model and show chat UI
async function initModel() {
  const model = document.getElementById("model-select").value;
  if (!model) {
    alert("Please select a model.");
    return;
  }

  const loadingEl = document.getElementById("loading");
  loadingEl.style.display = "block";

  try {
    const res = await fetch("/init_model", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model })
    });

    loadingEl.style.display = "none";

    if (res.ok) {
      document.getElementById("chat-window").style.display = "block";
      document.getElementById("messages").innerHTML = "";
    } else {
      alert("Failed to initialize model.");
    }
  } catch (err) {
    loadingEl.style.display = "none";
    alert("An error occurred while initializing the model.");
  }
}

// Handle sending a message and receiving a response
async function sendMessage() {
  const promptInput = document.getElementById("prompt");
  const prompt = promptInput.value.trim();
  if (!prompt) return;

  // Show user message
  appendMessage("You", prompt, "msg-user");
  promptInput.value = "";
  promptInput.disabled = true;

  // Temporary bot response placeholder
  const loadingMsg = document.createElement("div");
  loadingMsg.className = "msg-bot";
  loadingMsg.innerText = "Bot: Thinking...";
  document.getElementById("messages").appendChild(loadingMsg);

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt })
    });

    const data = await res.json();
    loadingMsg.innerText = `Bot: ${data.response}`;
  } catch (err) {
    loadingMsg.innerText = "Bot: Error getting response.";
    loadingMsg.style.color = "red";
  }

  promptInput.disabled = false;
  promptInput.focus();

  // Scroll to bottom
  const msgBox = document.getElementById("messages");
  msgBox.scrollTop = msgBox.scrollHeight;
}

// Append a message to the chat window
function appendMessage(sender, text, className) {
  const msgDiv = document.createElement("div");
  msgDiv.className = className;
  msgDiv.innerText = `${sender}: ${text}`;
  document.getElementById("messages").appendChild(msgDiv);
}

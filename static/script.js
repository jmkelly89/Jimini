const chat = document.getElementById("chat");
const form = document.getElementById("chat-form");
const input = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");

function addBubble(text, role, extraClass = "") {
  const row = document.createElement("div");
  row.className = `message ${role}`;

  const bubble = document.createElement("span");
  bubble.className = `bubble ${extraClass}`.trim();
  bubble.textContent = text;

  row.appendChild(bubble);
  chat.appendChild(row);
  chat.scrollTop = chat.scrollHeight;
  return row;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  addBubble(message, "user");
  input.value = "";
  input.disabled = true;
  sendBtn.disabled = true;

  const typingRow = addBubble("Jimini is typing…", "jimini", "typing");

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await response.json();

    typingRow.remove();

    if (!response.ok) {
      addBubble(data.error || "Something went wrong.", "jimini", "error");
    } else {
      addBubble(data.reply, "jimini");
    }
  } catch (err) {
    typingRow.remove();
    addBubble("Couldn't reach Jimini. Check your connection.", "jimini", "error");
  } finally {
    input.disabled = false;
    sendBtn.disabled = false;
    input.focus();
  }
});

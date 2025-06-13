document.addEventListener("DOMContentLoaded", function () {
  const userInput = document.getElementById("user-input");
  const sendButton = document.querySelector(".send-button");
  const chatContainer = document.getElementById("chat-container");
  const welcomePrompt = document.getElementById("welcome-prompt");
  const footer = document.getElementById("footer");
  let isProcessing = false;

  // 👉 Thêm tin nhắn vào khung chat
  function addMessage(message, isUser) {
    if (welcomePrompt) welcomePrompt.style.display = "none";

    const messageDiv = document.createElement("div");
    messageDiv.classList.add("chat-message", isUser ? "user-message" : "bot-message");

    // Nếu là người dùng: hiển thị text thường
    // Nếu là bot: hiển thị HTML từ Markdown
    if (isUser) {
      messageDiv.textContent = message;
    } else {
      try {
        messageDiv.innerHTML = marked.parse(message); // dùng thư viện marked để parse markdown
      } catch (e) {
        messageDiv.textContent = message;
      }
    }

    chatContainer.appendChild(messageDiv);
    window.scrollTo(0, document.body.scrollHeight);

    // Ẩn/hiện footer
    const messages = chatContainer.querySelectorAll(".chat-message");
    if (messages.length > 0) {
      footer?.classList.add("hidden");
    } else {
      footer?.classList.remove("hidden");
    }
  }

  // 👉 Gửi câu hỏi đến server
  async function sendMessage() {
    if (isProcessing) return;

    const message = userInput.value.trim();
    if (!message) return;

    isProcessing = true;
    addMessage(message, true);
    userInput.value = "";

    try {
      const response = await fetch("/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ question: message }) // 🔍 key phải là 'question' để Flask đọc được
      });

      // Parse kết quả từ backend
      const data = await response.json();

      if (response.ok && data.answer) {
        addMessage(data.answer, false);
      } else if (data.error) {
        addMessage(`❗ Lỗi: ${data.error}`, false);
      } else {
        addMessage("⚠️ Đã xảy ra lỗi không xác định.", false);
      }
    } catch (error) {
      console.error("❌ Lỗi khi gửi yêu cầu:", error);
      addMessage("Không thể kết nối đến máy chủ. Vui lòng kiểm tra lại kết nối.", false);
    } finally {
      isProcessing = false;
    }
  }

  // 👉 Gửi bằng Enter
  userInput.addEventListener("keypress", function (event) {
    if (event.key === "Enter" && !event.shiftKey && !isProcessing) {
      event.preventDefault(); // tránh xuống dòng
      sendMessage();
    }
  });

  // 👉 Gửi bằng nút "Gửi"
  sendButton.addEventListener("click", function () {
    if (!isProcessing) {
      sendMessage();
    }
  });
});

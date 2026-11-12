
const input = document.getElementById("userInput");
const chatMessages = document.getElementById("chatMessages");
const sendButton = document.getElementById("sendButton");


function addMessage(content, role) {

    const message = document.createElement("div");
    message.className = `message ${role}`;

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = role === "assistant" ? "✦" : "U";

    const messageContent = document.createElement("div");
    messageContent.className = "message-content";

    // Use textContent to safely display chatbot responses
    messageContent.textContent = content;

    message.appendChild(avatar);
    message.appendChild(messageContent);

    chatMessages.appendChild(message);

    chatMessages.scrollTop = chatMessages.scrollHeight;

    return message;
}


async function sendMessage() {

    const message = input.value.trim();

    if (!message || sendButton.disabled) {
        return;
    }

    // Display user message
    addMessage(message, "user");

    input.value = "";
    sendButton.disabled = true;

    // Show loading message
    const loadingMessage = addMessage(
        "Thinking...",
        "assistant"
    );

    try {

        const response = await fetch(
            "http://127.0.0.1:8001/chat",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    message: message
                })
            }
        );

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Backend request failed");
        }

        const data = await response.json();

        // Remove loading message
        loadingMessage.remove();

        // Display AI response
        addMessage(data.reply, "assistant");

    } catch (error) {

        loadingMessage.remove();

        addMessage(
            "Sorry, something went wrong. Please check your backend and Ollama connection. " + error.message,
            "assistant"
        );

    } finally {

        sendButton.disabled = false;
        input.focus();

    }
}


// Handle suggestion buttons
function useSuggestion(text) {

    input.value = text;
    sendMessage();

}


// Send message when Enter is pressed
input.addEventListener("keydown", function(event) {

    if (event.key === "Enter") {
        sendMessage();
    }

});

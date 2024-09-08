// This function retrieves the user's message, sends it to Dialogflow,
// and handles any potential errors by displaying a message in the chat.
document.getElementById("send").addEventListener("click", async function () {
  let message = document.getElementById("message").value;
  if (message) {
    appendMessage("You", message);
    try {
      await sendToDialogflow(message);
    } catch (error) {
      console.error("Error sending message to Dialogflow:", error);
      appendMessage(
        "Bot",
        "Sorry, I encountered an error processing your request."
      );
    }
    document.getElementById("message").value = "";
  }
});

// Creates a new message element and appends it to the 'messages' div,
// and ensures the chat window scrolls to show the latest message.
function appendMessage(sender, message) {
  let messagesDiv = document.getElementById("messages");
  let messageElement = document.createElement("div");
  messageElement.classList.add("message");
  messageElement.innerHTML = `<strong>${sender}:</strong> <span>${message}</span>`;
  messagesDiv.appendChild(messageElement);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Fetch the access token from the server.
// Makes a request to your server to obtain an access token needed for authenticating with Dialogflow.
async function getAccessTokenFromServer() {
  try {
    const response = await fetch("http://localhost:3000/getAccessToken");
    if (!response.ok) throw new Error("Failed to fetch access token");
    const data = await response.json();
    return data.token;
  } catch (error) {
    console.error("Error fetching access token:", error);
    throw error;
  }
}

// This function creates a new session, sends the user's message to Dialogflow,
// and then appends the bot's reply to the chat window. Handles errors and logs responses.
async function sendToDialogflow(message) {
  const sessionId = Math.random().toString(36).substring(7);
  const accessToken = await getAccessTokenFromServer();

  try {
    const response = await fetch(
      `https://dialogflow.googleapis.com/v2/projects/scheduling-chatbot-434201/agent/sessions/${sessionId}:detectIntent`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          queryInput: {
            text: {
              text: message,
              languageCode: "en-US",
            },
          },
        }),
      }
    );

    if (!response.ok) {
      throw new Error(
        `Dialogflow request failed with status ${response.status}`
      );
    }

    const data = await response.json();
    console.log("Dialogflow Response:", data);
    const reply =
      data.queryResult.fulfillmentText || "No response from Dialogflow";
    appendMessage("Bot", reply);
  } catch (error) {
    console.error("Error sending message to Dialogflow:", error);
    appendMessage("Bot", "An error occurred while processing your request.");
  }
}

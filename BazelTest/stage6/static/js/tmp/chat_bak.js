const socket = new WebSocket("ws://127.0.0.1:8888/ws");
const messagesDiv = document.getElementById("messages");
const inputField = document.getElementById("chat_input");
const sendButton = document.getElementById("sendButton");

socket.onopen = event => {
    console.log("WebSocket connection opened");
};

socket.onmessage = event => {
    const response = event.data;
    // const responseDiv = document.createElement("div");
    // responseDiv.textContent = "Bot: ";
    displayResponse(response);
};


socket.onclose = event => {
    console.log("WebSocket connection closed");
};

// function displayResponse(response, responseDiv) {
//     messagesDiv.appendChild(responseDiv);
//     console.log(response.length,response)
//     if (response.includes("\n")){
//         response = "<br>";
//     }
//     responseDiv.innerHTML += response;
//     // const words = response.split(" ");
//     // response.forEach((word, index) => {
//     //     setTimeout(() => {
//     //         responseDiv.textContent += word + " ";
//     //     }, index * 100); // Adjust the delay as needed
//     // });
// }


var responseDiv;
var isCollecting = false;
var accumulatedResponse = "";

async function formatResponse(response) {
    if (response.includes("\n")){
        response = "<br>";
    }
    responseDiv.innerHTML += response;

}


function displayResponse(response) {
    if (response === "START MSG") {
        isCollecting = true;
        responseDiv = document.createElement("div");
        responseDiv.textContent = "Bot: ";
        messagesDiv.appendChild(responseDiv);
    } else if (response === "END MSG") {
        isCollecting = false;
    } else {
        if (isCollecting) {
                if (response.includes("\n")){
        response = "<br><br>";
    }
        responseDiv.innerHTML += response;

        }
    }
}


sendButton.addEventListener("click", () => {
    const userQuestion = inputField.value;



    if (userQuestion.trim() !== "") {
        displayMessage(`${userQuestion}`);
        socket.send(userQuestion);

        // Clear input field
        inputField.value = "";
    }
});

function displayMessage(message) {
    // const messageDiv = document.createElement("div");
    // messageDiv.textContent = message;

    var user_model = document.createElement("div")
    user_model.className = "user";
    var user_content = document.createElement("div");
    user_content.style.width = "50%";
    user_content.style.marginLeft = "25%";

    user_content.innerHTML = message;
    user_model.appendChild(user_content);
    messagesDiv.appendChild(user_model);
}

inputField.addEventListener("keyup", event => {
    if (event.key === "Enter") {
        sendButton.click();
    }
});

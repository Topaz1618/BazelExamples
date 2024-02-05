const socket = new WebSocket("ws://127.0.0.1:8888/ws");
const messagesDiv = document.getElementById("messages");
const inputField = document.getElementById("chat_input");
const sendButton = document.getElementById("sendButton");

socket.onopen = event => {
    console.log("WebSocket connection opened");
    var type = window.location.pathname;
    // 在这里可以使用 JavaScript 中的 type 变量
    console.log(type);

    const data = {
      "command_type": 1,
      "payload": type.split("/")[1]
    };

    const jsonData = JSON.stringify(data);
    socket.send(jsonData);

    // socket.send(jsonData);
};

socket.onmessage = event => {
    const response = event.data;
    // console.log(response)
    displayResponse(response);
};


socket.onclose = event => {
    console.log("WebSocket connection closed");
};

var responseDiv;
var isCollecting = false;
var accumulatedResponse = "";

async function formatResponse(response) {
    if (response.includes("\n")){
        response = "<br>";
        // console.log("ok")
    }
    responseDiv.innerHTML += response;

}


function codeBtnCreator(){
    var button = document.createElement("button");
    button.className = "copy-button";
    button.setAttribute("onclick", "copyContent(this)");

    var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.style.height = "16px";
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("fill", "none");
    svg.setAttribute("stroke", "currentColor");
    svg.setAttribute("stroke-width", "2");
    svg.setAttribute("stroke-linecap", "round");
    svg.setAttribute("stroke-linejoin", "round");

    var path1 = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path1.setAttribute("d", "M17 3H7C5.89543 3 5 3.89543 5 5V19C5 20.1046 5.89543 21 7 21H17C18.1046 21 19 20.1046 19 19V5C19 3.89543 18.1046 3 17 3Z");

    var path2 = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path2.setAttribute("d", "M15 1H9C7.89543 1 7 1.89543 7 3V5H17V3C17 1.89543 16.1046 1 15 1Z");

    var path3 = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path3.setAttribute("d", "M8 9H16");

    svg.appendChild(path1);
    svg.appendChild(path2);
    svg.appendChild(path3);

    button.appendChild(svg);

    var span = document.createElement("span");
    span.style.height = "16px";
    span.innerText = "Copy code";

    button.appendChild(span);

    return button

}


function displayResponse(response) {
    // console.log(response)
    if (response === "START MSG") {
        isCollecting = true;
        is_code = false;
        end_flag = "";

        responseDiv = document.createElement("div");
        responseDiv.className = "bot"
        responseDiv.style.color = "#374151"
        responseDiv.style.borderBottom = "solid 1px rgba(0,0,0,.1)"
        bot_content = document.createElement("div");
        bot_content.style.width = "50%";
        bot_content.style.marginLeft = "25%";
        bot_content.style.marginTop = "17px";
        bot_content.style.marginBottom = "17px";
        bot_content.textContent = "";

        responseDiv.appendChild(bot_content)
        messagesDiv.appendChild(responseDiv);

    } else if (response === "END MSG") {
        isCollecting = false;
    } else {
        if (isCollecting) {
            console.log(response);
            if (response.includes("\n") && is_code == false){
                response += "<br>";
            }
            window.scrollTo(0, document.body.scrollHeight);

            console.log("code：", is_code);
            if (response.includes('```') && is_code == false){
                is_code = true;
                end_flag = "";
                lang = "";

                CodeModel = document.createElement("div");
                CodeModel.className = "code-block";
                CodeModel.style.position = "relative"

                var CodeHeader = document.createElement("div");
                CodeHeader.className = "code-header"
                CodeHeader.style.height = "26px"

                lang_info = document.createElement("span");
                lang_info.className = "language";

                var btn = codeBtnCreator();
                CodeHeader.appendChild(lang_info);
                CodeHeader.appendChild(btn);
                CodeModel.appendChild(CodeHeader);

                var CodePre = document.createElement("pre");

                Code = document.createElement("code");

                Code.style.marginTop = "28px";

                Code.innerHTML = ""

                CodePre.appendChild(Code);
                CodeModel.appendChild(CodePre);
                bot_content.appendChild(CodeModel)


            }else if(end_flag.includes('```') && is_code == true){
                is_code = false;
                end_flag = "";
                bot_content.innerHTML += response;

            }else if(is_code == true) {
                if(response.includes('`')){
                    end_flag += response;
                }else if(lang==""){
                    lang = response;
                    lang_info.innerText = lang;
                    Code.className = `code language-${lang} hljs`;
                }else{
                    console.log("!!!!!!",response);
                    Code.textContent += response;
                }

                hljs.highlightBlock(Code);

            }else{
                if (response.includes('div')){
                    // response =  "<span>" + response + "</span>";
                    var element = document.createElement('span');
                    element.innerText = response;
                    bot_content.appendChild(element);
                }
                else if (response.includes('`<') || response.includes('<h')){
                    var element = document.createElement('span');
                    // response =  "<span>" + response + "</span>";
                    element.innerText = response;
                    bot_content.appendChild(element);
                }

                else {
                    bot_content.innerHTML += response;
                }
            }

        }
    }
}

sendButton.addEventListener("click", () => {
    inputField.scrollLeft = inputField.scrollWidth

    const userQuestion = inputField.value;
    if (userQuestion.trim() !== "") {
        displayMessage(`${userQuestion}`);

        const data = {
          "command_type": 2,
          "payload": userQuestion
        };
        const jsonData = JSON.stringify(data);

        socket.send(jsonData);
        // Clear input field
        inputField.value = "";

        document.querySelector(".formbold-email-subscription-form").style.height = "48px"
        document.getElementById("chat_input").style.height = "44px";
         window.scrollTo(0, document.body.scrollHeight);
    }
});


function displayMessage(message) {
    var user_model = document.createElement("div")
    user_model.className = "user";
    user_model.style.borderBottom = "solid 1px rgba(0,0,0,.1)"
    user_model.style.color = "#343541";

    var user_content = document.createElement("div");
    user_content.style.width = "50%";
    user_content.style.marginLeft = "25%";
    user_content.style.marginTop = "17px";
    user_content.style.marginBottom = "17px";


    user_content.innerText = message;
    user_model.appendChild(user_content);
    messagesDiv.appendChild(user_model);
}

inputField.addEventListener("keyup", event => {
    if (event.key === "Enter") {
        sendButton.click();
    }
});



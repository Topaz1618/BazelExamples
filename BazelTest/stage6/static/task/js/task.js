const TaskStatusEN = {
  1: "PENDING",
  2: "IN_PROGRESS",
  3: "COMPLETED",
  4: "FAILED",
  5: "CANCELLED",
  6: "RETRYING",
  7: "TIMEOUT"
};

const TaskStatusENToCN = {
  1: "PENDING",
  2: "IN_PROGRESS",
  3: "COMPLETED",
  4: "FAILED",
  5: "CANCELLED",
  6: "RETRYING",
  7: "TIMEOUT"
};

const TaskStatus = {
  PENDING: { value: 1 },
  IN_PROGRESS: { value: 2 },
  COMPLETED: { value: 3 },
  FAILED: { value: 4 },
  CANCELLED: { value: 5 },
  RETRYING: { value: 6 },
  TIMEOUT: { value: 7 }
};


// 通过值获取键名
function getStatusKey(status) {
  return Object.keys(TaskStatus).find(key => TaskStatus[key].value === status);
}

function getStatusText(status) {
  return TaskStatusEN[status];
}

function updateProgressBar(percentage) {
    var progressBarFill = document.getElementById("progress-bar-fill");
    progressBarFill.style.width = percentage + "%";
    progressBarFill.innerHTML = percentage + "%";
}


function updateProgressBarFailed() {
    console.log("!!!")
    var progressBarFill = document.getElementById("progress-bar-fill");
    progressBarFill.style.backgroundColor = "#e74c3c"; /* Red */
}

function updateProgressBarCanceled() {
    console.log("!!!")
    var progressBar = document.getElementById("progress-bar");
    progressBar.style.backgroundColor = "#e74c3c"; /* Red */
}


function ConvertIntToText(){
    var status = document.getElementById("task_status").innerText;
    var statusText = getStatusText(status);
    document.getElementById("task_status").innerText = statusText;
}


function updateTaskStatusDiv(status){
    var status_tag = document.getElementById("task_status");
    var statusText = getStatusText(status);
    status_tag.innerText = statusText;
    status_tag.className = statusText.toLowerCase();
}



function openModal() {
    var modal = document.getElementById('myModal');
    modal.style.display = 'block';
}

// Function to close the modal
function closeModal() {
    var modal = document.getElementById('myModal');
    modal.style.display = 'none';
}


function showDetails(nodeId) {
    var detailsDropdown = document.getElementById('detailsDropdown');
    var detailsContent = document.getElementById('detailsContent');

    var detailsIdleNodes = document.getElementById('detailsIdleNodes');
    var detailsPendingTasks = document.getElementById('detailsPendingTasks');
    var detailsProcessingTasks = document.getElementById('detailsProcessingTasks');
    // Set all details content divs to display: none
    detailsIdleNodes.style.display = "none";
    detailsPendingTasks.style.display = "none";
    detailsProcessingTasks.style.display = "none";
    // Show the specific details content based on the clicked button
    if (nodeId === "idleNodes") {
        detailsIdleNodes.style.display = "";
    } else if (nodeId === "pendingTasks") {
        detailsPendingTasks.style.display = "";
    } else {
        detailsProcessingTasks.style.display = "";
    }

    detailsContent.style.display = ""
    var button = document.getElementById(nodeId);
    var rect = button.getBoundingClientRect();

    detailsDropdown.style.top = rect.bottom + 'px';
    detailsDropdown.style.display = 'block';
}

function hideDetails() {
    document.getElementById('detailsDropdown').style.display = 'none';
}

function showTooltip(element) {
    console.log("?????",element.innerText, );
    var tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    if (element.innerText > 0){
        element.disabled = false;
        element.style.cursor = '';
        tooltip.innerHTML = '点击查看详情';
        element.appendChild(tooltip);
        element.addEventListener('mousemove', function (e) {
            tooltip.style.left = e.clientX + 'px';
            tooltip.style.top = e.clientY + 'px';
        });
        tooltip.style.display = 'block';
    }else{
        element.disabled = true;
        element.style.cursor = 'not-allowed';
    }
}

function hideTooltip(element) {
    var tooltip = element.querySelector('.tooltip');
    if (tooltip) {
        tooltip.style.display = 'none';
        element.removeChild(tooltip);
    }
}


function UpdateDetailsIdleNodes(detailsId, data){
    var IdleNodes = document.getElementById("idleNodes")
    var detailsIdleNodes = document.getElementById("detailsIdleNodes");
    detailsIdleNodes.innerHTML = ''; // Clear previous content

    if (data && data.length > 0){
        IdleNodes.classList.remove('inactive');
        IdleNodes.classList.add('active');

        for (var i = 0; i < data.length; i++) {
            var node = data[i].node;
            var capacityNum = data[i].capacity_num;
              console.log("Node:", node, "Capacity Num:", capacityNum);
              // detailsIdleNodes.innerHTML += `<p>节点名称：${node}, 节点剩余能力: ${capacityNum}</p>`;

              var IdxElement = document.createElement('span');
              IdxElement.textContent = i + 1;
              IdxElement.classList.add('badge_node', 'bg-green');

              var NodeElement = document.createElement('span');
              NodeElement.textContent = 'Node: ' + node;
              NodeElement.classList.add('badge_node', 'bg-green');

              var capacityNumElement = document.createElement('span');
              capacityNumElement.textContent = 'Node capacity: ' + capacityNum;
              capacityNumElement.classList.add('badge_node', 'bg-teal');

              detailsIdleNodes.appendChild(IdxElement);
              detailsIdleNodes.appendChild(NodeElement);
              detailsIdleNodes.appendChild(capacityNumElement);
              detailsIdleNodes.appendChild(document.createElement("p"));

            }
    }else{

        IdleNodes.classList.remove('active');
        IdleNodes.classList.add('inactive');

        var NoteElement = document.createElement('span');
        NoteElement.textContent = "当前无可用节点";
        NoteElement.classList.add('badge_node', 'bg-red');
        detailsIdleNodes.appendChild(NoteElement);

    }
}

function UpdateDetailsPendingTasks(detailsId, data){
    var detailsPendingTasks = document.getElementById("detailsPendingTasks");
    detailsPendingTasks.innerHTML = ''; // Clear previous content
    var pendingTasks = document.getElementById("pendingTasks")

    if (pendingTasks && data.length > 0) {
        pendingTasks.classList.remove('inactive');
        pendingTasks.classList.add('active');
        for (var j = 0; j < data.length; j++) {
            var taskId = data[j].task_id;
            var createTime = data[j].create_time;
            // detailsPendingTasks.innerHTML += `<p>Task ID： ${taskId}, 创建时间: ${createTime}</p>`;
            console.log(j,"Task ID:", taskId, "Create Time:", createTime);

            var IdxElement = document.createElement('span');
            IdxElement.textContent = j + 1;
            IdxElement.classList.add('badge_node', 'bg-green');

            var taskIDElement = document.createElement('span');
            var a_tag = document.createElement('a')
            var path = window.location.pathname
            if (path.includes("training")){
                a_tag.href = "training_model/progress/" + taskId
            }else{
                a_tag.href = "detect/progress/" + taskId
            }

            a_tag.target = "_blank";
            a_tag.innerText = 'Task ID: ' + taskId;
            a_tag.style.color = "white"
            // http://127.0.0.1:8011/detect/progress/1a773a38-4273-4287-95c4-55f41abcfd22
            // taskIDElement.textContent = 'Task ID: ' + taskId;
            // taskIDElement.innerHTML = 'Task ID: ' + a_tag;
            taskIDElement.appendChild(a_tag);
            taskIDElement.classList.add('badge_node', 'bg-green');

            var createdElement = document.createElement('span');
            createdElement.textContent = 'Created Time: ' + createTime;
            createdElement.classList.add('badge_node', 'bg-teal');

            detailsPendingTasks.appendChild(IdxElement);
            detailsPendingTasks.appendChild(taskIDElement);
            detailsPendingTasks.appendChild(createdElement);
            detailsPendingTasks.appendChild(document.createElement("p"));
        }
    }else{
        pendingTasks.classList.remove('active');
        pendingTasks.classList.add('inactive');

        var NoteElement = document.createElement('span');
        NoteElement.textContent = "当前待处理任务为空";
        NoteElement.classList.add('badge_node', 'bg-red');
        detailsPendingTasks.appendChild(NoteElement);

    }
}

function UpdateDetailsProcessingTasks(detailsId, data){
    var detailsProcessingTasks = document.getElementById("detailsProcessingTasks");
    detailsProcessingTasks.innerHTML = ''; // Clear previous content
    var processingTasks = document.getElementById("processingTasks")

    if (processingTasks && data.length > 0) {
        processingTasks.classList.remove('inactive');
        processingTasks.classList.add('active');
        for (var k = 0; k < data.length; k++) {
            var taskId = data[k].task_id;
            var createTime = data[k].create_time;
            var node = data[k].node;
            console.log(node, )
            // detailsProcessingTasks.innerHTML += `<p>Task ID： ${taskId}, 运行节点: ${node}, 创建时间: ${createTime}</p>`;

            var IdxElement = document.createElement('span');
            IdxElement.textContent = k + 1;
            IdxElement.classList.add('badge_node', 'bg-green');

            var taskIDElement = document.createElement('span');

            taskIDElement.classList.add('badge_node', 'bg-green');

            var a_tag = document.createElement('a')

           var path = window.location.pathname
            if (path.includes("training")){
                a_tag.href = "training_model/progress/" + taskId
            }else{
                a_tag.href = "detect/progress/" + taskId
            }
            a_tag.target = "_blank";
            a_tag.innerText = 'Task ID: ' + taskId;
            a_tag.style.color = "white"

            taskIDElement.appendChild(a_tag);

            var NodeElement = document.createElement('span');
            NodeElement.textContent = 'Node: ' + node;
            NodeElement.classList.add('badge_node', 'bg-teal');



            var createdElement = document.createElement('span');
            createdElement.textContent = 'Created Time: ' + createTime;
            createdElement.classList.add('badge_node', 'bg-teal');


            detailsProcessingTasks.appendChild(IdxElement);
            detailsProcessingTasks.appendChild(taskIDElement);
            detailsProcessingTasks.appendChild(NodeElement);
            detailsProcessingTasks.appendChild(createdElement);
            detailsProcessingTasks.appendChild(document.createElement("p"));

            console.log("Task ID:", taskId, "node", node,"Create Time:", createTime);
        }
    }else{
        processingTasks.classList.remove('active');
        processingTasks.classList.add('inactive');
        var NoteElement = document.createElement('span');
        NoteElement.textContent = "当前正在处理任务为空";
        NoteElement.classList.add('badge_node', 'bg-red');
        detailsProcessingTasks.appendChild(NoteElement);
    }

}





function update_status(socket){
    // Establish WebSocket connection

    // Event handler for when the WebSocket connection is opened
    socket.onopen = function(event) {
        console.log("WebSocket connection opened");
        const data = {
            "command": "start",
        };

        var jsonData = JSON.stringify(data);
        socket.send(jsonData);

    };

    // Event handler for receiving messages from the server
    socket.onmessage = function(event) {
        var tasks = JSON.parse(event.data);
        // Process the received tasks and update the frontend as needed
        console.log("!!", tasks);
        // Assuming `data` contains the returned data from the server
        var nodes = tasks.nodes;
        var pendingTasks = tasks.pending_task_list;
        var processingTasks = tasks.processing_task_list;

        // Calculate the length of each value for the `nodes` key
        var nodesLength =  nodes ? nodes.length : 0;
        var pendingTasksLength = pendingTasks ? pendingTasks.length: 0;
        var processingTasksLength = processingTasks ? processingTasks.length:0;
        console.log(nodesLength, pendingTasksLength, processingTasksLength)

        // UpdateDetailsIdleLabel(nodesLength);
        // UpdateDetailsPendingTasksLabel(pendingTasksLength);
        // UpdateDetailsProcessingTasksLabel(processingTasksLength);

        UpdateDetailsIdleNodes("detailsIdleNodes", nodes);
        UpdateDetailsPendingTasks('detailsPendingTasks', pendingTasks);
        UpdateDetailsProcessingTasks('detailsProcessingTasks', processingTasks);

        document.getElementById("idleNodes").innerHTML = nodesLength;
        document.getElementById("pendingTasks").innerHTML = pendingTasksLength;
        document.getElementById("processingTasks").innerHTML = processingTasksLength;

    };

    // Event handler for when the WebSocket connection is closed
    socket.onclose = function(event) {
        console.log("WebSocket connection closed");
    };
}

let port;
let reader;
let writer;

const terminal = document.getElementById('terminal');
const input = document.getElementById('input');
const connectButton = document.getElementById('connect');
const disconnectButton = document.getElementById('disconnect');




const filters = [
    { usbVendorId: 11914 },
];

function logToTerminal(data) {
    terminal.textContent += data;
    terminal.scrollTop = terminal.scrollHeight;
}

function isNumber(n) { return !isNaN(parseFloat(n)) && !isNaN(n - 0) }
function cssEscape(id) { return CSS.escape(id); }

function getCookie(name) {
    const decodedCookies = decodeURIComponent(document.cookie);
    const cookies = decodedCookies.split(';');

    for (let cookie of cookies) {
        cookie = cookie.trim(); // Remove leading whitespace
        if (cookie.startsWith(name + "=")) {
            return cookie.substring((name + "=").length);
        }
    }
    return null;
}




function on_slider_change(event) {

    let value = event.target.value;
    let id = event.target.id

    numbox_id = "numbox" + id

    let number_box = document.getElementById(numbox_id);

    number_box.innerHTML = value;


    command = "S" + id + " " + value
    sendToSerial(command)


}

function execute_tmp_script() {

    script_content = document.getElementById("scode_box").value


    let script_b64 = btoa(script_content);
    let command = "LOAD|" + script_b64;
    sendToSerial(command)




}

function save_scode_to_cookie() {

    console.log("saving scode to cookie")
    let contents = document.getElementById("scode_box").value

    document.cookie = "scode_contents=" + encodeURIComponent(contents)


}

function add_to_textbox(line) {
    const textbox = document.getElementById("scode_box");

    // Get the current cursor position
    const start = textbox.selectionStart;
    const end = textbox.selectionEnd;
    const text = textbox.value;

    // Check if we're in the middle of a non-empty line
    const before = text.substring(0, start);
    const after = text.substring(end);
    const lastNewline = before.lastIndexOf("\n");
    const nextNewline = after.indexOf("\n");
    const lineStart = lastNewline === -1 ? 0 : lastNewline + 1;
    const lineEnd = nextNewline === -1 ? text.length : end + nextNewline;

    const currentLine = text.substring(lineStart, lineEnd).trim();
    const insertNewline = currentLine.length > 0;

    // Compose new value
    const insertText = (insertNewline ? "\n" : "") + line + "\n";
    textbox.value = before + insertText + after;

    // Set cursor after the inserted text
    const newCursorPos = start + insertText.length;
    textbox.selectionStart = textbox.selectionEnd = newCursorPos;

    // Optional: Keep focus on textbox
    textbox.focus();

    save_scode_to_cookie()
}


function click_add(event) {
    let servo_id = event.target.value;

    let servo_value = document.getElementById(servo_id).value;

    command = "S" + servo_id + " " + servo_value;

    add_to_textbox(command);


}

function pad(width, string, padding) {
    return (width <= string.length) ? string : pad(width, padding + string, padding)
}

function generate_sliders(servo_data) {



    const slider_box = document.getElementById("slider_container");



    //var servo_data = JSON.parse(servo_data_raw);
    var br = document.createElement("br");


    const slider_box_div = document.createElement("div");
    slider_box_div.style.width = "100%";
    slider_box_div.style.display = "table";

    for (const servo in servo_data) {


        var slider_row = document.createElement("div");

        slider_row.style.display = "table-row";

        let servo_id = servo_data[servo][0];
        let servo_range = servo_data[servo][1];
        let servo_angle = servo_data[servo][2];



        if (!isNumber(servo_angle)) {
            servo_angle_num = 0;
            servo_angle_text = "Err";
        } else {
            servo_angle_num = Math.floor(servo_angle)
            servo_angle_text = servo_angle_num
        }


        servo_angle_text = pad(10, servo_angle_text, " ")


        var slider_div = document.createElement("div");
        slider_div.style.display = "table-cell";
        slider_div.style.width = "75%";

        var servo_name_div = document.createElement("div");
        servo_name_div.style.display = "table-cell";
        servo_name_div.style.width = "8%";

        var servo_name_span = document.createElement("span");
        servo_name_span.textContent = "Servo " + servo_id;

        var slider = document.createElement("input");
        slider.id = servo_id;
        slider.type = "range";
        slider.min = 0;
        slider.max = servo_range;
        slider.value = servo_angle_num;
        slider.classList.add("slider_class");
        slider.step = 1;
        //slider.onchange = on_slider_change(event.target.id, event.target.value)
        slider.addEventListener("input", function (event) {
            on_slider_change(event);
        });

        var numbox_div = document.createElement("div");
        numbox_div.style.display = "table-cell";
        numbox_div.style.paddingLeft = "2%";

        var numbox = document.createElement("span");
        numbox.id = "numbox" + servo_id;
        numbox.classList.add("numbox_class")
        numbox.textContent = servo_angle_text;

        var addbutton_div = document.createElement("div");
        addbutton_div.style.display = "table-cell";

        let add_button = document.createElement("button");
        add_button.innerHTML = "+";
        add_button.id = "add" + servo_id;
        add_button.value = servo_id;
        //add_button.addEventListener("click",click_add)
        add_button.addEventListener("click", function (event) {
            click_add(event);
        });



        servo_name_div.appendChild(servo_name_span)
        slider_div.appendChild(slider)
        numbox_div.appendChild(numbox)
        addbutton_div.appendChild(add_button)

        slider_row.appendChild(servo_name_div);
        slider_row.appendChild(slider_div);
        slider_row.appendChild(numbox_div);
        slider_row.appendChild(addbutton_div);

        slider_box_div.appendChild(slider_row);


    }
    slider_box.append(slider_box_div);




}

function click_run_function(event) {


    let value = event.target.value;
    console.log(event.target);



    command = "R " + value


    sendToSerial(command)
}

function generate_function_keys(function_list) {


    const function_box = document.getElementById("function_container");

    for (const function_nr in function_list) {

        function_name = function_list[function_nr]


        let func_button = document.createElement("button");
        let func_span = document.createElement("span")
        func_span.innerHTML = function_name;
        func_span.value = function_name;
        //func_button.innerHTML = "<span> + function_name + "</span>" ;
        func_button.id = "function" + function_name;
        func_button.value = function_name;
        func_button.style.backgroundColor = "blue";
        func_button.classList.add("flex-item")
        func_button.classList.add("button")

        func_button.addEventListener("click", function (event) {
            click_run_function(event);
        });

        func_button.append(func_span)
        function_box.append(func_button)
        function_box.append(" ")


    }


}

function disconnectSerial() {
    if (reader) reader.cancel();
    if (writer) writer.releaseLock();
    if (port) port.close();
    localStorage.removeItem("serial_auto_reconnect");
    logToTerminal("🔌 Disconnected\n");
}

async function connectSerial(autoReconnect = false) {



    console.log("connect serial ...")
    try {
        // Step 1: Get or request port
        if (autoReconnect) {
            const ports = await navigator.serial.getPorts();
            const savedIndex = parseInt(localStorage.getItem("serial_port_index"));

            if (!isNaN(savedIndex) && ports[savedIndex]) {
                port = ports[savedIndex];
                logToTerminal(`🔁 Auto-reconnecting to port [${savedIndex}]...\n`);
            } else {
                logToTerminal("⚠️ No valid stored port index found or port not available.\n");
                return;
            }


        } else {
            port = await navigator.serial.requestPort({ filters });
            const allPorts = await navigator.serial.getPorts();
            const portIndex = allPorts.findIndex(p => p === port);
            localStorage.setItem("serial_auto_reconnect", "true");
            localStorage.setItem("serial_port_index", portIndex);

        }

        

        console.log("open port")
        // Step 2: Open the port
        const info = port.getInfo();
        await port.open({ baudRate: 9600 });

        logToTerminal("✅ Connected\n");

        // Step 3: Setup writer
        writer = port.writable.getWriter();

        console.log("setup reader")
        // Step 4: Setup reader
        const decoder = new TextDecoderStream();
        const inputDone = port.readable.pipeTo(decoder.writable);
        const inputStream = decoder.readable;
        reader = inputStream.getReader();

        console.log("send serial")
        // Step 5: Initialize device
        sendToSerial("_SDCC_INIT");
        let init_data = "";

        console.log("start read")
        while (true) {
            console.log(init_data)
            const { value, done } = await reader.read();
            if (done) break;
            init_data += value;
            if (init_data.includes("DONE")) break;
        }

        console.log(init_data)

        const init_data_json = JSON.parse(init_data);
        generate_sliders(init_data_json[0]);
        generate_function_keys(init_data_json[1]);

        // Step 6: Start read loop
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            if (value) logToTerminal(value);
        }

    } catch (err) {
        logToTerminal("❌ Connection error: " + err.message + "\n");
        localStorage.removeItem("serial_auto_reconnect");
    }
}

async function sendToSerial(data) {
    if (!writer) {
        logToTerminal("⚠️ Not connected.\n");
        return;
    }
    const encoded = new TextEncoder().encode(data + "\r\n");
    await writer.write(encoded);
    logToTerminal("> " + data + "\n");
}

//connectButton.addEventListener('click', connectSerial(false));

connectButton.addEventListener("click", () => {
    connectSerial(false); // Prompt user to select port
});

disconnectButton.addEventListener("click", () => {
    disconnectSerial(); // Prompt user to select port
});

input.addEventListener('keydown', async (e) => {
    if (e.key === 'Enter') {
        const value = input.value.trim();
        if (value !== '') {
            await sendToSerial(value);
            input.value = '';
        }
    }
});

document.getElementById("open_script").addEventListener("click", function () {
    // Create a hidden file input
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".scode"; // restrict to .scode files

    // Handle file selection
    input.onchange = function (event) {
        const file = event.target.files[0];
        if (!file) return;

        // Read the file
        const reader = new FileReader();
        reader.onload = function (e) {
            const contents = e.target.result;
            document.getElementById("scode_box").value = contents;
            save_scode_to_cookie()
        };
        reader.readAsText(file); // read the file as text
    };



    // Trigger file picker
    input.click();

});


document.getElementById("save_script").addEventListener("click", async function () {
    try {
        // Open a file save picker
        const handle = await window.showSaveFilePicker({
            suggestedName: "script.scode",
            types: [
                {
                    description: "Script Code Files",
                    accept: {
                        "text/plain": [".scode"]
                    }
                }
            ]
        });

        // Create a writable stream
        const writable = await handle.createWritable();

        // Get content from textarea
        const content = document.getElementById("scode_box").value;

        // Write content to file
        await writable.write(content);

        // Close the file and write to disk
        await writable.close();

        console.log("File saved successfully!");
    } catch (err) {
        if (err.name !== 'AbortError') {
            console.error("Save failed:", err);
        }
    }
});


document.getElementById("run_script").addEventListener("click", execute_tmp_script);


const savedContents = getCookie("scode_contents");

if (savedContents !== null) {
    if (savedContents == "") {
        add_to_textbox("[main]")
    } else {
        document.getElementById("scode_box").value = savedContents;
    }

} else {
    add_to_textbox("[main]")
}

document.getElementById("scode_box").addEventListener("input", save_scode_to_cookie);


const container = document.getElementById("terminal_container");
const handle = document.getElementById("resize_handle");

let isResizing = false;
let startY, startHeight;

handle.addEventListener("mousedown", function (e) {
    isResizing = true;
    startY = e.clientY;
    startHeight = container.offsetHeight;
    document.body.style.cursor = "row-resize";
    document.body.style.userSelect = "none";
});

document.addEventListener("mousemove", function (e) {
    if (!isResizing) return;
    const dy = e.clientY - startY;
    container.style.height = `${startHeight + dy}px`;
});

document.addEventListener("mouseup", function () {
    if (isResizing) {
        isResizing = false;
        document.body.style.cursor = "";
        document.body.style.userSelect = "";
        localStorage.setItem("terminal_height", container.offsetHeight);
    }
});

// Apply saved height on load
window.addEventListener("DOMContentLoaded", () => {
    const savedHeight = localStorage.getItem("terminal_height");
    if (savedHeight) {
        container.style.height = `${savedHeight}px`;
    }
});

window.addEventListener("DOMContentLoaded", () => {
    if (localStorage.getItem("serial_auto_reconnect") === "true") {
        connectSerial(true); // Try to auto-reconnect
    }
});


function preventInput(event) {
    if (event.key === "ArrowUp" || event.key === "ArrowDown") {
        event.preventDefault();
    }
}

function preventScroll(event) {
    event.preventDefault();
}

function predictPrice() {
    let company = document.getElementById("company").value;
    let ram = parseFloat(document.getElementById("ram").value);
    let rom = parseFloat(document.getElementById("rom").value);
    let front_camera = parseFloat(document.getElementById("front_camera").value);
    let back_camera = parseFloat(document.getElementById("back_camera").value);
    let battery = parseFloat(document.getElementById("battery").value);
    let resultElement = document.getElementById("result");
    let loadingElement = document.getElementById("loading");

    if (!company) {
        alert("Please select a company.");
        return;
    }

    resultElement.innerHTML = "";
    loadingElement.classList.remove("hidden");

    let data = {
        company: company,
        ram: ram,
        rom: rom,
        front_camera: front_camera,
        back_camera: back_camera,
        battery: battery
    };

    fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        loadingElement.classList.add("hidden");
        if (data.predicted_price) {
            resultElement.innerHTML = `💰 Predicted Price: ₹${data.predicted_price}`;
        } else {
            resultElement.innerHTML = `❌ Error: ${data.error}`;
        }
    })
    .catch(error => {
        loadingElement.classList.add("hidden");
        console.error("Error:", error);
        resultElement.innerHTML = `❌ Something went wrong. Try again!`;
    });
}

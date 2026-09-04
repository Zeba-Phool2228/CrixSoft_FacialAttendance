const video = document.getElementById("video-preview");
const statusBox = document.getElementById("status-box");
const canvas = document.createElement("canvas");

let checking = false;

async function startCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ 
      video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: "user" } 
    });
    video.srcObject = stream;
  } catch (err) {
    statusBox.textContent = "Camera access denied or unavailable.";
    statusBox.className = "status-box unknown";
  }
}

function captureFrame() {
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL("image/jpeg", 0.8);
}

async function checkFrame() {
  if (checking || video.videoWidth === 0) return;
  checking = true;

  const imageData = captureFrame();

  try {
    const response = await fetch("/attendance/face/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: imageData })
    });
    const result = await response.json();
    updateStatus(result);
  } catch (err) {
    statusBox.textContent = "Connection error. Retrying...";
    statusBox.className = "status-box unknown";
  }

  checking = false;
}

function updateStatus(result) {
  if (result.status === "match") {
    statusBox.textContent = `Welcome, ${result.name}! Attendance marked.`;
    statusBox.className = "status-box match";
  } else if (result.status === "duplicate") {
    statusBox.textContent = `${result.name}, you already checked in today.`;
    statusBox.className = "status-box duplicate";
  } else if (result.status === "unknown") {
    statusBox.textContent = "Face not recognized.";
    statusBox.className = "status-box unknown";
  } else if (result.status === "no_face") {
    statusBox.textContent = "Position your face in front of the camera.";
    statusBox.className = "status-box";
  } else {
    statusBox.textContent = "Waiting...";
    statusBox.className = "status-box";
  }
}

startCamera();
setInterval(checkFrame, 2000);

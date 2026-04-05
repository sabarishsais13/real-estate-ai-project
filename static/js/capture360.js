// ─── ROOMS DATA ──────────────────────────────────────────────────────────────
const rooms = [
  { id: "living",   name: "Living Room",     icon: "🛋️", captured: false, imageData: null },
  { id: "kitchen",  name: "Kitchen",          icon: "🍳", captured: false, imageData: null },
  { id: "master",   name: "Master Bedroom",   icon: "🛏️", captured: false, imageData: null },
  { id: "room2",    name: "Bedroom 2",        icon: "🛏️", captured: false, imageData: null },
  { id: "room3",    name: "Bedroom 3",        icon: "🛏️", captured: false, imageData: null },
  { id: "bathroom", name: "Bathroom",         icon: "🚿", captured: false, imageData: null },
];

// ─── STATE ────────────────────────────────────────────────────────────────────
let activeRoom       = null;
let stream           = null;
let facingMode       = "environment"; // rear camera
let capturedFrames   = [];
let isCapturing      = false;
let captureInterval  = null;
let rotationDeg      = 0;
let gyroStart        = null;
let lastGyroY        = null;
let previewRoomId    = null;

const FRAME_COUNT    = 24;   // frames to capture while rotating
const FRAME_DELAY    = 200;  // ms between frames

// ─── DOM REFS ─────────────────────────────────────────────────────────────────
const idleScreen      = () => document.getElementById("idleScreen");
const cameraScreen    = () => document.getElementById("cameraScreen");
const stitchScreen    = () => document.getElementById("stitchingScreen");
const startBar        = () => document.getElementById("startCameraBar");
const videoEl         = () => document.getElementById("cameraFeed");
const arcFill         = () => document.getElementById("arcFill");
const rotPct          = () => document.getElementById("rotationPct");
const stitchFill      = () => document.getElementById("stitchFill");

// ─── INIT ─────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  buildRoomsList();
  updateProgress();
  initParticles();
  requestGyro();
});

// ─── BUILD ROOMS LIST ─────────────────────────────────────────────────────────
function buildRoomsList() {
  const list = document.getElementById("roomsList");
  list.innerHTML = "";
  document.getElementById("totalNum").textContent = rooms.length;

  rooms.forEach(room => {
    const card = document.createElement("div");
    card.className = "room-card" + (room.captured ? " captured" : "");
    card.id = `rc-${room.id}`;
    card.innerHTML = `
      <span class="room-icon">${room.icon}</span>
      <div class="room-info">
        <div class="room-name">${room.name}</div>
        <div class="room-status-text ${room.captured ? "done" : ""}">
          ${room.captured ? "✓ Captured" : "Not captured yet"}
        </div>
      </div>
      <div class="room-badge ${room.captured ? "done" : ""}">${room.captured ? "✓" : "○"}</div>
    `;
    card.addEventListener("click", () => selectRoom(room));
    list.appendChild(card);
  });
}

// ─── SELECT ROOM ──────────────────────────────────────────────────────────────
function selectRoom(room) {
  // Stop any active camera first
  if (stream) stopCamera();

  activeRoom = room;

  // Update card styles
  document.querySelectorAll(".room-card").forEach(c => {
    c.classList.remove("active");
    const badge = c.querySelector(".room-badge");
    if (badge) badge.classList.remove("active-ind");
  });
  const card = document.getElementById(`rc-${room.id}`);
  if (card) {
    card.classList.add("active");
    const badge = card.querySelector(".room-badge");
    if (badge && !room.captured) badge.classList.add("active-ind");
  }

  // Update start bar
  document.getElementById("startRoomIcon").textContent = room.icon;
  document.getElementById("startRoomName").textContent = room.name;
  document.getElementById("btnStartCamera").disabled = false;

  // Show idle if camera not active
  showState("idle");
}

// ─── CAMERA: START ────────────────────────────────────────────────────────────
async function startCamera() {
  if (!activeRoom) return;

  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: facingMode,
        width: { ideal: 1920 },
        height: { ideal: 1080 }
      },
      audio: false
    });

    const video = videoEl();
    video.srcObject = stream;
    await video.play();

    // Reset state
    capturedFrames = [];
    rotationDeg = 0;
    gyroStart = null;
    lastGyroY = null;
    updateArc(0);
    rotPct().textContent = "0°";

    // Update cam label
    document.getElementById("camRoomLabel").textContent = activeRoom.name;

    showState("camera");

  } catch (err) {
    if (err.name === "NotAllowedError") {
      alert("Camera permission denied. Please allow camera access in your browser settings.");
    } else if (err.name === "NotFoundError") {
      alert("No camera found on this device.");
    } else {
      alert("Could not start camera: " + err.message);
    }
  }
}

// ─── CAMERA: STOP ─────────────────────────────────────────────────────────────
function stopCamera() {
  if (stream) {
    stream.getTracks().forEach(t => t.stop());
    stream = null;
  }
  stopFrameCapture();
  showState("idle");
}

// ─── CAMERA: FLIP ─────────────────────────────────────────────────────────────
async function flipCamera() {
  facingMode = facingMode === "environment" ? "user" : "environment";
  if (stream) {
    stopCamera();
    await startCamera();
  }
}

// ─── CAPTURE FRAMES ───────────────────────────────────────────────────────────
function captureFrames() {
  if (isCapturing) {
    // Stop capturing
    stopFrameCapture();
    if (capturedFrames.length >= 4) {
      startStitching();
    } else {
      alert("Please capture more frames — slowly rotate your phone for a full 360°.");
    }
    return;
  }

  // Start capturing
  isCapturing = true;
  capturedFrames = [];
  rotationDeg = 0;
  updateArc(0);

  // Visual feedback on shutter
  const shutter = document.getElementById("btnCapture");
  shutter.style.borderColor = "#ff4444";
  shutter.innerHTML = `
    <div class="shutter-inner">
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#ff4444" stroke-width="1.5">
        <rect x="6" y="6" width="12" height="12" rx="2" fill="rgba(255,68,68,0.3)"/>
      </svg>
    </div>`;

  captureInterval = setInterval(() => {
    captureOneFrame();
    // Simulate rotation progress if no gyro
    if (!gyroStart) {
      rotationDeg = Math.min(360, rotationDeg + (360 / FRAME_COUNT));
      updateArc(rotationDeg / 360);
      rotPct().textContent = `${Math.round(rotationDeg)}°`;
    }
    if (capturedFrames.length >= FRAME_COUNT) stopFrameCapture();
  }, FRAME_DELAY);
}

function captureOneFrame() {
  const video = videoEl();
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth   || 640;
  canvas.height = video.videoHeight || 360;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  capturedFrames.push(canvas);
}

function stopFrameCapture() {
  isCapturing = false;
  if (captureInterval) { clearInterval(captureInterval); captureInterval = null; }

  // Reset shutter
  const shutter = document.getElementById("btnCapture");
  if (shutter) {
    shutter.style.borderColor = "";
    shutter.innerHTML = `
      <div class="shutter-inner">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4" fill="#d4af37"/>
        </svg>
      </div>`;
  }
}

// ─── STITCHING ────────────────────────────────────────────────────────────────
function startStitching() {
  stopCamera();
  showState("stitching");

  let progress = 0;
  const interval = setInterval(() => {
    progress += 4;
    stitchFill().style.width = `${Math.min(progress, 95)}%`;
    if (progress >= 95) {
      clearInterval(interval);
      stitchFrames();
    }
  }, 60);
}

function stitchFrames() {
  const frames = capturedFrames;
  if (!frames.length) { showState("idle"); return; }

  const canvas = document.getElementById("stitchCanvas");
  const frameW = frames[0].width;
  const frameH = frames[0].height;

  // Stitch: place frames side by side (simple panorama)
  const sliceW = Math.floor(frameW / 3); // take center slice of each frame
  canvas.width  = sliceW * frames.length;
  canvas.height = frameH;

  const ctx = canvas.getContext("2d");
  frames.forEach((frame, i) => {
    const sx = Math.floor((frameW - sliceW) / 2);
    ctx.drawImage(frame, sx, 0, sliceW, frameH, i * sliceW, 0, sliceW, frameH);
  });

  stitchFill().style.width = "100%";

  setTimeout(() => {
    // Save result
    if (activeRoom) {
      activeRoom.imageData = canvas.toDataURL("image/jpeg", 0.9);
      activeRoom.captured = true;
    }
    showPreview();
  }, 400);
}

// ─── PREVIEW MODAL ────────────────────────────────────────────────────────────
function showPreview() {
  showState("idle");

  const modal = document.getElementById("previewModal");
  const canvas = document.getElementById("previewCanvas");
  const title  = document.getElementById("previewTitle");

  previewRoomId = activeRoom?.id;
  title.textContent = `${activeRoom?.name} — 360° Preview`;

  // Draw stitched image on preview canvas
  const stitched = document.getElementById("stitchCanvas");
  canvas.width  = stitched.width;
  canvas.height = stitched.height;
  canvas.getContext("2d").drawImage(stitched, 0, 0);

  modal.classList.add("open");
}

function closePreview() {
  document.getElementById("previewModal").classList.remove("open");
}

function retakeRoom() {
  closePreview();
  if (activeRoom) {
    activeRoom.captured = false;
    activeRoom.imageData = null;
  }
  buildRoomsList();
  updateProgress();
  if (activeRoom) selectRoom(activeRoom);
}

function saveRoom() {
  closePreview();
  buildRoomsList();
  updateProgress();

  // Auto-select next uncaptured room
  const next = rooms.find(r => !r.captured);
  if (next) selectRoom(next);
  else showState("idle");
}

// ─── PROGRESS ─────────────────────────────────────────────────────────────────
function updateProgress() {
  const done  = rooms.filter(r => r.captured).length;
  const total = rooms.length;
  document.getElementById("capturedNum").textContent = done;
  document.getElementById("totalNum").textContent    = total;
  document.getElementById("capturedFill").style.width = `${(done / total) * 100}%`;
}

// ─── STATE SWITCHER ───────────────────────────────────────────────────────────
function showState(state) {
  idleScreen().classList.toggle("hidden",   state !== "idle");
  cameraScreen().classList.toggle("active", state === "camera");
  stitchScreen().classList.toggle("active", state === "stitching");
}

// ─── ARC UPDATE ───────────────────────────────────────────────────────────────
function updateArc(pct) {
  const circumference = 553;
  const offset = circumference - (circumference * Math.min(pct, 1));
  const arc = arcFill();
  if (arc) arc.style.strokeDashoffset = offset;
}

// ─── GYROSCOPE ────────────────────────────────────────────────────────────────
function requestGyro() {
  if (typeof DeviceOrientationEvent !== "undefined" &&
      typeof DeviceOrientationEvent.requestPermission === "function") {
    // iOS 13+
    document.addEventListener("click", async () => {
      try {
        const perm = await DeviceOrientationEvent.requestPermission();
        if (perm === "granted") listenGyro();
      } catch (e) { /* silently fail */ }
    }, { once: true });
  } else if (window.DeviceOrientationEvent) {
    listenGyro();
  }
}

function listenGyro() {
  window.addEventListener("deviceorientation", (e) => {
    if (!isCapturing) return;

    const alpha = e.alpha; // compass heading 0-360
    const beta  = e.beta;  // tilt -180 to 180

    // Update tilt bar
    const tiltNorm = Math.max(0, Math.min(1, (beta + 90) / 180));
    const tiltFillEl = document.querySelector(".tilt-fill");
    if (tiltFillEl) tiltFillEl.style.height = `${tiltNorm * 100}%`;

    // Track rotation
    if (alpha !== null) {
      if (gyroStart === null) { gyroStart = alpha; lastGyroY = alpha; }

      let delta = alpha - lastGyroY;
      if (delta > 180) delta -= 360;
      if (delta < -180) delta += 360;

      rotationDeg = Math.min(360, rotationDeg + Math.abs(delta));
      lastGyroY = alpha;

      const pct = rotationDeg / 360;
      updateArc(pct);
      rotPct().textContent = `${Math.round(rotationDeg)}°`;

      // Auto stop at 360
      if (rotationDeg >= 360 && isCapturing) {
        stopFrameCapture();
        startStitching();
      }
    }
  });
}

// ─── ADD ROOM ─────────────────────────────────────────────────────────────────
function addRoom() {
  const name = prompt("Enter room name (e.g. Balcony, Study Room):");
  if (!name || !name.trim()) return;
  rooms.push({
    id: "custom_" + Date.now(),
    name: name.trim(),
    icon: "🚪",
    captured: false,
    imageData: null
  });
  buildRoomsList();
  updateProgress();
}

// ─── FINISH & PASS DATA ───────────────────────────────────────────────────────
function finishCapture() {
  const captured = rooms.filter(r => r.captured);
  if (captured.length === 0) {
    alert("Please capture at least one room before continuing.");
    return;
  }

  // In real app: send imageData to Django backend via fetch/FormData
  // For now, store in sessionStorage and go back to sell page
  const data = rooms.map(r => ({
    id: r.id,
    name: r.name,
    icon: r.icon,
    captured: r.captured,
    imageData: r.imageData
  }));

  sessionStorage.setItem("capturedRooms", JSON.stringify(
    data.map(r => ({ ...r, imageData: r.imageData ? "[captured]" : null }))
  ));

  // Navigate back to sell page
  window.location.href = "/sell/";
}

// ─── GOLD PARTICLES ───────────────────────────────────────────────────────────
function initParticles() {
  const canvas = document.getElementById("particles");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  let W = window.innerWidth, H = window.innerHeight;
  canvas.width = W; canvas.height = H;

  window.addEventListener("resize", () => {
    W = window.innerWidth; H = window.innerHeight;
    canvas.width = W; canvas.height = H;
  });

  const dots = Array.from({ length: 40 }, () => ({
    x: Math.random() * W, y: Math.random() * H,
    r: Math.random() * 1.5 + 0.4,
    speed: Math.random() * 0.25 + 0.08,
    opacity: Math.random() * 0.35 + 0.05,
    fade: Math.random() > 0.5 ? 0.003 : -0.003
  }));

  (function draw() {
    ctx.clearRect(0, 0, W, H);
    dots.forEach(d => {
      d.y -= d.speed;
      d.opacity += d.fade;
      if (d.opacity <= 0.02 || d.opacity >= 0.45) d.fade *= -1;
      if (d.y < -4) { d.y = H + 4; d.x = Math.random() * W; }
      ctx.beginPath();
      ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(212,175,55,${d.opacity})`;
      ctx.fill();
    });
    requestAnimationFrame(draw);
  })();
}
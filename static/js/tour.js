// ─── ROOM DEFINITIONS ────────────────────────────────────────────────────────
const rooms = [
  { id: "living_room_360", name: "Living Room",   icon: "🛋️", src: "" },
  { id: "kitchen_360",     name: "Kitchen",        icon: "🍳", src: "" },
  { id: "bedroom_360",     name: "Master Bedroom", icon: "🛏️", src: "" },
  { id: "bathroom_360",    name: "Bathroom",       icon: "🚿", src: "" },
];

// ─── STATE ────────────────────────────────────────────────────────────────────
let activeRoom  = null;
let rotationY   = -90;
let rotationX   = 0;
let rotInterval = null;

const zoomConfig = {
  cameraEl: null,
  baseFov: 80,
  current: 1.0,
  target: 1.0,
  minScale: 0.5,
  maxScale: 3.0,
  step: 0.1,
  smooth: 0.14,
};

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function getAFrameCamera() {
  return document.querySelector('#aScene a-camera');
}

function updateZoomIndicator() {
  const indicator = document.getElementById('zoomIndicator');
  if (!indicator) return;
  indicator.textContent = `Zoom ${zoomConfig.current.toFixed(1)}x`;
}

function setCameraFov(scale) {
  const camera = zoomConfig.cameraEl || getAFrameCamera();
  if (!camera) return;
  zoomConfig.cameraEl = camera; // cache it once found

  const clampedScale = clamp(scale, zoomConfig.minScale, zoomConfig.maxScale);
  const fov = clamp(zoomConfig.baseFov / clampedScale, 20, 120);
  
  // Set A-frame attribute
  camera.setAttribute('camera', 'fov', fov);
  
  // Force update Three.js native camera to bypass A-Frame rendering lag
  const threeCam = camera.components.camera && camera.components.camera.camera;
  if (threeCam) {
    threeCam.fov = fov;
    threeCam.updateProjectionMatrix();
  }
  
  zoomConfig.current = clampedScale;
  updateZoomIndicator();
}

let isZooming = false;

function applyZoomTarget() {
  if (isZooming) {
    const delta = zoomConfig.target - zoomConfig.current;
    if (Math.abs(delta) < 0.001) {
      zoomConfig.current = zoomConfig.target;
      setCameraFov(zoomConfig.current);
      isZooming = false;
    } else {
      zoomConfig.current += delta * zoomConfig.smooth;
      setCameraFov(zoomConfig.current);
    }
  }
  requestAnimationFrame(applyZoomTarget);
}

function handleZoomWheel(event) {
  // Only trigger if hovered over the 360 viewer container (A-frame canvas)
  if (!event.target.closest('#viewerContainer')) return;
  if (!activeRoom) return;
  
  event.preventDefault();
  const direction = event.deltaY < 0 ? 1 : -1;
  zoomConfig.target = clamp(zoomConfig.target + direction * zoomConfig.step, zoomConfig.minScale, zoomConfig.maxScale);
  isZooming = true;
}

function handleZoomKey(event) {
  if (!activeRoom) return;
  
  let changed = false;
  if (event.key === '+' || event.key === '=' || event.key === 'Add') {
    zoomConfig.target = clamp(zoomConfig.target + zoomConfig.step, zoomConfig.minScale, zoomConfig.maxScale);
    changed = true;
  } else if (event.key === '-' || event.key === '_' || event.key === 'Subtract') {
    zoomConfig.target = clamp(zoomConfig.target - zoomConfig.step, zoomConfig.minScale, zoomConfig.maxScale);
    changed = true;
  } else if (event.key === '0') {
    zoomConfig.target = 1.0;
    changed = true;
  }
  
  if (changed) {
    event.preventDefault();
    isZooming = true;
  }
}

function setupZoom() {
  // Attach to window to prevent A-Frame internal canvas from swallowing wheel events
  window.addEventListener('wheel', handleZoomWheel, { passive: false });
  window.addEventListener('keydown', handleZoomKey);
  
  // Kickstart animation loop
  isZooming = true;
  requestAnimationFrame(applyZoomTarget);
}


// ─── INIT ─────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", async () => {
  await loadPropertyData();
  buildRoomsList();
  setupArrows();
  setupFullscreen();
  setupZoom();
  detectGyro();
  initParticles();
});

// ─── FETCH FROM DJANGO API ────────────────────────────────────────────────────
async function loadPropertyData() {
  if (typeof PROPERTY_ID === "undefined" || PROPERTY_ID === 0) {
    rooms.forEach(r => r.src = FALLBACK_IMAGE);
    return;
  }

  try {
    const res = await fetch(`/api/properties/${PROPERTY_ID}/`);

    if (!res.ok) throw new Error("Property not found");

    const data = await res.json();

    // ── Fill 360° image URLs from model fields ──
    rooms.forEach(room => {
      room.src = data[room.id] || FALLBACK_IMAGE;
    });

    // ── Fill property bar (top section) ──
    document.getElementById("propName").textContent        = data.title    || "Property Tour";
    document.getElementById("propLocationText").textContent = data.location || "--";
    document.getElementById("propBhk").textContent         = data.bhk      || "--";
    document.getElementById("propArea").textContent         = data.area ? data.area + " sq.ft" : "--";
    document.getElementById("propPrice").textContent        = data.price ? "₹ " + data.price : "--";

    // ── Fill property details panel (right side) ──
    document.getElementById("detailType").textContent   = (data.bhk || "") + " " + (data.type || "--");
    document.getElementById("detailFloor").textContent  = data.floor   || "--";
    document.getElementById("detailArea").textContent   = data.area ? data.area + " sq.ft" : "--";
    document.getElementById("detailFacing").textContent = data.facing  || "--";
    document.getElementById("detailCity").textContent   = data.city    || data.location || "--";
    document.getElementById("detailBadge").textContent  = data.badge   || "Active";

  } catch (e) {
    console.warn("Could not load property data, using fallback.", e);
    rooms.forEach(r => r.src = FALLBACK_IMAGE);

    // Show fallback text
    document.getElementById("propName").textContent = "Virtual Tour";
  }
}

// ─── BUILD ROOMS LIST ─────────────────────────────────────────────────────────
function buildRoomsList() {
  const list  = document.getElementById("roomsList");
  const count = document.getElementById("roomsCount");

  // Only show rooms that have an image URL
  const available = rooms.filter(r => r.src);
  count.textContent = `${available.length} rooms available`;
  list.innerHTML = "";

  available.forEach(room => {
    const card = document.createElement("div");
    card.className = "room-card";
    card.id = `room-${room.id}`;
    card.innerHTML = `
      <div class="room-thumb">${room.icon}</div>
      <div class="room-info">
        <div class="room-name">${room.name}</div>
        <div class="room-size">Click to explore</div>
      </div>
      <div class="room-status"></div>
    `;
    card.addEventListener("click", () => loadRoom(room));
    list.appendChild(card);
  });

  // Auto-load first room
  if (available.length > 0) loadRoom(available[0]);
}

// ─── LOAD ROOM ────────────────────────────────────────────────────────────────
function loadRoom(room) {
  // Update active card highlight
  document.querySelectorAll(".room-card").forEach(c => c.classList.remove("active"));
  const card = document.getElementById(`room-${room.id}`);
  if (card) card.classList.add("active");

  // Update top label
  document.getElementById("roomLabelText").textContent = room.name;

  // Hide placeholder
  document.getElementById("viewerPlaceholder").classList.add("hidden");

  // Reset camera angle
  rotationY = -90;
  rotationX = 0;

  // Load 360° panorama into A-Frame sky
  const sky = document.getElementById("sky360");
  if (sky) {
    sky.setAttribute("rotation", `${rotationX} ${rotationY} 0`);
    sky.setAttribute("src", room.src);
  }

  activeRoom = room;
}

// ─── ARROW CONTROLS ───────────────────────────────────────────────────────────
function setupArrows() {
  const sky   = document.getElementById("sky360");
  const speed = 3;

  function startRotate(dx, dy) {
    if (rotInterval) clearInterval(rotInterval);
    rotInterval = setInterval(() => {
      rotationY += dx;
      rotationX  = Math.max(-60, Math.min(60, rotationX + dy));
      if (sky) sky.setAttribute("rotation", `${rotationX} ${rotationY} 0`);
    }, 30);
  }

  function stopRotate() {
    if (rotInterval) { clearInterval(rotInterval); rotInterval = null; }
  }

  const btns = {
    btnLeft:  { dx:  speed, dy: 0 },
    btnRight: { dx: -speed, dy: 0 },
    btnUp:    { dx: 0, dy:  speed },
    btnDown:  { dx: 0, dy: -speed },
  };

  Object.entries(btns).forEach(([id, { dx, dy }]) => {
    const btn = document.getElementById(id);
    if (!btn) return;
    btn.addEventListener("mousedown",  ()  => startRotate(dx, dy));
    btn.addEventListener("touchstart", (e) => { e.preventDefault(); startRotate(dx, dy); });
    btn.addEventListener("mouseup",    stopRotate);
    btn.addEventListener("mouseleave", stopRotate);
    btn.addEventListener("touchend",   stopRotate);
  });

  // Reset button
  const resetBtn = document.getElementById("btnReset");
  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      rotationY = -90; rotationX = 0;
      if (sky) sky.setAttribute("rotation", `${rotationX} ${rotationY} 0`);
    });
  }
}

// ─── FULLSCREEN ───────────────────────────────────────────────────────────────
function setupFullscreen() {
  const btn       = document.getElementById("fullscreenBtn");
  const container = document.getElementById("viewerContainer");
  if (!btn || !container) return;
  btn.addEventListener("click", () => {
    if (!document.fullscreenElement) container.requestFullscreen?.();
    else document.exitFullscreen?.();
  });
}

// ─── GYROSCOPE (mobile tilt to look around) ───────────────────────────────────
function detectGyro() {
  if (window.DeviceOrientationEvent && /Mobi|Android/i.test(navigator.userAgent)) {
    document.getElementById("gyroBadge")?.classList.add("show");
    const hint = document.getElementById("dragHint");
    if (hint) hint.style.display = "none";
  }
}

// ─── VASTU BOT ────────────────────────────────────────────────────────────────
function toggleVastu() {
  document.getElementById("vastuChat").classList.toggle("open");
}

function vastuSend(e) {
  if (e.key === "Enter") vastuSendBtn();
}

function getCSRFToken() {
  return document.cookie.split('; ')
    .find(row => row.startsWith('csrftoken'))
    ?.split('=')[1];
}

function vastuSendBtn() {
  const input = document.getElementById("vastuInput");
  const msg   = input.value.trim();
  if (!msg) return;

  input.value = "";
  addVastuMsg(msg, "user");
  addVastuMsg("Typing...", "bot", true);

  fetch("/vastu-chat/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
    },
    body: JSON.stringify({ query: msg }),
  })
  .then(res => {
    if (!res.ok) throw new Error('Network response was not ok');
    return res.json();
  })
  .then(data => {
    updateLastBotMessage(data.response || 'Sorry, I could not answer that.');
  })
  .catch(() => {
    updateLastBotMessage('Sorry, I could not answer that.');
  });
}

function addVastuMsg(text, type, temporary = false) {
  const messages = document.getElementById("vastuMessages");
  const div = document.createElement("div");
  div.className = type === "bot" ? "bot-msg" : "user-msg";
  div.dataset.temporary = temporary ? "true" : "false";
  div.innerHTML = type === "bot"
    ? `<span class="bot-avatar">🔮</span><span>${text}</span>`
    : `<span>${text}</span>`;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function updateLastBotMessage(text) {
  const messages = document.getElementById("vastuMessages");
  const botMessages = Array.from(messages.querySelectorAll('.bot-msg'));
  const lastBot = botMessages[botMessages.length - 1];
  if (lastBot && lastBot.dataset.temporary === "true") {
    lastBot.dataset.temporary = "false";
    lastBot.innerHTML = `<span class="bot-avatar">🔮</span><span>${text}</span>`;
  } else {
    addVastuMsg(text, "bot");
  }
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

  const dots = Array.from({ length: 50 }, () => ({
    x:       Math.random() * W,
    y:       Math.random() * H,
    r:       Math.random() * 1.8 + 0.5,
    speed:   Math.random() * 0.3 + 0.1,
    opacity: Math.random() * 0.4 + 0.05,
    fade:    Math.random() > 0.5 ? 0.004 : -0.004,
  }));

  (function draw() {
    ctx.clearRect(0, 0, W, H);
    dots.forEach(d => {
      d.y       -= d.speed;
      d.opacity += d.fade;
      if (d.opacity <= 0.02 || d.opacity >= 0.5) d.fade *= -1;
      if (d.y < -5) { d.y = H + 5; d.x = Math.random() * W; }
      ctx.beginPath();
      ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(212,175,55,${d.opacity})`;
      ctx.fill();
    });
    requestAnimationFrame(draw);
  })();
}
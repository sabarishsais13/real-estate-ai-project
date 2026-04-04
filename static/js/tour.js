// ─── ROOM DEFINITIONS ────────────────────────────────────────────────────────
// These IDs exactly match the model fields in models.py
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

// PROPERTY_ID and FALLBACK_IMAGE are set in virtual_tour.html by Django
// const PROPERTY_ID    = {{ property_id|default:0 }};
// const FALLBACK_IMAGE = '...';

// ─── INIT ─────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", async () => {
  await loadPropertyData();
  buildRoomsList();
  setupArrows();
  setupFullscreen();
  detectGyro();
  initParticles();
});

// ─── FETCH FROM DJANGO API ────────────────────────────────────────────────────
async function loadPropertyData() {
  // If no property ID, use fallback images for all rooms
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

function vastuSendBtn() {
  const input = document.getElementById("vastuInput");
  const msg   = input.value.trim();
  if (!msg) return;
  input.value = "";
  addVastuMsg(msg, "user");
  setTimeout(() => addVastuMsg(getVastuResponse(msg), "bot"), 700);
}

function addVastuMsg(text, type) {
  const messages = document.getElementById("vastuMessages");
  const div = document.createElement("div");
  div.className = type === "bot" ? "bot-msg" : "user-msg";
  div.innerHTML = type === "bot"
    ? `<span class="bot-avatar">🔮</span><span>${text}</span>`
    : `<span>${text}</span>`;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function getVastuResponse(msg) {
  const m = msg.toLowerCase();
  if (m.includes("kitchen"))                        return "Ideal Vastu for kitchen is the South-East corner (Agni corner). Avoid North-East. 🔥";
  if (m.includes("bedroom") || m.includes("room"))  return "Master bedroom is best in South-West direction for stability and good health. 🛏️";
  if (m.includes("entrance") || m.includes("door")) return "North or East-facing entrance is most auspicious for prosperity and positive energy. 🚪";
  if (m.includes("bathroom") || m.includes("toilet"))return "Bathrooms should be in North-West or West direction. Avoid South-East. 🚿";
  if (m.includes("living"))                         return "Living room in the North or North-East zone invites positive energy and good relationships. 🛋️";
  if (m.includes("window"))                         return "Windows on North and East walls allow positive morning sunlight and energy flow. ☀️";
  if (m.includes("color") || m.includes("colour"))  return "Earthy tones like cream, beige, and light yellow are Vastu-friendly. Avoid dark red in bedrooms. 🎨";
  return "According to Vastu Shastra, this property shows good energy alignment. What specific aspect would you like me to analyse? 🏠";
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
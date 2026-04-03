const canvas = document.getElementById('particle-canvas');
const ctx = canvas.getContext('2d');

let particles = [];
const particleCount = 60;

function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}

window.addEventListener('resize', resize);
resize();

class Particle {
    constructor() {
        this.init();
    }

    init() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height + canvas.height;
        this.size = Math.random() * 2 + 1; // 1px to 3px
        this.speedY = Math.random() * 0.3 + 0.1; // Very slow drift
        this.opacity = Math.random() * 0.3 + 0.1;
        this.fadeSpeed = Math.random() * 0.01 + 0.005;
    }

    update() {
        this.y -= this.speedY;
        if (this.y < -10) {
            this.init();
        }
    }

    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(212, 175, 55, ${this.opacity})`;
        ctx.fill();
    }
}

function createParticles() {
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }
}

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => {
        p.update();
        p.draw();
    });
    requestAnimationFrame(animate);
}

createParticles();
animate();

// Intersection Observer for scroll animations
const observerOptions = {
    threshold: 0.1
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

document.querySelectorAll('.glass-card, .property-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'all 0.8s ease-out';
    observer.observe(el);
});

// Modal Logic
const modal = document.getElementById('property-modal');
const closeBtn = document.querySelector('.close-btn');

document.querySelectorAll('.property-card').forEach(card => {
    card.addEventListener('click', () => {
        const title = card.querySelector('h3').innerText;
        const location = card.querySelector('.card-subtitle').innerText;
        const price = card.querySelector('.property-price').innerText;
        const img = card.querySelector('.property-image').style.backgroundImage;

        document.getElementById('modal-title').innerText = title;
        document.getElementById('modal-location').innerText = location;
        document.getElementById('modal-price').innerText = price;
        document.getElementById('modal-image').style.backgroundImage = img;

        modal.style.display = 'flex';
    });
});

closeBtn.onclick = () => modal.style.display = 'none';
window.onclick = (e) => { if (e.target == modal) modal.style.display = 'none'; };

// Hero Parallax Effect
window.addEventListener('mousemove', (e) => {
    const x = e.clientX / window.innerWidth - 0.5;
    const y = e.clientY / window.innerHeight - 0.5;
    
    const heroBg = document.querySelector('.hero-bg');
    heroBg.style.transform = `scale(1.1) translate(${x * 30}px, ${y * 30}px)`;
});

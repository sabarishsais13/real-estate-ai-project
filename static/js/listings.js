const API_BASE = window.location.origin;

async function loadProperties(params = {}) {
    const query = new URLSearchParams(params).toString();
    const url = `${API_BASE}/api/properties/${query ? '?' + query : ''}`;
    try {
        const res  = await fetch(url);
        const data = await res.json();
        renderCards(data.properties);
        updateCount(data.count);
    } catch (err) {
        console.error('API Error:', err);
        const grid = document.getElementById('propertiesGrid');
        if (grid) {
            grid.innerHTML = '<p style="color:#9a9a9a;text-align:center;padding:60px;grid-column:1/-1">Failed to load properties.</p>';
        }
    }
}

function filterProperties() {
    const city   = document.getElementById('filterLocation').value;
    const budget = document.getElementById('filterBudget').value;
    const type   = document.getElementById('filterType').value;
    const bhk    = document.getElementById('filterBHK').value;
    loadProperties({ city, budget, type, bhk });
}

function createCardHTML(p, index) {
    const badgeHTML = p.badge
        ? `<span class="card-badge">${p.badge}</span>` : '';
    // Use fallbacks for missing images
    let imageUrl = p.image || p.image_url || 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800';
    if (imageUrl && !imageUrl.startsWith('http')) {
        imageUrl = imageUrl.startsWith('/') ? `${API_BASE}${imageUrl}` : `${API_BASE}/${imageUrl}`;
    }
    
    return `
    <div class="listing-card" style="animation-delay:${index * 0.08}s">
        <div class="card-image-section">
            <img src="${imageUrl}" alt="${p.title}" loading="lazy"
                 onerror="this.src='https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800'">
            <div class="card-overlay"></div>
            <h3 class="card-title-text">${p.title}</h3>
            ${badgeHTML}
        </div>
        <div class="card-info">
            <div class="card-location">
                <svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
                    <circle cx="12" cy="9" r="2.5" fill="none"/>
                </svg>
                ${p.location}
            </div>
            <div class="card-specs">
                <span>🛏 ${p.bhk}</span>
                <span>&middot;</span>
                <span>📐 ${p.area}</span>
                <span>&middot;</span>
                <span>🏢 Floor ${p.floor}</span>
            </div>
            <div class="card-price">${p.price}</div>
            <div class="card-actions">
                <a href="/property/${p.id}/" class="btn-card btn-outline">
                    View Details
                </a>
                <a href="/virtual-tour/${p.id}/" class="btn-card btn-filled">
                    Virtual Tour &#8594;
                </a>
            </div>
        </div>
    </div>`;
}

function renderCards(list) {
    const grid = document.getElementById('propertiesGrid');
    if (!grid) return;
    grid.innerHTML = '';
    if (list.length === 0) {
        grid.innerHTML = '<p style="color:#9a9a9a;text-align:center;padding:60px;grid-column:1/-1">No properties found for selected filters.</p>';
        return;
    }
    list.forEach((p, i) => {
        const html = createCardHTML(p, i);
        grid.insertAdjacentHTML('beforeend', html);
    });
    
    // Re-trigger animation cleanly
    const newCards = grid.querySelectorAll('.listing-card');
    setTimeout(() => {
        newCards.forEach(c => c.classList.add('show'));
    }, 10);
}

function updateCount(n) {
    const el = document.getElementById('resultCount');
    if (el) el.textContent = 'Showing ' + n + ' Properties';
}

// Initialize on load
window.addEventListener('DOMContentLoaded', () => {
    loadProperties();
});

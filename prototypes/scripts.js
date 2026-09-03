document.addEventListener('DOMContentLoaded', () => {
  const saved = (() => {
    try {
      return localStorage.getItem('vatenxaTheme');
    } catch (e) {
      return null;
    }
  })();

  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  const initial = saved || (prefersDark ? 'dark' : 'light');
  if (initial === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
  }

  const toggle = document.createElement('button');
  toggle.className = 'theme-toggle';
  toggle.setAttribute('aria-label', 'Toggle theme');
  toggle.innerHTML = '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M6.76 4.84l-1.8-1.79L3.17 4.84l1.79 1.79 1.8-1.79zM1 13h3v-2H1v2zm10-9h2V1h-2v3zm7.03 1.05l1.79-1.79-1.79-1.79-1.79 1.79 1.79 1.79zM17.24 19.16l1.79 1.79 1.79-1.79-1.79-1.79-1.79 1.79zM20 11v2h3v-2h-3zM12 6a6 6 0 100 12 6 6 0 000-12z"/></svg>';

  document.body.appendChild(toggle);

  function setTheme(theme) {
    if (theme === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
    try {
      localStorage.setItem('vatenxaTheme', theme);
    } catch (e) { }
  }

  toggle.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    setTheme(next);
  });

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('in-view');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.14 });

  document.querySelectorAll('.fade-in, .reveal').forEach((el) => {
    observer.observe(el);
  });

  document.querySelectorAll('[data-count]').forEach((el) => {
    const target = parseInt(el.dataset.count, 10) || 0;
    const duration = 950;
    const start = performance.now();

    const tick = (time) => {
      const progress = Math.min(1, (time - start) / duration);
      el.textContent = Math.floor(progress * target);
      if (progress < 1) requestAnimationFrame(tick);
    };

    requestAnimationFrame(tick);
  });

  const navLinks = document.querySelectorAll('.nav-link');
  const sections = [...document.querySelectorAll('section[id]')];

  const setActiveNav = () => {
    let currentId = 'home';
    sections.forEach((section) => {
      const rect = section.getBoundingClientRect();
      if (rect.top <= 180 && rect.bottom >= 180) {
        currentId = section.id;
      }
    });

    navLinks.forEach((link) => {
      const href = link.getAttribute('href');
      const isActive = href === '#' + currentId || (currentId === 'home' && href === '/');
      link.classList.toggle('active', isActive);
    });
  };

  window.addEventListener('scroll', setActiveNav, { passive: true });
  setActiveNav();

  const toggleBtn = document.querySelector('.nav-toggle');
  const navList = document.querySelector('.vn-nav-links');
  if (toggleBtn && navList) {
    toggleBtn.addEventListener('click', () => {
      const expanded = toggleBtn.getAttribute('aria-expanded') === 'true';
      toggleBtn.setAttribute('aria-expanded', String(!expanded));
      navList.classList.toggle('open');
    });

    navLinks.forEach((link) => {
      link.addEventListener('click', () => {
        navList.classList.remove('open');
        toggleBtn.setAttribute('aria-expanded', 'false');
      });
    });
  }

  const chatBtn = document.querySelector('.chatbot-btn');
  const chatPanel = document.querySelector('.chat-panel');
  if (chatBtn && chatPanel) {
    chatBtn.addEventListener('click', () => {
      chatPanel.classList.toggle('open');
    });
  }

  const mapContainer = document.getElementById('map');
  if (mapContainer && window.L) {
    const map = L.map('map', {
      zoomControl: false,
      scrollWheelZoom: true,
    }).setView([19.7515, 75.7139], 7);

    const streetTiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
    const satelliteTiles = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 19,
      attribution: 'Tiles &copy; Esri'
    });
    let satelliteMode = false;

    const hotspotData = [
      { name: 'Village XYZ', location: 'Pune District, Maharashtra', coords: [18.5204, 73.8567], risk: 'High', reports: 18, affected: 42, animal: 'Cow', trend: 'Increasing', concern: 'Possible respiratory illness' },
      { name: 'District ABC', location: 'Nashik District, Maharashtra', coords: [20.0059, 73.7897], risk: 'Medium', reports: 12, affected: 26, animal: 'Goat', trend: 'Stable', concern: 'Possible nutritional deficiency' },
      { name: 'Location DEF', location: 'Kolhapur District, Maharashtra', coords: [16.7050, 74.2433], risk: 'Low', reports: 6, affected: 11, animal: 'Sheep', trend: 'Decreasing', concern: 'Routine monitoring' },
      { name: 'Farm Cluster GHI', location: 'Nagpur District, Maharashtra', coords: [21.1458, 79.0882], risk: 'High', reports: 14, affected: 31, animal: 'Pig', trend: 'Increasing', concern: 'Possible fever cluster' },
      { name: 'Village JKL', location: 'Satara District, Maharashtra', coords: [17.6805, 74.0183], risk: 'Medium', reports: 9, affected: 18, animal: 'Horse', trend: 'Stable', concern: 'Possible tick exposure' }
    ];

    const riskColors = {
      Low: '#27ae60',
      Medium: '#f29e4c',
      High: '#e85d5d'
    };

    const markerLayer = L.layerGroup().addTo(map);
    const circleLayer = L.layerGroup().addTo(map);
    let activeMode = 'markers';

    const popupFor = (place) => `<div class="map-popup"><strong>${place.name}</strong><small>${place.location}</small><hr><b>Animal Type:</b> ${place.animal}<br><b>Number of Reports:</b> ${place.reports}<br><b>Animals Affected:</b> ${place.affected}<br><b>Risk Level:</b> <span style="color:${riskColors[place.risk]}">${place.risk} Risk</span><br><b>Date:</b> 02 Sep 2026<br><b>Possible Health Concern:</b> ${place.concern}<br><button class="popup-details" type="button">View Details</button></div>`;

    const renderMap = () => {
      markerLayer.clearLayers();
      circleLayer.clearLayers();
      const risk = document.getElementById('risk-filter')?.value || 'All';
      const animal = document.getElementById('animal-filter')?.value || 'All Animals';
      const visible = hotspotData.filter((place) => (risk === 'All' || place.risk === risk) && (animal === 'All Animals' || place.animal === animal));
      visible.forEach((place) => {
        const radius = 8 + place.reports / 3;
        if (activeMode === 'markers') {
          const marker = L.circleMarker(place.coords, { radius: 9, color: '#ffffff', fillColor: riskColors[place.risk], fillOpacity: .9, weight: 3 }).addTo(markerLayer);
          marker.bindPopup(popupFor(place));
        } else if (activeMode === 'clusters') {
          L.circleMarker(place.coords, { radius: radius + 5, color: riskColors[place.risk], fillColor: riskColors[place.risk], fillOpacity: .24, weight: 2 }).bindTooltip(`${place.name}: ${place.reports} reports`).addTo(markerLayer);
          L.circleMarker(place.coords, { radius: 7, color: '#fff', fillColor: riskColors[place.risk], fillOpacity: 1, weight: 2 }).bindPopup(popupFor(place)).addTo(markerLayer);
        } else {
          L.circle(place.coords, { radius: radius * 9000, color: riskColors[place.risk], fillColor: riskColors[place.risk], fillOpacity: .24, weight: 1 }).addTo(circleLayer);
        }
      });
      if (activeMode === 'heatmap') map.getContainer().classList.add('heatmap-active'); else map.getContainer().classList.remove('heatmap-active');
    };

    const hotspotList = document.getElementById('hotspot-list');
    if (hotspotList) {
      hotspotList.innerHTML = hotspotData.slice(0, 3).map((place, index) => `<article class="hotspot-item ${place.risk.toLowerCase()}" data-hotspot-index="${index}"><h3>${place.name}</h3><p>${place.reports} Reports · ${place.affected} Animals Affected</p><div class="hotspot-meta"><span>${place.risk} Risk</span><span class="trend-${place.trend.toLowerCase()}">Trend: ${place.trend}</span></div></article>`).join('');
      hotspotList.addEventListener('click', (event) => {
        const card = event.target.closest('[data-hotspot-index]');
        if (!card) return;
        const place = hotspotData[Number(card.dataset.hotspotIndex)];
        map.flyTo(place.coords, 10, { duration: 1.1 });
        renderMap();
      });
    }
    document.querySelectorAll('.mode-button').forEach((button) => button.addEventListener('click', () => { activeMode = button.dataset.mode; document.querySelectorAll('.mode-button').forEach((item) => item.classList.toggle('active', item === button)); renderMap(); }));
    document.getElementById('apply-filters')?.addEventListener('click', () => { renderMap(); document.getElementById('map-filters')?.classList.remove('open'); });
    document.querySelector('.filter-open')?.addEventListener('click', () => document.getElementById('map-filters')?.classList.add('open'));
    document.querySelector('.drawer-close')?.addEventListener('click', () => document.getElementById('map-filters')?.classList.remove('open'));
    document.querySelectorAll('[data-map-control]').forEach((button) => button.addEventListener('click', () => {
      const control = button.dataset.mapControl;
      if (control === 'zoom-in') map.zoomIn();
      if (control === 'zoom-out') map.zoomOut();
      if (control === 'locate') map.flyTo([19.7515, 75.7139], 7);
      if (control === 'type') { satelliteMode = !satelliteMode; if (satelliteMode) { map.removeLayer(streetTiles); satelliteTiles.addTo(map); } else { map.removeLayer(satelliteTiles); streetTiles.addTo(map); } }
      if (control === 'fullscreen') document.querySelector('.map-canvas-wrap')?.requestFullscreen?.();
    }));
    renderMap();
    map.fitBounds(hotspotData.map((item) => item.coords), { padding: [30, 30] });
  } else if (mapContainer) {
    mapContainer.innerHTML = '<div class="map-fallback">Map failed to load. Please reload the page.</div>';
  }
});

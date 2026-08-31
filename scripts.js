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
});

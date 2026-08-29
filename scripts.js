// Minimal JS for micro-interactions and scroll reveal (UI/UX only)
document.addEventListener('DOMContentLoaded', ()=>{
  // Theme: initialize from localStorage or system preference
  const saved = (()=>{try{return localStorage.getItem('vatenxaTheme')}catch(e){return null}})();
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  const initial = saved || (prefersDark ? 'dark' : 'light');
  if(initial === 'dark') document.documentElement.setAttribute('data-theme','dark');

  // Floating theme toggle (available on all pages)
  const toggle = document.createElement('button'); toggle.className = 'theme-toggle'; toggle.setAttribute('aria-label','Toggle theme');
  toggle.innerHTML = '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M6.76 4.84l-1.8-1.79L3.17 4.84l1.79 1.79 1.8-1.79zM1 13h3v-2H1v2zm10-9h2V1h-2v3zm7.03 1.05l1.79-1.79-1.79-1.79-1.79 1.79 1.79 1.79zM17.24 19.16l1.79 1.79 1.79-1.79-1.79-1.79-1.79 1.79zM20 11v2h3v-2h-3zM12 6a6 6 0 100 12 6 6 0 000-12z"/></svg>';
  document.body.appendChild(toggle);
  function setTheme(t){ if(t==='dark') document.documentElement.setAttribute('data-theme','dark'); else document.documentElement.removeAttribute('data-theme'); try{localStorage.setItem('vatenxaTheme', t)}catch(e){} }
  toggle.addEventListener('click', ()=>{ const cur = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light'; const next = cur === 'dark' ? 'light' : 'dark'; setTheme(next); });
  // Scroll reveal
  const obs = new IntersectionObserver((entries)=>{
    entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in-view');obs.unobserve(e.target)}}),{threshold:0.12}
  })
  document.querySelectorAll('.fade-in').forEach(el=>obs.observe(el));

  // Count up numbers
  document.querySelectorAll('[data-count]').forEach(el=>{
    const to = parseInt(el.dataset.count,10)||0;let v=0;const dur=900;const start=performance.now();
    const step=(t)=>{let p=Math.min(1,(t-start)/dur);el.textContent=Math.floor(p*to);if(p<1)requestAnimationFrame(step)};requestAnimationFrame(step);
  });

  // Chatbot
  const btn=document.querySelector('.chatbot-btn');const panel=document.querySelector('.chat-panel');
  if(btn && panel){btn.addEventListener('click',()=>panel.classList.toggle('open'))}
});

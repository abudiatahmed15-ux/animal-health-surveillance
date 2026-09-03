// Backend status and realtime info for VetNexa frontend
document.addEventListener('DOMContentLoaded', ()=>{
  const POLL_MS = 10000;

  function createStatusCard(){
    let el = document.getElementById('vn-backend-status');
    if(el) return el;
    el = document.createElement('div');
    el.id = 'vn-backend-status';
    el.className = 'card';
    el.style.position = 'fixed';
    el.style.right = '18px';
    el.style.top = '80px';
    el.style.width = '260px';
    el.style.zIndex = 70;
    el.innerHTML = `<h4 style="margin:0 0 8px 0">Backend Status</h4><div id="vn-status-body" style="font-size:13px;color:var(--muted)">Checking...</div>`;
    document.body.appendChild(el);
    return el;
  }

  async function checkBackend(){
    const card = createStatusCard();
    const body = document.getElementById('vn-status-body');
    const origin = window.location.origin;
    // queries
    const results = {
      api: false,
      animals: null,
      reports: null,
      model_loaded: false,
      model_confidence: 0
    };

    try{
      // API reachable test
      const r = await fetch(origin + '/api/animals');
      results.api = r.ok;
      if(r.ok){
        const animals = await r.json();
        results.animals = Array.isArray(animals) ? animals.length : (animals.total_animals || null);
      }
    }catch(e){ results.api = false }

    try{
      const r2 = await fetch(origin + '/api/reports');
      if(r2.ok){
        const reports = await r2.json();
        results.reports = Array.isArray(reports) ? reports.length : null;
      }
    }catch(e){}

    // Test AI model by posting a harmless minimal payload
    try{
      const sample = { animal_type: 'Cow', breed: 'Unknown', age: 1, gender: 'Female', weight: 0, symptoms: [], duration_days:0 };
      const ra = await fetch(origin + '/api/ai/predict', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(sample)});
      if(ra.ok){
        const pj = await ra.json();
        // API returns structured object; support both {possible_condition,..} or {success:true,data:...}
        let data = pj;
        if(pj && pj.data) data = pj.data;
        if(data && typeof data.confidence !== 'undefined'){
          results.model_loaded = data.confidence > 0;
          results.model_confidence = data.confidence || 0;
        }
      }
    }catch(e){}

    // Update UI
    let html = '';
    html += `<div><strong>API:</strong> ${results.api ? '<span style="color:var(--success)">Online</span>' : '<span style="color:var(--danger)">Offline</span>'}</div>`;
    html += `<div style="margin-top:6px"><strong>Animals:</strong> ${results.animals===null? '—' : results.animals}</div>`;
    html += `<div style="margin-top:6px"><strong>Reports:</strong> ${results.reports===null? '—' : results.reports}</div>`;
    html += `<div style="margin-top:6px"><strong>AI Model:</strong> ${results.model_loaded ? '<span style="color:var(--success)">Loaded</span>' : '<span style="color:var(--warning)">Not loaded</span>'}</div>`;
    html += `<div style="margin-top:6px"><strong>Model conf:</strong> ${Number(results.model_confidence).toFixed(2)}</div>`;
    html += `<div style="margin-top:8px"><a href="/docs" style="font-size:12px">Open API docs</a></div>`;

    if(body) body.innerHTML = html;

    // Update landing page stats if available
    try{
      // find stat labels and set corresponding numbers
      document.querySelectorAll('.stat').forEach(card=>{
        const label = card.querySelector('.stat-label');
        const number = card.querySelector('.stat-number');
        if(!label || !number) return;
        const text = label.textContent.trim().toLowerCase();
        if(text.includes('animals')){
          if(results.animals !== null) number.textContent = results.animals;
        }
        if(text.includes('health reports') || text.includes('reports')){
          if(results.reports !== null) number.textContent = results.reports;
        }
      });
    }catch(e){}
  }

  // initial check + polling
  checkBackend();
  setInterval(checkBackend, POLL_MS);
});

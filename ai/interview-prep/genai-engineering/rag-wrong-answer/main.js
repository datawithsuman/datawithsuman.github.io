// RAG wrong-answer labs, fed by lesson.js (written by lesson_data.py). The refund-policy example is illustrative.
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');

(function (D) {
  $('#qual').textContent = D.qualifier;
  $('#src').innerHTML = `Source: ${esc(D.source.authors)}, <a href="${D.source.arxiv}" target="_blank" rel="noopener">${esc(D.source.title)}</a> (${esc(D.source.venue)}). The failure points, the chunk-size trade-off and the case-study notes come from it. The debugging order is a practical approach, and the refund-policy example is made up.`;

  const chunk = (c) => `<div class="chunk ${c.kind || ''}"><span class="rk">#${c.rank}</span><span>${esc(c.text)}</span></div>`;

  // ---------- 01 · the situation ----------
  $('#chat').innerHTML = `<div class="bubble u"><small>Customer</small>${esc(D.question)}</div>
    <div class="bubble b"><small>Chatbot</small>${esc(D.wrong)}</div>
    <div class="bubble g"><small>What it should say</small>${esc(D.truth)}</div>`;
  const dk = D.docs;
  $('#docs').innerHTML = ['monthly', 'annual', 'gift', 'method', 'old'].map((k, i) =>
    `<div class="chunk ${k === 'annual' ? 'right' : ''}"><span class="rk">doc ${i + 1}</span><span>${esc(dk[k])}</span></div>`).join('');

  // ---------- 03 · spot it ----------
  const STAGES = [['question', '1 · Question'], ['retrieved', '2 · Retrieved'], ['prompt', '3 · In the prompt'], ['answer', '4 · Answer']];
  let cs = 0, st = 'question', revealed = false;
  const seen = {};

  function status(c, key) {
    if (key === 'question') return null;
    if (key === 'answer') return false;
    return c.has[key];
  }
  function drawCase() {
    const c = D.cases[cs];
    $('#caseBadge').textContent = c.fp;
    $('#pipe').innerHTML = STAGES.map(([k, label], i) => {
      const s = (seen[c.id] || {})[k] ? status(c, k) : null;
      return `${i ? '<span class="arr">→</span>' : ''}<button class="btn${k === st ? ' on' : ''}${s === true ? ' ok' : s === false ? ' no' : ''}" data-s="${k}">${label}</button>`;
    }).join('');
    $('#pipe').querySelectorAll('.btn').forEach((b) => b.addEventListener('click', () => { st = b.dataset.s; (seen[c.id] = seen[c.id] || {})[st] = true; drawCase(); }));
    let body = '';
    if (st === 'question') body = `<h3>What the customer asked</h3><div class="qbox"><div class="bubble u"><small>Customer</small>${esc(D.question)}</div></div><p class="note">The system turns this into a search over the documents.</p>`;
    if (st === 'retrieved') body = `<h3>Chunks retrieved for this question</h3><div class="docs">${c.retrieved.map(chunk).join('')}</div><p class="note">${esc(c.retrieved_note)}</p><p class="verdict">Right answer in the retrieved chunks? <b style="color:var(--${c.has.retrieved ? 'green' : 'red'})">${c.has.retrieved ? 'Yes' : 'No'}</b></p>`;
    if (st === 'prompt') body = `<h3>Chunks the model actually received</h3><div class="docs">${c.prompt.map(chunk).join('')}</div><p class="note">${esc(c.prompt_note)}</p><p class="verdict">Right answer in the prompt? <b style="color:var(--${c.has.prompt ? 'green' : 'red'})">${c.has.prompt ? 'Yes' : 'No'}</b></p>`;
    if (st === 'answer') body = `<h3>What the chatbot said</h3><div class="qbox"><div class="bubble b"><small>Chatbot</small>${esc(c.answer)}</div></div><p class="verdict">Correct? <b style="color:var(--red)">No</b>. It should say: ${esc(D.truth)}</p>`;
    $('#stage').innerHTML = body;
    const lostLabel = { retrieved: '2 · Retrieved', prompt: '3 · In the prompt', answer: '4 · Answer' }[c.lost];
    $('#lostAt').textContent = revealed ? `The right answer is lost at: ${lostLabel}.` : '';
    $('#fixNote').textContent = revealed ? c.fix : '';
  }
  $('#caseSeg').innerHTML = D.cases.map((c, i) => `<button class="btn${i ? '' : ' on'}" data-c="${i}">Case ${c.id}: ${esc(c.name)}</button>`).join('');
  $('#caseSeg').querySelectorAll('.btn').forEach((b) => b.addEventListener('click', () => {
    $('#caseSeg').querySelectorAll('.btn').forEach((o) => o.classList.remove('on')); b.classList.add('on');
    cs = +b.dataset.c; st = 'question'; revealed = false; drawCase();
  }));
  $('#reveal').addEventListener('click', () => { revealed = !revealed; drawCase(); });
  drawCase();

  // ---------- 04 · seven failure points ----------
  const ZONES = [['all', 'All seven'], ['retrieval', 'Retrieval'], ['context', 'Building the prompt'], ['generation', 'Reading the prompt']];
  let zone = 'all';
  function drawFP() {
    $('#fpgrid').innerHTML = D.failure_points.filter((f) => zone === 'all' || f.zone === zone).map((f) =>
      `<div class="fp ${f.zone}"><b class="id">${f.id}</b><h3>${esc(f.name)}</h3><p>${esc(f.what)}</p><p class="chk"><strong>How to check:</strong> ${esc(f.check)}</p></div>`).join('');
  }
  $('#zones').innerHTML = ZONES.map(([k, l]) => `<button class="btn${k === 'all' ? ' on' : ''}" data-z="${k}">${l}</button>`).join('');
  $('#zones').querySelectorAll('.btn').forEach((b) => b.addEventListener('click', () => {
    $('#zones').querySelectorAll('.btn').forEach((o) => o.classList.remove('on')); b.classList.add('on'); zone = b.dataset.z; drawFP();
  }));
  drawFP();

  // ---------- 05 · diagnose before fixing ----------
  const T = D.tree;
  let path = ['n0'];
  function drawTree() {
    const last = path[path.length - 1], res = T.results[last];
    const trail = path.slice(0, -1).map((id, i) => `${esc(T[id].q)} → ${path[i + 1] === T[id].yes ? 'Yes' : 'No'}`).join('  ·  ');
    let h = trail ? `<div class="path">${trail}</div>` : '';
    if (res) {
      h += `<div class="res ${res.color}"><b>${esc(res.fp)}</b>${esc(res.text)}</div><p style="margin-top:12px"><button class="btn" id="again">Start again</button></p>`;
    } else {
      h += `<p class="q">${esc(T[last].q)}</p><div class="seg"><button class="btn" data-a="yes">Yes</button><button class="btn" data-a="no">No</button></div>`;
    }
    $('#tree').innerHTML = h;
    $('#tree').querySelectorAll('[data-a]').forEach((b) => b.addEventListener('click', () => { path.push(T[last][b.dataset.a]); drawTree(); }));
    $('#again')?.addEventListener('click', () => { path = ['n0']; drawTree(); });
  }
  drawTree();
})(window.LESSON);

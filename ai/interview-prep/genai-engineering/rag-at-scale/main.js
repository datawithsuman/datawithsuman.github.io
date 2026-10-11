// RAG at scale labs, fed by lesson.js (written by lesson_data.py). Costs are exact arithmetic; the refund example is illustrative.
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');

(function (D) {
  $('#qual').textContent = D.qualifier;
  $('#src').innerHTML = 'Sources: ' + D.sources.map((s) => `${esc(s.who)}, <a href="${s.url}" target="_blank" rel="noopener">${esc(s.title)}</a>`).join(' · ') +
    '. Costs are exact arithmetic, the recall curve is a seeded toy run, and the refund example is made up.';

  // ---------- 02 · exact search cost ----------
  const SIZES = [100, 10000, 100000, 1e6, 1e7, 1e8, 1e9, 1e10].slice(0, 8);
  const fmt = (n) => n >= 1e12 ? (n / 1e12).toFixed(n % 1e12 ? 1 : 0) + ' T' : n >= 1e9 ? (n / 1e9).toFixed(n % 1e9 ? 1 : 0) + ' B' : n >= 1e6 ? (n / 1e6).toFixed(n % 1e6 ? 1 : 0) + ' M' : n.toLocaleString('en-US');
  const bytes = (b) => b >= 1e12 ? (b / 1e12).toFixed(1) + ' TB' : b >= 1e9 ? (b / 1e9).toFixed(1) + ' GB' : b >= 1e6 ? (b / 1e6).toFixed(1) + ' MB' : (b / 1e3).toFixed(0) + ' KB';
  $('#dimNote').textContent = D.dim;
  function cost() {
    const n = SIZES[+$('#nDocs').value];
    $('#nOut').textContent = n.toLocaleString('en-US');
    $('#sims').textContent = fmt(n);
    $('#macs').textContent = fmt(n * D.dim);
    $('#mem').textContent = bytes(n * D.dim * 4);
    $('#ratio').textContent = (n / 100).toLocaleString('en-US') + '×';
  }
  $('#nDocs').max = SIZES.length - 1;
  $('#nDocs').value = 4;
  $('#nDocs').addEventListener('input', cost); cost();

  // ---------- 03 · IVF picture ----------
  const P = D.pic, S = 600;
  function pic() {
    const k = +$('#probe').value, probed = new Set(P.order.slice(0, k));
    const true5 = new Set(P.true5);
    const checked = P.points.filter((p) => probed.has(p[2])).length;
    const found = P.true5.filter((i) => probed.has(P.points[i][2])).length;
    let s = `<svg viewBox="0 0 ${S} ${S}" role="img" aria-label="Vectors grouped into clusters; only the nearest clusters are searched">`;
    P.points.forEach((p, i) => {
      const on = probed.has(p[2]);
      s += `<circle cx="${p[0] * S}" cy="${p[1] * S}" r="${on ? 4 : 3}" fill="${on ? 'var(--blue)' : '#3a3a44'}"/>`;
    });
    P.true5.forEach((i) => { const p = P.points[i]; s += `<circle cx="${p[0] * S}" cy="${p[1] * S}" r="9" fill="none" stroke="${probed.has(p[2]) ? 'var(--green)' : 'var(--red)'}" stroke-width="2.5"/>`; });
    P.centres.forEach((c, i) => { s += `<path d="M${c[0] * S - 7} ${c[1] * S}h14M${c[0] * S} ${c[1] * S - 7}v14" stroke="${probed.has(i) ? 'var(--ink)' : '#55555f'}" stroke-width="2"/>`; });
    s += `<circle cx="${P.query[0] * S}" cy="${P.query[1] * S}" r="9" fill="var(--yellow)"/></svg>`;
    $('#pic').innerHTML = s;
    $('#probeOut').textContent = `${k} of ${P.centres.length}`;
    const pct = Math.round(checked / P.points.length * 100);
    $('#probeBadge').textContent = `${pct}% of vectors checked`;
    $('#picNote').innerHTML = `Checked <b>${checked}</b> of ${P.points.length} vectors and found <b style="color:var(--${found === 5 ? 'green' : 'red'})">${found} of the true 5</b> nearest neighbours.` +
      (found < 5 ? ' The missed ones sit just across a cluster border.' : '');
  }
  $('#probe').max = P.centres.length;
  $('#probe').addEventListener('input', pic); pic();

  // ---------- 04 · recall vs vectors checked (toy run) ----------
  const C = D.ivf.curve, CW = 640, CH = 300, pad = { l: 52, r: 16, t: 14, b: 44 };
  const x = (v) => pad.l + (v / 100) * (CW - pad.l - pad.r);
  const ymin = Math.floor(Math.min(...C.map((c) => c.recall)) / 10) * 10;
  const y = (v) => pad.t + (1 - (v - ymin) / (100 - ymin)) * (CH - pad.t - pad.b);
  $('#nlist').textContent = D.ivf.nlist;
  $('#toyNote').textContent = D.ivf.src;
  function chart() {
    const i = +$('#np').value, c = C[i];
    let s = `<svg viewBox="0 0 ${CW} ${CH}" role="img" aria-label="Recall at 10 against the share of vectors checked">`;
    for (let g = ymin; g <= 100; g += 10) s += `<line x1="${pad.l}" x2="${CW - pad.r}" y1="${y(g)}" y2="${y(g)}" stroke="var(--line)"/><text x="${pad.l - 8}" y="${y(g) + 4}" fill="var(--muted)" font-size="12" text-anchor="end">${g}%</text>`;
    [0, 25, 50, 75, 100].forEach((g) => { s += `<text x="${x(g)}" y="${CH - 22}" fill="var(--muted)" font-size="12" text-anchor="middle">${g}%</text>`; });
    s += `<text x="${(CW + pad.l) / 2}" y="${CH - 4}" fill="var(--muted)" font-size="12" text-anchor="middle">vectors checked</text>`;
    s += `<text x="14" y="${CH / 2}" fill="var(--muted)" font-size="12" text-anchor="middle" transform="rotate(-90 14 ${CH / 2})">recall@10</text>`;
    s += `<polyline fill="none" stroke="var(--blue)" stroke-width="3" points="${C.map((p) => `${x(p.checked)},${y(p.recall)}`).join(' ')}"/>`;
    C.forEach((p) => { s += `<circle cx="${x(p.checked)}" cy="${y(p.recall)}" r="3.5" fill="var(--blue)"/>`; });
    s += `<circle cx="${x(c.checked)}" cy="${y(c.recall)}" r="8" fill="var(--yellow)"/></svg>`;
    $('#chart').innerHTML = s;
    $('#npOut').textContent = c.nprobe;
    $('#chk').textContent = c.checked + '%';
    $('#rec').textContent = c.recall + '%';
  }
  $('#np').max = C.length - 1;
  $('#np').addEventListener('input', chart); chart();

  // ---------- 05 · look-alikes, filter, rerank ----------
  let filt = false, rr = false;
  function ranks() {
    let list = D.results.filter((r) => !filt || (r.team === 'Support' && r.year === 2026));
    list = [...list].sort((a, b) => rr ? b.rr - a.rr : b.sim - a.sim);
    const pos = list.findIndex((r) => r.right) + 1;
    let h = '';
    list.forEach((r, i) => {
      if (i === 5) h += '<div class="cut"><span>TOP 5 → LLM</span></div>';
      h += `<div class="chunk ${r.right ? 'right' : ''} ${i >= 5 ? 'out' : ''}"><span class="rk">#${i + 1}</span><span>${esc(r.t)}</span><span class="meta">${esc(r.team)} · ${r.year} · ${(rr ? r.rr : r.sim).toFixed(2)}</span></div>`;
    });
    $('#results').innerHTML = h;
    $('#rankBadge').textContent = `right chunk: #${pos}`;
    $('#rankBadge').className = 'badge ' + (pos <= 5 ? 'good' : 'bad');
    $('#rankNote').innerHTML = pos > 5 ? 'The right chunk ranks <b class="red">#' + pos + '</b>, below the cut. The LLM never sees it and answers from a look-alike.'
      : pos === 1 ? 'The right chunk is <b class="green">#1</b>. ' + (filt && rr ? 'Filtering removed the look-alikes, and the reranker confirmed the order.' : filt ? 'Filtering removed the look-alikes before ranking.' : 'The reranker read each chunk with the question and moved the current policy to the top.')
      : 'The right chunk is <b class="green">#' + pos + '</b>, inside the top 5, but look-alikes still sit above it.';
    $('#tFilter').classList.toggle('on', filt); $('#tRerank').classList.toggle('on', rr);
  }
  $('#tFilter').addEventListener('click', () => { filt = !filt; ranks(); });
  $('#tRerank').addEventListener('click', () => { rr = !rr; ranks(); });
  ranks();
})(window.LESSON);

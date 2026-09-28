// Prefill vs Decode labs, fed by lesson.js (written by ../lesson_data.py). All numbers are ideal ceilings (exact arithmetic).
const $ = (s) => document.querySelector(s);
const C = { blue: 'var(--blue)', yellow: 'var(--yellow)', red: 'var(--red)', green: 'var(--green)', ink: '#ececec', dim: '#8a8a93', line: '#2c2c35' };
const fmt = (v, dp = 0) => v.toLocaleString('en-US', { minimumFractionDigits: dp, maximumFractionDigits: dp });
const time = (s) => (s >= 1 ? `${fmt(s, 1)} s` : s >= 0.01 ? `${fmt(s * 1e3, 0)} ms` : `${fmt(s * 1e3, 1)} ms`);

(function (D) {
  const S = Lesson.svg, G = D.gpu, PEAK = G.tflops_fp16 * 1e12, BW = G.tb_s * 1e12, RIDGE = G.ridge;
  const chart = (el, W, H) => { el.innerHTML = ''; return S('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img' }, el); };
  const text = (svg, x, y, s, a = {}) => { const t = S('text', { x, y, fill: C.dim, 'font-size': 13, ...a }, svg); t.textContent = s; return t; };
  function segs(box, onPick) {
    box.querySelectorAll('.btn').forEach((b) => b.addEventListener('click', () => {
      box.querySelectorAll('.btn').forEach((o) => o.classList.remove('on')); b.classList.add('on'); onPick(b.dataset);
    }));
  }
  const modelBtns = (box, sel) => { box.innerHTML = D.models.map((m, i) => `<button class="btn${i === sel ? ' on' : ''}" data-m="${i}">${m.name.split(' ').pop()}</button>`).join(''); };
  $('#qual').textContent = D.qualifier;

  // ---------- 01 · two phases (illustrative) ----------
  $('#ptoks').innerHTML = D.demo.prompt.map((t) => `<span class="tok p">${t}</span>`).join('');
  $('#atoks').innerHTML = D.demo.answer.map((t) => `<span class="tok a">${t}</span>`).join('');
  let timers = [];
  function reset() { timers.forEach(clearTimeout); timers = []; document.querySelectorAll('.tok').forEach((t) => t.classList.remove('on')); $('#passes').textContent = '0'; $('#phaseNow').textContent = 'ready'; }
  $('#play').addEventListener('click', () => {
    reset();
    timers.push(setTimeout(() => { document.querySelectorAll('.tok.p').forEach((t) => t.classList.add('on')); $('#passes').textContent = '1'; $('#phaseNow').textContent = 'prefill'; }, 250));
    document.querySelectorAll('.tok.a').forEach((t, i) => timers.push(setTimeout(() => {
      t.classList.add('on'); $('#passes').textContent = String(i + 2); $('#phaseNow').textContent = 'decode';
    }, 1100 + i * 550)));
    timers.push(setTimeout(() => { $('#phaseNow').textContent = 'done'; }, 1100 + D.demo.answer.length * 550));
  });

  // ---------- 03 · prefill ----------
  const PLENS = [100, 500, 1000, 2000, 4000, 8000, 16000];
  let pm = D.main;
  modelBtns($('#pModel'), pm);
  function drawPrefill() {
    const L = PLENS[+$('#plen').value], P = D.models[pm].params;
    const flops = 2 * P * L, comp = flops / PEAK, mem = (2 * P) / BW, t = Math.max(comp, mem), ai = flops / (2 * P);
    $('#plenOut').textContent = `${fmt(L)} tokens`;
    $('#pFlops').textContent = flops >= 1e15 ? `${fmt(flops / 1e15, 1)} PFLOP` : `${fmt(flops / 1e12, 1)} TFLOP`;
    $('#pTime').textContent = time(t);
    $('#pAI').textContent = fmt(ai);
    const b = $('#pBadge'), cb = ai > RIDGE;
    b.className = `badge ${cb ? 'info' : 'warn'}`;
    b.textContent = cb ? 'compute-bound' : 'short prompt: still memory-bound';
  }
  segs($('#pModel'), (d) => { pm = +d.m; drawPrefill(); });
  $('#plen').addEventListener('input', drawPrefill);
  drawPrefill();

  // ---------- 04 · decode ----------
  let dm = D.main, bpp = 2;
  modelBtns($('#dModel'), dm);
  function drawDecode() {
    const P = D.models[dm].params, bytes = P * bpp, mem = bytes / BW, comp = (2 * P) / PEAK, t = Math.max(mem, comp);
    $('#dGB').textContent = `${fmt(bytes / 1e9, 1)} GB`;
    $('#dMs').textContent = `${fmt(t * 1e3, 2)} ms`;
    $('#dTps').textContent = `${fmt(1 / t)} tok/s`;
    const used = (comp / t) * 100;
    $('#gComp').textContent = `${fmt(used, 1)}%  (${fmt(100 - used, 1)}% idle)`;
    $('#gCompFill').style.width = `${Math.max(used, 0.6)}%`;
  }
  segs($('#dModel'), (d) => { dm = +d.m; drawDecode(); });
  segs($('#dPrec'), (d) => { bpp = +d.b; drawDecode(); });
  drawDecode();

  // ---------- 05 · roofline + batching ----------
  const BATCH = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024];
  const P8 = D.models[D.main].params;
  function drawRoof() {
    const B = BATCH[+$('#bsz').value];
    const W = 720, H = 420, x0 = 86, x1 = W - 24, y0 = H - 56, y1 = 26;
    const lx = (v) => x0 + ((Math.log10(v) - 0) / (4 - 0)) * (x1 - x0);           // 1 … 10,000 FLOPs/byte
    const ly = (v) => y0 - ((Math.log10(v) - 0) / (3.2 - 0)) * (y0 - y1);           // 1 … ~1,585 TFLOPS
    const perf = (ai) => Math.min(G.tflops_fp16, (G.tb_s * ai));                     // attainable TFLOPS
    const svg = chart($('#roof'), W, H);
    [1, 10, 100, 1000, 10000].forEach((v) => { S('line', { x1: lx(v), x2: lx(v), y1: y1, y2: y0, stroke: C.line }, svg); text(svg, lx(v), y0 + 26, fmt(v), { 'text-anchor': 'middle', 'font-size': 19 }); });
    [1, 10, 100, 1000].forEach((v) => { S('line', { x1: x0, x2: x1, y1: ly(v), y2: ly(v), stroke: C.line }, svg); text(svg, x0 - 10, ly(v) + 6, fmt(v), { 'text-anchor': 'end', 'font-size': 19 }); });
    text(svg, (x0 + x1) / 2, H - 4, 'FLOPs per byte read (log)', { 'text-anchor': 'middle', 'font-size': 18 });
    text(svg, 8, y1 - 6, 'TFLOPS', { 'font-size': 17 });
    const pts = []; for (let a = 1; a <= 10000; a *= 1.12) pts.push(`${lx(a)},${ly(perf(a))}`);
    S('polyline', { points: pts.join(' '), fill: 'none', stroke: C.ink, 'stroke-width': 2.5 }, svg);
    S('line', { x1: lx(RIDGE), x2: lx(RIDGE), y1: y1, y2: y0, stroke: C.dim, 'stroke-dasharray': '5 5' }, svg);
    text(svg, lx(RIDGE) + 8, y0 - 12, `knee ≈ ${fmt(RIDGE)}`, { 'font-size': 18 });
    text(svg, lx(2.2), ly(perf(2.2)) - 22, 'memory-bound', { fill: C.yellow, 'font-size': 20 });
    text(svg, lx(RIDGE) - 12, ly(G.tflops_fp16) - 2, 'compute-bound', { fill: C.blue, 'font-size': 20, 'text-anchor': 'end' });
    // prefill dot (2,000-token prompt) and decode dot (batch B)
    S('circle', { cx: lx(2000), cy: ly(perf(2000)), r: 10, fill: C.blue }, svg);
    text(svg, lx(2000), ly(perf(2000)) + 32, 'prefill', { fill: C.blue, 'text-anchor': 'middle', 'font-size': 18 });
    S('circle', { cx: lx(B), cy: ly(perf(B)), r: 12, fill: C.yellow, stroke: '#0f0f12', 'stroke-width': 2 }, svg);
    text(svg, lx(B) + (B > 300 ? -18 : 18), ly(perf(B)) + (B > 300 ? 34 : 6), `decode × ${B}`, { fill: C.yellow, 'text-anchor': B > 300 ? 'end' : 'start', 'font-size': 19 });

    const mem = (2 * P8) / BW, comp = (2 * P8 * B) / PEAK, t = Math.max(mem, comp);
    $('#bOut').textContent = B;
    $('#bUser').textContent = `${fmt(1 / t)} tok/s`;
    $('#bTotal').textContent = `${fmt(B / t)} tok/s`;
    $('#bAI').textContent = fmt(B);
    const b = $('#bBadge'), cb = B > RIDGE;
    b.className = `badge ${cb ? 'info' : 'warn'}`;
    b.textContent = cb ? 'compute-bound: per-user speed now drops' : 'memory-bound: more users ≈ free throughput';
  }
  $('#bsz').addEventListener('input', drawRoof);
  drawRoof();

  $('#collideNote').textContent = `Sources: ${D.papers.vllm.src}; ${D.papers.modular.src}.`;
})(window.LESSON);

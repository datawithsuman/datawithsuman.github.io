// LLM Quantization labs, fed by lesson.js (written by ../lesson_data.py from the papers' tables).
const $ = (s) => document.querySelector(s);
const f2 = (v) => (v >= 1000 ? Math.round(v).toLocaleString('en-US') : v >= 100 ? v.toFixed(0) : v.toFixed(2));
const C = { blue: 'var(--blue)', yellow: 'var(--yellow)', red: 'var(--red)', green: 'var(--green)', ink: '#ececec', dim: '#8a8a93', line: '#2c2c35' };

(function (D) {
  const S = Lesson.svg, P = D.papers;
  const chart = (el, W, H) => { el.innerHTML = ''; return S('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img' }, el); };
  const text = (svg, x, y, s, a = {}) => { const t = S('text', { x, y, fill: C.dim, 'font-size': 13, ...a }, svg); t.textContent = s; return t; };
  function segs(box, onPick) {
    box.querySelectorAll('.btn').forEach((b) => b.addEventListener('click', () => {
      box.querySelectorAll('.btn').forEach((o) => o.classList.remove('on')); b.classList.add('on'); onPick(b.dataset);
    }));
  }
  const on = (box) => box.querySelector('.btn.on').dataset;

  // ---------- 01 · memory (exact arithmetic) ----------
  const PRECS = [16, 8, 4];
  $('#precBtns').innerHTML = PRECS.map((b, i) => `<button class="btn${i ? '' : ' on'}" data-b="${b}">${b}-bit</button>`).join('');
  function drawMem(bits) {
    const W = 720, H = 210, x0 = 150, xmax = 820, sx = (v) => x0 + (v / xmax) * (W - x0 - 70);
    const svg = chart($('#memChart'), W, H);
    D.models.forEach((m, i) => {
      const gb = (m.params * bits) / 8 / 1e9, y = 30 + i * 58;
      text(svg, 16, y + 24, m.name, { fill: C.ink, 'font-size': 15 });
      S('rect', { x: x0, y, width: Math.max(2, sx(gb) - x0), height: 34, rx: 6, fill: gb <= D.gpu_gb ? C.green : C.blue, 'fill-opacity': 0.85 }, svg);
      text(svg, sx(gb) + 8, y + 23, `${gb < 10 ? gb.toFixed(1) : Math.round(gb)} GB`, { fill: C.ink, 'font-size': 14 });
    });
    S('line', { x1: sx(D.gpu_gb), x2: sx(D.gpu_gb), y1: 14, y2: H - 6, stroke: C.yellow, 'stroke-dasharray': '5 5', 'stroke-width': 2 }, svg);
    text(svg, sx(D.gpu_gb) + 6, 16, '1 GPU (80 GB)', { fill: C.yellow, 'font-size': 12 });
    const gb70 = (D.models[1].params * bits) / 8 / 1e9;
    $('#mem70').textContent = `${Math.round(gb70)} GB`;
    $('#gpus70').textContent = Math.ceil(gb70 / D.gpu_gb);
    $('#whyBadge').textContent = bits === 16 ? 'the usual precision' : `${16 / bits}× smaller than 16-bit`;
  }
  segs($('#precBtns'), (d) => drawMem(+d.b));
  drawMem(16);
  $('#bookStep').textContent = P.book.step.replace(/^./, (c) => c.toUpperCase());
  $('#gptqSpeed').textContent = P.gptq.speed;

  // ---------- 02 + 05 · snap real weights to the grid ----------
  const WV = D.weights.values;
  function quant(vals, bits) {                        // asymmetric min-max rounding (as in GPTQ/AWQ)
    const maxq = 2 ** bits - 1, lo = Math.min(0, ...vals), hi = Math.max(0, ...vals);
    const scale = Math.max((hi - lo) / maxq, 1e-8), zero = Math.round(-lo / scale);
    return { q: vals.map((w) => scale * (Math.min(maxq, Math.max(0, Math.round(w / scale) + zero)) - zero)),
             levels: Array.from({ length: maxq + 1 }, (_, k) => scale * (k - zero)) };
  }
  function snap(el, bits, group) {
    const W = 720, H = 300, pad = 24, lo = Math.min(...WV), hi = Math.max(...WV), span = hi - lo;
    const sy = (v) => pad + (1 - (v - lo + span * 0.08) / (span * 1.16)) * (H - 2 * pad), sx = (i) => 30 + (i + 0.5) * ((W - 50) / WV.length);
    const svg = chart(el, W, H), out = [];
    for (let g = 0; g < WV.length; g += group) {
      const part = WV.slice(g, g + group), r = quant(part, bits), xa = sx(g) - 10, xb = sx(g + part.length - 1) + 10;
      if (r.levels.length <= 64) r.levels.forEach((l) => S('line', { x1: xa, x2: xb, y1: sy(l), y2: sy(l), stroke: '#34343e', 'stroke-width': 1 }, svg));
      else S('rect', { x: xa, y: sy(Math.max(...r.levels)), width: xb - xa, height: sy(Math.min(...r.levels)) - sy(Math.max(...r.levels)), fill: '#1e1e25' }, svg);
      if (group < WV.length && g + group < WV.length) S('line', { x1: xb + 4, x2: xb + 4, y1: pad, y2: H - pad, stroke: '#4a4a55', 'stroke-dasharray': '3 5' }, svg);
      out.push(...r.q);
    }
    S('line', { x1: 20, x2: W - 10, y1: sy(0), y2: sy(0), stroke: '#55555f', 'stroke-width': 1.2 }, svg);
    let err = 0, zero = 0;
    WV.forEach((w, i) => {
      const q = out[i], crushed = q === 0 && w !== 0;
      err += Math.abs(w - q); zero += crushed;
      S('line', { x1: sx(i), x2: sx(i), y1: sy(w), y2: sy(q), stroke: C.dim, 'stroke-width': 1 }, svg);
      S('circle', { cx: sx(i), cy: sy(w), r: 5, fill: C.blue }, svg);
      S('circle', { cx: sx(i), cy: sy(q), r: 4, fill: crushed ? C.red : C.yellow }, svg);
    });
    const meanAbs = WV.reduce((a, w) => a + Math.abs(w), 0) / WV.length;
    return { err: `${Math.round((err / WV.length / meanAbs) * 100)}%`, zero: `${zero} / ${WV.length}` };
  }
  function drawSnap() {
    const bits = +$('#bits').value, r = snap($('#snapChart'), bits, 32);
    $('#bitsOut').textContent = bits; $('#snapLevels').textContent = 2 ** bits;
    $('#snapErr').textContent = r.err; $('#snapZero').textContent = r.zero;
  }
  $('#bits').addEventListener('input', drawSnap);
  drawSnap();
  const absW = WV.map(Math.abs).sort((a, b) => a - b);
  $('#snapNote').textContent = `${D.weights.src}. The biggest is ${Math.round(absW.at(-1) / absW[absW.length >> 1])}× the median. Slide down to 4 bits and watch the small ones collapse.`;

  function drawGrp(g) {
    const r = snap($('#grpChart'), 3, g);
    $('#grpErr').textContent = r.err; $('#grpZero').textContent = r.zero;
    $('#grpOver').textContent = `+${(32 / g).toFixed(g >= 16 ? 1 : 0)} bits/weight`;
    $('#grpBadge').textContent = `${32 / g} scale${g === 32 ? '' : 's'} for 32 weights`;
  }
  segs($('#grpBtns'), (d) => drawGrp(+d.g));
  drawGrp(32);
  const GG = P.gptq_groups;
  $('#grpTable').innerHTML = `<tr><th>3-bit GPTQ, scale shared by</th><th>Extra bits</th><th>OPT-175B</th><th>BLOOM-176B</th></tr>` +
    GG.rows.map((r) => `<tr><td>${r.label}</td><td class="num">${r.extra}</td><td class="num">${r.opt}</td><td class="num">${r.bloom}</td></tr>`).join('') +
    `<tr><td class="muted">16-bit original</td><td></td><td class="num muted">${GG.fp16.opt}</td><td class="num muted">${GG.fp16.bloom}</td></tr>`;
  $('#grpTableNote').textContent = `${GG.src}. At 3 bits, groups of 128 recover most of what is left for ≈0.15 extra bits per weight.`;

  // ---------- 04 · the cliff (GPTQ Table 3) ----------
  const O = P.gptq_opt;
  const logY = (lo, hi, top, bot) => (v) => bot - ((Math.log10(v) - Math.log10(lo)) / (Math.log10(hi) - Math.log10(lo))) * (bot - top);
  function drawCliff() {
    const k = +$('#size').value, W = 720, H = 300, top = 20, bot = 262, x0 = 70;
    const sy = logY(5, 30000, top, bot), bw = (W - x0 - 20) / O.sizes.length;
    const svg = chart($('#cliffChart'), W, H);
    [10, 100, 1000, 10000].forEach((v) => {
      S('line', { x1: x0 - 6, x2: W - 10, y1: sy(v), y2: sy(v), stroke: C.line }, svg);
      text(svg, x0 - 10, sy(v) + 4, v.toLocaleString('en-US'), { 'text-anchor': 'end' });
    });
    O.sizes.forEach((s, i) => {
      const x = x0 + i * bw, sel = i === k;
      if (sel) S('rect', { x: x + 2, y: top - 10, width: bw - 4, height: bot - top + 10, rx: 8, fill: '#1e1e25' }, svg);
      [[O.fp16[i], C.dim], [O.rtn4[i], C.yellow], [O.rtn3[i], C.red]].forEach(([v, col], j) => {
        const bx = x + 8 + j * ((bw - 16) / 3);
        S('rect', { x: bx, y: sy(v), width: (bw - 16) / 3 - 2, height: bot - sy(v), fill: col, 'fill-opacity': sel ? 1 : 0.45, rx: 2 }, svg);
      });
      text(svg, x + bw / 2, H - 14, s, { 'text-anchor': 'middle', fill: sel ? C.ink : C.dim, 'font-size': 12 });
    });
    const r4 = O.rtn4[k] / O.fp16[k], r3 = O.rtn3[k] / O.fp16[k];
    $('#sizeOut').textContent = `OPT-${O.sizes[k]}`;
    $('#cliff4').textContent = r4 < 1.3 ? `+${Math.round((r4 - 1) * 100)}%` : `${r4.toFixed(1)}×`;
    $('#cliff3').textContent = `${Math.round(r3).toLocaleString('en-US')}×`;
    const b = $('#cliffBadge');
    b.className = 'badge bad'; b.textContent = `3-bit: ${f2(O.fp16[k])} → ${f2(O.rtn3[k])}`;
  }
  $('#size').addEventListener('input', drawCliff);
  drawCliff();
  $('#cliffNote').textContent = `${O.src}. Log scale. 4-bit plain rounding costs something at every size (and breaks OPT-66B). 3-bit breaks them all.`;

  // ---------- 06 · outliers (illustrative) + keep 1% (AWQ Table 1) ----------
  const IC = D.illustrative_channels;
  function bars(el, vals, col, H = 120, top = null) {
    const W = 720, n = vals.length, mx = top ?? Math.max(...vals), bw = (W - 20) / n, svg = chart(el, W, H);
    vals.forEach((v, i) => { const h = Math.max(1, (v / mx) * (H - 12)); S('rect', { x: 10 + i * bw, y: H - 4 - h, width: Math.max(bw - 0.6, 0.8), height: h, fill: col }, svg); });
  }
  const topAll = Math.max(...IC.act);
  bars($('#actChart'), IC.act, C.yellow, 120, topAll);
  bars($('#wChart'), IC.w, C.blue, 120);
  const K = P.awq_keep;
  function drawKeep(m) {
    const row = (lab, arr, cls = '') => `<tr><td>${lab}</td>${['0.1%', '1%', '3%'].map((f) => `<td class="num ${cls}">${f2(arr[f][m])}</td>`).join('')}</tr>`;
    $('#keepTable').innerHTML = `<tr><th>Which channels stay 16-bit</th><th>0.1%</th><th>1%</th><th>3%</th></tr>
      <tr><td>none (plain 3-bit RTN)</td><td class="num red" colspan="3">${f2(K.rtn[m])}</td></tr>` +
      row('biggest <b class="yellow">activations</b>', K.act, 'yellow') + row('biggest weights', K.weight) + row('random', K.random) +
      `<tr><td class="muted">16-bit original</td><td class="num muted" colspan="3">${f2(K.fp16[m])}</td></tr>`;
  }
  segs($('#keepBtns'), (d) => drawKeep(+d.m));
  drawKeep(1);
  $('#keepNote').textContent = `${K.src}. Picking by activation brings 3-bit close to 16-bit; picking by weight size or at random barely helps.`;

  // ---------- 07 · methods (AWQ Table 4) ----------
  const AL = P.awq_llama;
  function drawMethods() {
    const m = +on($('#mModel')).m, b = on($('#mBits')).b, M = AL[b], base = AL.fp16[m];
    const W = 720, H = 260, bot = 220, keys = [['rtn', 'RTN', C.red], ['gptq', 'GPTQ', C.blue], ['awq', 'AWQ', C.yellow]];
    const lo = base * 0.9, hi = Math.max(...keys.map(([k]) => M[k][m])) * 1.04, sy = (v) => bot - ((v - lo) / (hi - lo)) * (bot - 24);
    const svg = chart($('#methodChart'), W, H);
    keys.forEach(([k, l, col], i) => {
      const x = 120 + i * 180, v = M[k][m];
      S('rect', { x, y: sy(v), width: 110, height: bot - sy(v), rx: 6, fill: col, 'fill-opacity': 0.85 }, svg);
      text(svg, x + 55, sy(v) - 8, v.toFixed(2), { 'text-anchor': 'middle', fill: C.ink, 'font-size': 16 });
      text(svg, x + 55, bot + 22, l, { 'text-anchor': 'middle', fill: C.ink, 'font-size': 15 });
    });
    S('line', { x1: 90, x2: W - 40, y1: sy(base), y2: sy(base), stroke: C.dim, 'stroke-dasharray': '6 5', 'stroke-width': 1.5 }, svg);
    text(svg, W - 40, sy(base) - 6, `16-bit ${base.toFixed(2)}`, { 'text-anchor': 'end', 'font-size': 12 });
    const gap = (k) => M[k][m] - base;
    $('#methodNote').textContent = `${AL.src}. The y-axis starts near the 16-bit score to show the gaps. At ${b} bits AWQ closes ${Math.round((1 - gap('awq') / gap('rtn')) * 100)}% of RTN's gap to 16-bit on ${AL.models[m]}. ${AL.speed}.`;
  }
  segs($('#mModel'), drawMethods); segs($('#mBits'), drawMethods);
  drawMethods();

  // ---------- 08 · SmoothQuant α (illustrative channels) + Table 3 ----------
  const A = IC.act, Wm = IC.w;
  const median = (arr) => { const s = [...arr].sort((a, b) => a - b); return s[s.length >> 1]; };
  const ratio0 = Math.max(...A) / median(A);
  function drawSmooth() {
    const alpha = +$('#alpha').value / 20;
    const s = A.map((a, j) => Math.pow(a, alpha) / Math.pow(Wm[j], 1 - alpha));
    const xa = A.map((a, j) => a / s[j]), wa = Wm.map((w, j) => w * s[j]);
    const W = 720, H = 240, mid = 120, bw = (W - 20) / A.length, svg = chart($('#smChart'), W, H);
    const ma = Math.max(...xa), mw = Math.max(...wa);
    xa.forEach((v, i) => { const h = Math.max(1, (v / ma) * (mid - 10)); S('rect', { x: 10 + i * bw, y: mid - h, width: Math.max(bw - 0.6, 0.8), height: h, fill: C.yellow }, svg); });
    wa.forEach((v, i) => { const h = Math.max(1, (v / mw) * (mid - 10)); S('rect', { x: 10 + i * bw, y: mid + 2, width: Math.max(bw - 0.6, 0.8), height: h, fill: C.blue }, svg); });
    const ra = ma / median(xa), rw = mw / median(wa);
    $('#alphaOut').textContent = alpha.toFixed(2);
    $('#smA').textContent = `${ra.toFixed(1)}×`; $('#smW').textContent = `${rw.toFixed(1)}×`;
    const b = $('#smBadge'), balanced = Math.max(ra, rw) < 0.25 * ratio0;
    b.className = `badge ${alpha === 0 ? 'bad' : balanced ? 'good' : 'warn'}`;
    b.textContent = alpha === 0 ? 'No smoothing: activations hold all the outliers' : balanced ? '✓ Difficulty shared' : alpha > 0.8 ? 'Too far: now the weights are spiky' : 'Moving it…';
  }
  $('#alpha').addEventListener('input', drawSmooth);
  drawSmooth();
  const SQ = P.smoothquant;
  $('#w8Table').innerHTML = `<tr><th>OPT-175B, 8-bit weights + activations</th><th>Avg accuracy ↑</th><th>Perplexity ↓</th></tr>` +
    SQ.rows.map(([n, acc, p], i) => {
      const cls = i === 0 ? '' : acc > 60 ? 'green' : 'red';
      return `<tr><td>${n}</td><td class="num ${cls}">${acc}%</td><td class="num ${cls}">${f2(p)}</td></tr>`;
    }).join('');
  $('#w8Note').textContent = `${SQ.src}. Naive INT8 activations break a 175B model; SmoothQuant matches FP16 and is ${SQ.speed}.`;
})(window.LESSON);

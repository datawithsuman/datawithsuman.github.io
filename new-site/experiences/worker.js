// AIML Rounds interview experiences: a Cloudflare Worker + D1.
// Public:  GET  /v1/experiences?q=&family=&before=&limit=   approved posts, newest first; q = keyword search
//          POST /v1/experiences  {role, company?, body, token}         new post: Turnstile + rules.js → pending (or rejected)
//          POST /v1/report       {id}                        two different reporters send a post back to review
//          GET  /v1/export                                   every approved post (nightly backup)
// Clean-up (the 7 AM Claude routine, Bearer BOT_TOKEN):
//          GET  /bot/pending                                 posts waiting for clean-up
//          POST /bot/decide  {id, action, role?, family?, company?, body?, note?}   action: publish | reject | hold
// Owner:   GET  /admin, POST /admin/decide {id, action}      behind Cloudflare Access (JWT checked here too)
// Cron:    daily — clear connection hashes after 2 days, purge rejected posts after 30 days.

import { FAMILIES, moderate, normalise, normaliseRole, normaliseCompany, shingles, similarity, DUPLICATE_AT, SIMILAR_AT } from "./rules.js";

const json = (data, status = 200, headers = {}) =>
  new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json; charset=utf-8", ...headers } });

function cors(req, env) {
  const origin = req.headers.get("origin") || "";
  const allowed = (env.ALLOWED_ORIGINS || "https://aimlrounds.com").split(",").map((s) => s.trim());
  return allowed.includes(origin)
    ? { "access-control-allow-origin": origin, "access-control-allow-methods": "GET, POST, OPTIONS", "access-control-allow-headers": "content-type", vary: "origin" }
    : {};
}

async function sha256(s) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
const ipHash = (req, env) => sha256((env.HASH_SALT || "dev-salt") + "|" + (req.headers.get("cf-connecting-ip") || "local"));
const now = () => new Date().toISOString();
const shown = (r) => ({ id: r.id, role: r.role, family: r.family, company: r.company || "", body: r.body, date: r.created_at.slice(0, 10) });

async function verifyTurnstile(token, req, env) {
  if (!env.TURNSTILE_SECRET) return false;
  const form = new FormData();
  form.append("secret", env.TURNSTILE_SECRET);
  form.append("response", token || "");
  const ip = req.headers.get("cf-connecting-ip");
  if (ip) form.append("remoteip", ip);
  const r = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", { method: "POST", body: form });
  const out = await r.json().catch(() => ({}));
  return !!out.success;
}

// Turn free text into a safe FTS5 query: every word must appear, last word as a prefix ("embed" finds "embeddings").
function ftsQuery(q) {
  const words = normalise(q).split(" ").filter((w) => w.length > 1).slice(0, 8);
  if (!words.length) return "";
  return words.map((w, i) => `"${w}"${i === words.length - 1 ? "*" : ""}`).join(" ");
}

// ---------- public ----------
async function list(req, env, url) {
  const family = url.searchParams.get("family") || "";
  const q = ftsQuery(url.searchParams.get("q") || "");
  const before = parseInt(url.searchParams.get("before") || "0", 10);
  const limit = Math.min(30, Math.max(1, parseInt(url.searchParams.get("limit") || "20", 10)));
  if (family && !FAMILIES.includes(family)) return json({ error: "unknown family" }, 400);
  const where = ["p.status = 'approved'"], args = [];
  let from = "posts p";
  if (q) { from = "posts_fts f JOIN posts p ON p.id = f.rowid"; where.push("posts_fts MATCH ?"); args.push(q); }
  if (family) { where.push("p.family = ?"); args.push(family); }
  if (before > 0) { where.push("p.id < ?"); args.push(before); }
  const { results } = await env.DB.prepare(
    `SELECT p.id, p.role, p.family, p.company, p.body, p.created_at FROM ${from} WHERE ${where.join(" AND ")} ORDER BY p.id DESC LIMIT ?`
  ).bind(...args, limit + 1).all();
  const more = results.length > limit;
  const posts = results.slice(0, limit).map(shown);
  return json({ posts, next: more ? posts[posts.length - 1].id : null }, 200, { "cache-control": "public, max-age=60" });
}

async function create(req, env) {
  const data = await req.json().catch(() => null);
  if (!data) return json({ status: "rejected", message: "Something went wrong. Please try again." }, 400);
  if (!(await verifyTurnstile(data.token, req, env)))
    return json({ status: "rejected", message: "The bot check didn't pass. Please refresh the page and try again." }, 400);
  const rawRole = String(data.role || "").trim().slice(0, 200), rawCompany = String(data.company || "").trim().slice(0, 200), rawBody = String(data.body || "").trim();
  const ip = await ipHash(req, env);
  const norm = normalise(rawBody);
  const [normHash, prefixHash] = await Promise.all([sha256(norm), sha256(norm.slice(0, 300))]);
  const since = new Date(Date.now() - 864e5).toISOString();
  const fam = normaliseRole(rawRole).family || "Other", comp = normaliseCompany(rawCompany);
  const [today, dup, near, recent] = await env.DB.batch([
    env.DB.prepare("SELECT COUNT(*) AS n FROM posts WHERE ip_hash = ? AND created_at > ? AND status != 'rejected'").bind(ip, since),
    env.DB.prepare("SELECT 1 FROM posts WHERE norm_hash = ? AND status != 'rejected' LIMIT 1").bind(normHash),
    env.DB.prepare("SELECT 1 FROM posts WHERE prefix_hash = ? AND status != 'rejected' LIMIT 1").bind(prefixHash),
    // Close rewrites: compare with recent posts for the same role group or company.
    env.DB.prepare("SELECT raw_body FROM posts WHERE status != 'rejected' AND (family = ? OR (company != '' AND company = ?)) ORDER BY id DESC LIMIT 300").bind(fam, comp),
  ]);
  const mine = shingles(rawBody);
  const best = recent.results.reduce((m, r) => Math.max(m, similarity(mine, shingles(r.raw_body))), 0);
  const v = moderate(rawRole, rawBody, { postsToday: today.results[0].n, duplicate: dup.results.length > 0 || best >= DUPLICATE_AT, nearDuplicate: near.results.length > 0 || best >= SIMILAR_AT }, rawCompany);
  // Rejected posts keep only a short excerpt, for tuning the rules; they are purged after 30 days.
  const keep = v.status === "rejected" ? rawBody.slice(0, 500) : rawBody;
  await env.DB.prepare(
    "INSERT INTO posts (role_raw, role, family, company_raw, company, raw_body, body, status, reason, created_at, ip_hash, norm_hash, prefix_hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
  ).bind(rawRole, v.role.title || "Unknown", v.role.family || "Other", rawCompany, v.company || "", keep, v.status === "rejected" ? "" : v.body, v.status, v.reason, now(), ip, normHash, prefixHash).run();
  return json({ status: v.status, message: v.message }, v.status === "rejected" ? 422 : 200);
}

async function report(req, env) {
  const data = await req.json().catch(() => ({}));
  const id = parseInt(data.id, 10);
  if (!id) return json({ ok: false }, 400);
  const ip = await ipHash(req, env);
  const since = new Date(Date.now() - 864e5).toISOString();
  const recent = await env.DB.prepare("SELECT COUNT(*) AS n FROM reports WHERE ip_hash = ? AND created_at > ?").bind(ip, since).first();
  if (recent.n >= 10) return json({ ok: true }); // quietly ignore report floods
  await env.DB.prepare("INSERT OR IGNORE INTO reports (post_id, ip_hash, created_at) VALUES (?, ?, ?)").bind(id, ip, now()).run();
  const n = await env.DB.prepare("SELECT COUNT(*) AS n FROM reports WHERE post_id = ?").bind(id).first();
  if (n.n >= 2) await setStatus(env, id, "review", "reported by readers");
  return json({ ok: true });
}

async function exportAll(env) {
  const { results } = await env.DB.prepare("SELECT id, role, family, company, body, created_at FROM posts WHERE status = 'approved' ORDER BY id").all();
  return json({ exported: now(), count: results.length, posts: results.map(shown) });
}

// Status changes keep the search index in step: only approved posts are searchable.
async function setStatus(env, id, status, note, edits = {}) {
  const sets = ["status = ?", "decided_at = ?"], args = [status, now()];
  if (note !== undefined) { sets.push("reason = ?"); args.push(note); }
  for (const k of ["role", "family", "company", "body"]) if (edits[k] !== undefined && edits[k] !== null) { sets.push(`${k} = ?`); args.push(edits[k]); }
  const stmts = [
    env.DB.prepare(`UPDATE posts SET ${sets.join(", ")} WHERE id = ?`).bind(...args, id),
    env.DB.prepare("DELETE FROM posts_fts WHERE rowid = ?").bind(id),
  ];
  if (status === "approved") stmts.push(env.DB.prepare("INSERT INTO posts_fts (rowid, role, company, body) SELECT id, role, company, body FROM posts WHERE id = ?").bind(id));
  await env.DB.batch(stmts);
}

// ---------- clean-up routine (Bearer token) ----------
function isBot(req, env) {
  const auth = req.headers.get("authorization") || "";
  return !!env.BOT_TOKEN && auth === `Bearer ${env.BOT_TOKEN}`;
}
async function botPending(env) {
  const { results } = await env.DB.prepare(
    "SELECT id, role_raw, role, family, company_raw, company, raw_body, body AS rules_body, reason AS flags, created_at FROM posts WHERE status = 'pending' ORDER BY id LIMIT 200"
  ).all();
  // For each pending post, the most similar live posts, so the clean-up can reject repeats of the same interview.
  for (const p of results) {
    const { results: live } = await env.DB.prepare(
      "SELECT id, role, company, body FROM posts WHERE status = 'approved' AND (family = ? OR (company != '' AND company = ?)) ORDER BY id DESC LIMIT 300"
    ).bind(p.family, p.company).all();
    const mine = shingles(p.raw_body);
    p.similar_live_posts = live.map((r) => ({ id: r.id, role: r.role, company: r.company, overlap: +similarity(mine, shingles(r.body)).toFixed(2), body: r.body.slice(0, 1200) }))
      .filter((r) => r.overlap >= 0.05).sort((a, b) => b.overlap - a.overlap).slice(0, 5);
  }
  return json({ families: FAMILIES, count: results.length, posts: results });
}
async function botDecide(req, env) {
  const d = await req.json().catch(() => ({}));
  const id = parseInt(d.id, 10);
  const row = id && (await env.DB.prepare("SELECT status FROM posts WHERE id = ?").bind(id).first());
  if (!row) return json({ ok: false, error: "unknown id" }, 404);
  if (row.status !== "pending") return json({ ok: false, error: "not pending" }, 409);
  const note = String(d.note || "").slice(0, 300);
  if (d.action === "publish") {
    const body = String(d.body || "").trim(), role = String(d.role || "").trim().slice(0, 60);
    if (!body || body.length > 12000) return json({ ok: false, error: "body missing or too long" }, 400);
    if (d.family && !FAMILIES.includes(d.family)) return json({ ok: false, error: "unknown family" }, 400);
    await setStatus(env, id, "approved", note, { body, role: role || undefined, family: d.family, company: d.company === undefined ? undefined : String(d.company).trim().slice(0, 60) });
  } else if (d.action === "reject") await setStatus(env, id, "rejected", note || "rejected by clean-up");
  else if (d.action === "hold") await setStatus(env, id, "review", note || "held by clean-up");
  else return json({ ok: false, error: "action must be publish, reject or hold" }, 400);
  return json({ ok: true });
}

// ---------- owner (Cloudflare Access) ----------
const b64url = (s) => Uint8Array.from(atob(s.replace(/-/g, "+").replace(/_/g, "/") + "===".slice((s.length + 3) % 4)), (c) => c.charCodeAt(0));
let certs = null;
async function isOwner(req, env) {
  if (env.ADMIN_DEV === "1") return true; // local testing only, never set in production
  const token = req.headers.get("cf-access-jwt-assertion");
  if (!token || !env.ACCESS_TEAM || !env.ACCESS_AUD) return false;
  try {
    const [h, p, s] = token.split(".");
    const header = JSON.parse(new TextDecoder().decode(b64url(h)));
    const payload = JSON.parse(new TextDecoder().decode(b64url(p)));
    const iss = `https://${env.ACCESS_TEAM}.cloudflareaccess.com`;
    if (payload.iss !== iss || payload.exp * 1000 < Date.now()) return false;
    if (![].concat(payload.aud).includes(env.ACCESS_AUD)) return false;
    if (!certs || Date.now() - certs.at > 36e5) certs = { at: Date.now(), keys: (await (await fetch(iss + "/cdn-cgi/access/certs")).json()).keys };
    const jwk = certs.keys.find((k) => k.kid === header.kid);
    if (!jwk) return false;
    const key = await crypto.subtle.importKey("jwk", jwk, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["verify"]);
    return await crypto.subtle.verify("RSASSA-PKCS1-v1_5", key, b64url(s), new TextEncoder().encode(h + "." + p));
  } catch { return false; }
}

async function ownerDecide(req, env) {
  const { id, action } = await req.json().catch(() => ({}));
  if (action === "delete") await env.DB.batch([env.DB.prepare("DELETE FROM posts WHERE id = ?").bind(id), env.DB.prepare("DELETE FROM posts_fts WHERE rowid = ?").bind(id)]);
  else if (action === "approve") { await setStatus(env, id, "approved", ""); await env.DB.prepare("DELETE FROM reports WHERE post_id = ?").bind(id).run(); }
  else if (action === "reject") await setStatus(env, id, "rejected", "rejected by owner");
  else if (action === "hide") await setStatus(env, id, "review", "hidden by owner");
  else return json({ ok: false }, 400);
  return json({ ok: true });
}

async function adminPage(env, url) {
  const tabs = { review: "review", pending: "pending", live: "approved", rejected: "rejected" };
  const tab = tabs[url.searchParams.get("tab")] ? url.searchParams.get("tab") : "review";
  const { results } = await env.DB.prepare("SELECT id, role_raw, role, company_raw, company, raw_body, body, reason, created_at FROM posts WHERE status = ? ORDER BY id DESC LIMIT 100").bind(tabs[tab]).all();
  const counts = await env.DB.prepare("SELECT status, COUNT(*) AS n FROM posts GROUP BY status").all();
  const c = Object.fromEntries(counts.results.map((r) => [r.status, r.n]));
  const esc = (s) => String(s || "").replace(/[&<>"]/g, (m) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[m]));
  const buttons = { review: ["approve", "reject"], pending: ["approve", "reject"], live: ["hide", "delete"], rejected: ["approve", "delete"] }[tab];
  const rows = results.map((r) => `<article data-id="${r.id}"><header><b>${esc(r.role)}</b> <span class="dim">(typed: ${esc(r.role_raw)})</span>${r.company_raw ? ` · <b>${esc(r.company)}</b> <span class="dim">(typed: ${esc(r.company_raw)})</span>` : ""} · ${r.created_at.slice(0, 16).replace("T", " ")} UTC${r.reason ? ` · <span class="why">${esc(r.reason)}</span>` : ""}</header>
    <div class="cols"><div><h4>Shown</h4><p>${esc(r.body).replace(/\n/g, "<br>")}</p></div><div><h4>Original</h4><p>${esc(r.raw_body).replace(/\n/g, "<br>")}</p></div></div>
    <footer>${buttons.map((b) => `<button data-a="${b}">${b[0].toUpperCase() + b.slice(1)}</button>`).join("")}</footer></article>`).join("") || "<p>Nothing here.</p>";
  const nav = [["review", "Needs review", c.review], ["pending", "Waiting for 7 AM clean-up", c.pending], ["live", "Live", c.approved], ["rejected", "Rejected", c.rejected]]
    .map(([k, l, n]) => `<a href="?tab=${k}" class="${tab === k ? "on" : ""}">${l} (${n || 0})</a>`).join("");
  return new Response(`<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Experiences review</title>
<style>body{font:15px/1.55 system-ui,sans-serif;max-width:1000px;margin:0 auto;padding:20px 16px;background:#F5F6F8;color:#11141B}
nav{display:flex;flex-wrap:wrap;gap:6px 16px}nav a{font-weight:600;color:#4B5363}nav a.on{color:#11141B;text-decoration:underline}
article{background:#fff;border:1px solid #DDE1E8;border-radius:12px;padding:14px 16px;margin:12px 0}header{font-size:13px;color:#4B5363}.why{color:#B4540A}.dim{color:#7A8292}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:16px}@media(max-width:700px){.cols{grid-template-columns:1fr}}h4{margin:10px 0 4px;font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:#7A8292}
article p{margin:0}footer{display:flex;gap:8px;margin-top:10px}button{font:600 13px system-ui;padding:6px 14px;border-radius:8px;border:1px solid #C9CFD9;background:#fff;cursor:pointer}
button[data-a=approve]{background:#11141B;color:#fff;border-color:#11141B}button[data-a=delete],button[data-a=reject]{color:#B42318}</style>
<h1>Interview experiences</h1><nav>${nav}</nav>
${rows}
<script>document.addEventListener("click",async e=>{const b=e.target.closest("button[data-a]");if(!b)return;const a=b.closest("article");b.disabled=true;
const r=await fetch("/admin/decide",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({id:+a.dataset.id,action:b.dataset.a})});
if(r.ok)a.remove();else{b.disabled=false;b.textContent="Failed, retry";}});</script>`, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" } });
}

// ---------- router ----------
export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const path = url.pathname.replace(/\/+$/, "") || "/";
    const h = cors(req, env);
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: h });
    try {
      if (path.startsWith("/bot/")) {
        if (!isBot(req, env)) return json({ error: "not allowed" }, 403);
        if (path === "/bot/pending" && req.method === "GET") return botPending(env);
        if (path === "/bot/decide" && req.method === "POST") return botDecide(req, env);
        return json({ error: "not found" }, 404);
      }
      if (path === "/admin" || path === "/admin/decide") {
        if (!(await isOwner(req, env))) return new Response("Not allowed", { status: 403 });
        return path === "/admin" ? adminPage(env, url) : ownerDecide(req, env);
      }
      let res;
      if (path === "/v1/experiences" && req.method === "GET") res = await list(req, env, url);
      else if (path === "/v1/experiences" && req.method === "POST") res = await create(req, env);
      else if (path === "/v1/report" && req.method === "POST") res = await report(req, env);
      else if (path === "/v1/export" && req.method === "GET") res = await exportAll(env);
      else res = json({ error: "not found" }, 404);
      for (const [k, v] of Object.entries(h)) res.headers.set(k, v);
      return res;
    } catch (err) {
      console.error(err);
      return json({ error: "server error" }, 500, h);
    }
  },
  async scheduled(event, env) {
    const two = new Date(Date.now() - 2 * 864e5).toISOString(), thirty = new Date(Date.now() - 30 * 864e5).toISOString();
    await env.DB.batch([
      env.DB.prepare("UPDATE posts SET ip_hash = NULL WHERE ip_hash IS NOT NULL AND created_at < ?").bind(two),
      env.DB.prepare("DELETE FROM posts WHERE status = 'rejected' AND created_at < ?").bind(thirty),
      env.DB.prepare("UPDATE reports SET ip_hash = 'x' || rowid WHERE created_at < ? AND ip_hash NOT LIKE 'x%'").bind(two),
    ]);
  },
};

-- AIML Rounds interview experiences (Cloudflare D1).
-- status: pending  (passed the instant rules, waiting for the 7 AM Claude clean-up)
--         approved (cleaned and shown)
--         review   (held for the owner)
--         rejected (kept briefly for tuning the rules, then purged)
CREATE TABLE IF NOT EXISTS posts (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  role_raw    TEXT NOT NULL,          -- what the person typed
  role        TEXT NOT NULL,          -- cleaned title, e.g. "Senior ML Engineer"
  family      TEXT NOT NULL,          -- filter group, e.g. "ML Engineer"
  company_raw TEXT NOT NULL DEFAULT '', -- optional, what the person typed
  company     TEXT NOT NULL DEFAULT '', -- cleaned name, e.g. "Google"; empty if not given
  raw_body    TEXT NOT NULL,          -- what the person wrote (never shown; kept so a clean-up can be undone)
  body        TEXT NOT NULL,          -- the cleaned post that is shown
  status      TEXT NOT NULL,
  reason      TEXT,                   -- rule flags or the clean-up decision note
  created_at  TEXT NOT NULL,          -- ISO time, shown as the posted date
  decided_at  TEXT,
  ip_hash     TEXT,                   -- salted hash of the connection, for the daily post limit; cleared after 2 days
  norm_hash   TEXT,
  prefix_hash TEXT
);
CREATE INDEX IF NOT EXISTS posts_status_id ON posts (status, id DESC);
CREATE INDEX IF NOT EXISTS posts_family_status_id ON posts (family, status, id DESC);
CREATE INDEX IF NOT EXISTS posts_norm ON posts (norm_hash);
CREATE INDEX IF NOT EXISTS posts_prefix ON posts (prefix_hash);
CREATE INDEX IF NOT EXISTS posts_ip ON posts (ip_hash, created_at);

-- Keyword search over approved posts only. rowid = posts.id.
CREATE VIRTUAL TABLE IF NOT EXISTS posts_fts USING fts5(role, company, body, tokenize = 'porter unicode61');

CREATE TABLE IF NOT EXISTS reports (
  post_id    INTEGER NOT NULL,
  ip_hash    TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY (post_id, ip_hash)
);

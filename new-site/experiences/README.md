# Interview experiences

Anonymous AI/ML interview experiences: role + text, no accounts, no comments.

- `worker.js`: Cloudflare Worker at `https://experiences.aimlrounds.com` (list, post, report, export, review page).
- `rules.js`: the moderation rules. Edit word lists and limits here, then `npx wrangler deploy`.
- `schema.sql`: D1 tables.
- `backup.json`: approved posts, exported nightly by `.github/workflows/experiences-backup.yml`.
- Site pages: `build.py` → `experiences_pages()` writes `/experiences/` and `/experiences/share/`; browser code in `assets/experiences.js`.

## How a post flows

1. **Instant rules** (`rules.js`) when someone posts: free-text role is cleaned into a title + filter group,
   the text gets light clean-up (case, terms, rounds, punctuation), and spam or vague posts are rejected on the spot
   (bot check, links, emails, phones, promotion, gibberish, abuse, duplicates, daily limit, too vague, off topic).
   Everything else is saved as **pending** with flags.
2. **7 AM IST Claude clean-up** (scheduled Claude Code routine, instructions in `CLEANUP.md`): pulls pending posts
   with `bot.py pull`, tidies and formats each one without changing what it says, and publishes, rejects or holds it
   with `bot.py push`. The original text is kept in the database (`raw_body`) so a clean-up can be undone.
3. **You** check the held posts at `https://experiences.aimlrounds.com/admin` (behind Cloudflare Access).

Keyword search uses a D1 FTS5 index of approved posts only.

## First deploy (once)

    cd new-site/experiences
    npx wrangler login
    npx wrangler d1 create aimlrounds-experiences        # paste the database_id into wrangler.toml
    npx wrangler d1 execute aimlrounds-experiences --remote --file schema.sql
    npx wrangler secret put HASH_SALT                     # any long random string
    npx wrangler secret put TURNSTILE_SECRET              # from the Turnstile widget (dashboard)
    npx wrangler secret put BOT_TOKEN                     # long random string; the 7 AM routine sends it as EXP_BOT_TOKEN
    npx wrangler deploy

Dashboard steps:
1. **Turnstile** → add widget for `aimlrounds.com` → copy the site key into `TURNSTILE_SITEKEY` (build.py env or default)
   and the secret into `wrangler secret put TURNSTILE_SECRET`.
2. **Zero Trust → Access → Applications** → self-hosted app for `experiences.aimlrounds.com/admin*`, policy "Emails: your email".
   Copy the team name and the application's AUD tag into `ACCESS_TEAM` and `ACCESS_AUD` in `wrangler.toml`, then deploy again.

Then build the site with the real site key: `TURNSTILE_SITEKEY=... python3 new-site/build.py`, commit and push.

## Local test

    npx wrangler d1 execute aimlrounds-experiences --local --file schema.sql
    npx wrangler dev --local --port 8790 --var TURNSTILE_SECRET:1x0000000000000000000000000000000AA \
      --var ADMIN_DEV:1 --var ALLOWED_ORIGINS:http://localhost:8765 --var HASH_SALT:local --var BOT_TOKEN:local-bot-token
    EXPERIENCES_API=http://localhost:8790/ TURNSTILE_SITEKEY=1x00000000000000000000AA python3 new-site/build.py
    cd docs && python3 -m http.server 8765

The `1x000…` keys are Cloudflare's always-pass Turnstile test keys. Never set `ADMIN_DEV` in production.
Rebuild without those env vars before committing.

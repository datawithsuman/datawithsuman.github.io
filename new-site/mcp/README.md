# AIML Rounds MCP server

A Cloudflare Worker (`worker.js`, no dependencies) that serves the site's lessons, roadmaps, quizzes,
mock interviews and jobs to Claude and other MCP clients at `https://mcp.aimlrounds.com/mcp`.
It reads the files `build.py` publishes (`/api/v1/*`, `/jobs/jobs.json`), so every site build updates it.

Tools: search, browse, get_lesson, roadmap, quiz, mock_interview, jobs, whats_new.
Prompts: mock_interview, study_topic, study_plan, job_prep.

Deploy (from this folder):

    npx wrangler login
    npx wrangler deploy

Local test: build the site, serve `docs/` on port 8765, then
`npx wrangler dev --var DATA_BASE:http://127.0.0.1:8765/` and POST JSON-RPC to http://localhost:8787/mcp.

## Official listing (MCP Registry)

`server.json` lists this server in the official MCP Registry as `com.aimlrounds/aimlrounds`.
Names under `com.aimlrounds/` can only be published by whoever proves control of aimlrounds.com,
so nobody else can publish under the site's name.

Proof is the public key in `mcp-registry-auth`, which `build.py` publishes at
`https://aimlrounds.com/.well-known/mcp-registry-auth`. The private key lives only at
`~/.config/aimlrounds/mcp-registry-key.pem`: never commit it, and back it up (a password manager is fine).
If it's lost, make a new pair, replace `mcp-registry-auth`, rebuild and push.

Published 19 Nov 2026 as version 1.0.0. To publish again (after the worker is deployed and the site is pushed):

    brew install mcp-publisher
    curl -sS -A 'mcp-registry/1.0' -H 'Accept: text/plain' https://aimlrounds.com/.well-known/mcp-registry-auth
    # raw 32-byte key as hex (works with OpenSSL 3 and 4; the docs' grep version breaks on OpenSSL 4)
    KEY="$(openssl pkey -in ~/.config/aimlrounds/mcp-registry-key.pem -outform DER | tail -c 32 | xxd -p -c 64)"
    mcp-publisher login http --domain aimlrounds.com --private-key "$KEY"
    mcp-publisher publish server.json

For each new release, bump `version` in `server.json` and publish again.
If the HTTP check fails, use DNS instead: add the line from `mcp-registry-auth` as a TXT record on
aimlrounds.com in Cloudflare, then `mcp-publisher login dns --domain aimlrounds.com --private-key "$KEY"`.

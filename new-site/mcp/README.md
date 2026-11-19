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

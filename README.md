# @datawithsuman: AI & ML, explained simply

Published at **https://datawithsuman.github.io/**. The interactive lessons are at **https://datawithsuman.github.io/ai/interview-prep/**.

Free, interactive lessons for AI/ML interview prep by **@datawithsuman**.

Each lesson is a short page you can play with: sliders, charts, quizzes and interview follow-ups.

## Tracks
- **LLM Inference**: how LLMs actually run (prefill vs decode, quantization, …)
- **ML Scenarios**: real interview scenarios, diagnosed step by step
- **ML System Design**: ML systems from an ML engineer's view
- **ML Papers Explained**: key papers, simply
- **GenAI & LLM Engineering**: RAG, agents, fine-tuning, evaluation
- **ML Fundamentals**: the core ideas every interview asks about

## How it's organised
- `index.html`: the site's landing page
- `ai/interview-prep/`: the lessons
  - `index.html`: lessons home (one card per track)
  - `<track>/index.html`: the track's numbered lesson list
  - `<track>/<lesson>/`: one lesson (`index.html`, `main.js`, `lesson.js`)
  - `lessons.js`: the single ordered list of tracks and lessons that drives the home page, track pages, breadcrumbs and Previous / Next
  - `kit/`: the shared dark theme, fonts and navigation

Plain static files: open `index.html` locally, or serve with GitHub Pages.

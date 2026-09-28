<div align="center">

# 🧠 AI & ML, explained simply

**Free, interactive lessons to understand AI/ML deeply and walk into interviews prepared.**

[![Start learning](https://img.shields.io/badge/▶_Start_learning-datawithsuman.github.io-F4D345?style=for-the-badge&labelColor=0f0f12)](https://datawithsuman.github.io/ai/interview-prep/)

![Lessons](https://img.shields.io/badge/lessons-2-58C4DD?labelColor=0f0f12)
![Tracks](https://img.shields.io/badge/tracks-6-58C4DD?labelColor=0f0f12)
![Price](https://img.shields.io/badge/price-free-83C167?labelColor=0f0f12)

by **@datawithsuman**

</div>

---

## ✨ What is this?

Short, visual lessons you can **play with**, not just read. Every lesson has:

- 🎛️ **Interactive labs**: sliders, toggles and live charts
- ❓ **A quick quiz** to test the key idea
- 🧭 **Step-by-step recipes** for real-world use
- 🎤 **Interview follow-ups** with crisp answers
- 🎬 **A short Reel** version on Instagram and YouTube

Pick a track and go in order. Each lesson takes about 10 minutes.

---

## 🗺️ Tracks

| Track | What you'll learn | Lessons |
|---|---|:---:|
| 🚀 [**LLM Inference**](https://datawithsuman.github.io/ai/interview-prep/llm-inference/) | How LLMs actually run: speed, memory, and the tricks that make serving fast and cheap | 2 |
| 🩺 [**ML Scenarios**](https://datawithsuman.github.io/ai/interview-prep/ml-scenarios/) | Real interview scenarios: your model does X, what do you do? | Soon |
| 🏗️ [**ML System Design**](https://datawithsuman.github.io/ai/interview-prep/ml-system-design/) | ML systems from an ML engineer's view: data, features, serving, monitoring | Soon |
| 📄 [**ML Papers Explained**](https://datawithsuman.github.io/ai/interview-prep/ml-papers/) | The idea and the key result of important papers | Soon |
| 🤖 [**GenAI & LLM Engineering**](https://datawithsuman.github.io/ai/interview-prep/genai-engineering/) | Building with LLMs: RAG, agents, fine-tuning, evaluation | Soon |
| 📐 [**ML Fundamentals**](https://datawithsuman.github.io/ai/interview-prep/ml-fundamentals/) | The core ideas every AI/ML interview still asks about | Soon |

---

## 📚 Lessons

### 🚀 LLM Inference

| # | Lesson | The question it answers | Level | Time |
|:---:|---|---|:---:|:---:|
| 1 | [**Prefill vs Decode**](https://datawithsuman.github.io/ai/interview-prep/llm-inference/prefill-vs-decode/) | Why does an LLM read your prompt fast but write its answer slowly? | 🟢 Beginner | 8 min |
| 2 | [**LLM Quantization**](https://datawithsuman.github.io/ai/interview-prep/llm-inference/llm-quantization/) | How does an LLM survive losing 75% of its bits? | 🟡 Intermediate | 12 min |

<details>
<summary><b>🔜 Coming soon in other tracks</b></summary>

<br>

New lessons land every week across **ML Scenarios**, **ML System Design**, **ML Papers Explained**, **GenAI & LLM Engineering** and **ML Fundamentals**. ⭐ Star this repo to follow along.

</details>

---

## 🎯 Who is this for?

- **Preparing for AI/ML or ML engineering interviews** and want intuition, not just definitions
- **Engineers moving into GenAI / LLM work** who want to understand what happens under the hood
- **Anyone who learns better by seeing and trying** than by reading dense papers

---

## 💬 Found a mistake or want a topic?

[Open an issue](https://github.com/datawithsuman/datawithsuman.github.io/issues). Corrections and topic requests are very welcome.

---

<details>
<summary><b>🛠️ For developers: how this repo is organised</b></summary>

<br>

Plain static files served by GitHub Pages. No build step, no tracking.

```
datawithsuman.github.io/
├── index.html                  landing page
└── ai/interview-prep/          the lessons
    ├── index.html              lessons home (one card per track)
    ├── lessons.js              ordered list of tracks + lessons (drives every menu)
    ├── kit/                    shared dark theme, fonts, navigation
    └── <track>/
        ├── index.html          numbered lesson list
        └── <lesson>/           index.html · main.js · lesson.js
```

**Run locally:** clone the repo and open `index.html` in a browser. Everything works offline.

**Add a lesson:** add its folder under a track, then one entry in `lessons.js`. The menus, numbering and Previous/Next update automatically. (Update the tables in this README too.)

</details>

<div align="center">

**If a lesson helped you, ⭐ star the repo and share it with a friend who's prepping.**

@datawithsuman · AI & ML, explained simply

</div>

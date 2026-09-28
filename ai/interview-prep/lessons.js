// The single list of tracks and lessons, in order. The home page, track pages, breadcrumbs and
// Previous / Next buttons are all built from this. To add a lesson: add its folder, then one line here.
// Addresses use the slug (never the number), so shared links keep working when lessons are reordered.
window.LESSONS = {
  tracks: [
    { id: 'llm-inference', title: 'LLM Inference', desc: 'How LLMs actually run: speed, memory, and the tricks that make serving fast and cheap.', lessons: [
      { slug: 'prefill-vs-decode', title: 'Prefill vs Decode', sub: 'Why does an LLM read your prompt fast but write its answer slowly?', level: 'Beginner', mins: 8 },
      { slug: 'llm-quantization', title: 'LLM Quantization', sub: 'How does an LLM survive losing 75% of its bits?', level: 'Intermediate', mins: 12 },
    ] },
    { id: 'ml-scenarios', title: 'ML Scenarios', prefix: 'Q', desc: 'Real interview scenarios: your model does X, what do you do? Diagnose first, then fix.', lessons: [] },
    { id: 'ml-system-design', title: 'ML System Design', desc: 'ML systems from an ML engineer\'s view: data, features, serving, monitoring and trade-offs.', lessons: [] },
    { id: 'ml-papers', title: 'ML Papers Explained', desc: 'The idea and the key result of important papers, explained simply.', lessons: [] },
    { id: 'genai-engineering', title: 'GenAI & LLM Engineering', desc: 'Building with LLMs in practice: RAG, agents, fine-tuning and evaluation.', lessons: [] },
    { id: 'ml-fundamentals', title: 'ML Fundamentals', desc: 'The core ideas every AI/ML interview still asks about.', lessons: [] },
  ],
};

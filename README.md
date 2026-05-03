# 🎯 Placement Prep Assistant

> **An AI-powered study companion for technical placement interviews — built with RAG, Groq LLM, local HuggingFace embeddings, and a premium Streamlit UI.**

---

## 🚀 What It Does

The **Placement Prep Assistant** is a Retrieval-Augmented Generation (RAG) chatbot that helps you prepare for technical interviews. Ask any question on **DSA, DBMS, OS, OOP, or Machine Learning** and get a structured, interview-ready answer.

Key behaviours:
- Answers are grounded in a curated 24-topic knowledge base stored as FAISS vectors
- A **hybrid routing engine** automatically decides whether to use the knowledge base, blend it with general LLM knowledge, or fall back to pure LLM when the query is outside the corpus
- Real-time **learning links** are fetched via Tavily web search and appended to every answer
- The UI never exposes internal retrieval mechanics — the assistant speaks like a confident tutor, not a search engine

---

## 🏗️ Project Structure

```
Placement Prep Assistant/
├── app.py                     # Streamlit UI (dark glassmorphism theme)
├── rag_pipeline.py            # Core RAG logic — loading, chunking, retrieval, routing
├── tavily_search.py           # Tavily web-search helper (learning links)
├── requirements.txt           # Python dependencies
├── .env                       # API keys (not committed)
├── README.md                  # This file
│
├── data/                      # 24 curated study-note files (.txt)
│   ├── data_structures.txt
│   ├── arrays.txt
│   ├── linked_list.txt
│   ├── stack_queue.txt
│   ├── trees.txt
│   ├── graphs.txt
│   ├── dynamic_programming.txt
│   ├── recursion.txt
│   ├── sorting_searching.txt
│   ├── dbms.txt
│   ├── dbms_basics.txt
│   ├── normalization.txt
│   ├── indexing.txt
│   ├── transactions.txt
│   ├── sql.txt
│   ├── os_processes.txt
│   ├── os_threads.txt
│   ├── os_deadlocks.txt
│   ├── os_scheduling.txt
│   ├── oops.txt
│   ├── machine_learning.txt
│   ├── ml_basics.txt
│   ├── ml_algorithms.txt
│   └── ml_overfitting_bias_variance.txt
│
└── vector_store/              # FAISS index (auto-created on first run)
    └── faiss_index
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | Groq — `llama-3.3-70b-versatile` (fast inference, free tier) |
| **Embeddings** | HuggingFace `all-MiniLM-L6-v2` (runs fully offline, no API key) |
| **Vector DB** | FAISS (local, in-memory, persisted to disk) |
| **RAG Framework** | LangChain (text splitters, prompts, chains) |
| **Web Search** | Tavily API (real-time learning links) |
| **UI** | Streamlit with custom CSS (dark mode, glassmorphism) |

---

## 📋 Prerequisites

- Python 3.9+
- **Groq API key** — free at [console.groq.com](https://console.groq.com)
- **Tavily API key** *(optional)* — free at [tavily.com](https://tavily.com) — learning links are silently skipped if missing

---

## 🚀 Quick Start

### 1. Create & activate a virtual environment

```bash
python -m venv ragenv
# Windows
ragenv\Scripts\activate
# macOS / Linux
source ragenv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure your `.env`

```env
GROQ_API_KEY=your_groq_key_here
TAVILY_API_KEY=your_tavily_key_here   # optional
```

### 4. Run the app

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser. The FAISS index is built automatically on the first launch (~10–20 s).

---

## 🧠 How the RAG Pipeline Works

```
User Question
      │
      ▼
 [HuggingFace Embeddings]  ──  local, no API call
      │
      ▼
 [FAISS Similarity Search]  ── top-5 chunks, FAISS L2 distance
      │
      ▼
 [SHA-256 Deduplication]  ── remove near-duplicate chunks
      │
      ▼
 [Hybrid Router]
   ├── score ≤ 0.8  → RAG mode     (answer from knowledge base)
   ├── score ≤ 1.3  → Hybrid mode  (blend KB + general LLM)
   └── score > 1.3  → General mode (pure LLM)
      │
      ▼
 [Groq LLM — llama-3.3-70b]  ── structured answer generation
      │
      ▼
 [Meta-phrase Filter]  ── strips "based on the notes…" style leakage
      │
      ▼
 [Tavily Web Search]  ── 2–3 curated learning links
      │
      ▼
 [Streamlit UI]  ── answer + optional source chips + link cards
```

### Chunking Strategy

| Parameter | Value | Reason |
|---|---|---|
| `chunk_size` | 400 chars | Captures a complete idea without being too broad |
| `chunk_overlap` | 80 chars | ~20% overlap prevents ideas from being cut at boundaries |
| Min chunk length | 80 chars | Filters noise chunks that won't carry meaningful semantics |
| Separators | `\n\n → \n → . → ,` | Prefers paragraph/sentence splits |

---

## 📚 Knowledge Base — 24 Topics

### Data Structures & Algorithms
`data_structures` · `arrays` · `linked_list` · `stack_queue` · `trees` · `graphs` · `dynamic_programming` · `recursion` · `sorting_searching`

### Database Management Systems
`dbms` · `dbms_basics` · `normalization` · `indexing` · `transactions` · `sql`

### Operating Systems
`os_processes` · `os_threads` · `os_deadlocks` · `os_scheduling`

### Object-Oriented Programming
`oops`

### Machine Learning
`machine_learning` · `ml_basics` · `ml_algorithms` · `ml_overfitting_bias_variance`

---

## 🎨 UI Features

- **Dark glassmorphism theme** with Indigo/Violet gradient accents
- **Quick-pick buttons** — 8 one-click topic launchers
- **Status pill** — live indicator showing the knowledge base is ready
- **Source chips & expandable panels** — inspect which chunks were retrieved
- **Link cards** — clickable Tavily results (GFG, W3Schools, etc.)
- **Clear Chat** button in the sidebar
- Smooth `popIn` micro-animation on every chat bubble

---

## 🔧 Rebuilding the Vector Store

If you add or edit files in `data/`, rebuild the FAISS index:

```python
# In Python (or add a CLI flag in rag_pipeline.py)
rag = RAGPipeline(groq_api_key=os.getenv("GROQ_API_KEY"))
rag.initialize(rebuild_vector_store=True)
```

Or simply delete the `vector_store/` folder and restart the app — it will rebuild automatically.

---

## ⚡ Performance

| Operation | Time |
|---|---|
| First launch (builds FAISS index) | ~10–20 s |
| Subsequent launches (loads cached index) | < 1 s |
| Query response (retrieval + Groq LLM) | ~1–3 s |

---

## 🚨 Troubleshooting

| Problem | Fix |
|---|---|
| `GROQ_API_KEY missing` | Add key to `.env` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` in the active venv |
| Answers seem generic | Rebuild the vector store with `rebuild_vector_store=True` |
| Tavily links not showing | Add `TAVILY_API_KEY` to `.env` (optional feature) |
| Slow first launch | Normal — HuggingFace model downloads on first use |

---

## 🔄 Extending the Assistant

1. **Add a new topic** — drop a `.txt` file into `data/` and rebuild the index
2. **Change the LLM** — swap the `model=` parameter in `RAGPipeline.__init__` (any Groq-supported model works)
3. **Tune retrieval** — adjust `RAG_THRESHOLD` / `HYBRID_THRESHOLD` in `rag_pipeline.py`
4. **Add more quick-picks** — extend `QUICK_PROMPTS` list in `app.py`

---

## 📄 License

This project is provided as-is for educational purposes.

---

**Happy Learning! 🚀**

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

## Live App : https://placement-prep-assistant-aapptwyurpe5yl8rpealcph.streamlit.app/

---

## 🏗️ Project Structure

```
Placement Prep Assistant/
├── app.py                     # Streamlit UI (dark glassmorphism theme)
├── rag_pipeline.py            # Core RAG logic — loading, chunking, retrieval, routing
├── tavily_search.py           # Tavily web-search helper (learning links)
├── requirements.txt           # Python dependencies
├── .env                       # API keys for local dev (not committed)
├── README.md                  # This file
│
├── .streamlit/
│   ├── config.toml            # Dark theme + server settings
│   └── secrets.toml           # API keys for Streamlit Cloud (not committed)
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

Before you begin, make sure you have:

| Requirement | Details |
|---|---|
| **Python 3.9+** | Check with `python --version` |
| **pip** | Comes bundled with Python |
| **Git** | For cloning the repo |
| **Groq API key** | Free at [console.groq.com](https://console.groq.com) — required |
| **Tavily API key** | Free at [app.tavily.com](https://app.tavily.com) — optional (learning links) |
| **YouTube Data API v3 key** | Free via [Google Cloud Console](https://console.cloud.google.com/) — optional (video recommendations) |

---

## ⚙️ Local Setup Guide

### Step 1 — Clone the Repository

```bash
git clone https://github.com/<your-username>/placement-prep-assistant.git
cd "placement-prep-assistant"
```

### Step 2 — Create a Virtual Environment

It is strongly recommended to isolate dependencies in a virtual environment.

```bash
python -m venv ragenv
```

**Activate the environment:**

```bash
# Windows (Command Prompt)
ragenv\Scripts\activate.bat

# Windows (PowerShell)
ragenv\Scripts\Activate.ps1

# macOS / Linux
source ragenv/bin/activate
```

> You should see `(ragenv)` prepended to your terminal prompt once activated.

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `langchain`, `langchain-core`, `langchain-community`, `langchain-text-splitters`, `langchain-groq`
- `sentence-transformers` (HuggingFace embeddings — downloads `all-MiniLM-L6-v2` on first use, ~90 MB)
- `faiss-cpu` (local vector store)
- `streamlit`
- `python-dotenv`
- `tavily-python`

### Step 4 — Configure API Keys

Create a `.env` file in the project root. You can copy the example below:

```bash
# Windows (PowerShell)
Copy-Item .env.example .env   # if an example file exists, otherwise create manually
```

Open `.env` and fill in your keys:

```env
# Required
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional — learning links are silently skipped if not provided
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional — YouTube video recommendations
YOUTUBE_API_KEY=AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> **Note:** The `.env` file is listed in `.gitignore` and will never be committed.

### Step 5 — Run the App

```bash
streamlit run app.py
```

Open **[http://localhost:8501](http://localhost:8501)** in your browser.

> **First launch:** The HuggingFace embedding model (~90 MB) is downloaded automatically and the FAISS index is built from the `data/` files. This takes **10–20 seconds**. Subsequent launches load the cached index in **< 1 second**.

---

## ☁️ Streamlit Cloud Deployment

### Step 1 — Push to GitHub

Make sure your repository is public (or private with Streamlit Community Cloud access).

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

> **Important:** Ensure `.env` and `.streamlit/secrets.toml` are listed in `.gitignore` before pushing.

### Step 2 — Add Secrets on Streamlit Cloud

On [share.streamlit.io](https://share.streamlit.io), after creating your app:

1. Go to **App settings → Secrets**
2. Paste the following block and substitute your actual keys:

```toml
GROQ_API_KEY     = "gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TAVILY_API_KEY   = "tvly-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
YOUTUBE_API_KEY  = "AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

Streamlit Cloud injects these as environment variables — no `.env` file is needed.

### Step 3 — Deploy

Click **Deploy** and wait for the build to complete. The FAISS index will be built on the first cold start.

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

**Option A — Python snippet:**
```python
import os
from rag_pipeline import RAGPipeline

rag = RAGPipeline(groq_api_key=os.getenv("GROQ_API_KEY"))
rag.initialize(rebuild_vector_store=True)
```

**Option B — Delete and restart:**
```bash
# Windows (PowerShell)
Remove-Item -Recurse -Force vector_store

# macOS / Linux
rm -rf vector_store/
```
Then run `streamlit run app.py` — the index rebuilds automatically.

---

## ⚡ Performance

| Operation | Time |
|---|---|
| First launch (builds FAISS index + downloads model) | ~10–20 s |
| Subsequent launches (loads cached index) | < 1 s |
| Query response (retrieval + Groq LLM) | ~1–3 s |

---

## 🚨 Troubleshooting

| Problem | Fix |
|---|---|
| `GROQ_API_KEY missing` or `AuthenticationError` | Add your key to `.env` (local) or Streamlit Secrets (cloud) |
| `ModuleNotFoundError` | Activate the venv first, then run `pip install -r requirements.txt` |
| PowerShell says "cannot be loaded because running scripts is disabled" | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` and retry |
| Answers seem generic / off-topic | Rebuild the vector store (see above) |
| Tavily links not showing | Add `TAVILY_API_KEY` to `.env` — it's optional but enables learning links |
| YouTube recommendations missing | Add `YOUTUBE_API_KEY` to `.env` — optional feature |
| Slow first launch | Normal — `all-MiniLM-L6-v2` (~90 MB) downloads on first use |
| `faiss` install fails on Windows | Use `pip install faiss-cpu` explicitly; avoid `faiss-gpu` unless you have CUDA |
| Port 8501 already in use | Run `streamlit run app.py --server.port 8502` |

---

## 🔄 Extending the Assistant

1. **Add a new topic** — drop a `.txt` file into `data/` and rebuild the index
2. **Change the LLM** — swap the `model=` parameter in `RAGPipeline.__init__` (any Groq-supported model works)
3. **Tune retrieval** — adjust `RAG_THRESHOLD` / `HYBRID_THRESHOLD` in `rag_pipeline.py`
4. **Add more quick-picks** — extend `QUICK_PROMPTS` list in `app.py`

---

## 🔑 API Key Reference

| Key | Where to Get | Required? |
|---|---|---|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) — free tier, no credit card | ✅ Yes |
| `TAVILY_API_KEY` | [app.tavily.com](https://app.tavily.com) — 1000 free searches/month | ⚪ Optional |
| `YOUTUBE_API_KEY` | [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → YouTube Data API v3 | ⚪ Optional |

---

## 📄 License

This project is provided as-is for educational purposes.

---

**Happy Learning! 🚀**

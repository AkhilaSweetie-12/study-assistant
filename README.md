# 🧠 AI Study & Code Documentation Assistant

A RAG (Retrieval-Augmented Generation) application built with **Azure OpenAI** and **Azure AI Search**, providing two modes in a single Gradio UI:

| Mode | What it does |
|---|---|
| 📚 **Study Assistant** | Upload PDFs/notes → ask questions, generate quizzes & summaries |
| 💻 **Code Docs Search** | Upload source code/docs → semantic search with code-aware answers |

---

## Architecture

```
Data Sources (PDF / Code / Markdown)
        │
        ▼
  Text Chunking  (processor.py)
        │
        ▼
  Embedding Model  ──────────────────────► Azure OpenAI
  (text-embedding-ada-002)                 (text-embedding-ada-002)
        │
        ▼
  Vector Store  ─────────────────────────► Azure AI Search
  (Hybrid: vector + keyword)               (two indexes)
        │
   User Query ──► Embedding ──► Top-K Retrieval
                                      │
                                      ▼
                               Azure OpenAI GPT-4o
                                      │
                                      ▼
                              AI-Powered Response
```

---

## Setup

### 1. Azure Resources Required

- **Azure OpenAI** — deploy `gpt-4o` (chat) and `text-embedding-ada-002` (embeddings)
- **Azure AI Search** — any tier (Free works for testing)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Fill in your Azure credentials in .env
```

### 4. Run

```bash
python app.py
```

Open `http://localhost:7860` in your browser.

---

## Project Structure

```
study-assistant/
├── app.py                    # Gradio UI + event handlers
├── config.py                 # Environment config
├── requirements.txt
├── .env.example
├── indexing/
│   └── processor.py          # PDF/code loading + text chunking
├── search/
│   └── azure_search.py       # Azure AI Search index + hybrid search
└── llm/
    └── azure_openai.py       # Embeddings + RAG prompts + quiz/summary generation
```

---

## Features

### Study Assistant
- Upload **PDF, TXT, MD** study materials
- Chat to get answers grounded in your materials
- **Quiz Generator** — 5 MCQs on any topic from indexed content
- **Topic Summary** — bullet-point summary of any topic

### Code Documentation Search
- Upload **Python, JS, TS, Java, C#, Go, Rust, Markdown, YAML, JSON**
- Ask natural language questions ("How does auth work?")
- Responses cite specific filenames and include relevant code snippets
- Hybrid search (vector + keyword) for precise retrieval

---

## Tuning

| Parameter | Default | Effect |
|---|---|---|
| `CHUNK_SIZE` | 1000 | Larger = more context per chunk, fewer chunks |
| `CHUNK_OVERLAP` | 200 | Prevents context loss at chunk boundaries |
| `TOP_K` | 5 | Number of chunks passed to GPT-4o |

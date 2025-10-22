# Kaikei - Accounting Application

Kaikei is a desktop-first accounting application inspired by popular Japanese bookkeeping tools. It features a PyQt6 user interface and a FastAPI backend so the app can evolve from a local workflow into a cloud-ready accounting service.

## Features
- Journal entry screen with table-based data entry similar to traditional accounting software
- FastAPI backend providing journal, account, and automation APIs
- SQLAlchemy models with SQLite for local storage
- Abstractions for future integrations such as banking connectors, APScheduler jobs, and AI-powered journal suggestions

## Getting Started
1. Create a virtual environment and install requirements
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run the FastAPI server
   ```bash
   uvicorn backend.api.main:app --reload
   ```
3. Launch the desktop client
   ```bash
   python main.py
   ```

The UI communicates with the backend via HTTP, making it possible to swap the desktop interface with a web frontend in the future without redesigning the backend.

## Local LLM (Ollama/LM Studio)
- The app can use a local LLM to suggest debit/credit accounts when calling `POST /api/auto_journal`.
- It expects an OpenAI-compatible API (e.g., Ollama, LM Studio) running locally.

### Configure
1. Install and run an OpenAI-compatible local server:
   - Ollama: https://ollama.com
     - Start the server and pull a model, for example:
       ```bash
       ollama pull llama3.1:8b
       ```
     - The default API base is `http://127.0.0.1:11434/v1`.
   - LM Studio: enable the local server and note the base URL and model.

2. Create `.env` (next to `requirements.txt`) and set:
   ```env
   AI_MODE=llm
   LLM_BASE_URL=http://127.0.0.1:11434/v1
   LLM_MODEL=llama3.1:8b
   # LLM_API_KEY=your_key_if_required
   ```

3. Start the backend:
   ```bash
   uvicorn backend.api.main:app --reload
   ```

When `AI_MODE=llm`, the `/api/auto_journal` endpoint will call the local LLM with the chart of accounts and the provided summary, then map the chosen account codes back to their IDs.

## ScanSnap OCR Auto-Posting
- Automatically imports receipts/invoices recognized by ScanSnap Home (XML output) and posts journals.

### How it works
- APScheduler watches a folder for new `*.xml` files.
- XML is parsed (`Date`, `Vendor`, `Amount`, `TaxIncluded`).
- AI classifier suggests debit/credit; journal is saved via SQLAlchemy.
- Manual upload is available at `POST /api/scan/import`.

### Configure
Add to `.env`:
```env
SCANSNAP_FOLDER=C:/Users/USER/Documents/ScanSnap Home/
SCANSNAP_POLL_MINUTES=3
```

The scheduler starts with the API server and scans every 3 minutes by default.

### Manual Upload API
```bash
curl -F file=@sample.xml http://127.0.0.1:8000/api/scan/import
```

## Multi-Tenant (Clients)
- Manage multiple clients with separate ScanSnap folders and journal history.

### Configure clients (.env)
```env
CLIENTS=A001,B002
SCANSNAP_FOLDER_A001=C:/ScanSnap/ClientA/
SCANSNAP_FOLDER_B002=D:/ScanSnap/ClientB/
```

Create `Client` rows in the database with `code` and `api_key`. API calls include `X-Client-Key`:
```bash
curl -H "X-Client-Key: <api_key>" http://127.0.0.1:8000/api/journal
```

- Scheduler watches each folder and posts XMLs with the corresponding `client_code`.
- LLM few-shot examples are filtered by `client_id` when suggesting accounts.

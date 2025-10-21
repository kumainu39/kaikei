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

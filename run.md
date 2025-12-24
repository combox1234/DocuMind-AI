# DocuMind AI - Run Guide

## Project Overview
**DocuMind AI** is an advanced, privacy-focused RAG (Retrieval-Augmented Generation) system. It features:
*   **Strict RAG**: Answers queries *exclusively* from your documents (no hallucinations).
*   **Async Ingestion**: Supports uploading hundreds of files instantly using a background queue (Redis + Celery).
*   **Hierarchical Sorting**: Automatically classifies and sorts files into folders (e.g., `Finance/Invoices/pdf`).
*   **Local First**: Runs entirely on your machine using Ollama and ChromaDB.

---

## Mode 1: Docker (Recommended)
*Best for: Stability, clean environment, "hospital-grade" simulation.*

**Prerequisites**: Docker Desktop installed.

### 0. Install Docker (First Time Only)
1.  **Download**: Go to [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) and download the installer.
2.  **Install**: Run the installer. Ensure "Use WSL 2 instead of Hyper-V" is checked (recommended).
3.  **Restart**: You will likely need to restart your laptop.
4.  **Start**: Open "Docker Desktop" from your Start Menu and wait until the whale icon in the bottom bar stops moving (or says "Engine Running").

### 1. Start the System
Run this single command to start App, Database, AI Model, and Worker:
```powershell
docker-compose up --build
```

### 2. Pull the AI Model (One-time only)
Once the containers are running, open a new terminal and run:
```powershell
docker exec -it documind-ollama ollama pull llama3.2
```

### 3. Access
*   **Web UI**: [http://localhost:5000](http://localhost:5000)
*   **Stop**: Press `Ctrl+C` in the running terminal.

---

## Future Development & Workflow
**Q: Can I edit my code (HTML, CSS, Python) after Dockerizing?**
**A: YES.** You have full control. You can use a "Hybrid Workflow":

### Option A: Local Development (Fastest for UI/Logic edits)
1.  Stop Docker (`Ctrl+C`).
2.  Edit your files in VS Code normally.
3.  Run `python app.py` locally to test changes instantly.
4.  *Note: Ensure your local Redis is running.*

### Option B: Docker Testing (Production Check)
When you are happy with your changes and want to verify the "Final Product":
1.  Run:
    ```powershell
    docker-compose up --build
    ```
2.  This command rebuilds the container with your new code. It is fast because it caches the heavy libraries.

---

## Mode 2: Manual / Local (Development)
*Best for: Debugging code, quick edits.*

**Prerequisites**: 
*   Python 3.11+
*   Redis Server (Memurai or WSL) running on `localhost:6379`.

### 1. Start Redis
Make sure Memurai or your Redis service is running.
Test it: `.\venv\Scripts\python -c "import redis; print(redis.Redis(host='localhost').ping())"`

### 2. Start the Celery Worker (Background Processor)
Open **Terminal 1**:
```powershell
.\venv\Scripts\celery -A worker.celery_app worker --pool=solo -l info
```

### 3. Start the File Watcher (Ingestion)
Open **Terminal 2**:
```powershell
.\venv\Scripts\python watcher.py
```

### 4. Start the Web App (Frontend)
Open **Terminal 3**:
```powershell
.\venv\Scripts\python app.py
```

### 5. Access
*   **Web UI**: [http://localhost:5000](http://localhost:5000)

---

## How to Use
1.  **Upload**: Drag and drop files (PDF, Images, Audio, Text) into the `data/incoming/` folder.
    *   *Note: In Docker mode, this folder is shared between your host and the container.*
2.  **Monitor**: Watch the logs in the "Worker" terminal (or Docker logs). You will see it process and sort the files.
3.  **Chat**: Go to `localhost:5000`, type a question. The AI will answer citing the specific documents.

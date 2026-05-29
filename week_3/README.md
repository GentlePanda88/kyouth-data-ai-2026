# Resume Helper Chatbot — Week 3

A containerized full-stack chat application that acts as an AI recruiter assistant. Users can upload their resume (PDF or TXT), and the system compares their skills against real job postings from a SQLite database, then uses an LLM (Gemini or Ollama) to provide personalized feedback and skill gap analysis.

---

## Project Structure

```
week_3/
├── docker-compose.yml
├── frontend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env
│   ├── jobs.db
│   └── src/
│       ├── main.py
│       └── templates/
│           ├── index.html      ← Chat page
│           └── dashboard.html  ← DB visualisation
└── backend/
    ├── Dockerfile
    ├── requirements.txt
    ├── .env
    ├── jobs.db
    ├── main.py
    ├── find_skill_gaps.py
    ├── prompt_model.py
    └── tag_data.py
```

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)
- [Ollama](https://ollama.com/) (optional — used as fallback if Gemini quota is exceeded)
- A Gemini API key from [aistudio.google.com](https://aistudio.google.com)

---

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd week_3
```

### 2. Configure environment variables

Create a `.env` file in `frontend/` based on the example:

```bash
cp frontend/.env.example frontend/.env
```

Create a `.env` file in `backend/` based on the example:

```bash
cp backend/.env.example backend/.env
```

Fill in your actual values — see `.env.example` files below for reference.

**`frontend/.env`**
```
BACKEND_URL=http://localhost:8001
DB_PATH=jobs.db
```

**`backend/.env`**
```
GEMINI_API_KEY=your_gemini_api_key_here
DB_PATH=jobs.db
MODEL_NAME=gemini-2.5-flash
OLLAMA_HOST=http://localhost:11434
```

> ⚠️ Never commit your `.env` files. They are listed in `.gitignore`.

### 3. Add the database

Place `jobs.db` (from Week 1) into both `frontend/` and `backend/` folders.

---

## Running the Application

### With Docker (recommended)

```bash
cd week_3
docker compose up --build
```

First run takes a few minutes to download the Python image and install dependencies. Subsequent runs are faster.

To stop:
```bash
Ctrl+C
docker compose down
```

### Without Docker (local development)

**Frontend:**
```bash
cd frontend
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

**Backend:**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

---

## Accessing the Application

| Page | URL |
|------|-----|
| Chat | http://localhost |
| Dashboard | http://localhost/dashboard |
| Backend health check | http://localhost:8001/health |

---

## Usage

### Chat page

1. Open `http://localhost` in your browser
2. Type a message and press **Enter** or click **Send**
3. Optionally attach a resume (PDF or TXT) using the 📎 button
4. After attaching, ask: *"What are my skill gaps based on my resume?"*
5. The AI will analyse your skills against the jobs database and respond

**Example inputs:**
- `"What skills are most in demand for data roles?"`
- `"I know Python and SQL, what jobs am I suited for?"`
- Upload a resume → `"What am I missing for a data engineer role?"`

**Example output:**
```
Based on your resume, your current skills include Python, SQL, and Azure.
Compared to job requirements, you may want to strengthen: Docker, Kubernetes, and Spark.
Here are some suggestions to address these gaps...
```

### Dashboard page

- Open `http://localhost/dashboard`
- View job category distribution, top technologies, and top companies
- Use the search bar to filter jobs by title, company, or keyword
- Click any job row to read the full description

---

## API Reference

### Backend

#### `POST /chat`

Processes a user message and returns an AI-generated recruiter response.

**Request payload:**
```json
{
  "message": "What are my skill gaps?",
  "pdf_text": "Optional resume text extracted from uploaded file"
}
```

**Response:**
```json
{
  "reply": "Based on your resume, your skill gaps are..."
}
```

**Behaviour:**
- If `pdf_text` is provided → runs skill gap analysis using `find_skill_gaps.py`, then passes results to the LLM
- If no `pdf_text` → passes the message directly to the LLM as a recruiter Q&A

#### `GET /health`

Returns the current model and database configuration.

```json
{"status": "ok", "model": "gemini-2.5-flash", "db": "jobs.db"}
```

### Frontend API routes

| Endpoint | Description |
|----------|-------------|
| `GET /api/jobs/categories` | Job category distribution for pie chart |
| `GET /api/jobs/techstack` | Top 15 technologies extracted from descriptions |
| `GET /api/jobs/companies` | Top companies by job count |
| `GET /api/jobs/search?q=` | Search jobs by title, company, or keyword |

### Key JavaScript functions (`index.html`)

| Function | Description |
|----------|-------------|
| `sendMessage()` | Collects user input and file text, sends POST to `/chat`, renders response bubble |
| `handleFileSelect()` | Routes uploaded file to TXT or PDF extractor |
| `extractTxtText()` | Reads `.txt` file directly using `file.text()` |
| `extractPdfText()` | Extracts text from PDF using PDF.js |
| `appendBubble()` | Renders a chat bubble (user or bot) in the chat history |
| `showTyping()` | Shows animated typing indicator while waiting for response |

### Service communication

```
Browser
  │
  ├─ GET http://localhost        → frontend container (port 80)
  │    └─ serves index.html with BACKEND_URL injected
  │
  └─ POST http://localhost:8001  → backend container (port 8001)
       └─ processes message, calls Gemini/Ollama, returns reply
```

Inside Docker, frontend and backend share `app-network` (bridge driver). The browser communicates with the backend directly via `localhost:8001` — not through Docker's internal network.

---

## Data & Assumptions

### Data flow

```
User types message + uploads resume
       ↓
Browser extracts text from PDF/TXT (client-side, PDF.js)
       ↓
JSON payload sent to POST /chat
       ↓
Backend runs extract_resume_skills() on resume text
Backend runs load_required_skills() from jobs.db
Backend computes skill gaps
       ↓
Prompt built and sent to Gemini (or Ollama fallback)
       ↓
AI response returned as JSON { "reply": "..." }
       ↓
Chat bubble rendered in browser
```

### Assumptions

- Resume files are plain text or selectable-text PDFs (scanned/image PDFs will not extract correctly)
- `jobs.db` must be present in both `frontend/` and `backend/` folders
- Ollama must be running locally for the fallback to work (`ollama serve`)
- The `BACKEND_URL` must be `http://localhost:8001` when running via Docker (browser-initiated requests cannot use Docker internal hostnames)
- No authentication — the app is intended for local/demo use only

### Constraints

- Maximum recommended file size: ~5MB
- Very long resumes may slow down Gemini response time
- No conversation history — each message is independent

---

## Testing

### Backend — curl / PowerShell

**Health check:**
```bash
curl http://localhost:8001/health
```

**Chat without resume:**
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What skills are in demand for data engineering?"}'
```

**Chat with resume text:**
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are my skill gaps?", "pdf_text": "Skills: Python, SQL, Excel"}'
```

**PowerShell equivalent:**
```powershell
Invoke-WebRequest -Uri http://localhost:8001/health -UseBasicParsing
```

### Frontend — manual test cases

| Test | Steps | Expected Result |
|------|-------|-----------------|
| Send message | Type a message, press Enter | Bot responds with recruiter reply |
| Upload TXT resume | Click 📎, select `.txt` file, ask about skill gaps | AI analyses skills and returns gaps |
| Upload PDF resume | Click 📎, select `.pdf` file, ask about skill gaps | AI analyses skills and returns gaps |
| Dashboard charts | Visit `/dashboard` | All 3 charts load with data |
| Dashboard search | Type "python" in search bar | Filtered job results appear |
| Remove attachment | Click ✕ on file badge | File removed, next message sent without resume |

### Verifying Docker communication

```bash
# Check containers are running
docker ps

# Verify frontend env
docker exec week_3-frontend-1 cat /app/.env

# Verify backend env
docker exec week_3-backend-1 cat /app/.env

# Check backend is reachable from host
curl http://localhost:8001/health
```

---

## Limitations

- **No chat history** — the model has no memory of previous messages; each request is stateless
- **No user authentication** — anyone with access to the URL can use the app
- **Scanned PDFs not supported** — PDF.js can only extract text from selectable PDFs, not image-based scans
- **Skill gap accuracy** — skill extraction uses keyword matching against a predefined list; uncommon or aliased skill names may be missed
- **Gemini rate limits** — free tier allows ~15 requests/minute; heavy usage triggers Ollama fallback which is slower
- **Ollama requires local setup** — fallback only works if Ollama is installed and running on the host machine
- **jobs.db is static** — the database reflects a fixed snapshot of job postings from Week 1; it is not updated in real time
- **Single user design** — no multi-user support or session isolation

---

## Architecture Reflection

### Design Choices

The project uses a **microservices architecture** with separate frontend and backend containers. This separation means each service has its own dependencies, can be updated independently, and fails in isolation — a bug in the backend doesn't crash the frontend.

Docker was chosen to eliminate the classic "works on my machine" problem. By packaging each service with its exact dependencies, the application runs identically on any machine with Docker installed.

### Trade-offs

- **Docker Compose over Kubernetes** — Compose is simpler and sufficient for a single-machine deployment. Kubernetes would add unnecessary complexity at this scale.
- **Jinja2 templates over a React frontend** — Keeping the frontend as server-rendered HTML with vanilla JavaScript reduces complexity and avoids a separate build step, at the cost of a less dynamic UI.
- **Gemini as primary model with Ollama fallback** — Gemini provides higher quality responses with no local resource usage, while Ollama ensures the app still works when API limits are hit or internet is unavailable.
- **Browser-side PDF extraction** — Using PDF.js in the browser avoids sending raw binary files to the backend, keeping the API simple (JSON only).

### Improvements

Given more time, the following would make the system more robust:

- **Persistent chat history** — store conversations in a database (e.g., PostgreSQL) so users can revisit past sessions
- **Streaming responses** — use server-sent events to stream the AI response token by token, improving perceived speed
- **Cloud deployment** — deploy to AWS/GCP/Azure with proper secrets management (e.g., AWS Secrets Manager) instead of `.env` files
- **React frontend** — replace Jinja2 templates with a proper React app for a more dynamic and maintainable UI
- **User authentication** — add login/session management so multiple users can use the app securely
- **Live job data** — connect to a job posting API to keep the database current instead of using a static snapshot

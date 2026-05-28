from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os, sqlite3, re

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="src/templates")

DB_PATH = os.getenv("DB_PATH", "jobs.db")

TECH_KEYWORDS = [
    "Python", "JavaScript", "TypeScript", "Java", "PHP", "SQL", "React",
    "Node.js", "AWS", "Docker", "Kubernetes", "FastAPI", "Flask", "Django",
    "TensorFlow", "PyTorch", "Git", "Linux", "MongoDB", "PostgreSQL", "MySQL",
    "Redis", "LangChain", "OpenAI", "Azure", "GCP", "Spark", "Kafka",
    "Airflow", "dbt", "HTML", "CSS", "Vue", "Angular", "Laravel"
]

JOB_CATEGORIES = {
    "AI / ML":        ["ai", "machine learning", "ml", "deep learning", "llm", "gen ai",
                       "generative", "computer vision", "nlp", "algorithm"],
    "Data":           ["data engineer", "data analyst", "data scientist", "analytics", "analytic"],
    "Software Eng":   ["software engineer", "software developer", "executive, software"],
    "Full Stack":     ["full stack", "full-stack"],
    "Backend":        ["backend", "back-end", "back end"],
    "Frontend":       ["frontend", "front-end", "front end", "web developer"],
    "Automation/QA":  ["automation", "qa engineer", "quality assurance", "selenium", "tester"],
    "DevOps / Cloud": ["devops", "cloud", "system administrator", "sysadmin"],
    "Other":          [],
}

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def categorise_title(title: str) -> str:
    t = title.lower()
    for cat, keywords in JOB_CATEGORIES.items():
        if cat == "Other":
            continue
        if any(k in t for k in keywords):
            return cat
    return "Other"

# ── Pages ──────────────────────────────────────────────────────────────────
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "backend_url": os.getenv("BACKEND_URL", "http://127.0.0.1:8001"),
    })

@app.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# ── API: job category distribution ─────────────────────────────────────────
@app.get("/api/jobs/categories")
def jobs_categories():
    conn = get_conn()
    rows = conn.execute("SELECT job_title FROM jobs").fetchall()
    conn.close()
    counts = {cat: 0 for cat in JOB_CATEGORIES}
    for r in rows:
        counts[categorise_title(r["job_title"])] += 1
    return {"labels": list(counts.keys()), "values": list(counts.values())}

# ── API: top tech stack from descriptions ───────────────────────────────────
@app.get("/api/jobs/techstack")
def jobs_techstack():
    conn = get_conn()
    rows = conn.execute("SELECT description FROM jobs WHERE description IS NOT NULL").fetchall()
    conn.close()
    counts = {}
    for kw in TECH_KEYWORDS:
        c = sum(1 for r in rows if re.search(rf'\b{re.escape(kw)}\b', r["description"] or "", re.IGNORECASE))
        if c > 0:
            counts[kw] = c
    sorted_counts = dict(sorted(counts.items(), key=lambda x: -x[1])[:15])
    return {"labels": list(sorted_counts.keys()), "values": list(sorted_counts.values())}

# ── API: top companies ───────────────────────────────────────────────────────
@app.get("/api/jobs/companies")
def jobs_companies():
    conn = get_conn()
    rows = conn.execute("""
        SELECT company, COUNT(*) as c FROM jobs
        WHERE company != 'Private Advertiser'
        GROUP BY company ORDER BY c DESC LIMIT 10
    """).fetchall()
    conn.close()
    return {"labels": [r["company"] for r in rows], "values": [r["c"] for r in rows]}

# ── API: search ──────────────────────────────────────────────────────────────
@app.get("/api/jobs/search")
def jobs_search(q: str = ""):
    conn = get_conn()
    if q.strip():
        rows = conn.execute("""
            SELECT source_id, job_title, company, description
            FROM jobs
            WHERE job_title LIKE ? OR company LIKE ? OR description LIKE ?
            LIMIT 20
        """, (f"%{q}%", f"%{q}%", f"%{q}%")).fetchall()
    else:
        rows = conn.execute(
            "SELECT source_id, job_title, company, description FROM jobs LIMIT 20"
        ).fetchall()
    conn.close()
    return {"results": [dict(r) for r in rows]}
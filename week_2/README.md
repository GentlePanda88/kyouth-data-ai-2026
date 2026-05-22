# AI-Powered Job Skill Extraction & Skill Gap Analyzer

## 📌 Project Title
**AI Job Skill Extraction & Resume Skill Gap Analysis System**

---

## 📖 Project Description

This project is an AI-assisted pipeline that extracts technical skills from job descriptions stored in a SQLite database and compares them against a candidate’s resume to identify skill gaps.

It consists of two main components:

### 1. Job Skill Extraction (`tag_data.py`)
- Uses a local LLM (e.g., LLaMA 3.1 via `prompt_model.py`)
- Extracts structured technical skills from unstructured job descriptions
- Stores extracted skills into a SQLite database (`tech_stack` column)
- Handles batching, retries, and JSON validation
- Includes basic token usage estimation and quality metrics

### 2. Skill Gap Analysis (`find_skill_gaps.py`)
- Extracts skills from a resume text file
- Loads required skills from the job database
- Normalizes and compares both skill sets
- Outputs:
  - Resume skills
  - Required skills
  - Missing skills (skill gaps)
  - Execution time and token estimate

---

## 🧠 Key Features

- LLM-based skill extraction (structured JSON output)
- Batch processing for scalable inference
- Robust JSON parsing and error handling
- Skill normalization and alias mapping (e.g., MySQL → SQL)
- Resume vs job-market skill gap analysis
- Lightweight token/time estimation metrics

---

## 📁 Project Structure

```bash
week_2/
├── data/
│ ├── jobs_d1.db # SQLite database (job postings)
│ └── resume_d3.txt # Resume text file
├── prompt_model.py
├── find_skill_gaps.py
├── rate_limits.txt
├── tag_data.py
├── pyproject.toml       # Environment & Dependencies (using `uv`)
├── uv.lock
└── README.md
```
---

## ⚙️ Setup Instructions

### 1. Requirements

- Python 3.14.*
- ruff 0.15.*
- uv 0.8.*
- ollama 0.21.* (install following models)
    - llama3.1
    - phi3
    - deepseek-r1:1.5b

- Required Python packages:

```bash
pip install pydantic
```
### 2. Setup Local Model (if using Ollama)

```bash
ollama run llama3.1
```

### 3. Database Setup

Ensure SQLite database exist:

```bash
data/jobs_d1.db
```
Required table:
```bash
CREATE TABLE jobs (
    source_id INTEGER PRIMARY KEY,
    job_title TEXT,
    description TEXT,
    tech_stack TEXT
);
```
---
## 🚀 How to Run

### Step 1: Extract skills from job descriptions

```bash
uv run tag_data.py
```

This will:
- Read job descriptions from SQLite
- Extract technical skills using LLM
- Store results in tech_stack column

### Step 2: Run skill gap analysis

```bash
uv run find_skill_gaps.py
```

This will:
- Read resume from data/resume_d3.txt
- Load required skills from database
- Output missing skills and analysis report
---

### 📊 Output format
---
===== SKILL GAP REPORT =====

📌 Resume Skills:
python, sql, azure, powershell

📌 Required Skills:
python, sql, java, docker, aws, ci/cd

❌ Missing Skills:
aws, ci/cd, docker, java

⏱ Time Taken: 12.34 ms
🔢 Tokens: 842









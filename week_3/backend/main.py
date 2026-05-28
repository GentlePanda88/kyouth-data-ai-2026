from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from find_skill_gaps import extract_resume_skills, load_required_skills
from prompt_model import prompt_model

load_dotenv()

app = FastAPI()

# Allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH  = os.getenv("DB_PATH",    "jobs.db")
MODEL    = os.getenv("MODEL_NAME", "gemini-2.5-flash")


# =========================
# REQUEST SCHEMA
# =========================
class ChatRequest(BaseModel):
    message: str
    pdf_text: str | None = None   # resume text extracted by frontend


# =========================
# POST /chat
# =========================
@app.post("/chat")
def chat(body: ChatRequest):

    resume_text = body.pdf_text or ""
    user_message = body.message.strip()

    # ── If a resume was uploaded, run skill gap analysis ──────────────────
    skill_context = ""

    if resume_text:
        resume_skills  = extract_resume_skills(resume_text)
        required_skills = load_required_skills(DB_PATH)
        gaps           = sorted(required_skills - resume_skills)

        skill_context = f"""
The candidate uploaded their resume. Here is the skill gap analysis:

✅ Resume Skills:   {", ".join(sorted(resume_skills)) or "None detected"}
📋 Required Skills: {", ".join(sorted(required_skills)) or "None found in DB"}
❌ Skill Gaps:      {", ".join(gaps) or "None — great match!"}

Use the above analysis to answer the candidate's question.
"""

    # ── Build final prompt ────────────────────────────────────────────────
    prompt = f"""You are an AI recruiter assistant helping candidates understand job market requirements.

{skill_context}
Candidate's question: {user_message}

Give a helpful, concise, and encouraging response. If skill gaps exist, suggest how to address them.
"""

    # ── Call the model ────────────────────────────────────────────────────
    reply = prompt_model(MODEL, prompt)

    if reply is None:
        return JSONResponse(
            status_code=500,
            content={"reply": "[Error] Model failed to respond. Please try again."}
        )

    return {"reply": reply}


# =========================
# HEALTH CHECK
# =========================
@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL, "db": DB_PATH}

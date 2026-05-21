import time
import sqlite3
import re
from typing import List, Set
from pydantic import BaseModel


# =========================
# OUTPUT SCHEMA
# =========================
class SkillGapResult(BaseModel):
    gaps: List[str]
    resume_skills: List[str]
    required_skills: List[str]
    time_ms: float
    tokens: int


# =========================
# NORMALIZER
# =========================
def normalize(skill: str) -> str:
    skill = skill.lower().strip()

    skill = skill.replace("c++", "cpp")
    skill = skill.replace("c/c++", "cpp")
    skill = skill.replace("node js", "node.js")
    skill = skill.replace("springboot", "spring boot")
    skill = skill.replace("springframework", "spring framework")
    skill = skill.replace("rest api", "restful api")

    return skill


# =========================
# EXTRACT SKILLS FROM RESUME
# =========================
def extract_resume_skills(text: str) -> Set[str]:

    text = text.lower()

    known_skills = [
        "python", "sql", "mcp", "regex", "pydantic",
        "docker", "git", "github", "linux",
        "api", "rest", "restful api",
        "tensorflow", "pytorch", "scikit-learn",
        "aws", "gcp", "google cloud", "azure",
        "ci/cd", "testing", "benchmarking",
        "token optimization", "prompt engineering"
    ]

    found = set()

    for skill in known_skills:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text):
            found.add(normalize(skill))

    return found


# =========================
# LOAD REQUIRED SKILLS FROM DB
# =========================
def load_required_skills(db_url: str) -> Set[str]:

    conn = sqlite3.connect(db_url)
    cursor = conn.cursor()

    cursor.execute("SELECT tech_stack FROM jobs WHERE tech_stack IS NOT NULL")

    rows = cursor.fetchall()
    conn.close()

    required = set()

    for (tech_stack,) in rows:

        if not tech_stack:
            continue

        for s in tech_stack.split(","):
            required.add(normalize(s))

    return required


# =========================
# MAIN FUNCTION
# =========================
def find_skill_gaps(
    input_file_path: str = "data/resume_d3.txt",
    db_url: str = "data/jobs_d1.db"
) -> SkillGapResult:

    start_time = time.time()   # ⏱ start timer

    try:
        # read resume file
        with open(input_file_path, "r", encoding="utf-8") as f:
            resume_text = f.read()

        # extract skills from resume
        resume_skills = extract_resume_skills(resume_text)

        # load required skills from DB
        required_skills = load_required_skills(db_url)

        # compute gaps
        gaps = sorted(list(required_skills - resume_skills))

        # =========================
        # TIME + TOKEN METRICS
        # =========================

        time_ms = round((time.time() - start_time) * 1000, 2)

        tokens = (
            len(str(resume_skills).split()) +
            len(str(required_skills).split()) +
            len(str(gaps).split())
        ) * 4

        return SkillGapResult(
            gaps=gaps,
            resume_skills=sorted(list(resume_skills)),
            required_skills=sorted(list(required_skills)),
            time_ms=time_ms,
            tokens=tokens
        )

    except FileNotFoundError:
        return SkillGapResult(
            gaps=[],
            resume_skills=[],
            required_skills=[],
            time_ms=0,
            tokens=0
        )

    except sqlite3.Error:
        return SkillGapResult(
            gaps=[],
            resume_skills=[],
            required_skills=[],
            time_ms=0,
            tokens=0
        )

    except Exception:
        return SkillGapResult(
            gaps=[],
            resume_skills=[],
            required_skills=[],
            time_ms=0,
            tokens=0
        )


# =========================
# RUN DIRECTLY
# =========================
if __name__ == "__main__":

    result = find_skill_gaps()

    print("\n===== SKILL GAP REPORT =====\n")

    print("📌 Resume Skills:")
    print(", ".join(result.resume_skills))

    print("\n📌 Required Skills:")
    print(", ".join(result.required_skills))

    print("\n❌ Missing Skills (Gaps):")
    print(", ".join(result.gaps))

    print("\n⏱ Time Taken:", result.time_ms, "ms")
    print("🔢 Tokens:", result.tokens)

    print("\n=============================\n")
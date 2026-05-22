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
# SKILL ALIAS MAP
# =========================
SKILL_ALIASES = {
    "mysql": "sql",
    "postgresql": "sql",
    "sqlite": "sql",
    "mssql": "sql",

    "c++": "c++",
    "c/c++": "c++",

    "node js": "node.js",

    "springboot": "spring boot",
    "springframework": "spring framework",

    "rest api": "restful api"
}


# =========================
# MASTER SKILL LIST
# =========================
KNOWN_SKILLS = [

    # languages
    "python",
    "java",
    "javascript",
    "typescript",
    "php",
    "c",
    "c++",
    "cpp",
    "c#",
    "go",
    "rust",
    "r",
    "bash",
    "powershell",

    # databases
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "sqlite",

    # ai/ml
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "llm",
    "llms",
    "rag",
    "langchain",
    "llamaindex",
    "deep learning",
    "machine learning",

    # cloud/devops
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "google cloud",
    "ci/cd",
    "jenkins",
    "github actions",
    "gitlab ci",
    "linux",
    "nginx",

    # frameworks/tools
    "spring framework",
    "spring boot",
    "fastapi",
    "flask",
    "node.js",
    "git",
    "github",

    # analytics
    "tableau",
    "powerbi",
    "datastudio",
    "excel",
    "a/b testing",

    # engineering
    "etl",
    "api",
    "restful api",
    "feature engineering",
    "data processing",
    "data engineering",
    "prompt engineering",
    "benchmarking",
    "regex",
    "pydantic",
    "mcp"
]


# =========================
# NORMALIZER
# =========================
def normalize(skill: str) -> str:

    skill = skill.lower().strip()

    skill = re.sub(r"\s+", " ", skill)

    if skill in SKILL_ALIASES:
        return SKILL_ALIASES[skill]

    return skill


# =========================
# EXTRACT SKILLS FROM RESUME
# =========================
def extract_resume_skills(text: str) -> Set[str]:

    text = text.lower()

    found = set()

    for skill in KNOWN_SKILLS:

        skill_lower = skill.lower()

        # special handling for symbols
        if skill_lower in ["c++", "c#", "node.js"]:

            if skill_lower in text:
                found.add(normalize(skill))

        else:
            pattern = r"\b" + re.escape(skill_lower) + r"\b"

            if re.search(pattern, text):
                found.add(normalize(skill))

    return found

# =========================
# LOAD REQUIRED SKILLS
# =========================
def load_required_skills(db_url: str) -> Set[str]:

    conn = sqlite3.connect(db_url)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tech_stack
        FROM jobs
        WHERE tech_stack IS NOT NULL
    """)

    rows = cursor.fetchall()

    conn.close()

    required = set()

    for (tech_stack,) in rows:

        if not tech_stack:
            continue

        for skill in tech_stack.split(","):

            cleaned = normalize(skill)

            if cleaned:
                required.add(cleaned)

    return required


# =========================
# MAIN FUNCTION
# =========================
def find_skill_gaps(
    input_file_path: str = "data/resume_d3.txt",
    db_url: str = "data/jobs_d1.db"
) -> SkillGapResult:

    start_time = time.time()

    try:

        # =========================
        # READ RESUME
        # =========================
        with open(input_file_path, "r", encoding="utf-8") as f:
            resume_text = f.read()

        # =========================
        # EXTRACT RESUME SKILLS
        # =========================
        resume_skills = extract_resume_skills(resume_text)

        # =========================
        # LOAD REQUIRED SKILLS
        # =========================
        required_skills = load_required_skills(db_url)

        # =========================
        # COMPUTE GAPS
        # =========================
        gaps = sorted(list(required_skills - resume_skills))

        # =========================
        # METRICS
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

    except Exception as e:

        print("ERROR:", e)

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
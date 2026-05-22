import sqlite3
import time
import json
import re
from typing import List, Dict

from prompt_model import prompt_model

BATCH_SIZE = 2
MODEL_NAME = "gemini-2.5-flash"
MAX_RETRIES = 3
RETRY_DELAY = 2


# =========================
# CLEAN TEXT
# =========================
def clean_text(text: str) -> str:
    return " ".join(text.split()) if text else ""


# =========================
# FIXED JSON EXTRACTOR
# =========================
def extract_json(text: str):

    matches = re.findall(r"\[\s*\{.*?\}\s*\]", text, re.DOTALL)

    if not matches:
        raise ValueError("No JSON found")

    all_items = []

    for m in matches:
        try:
            parsed = json.loads(m)
            if isinstance(parsed, list):
                all_items.extend(parsed)
        except:
            continue

    if not all_items:
        raise ValueError("Failed to parse JSON")

    return all_items


# =========================
# PROMPT
# =========================
def build_prompt(batch: List[Dict]) -> str:

    prompt = f"""
Extract ONLY technical skills.

Return EXACTLY {len(batch)} JSON objects.

FORMAT ONLY:
[{{"source_id":123,"tech_stack":"skill1, skill2"}}]

NO explanation. NO markdown.
"""

    for job in batch:
        prompt += f"\n{job['source_id']} | {clean_text(job['description'])}"

    return prompt


# =========================
# QUALITY METRICS
# =========================
def compute_quality(results):
    total_tags = 0
    duplicate_count = 0

    for r in results:
        tags = [t.strip().lower() for t in r["tech_stack"].split(",") if t.strip()]
        total_tags += len(tags)
        duplicate_count += len(tags) - len(set(tags))

    return {
        "duplicate_rate": (duplicate_count / total_tags * 100) if total_tags else 0
    }


# =========================
# MAIN FUNCTION (FIXED FINAL)
# =========================
def tag_data(db_url: str):

    start_time = time.time()

    total_tokens = 0
    total_updated = 0

    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT source_id, description
        FROM jobs
        WHERE tech_stack IS NULL OR tech_stack = ''
    """)

    jobs = [dict(r) for r in cursor.fetchall()]

    if not jobs:
        print("No data to tag")
        return

    for i in range(0, len(jobs), BATCH_SIZE):

        batch = jobs[i:i+BATCH_SIZE]
        prompt = build_prompt(batch)

        success = False

        for attempt in range(MAX_RETRIES):

            try:
                response = prompt_model(MODEL_NAME, prompt)

                if not response:
                    raise ValueError("Empty response")

                print("\nRAW RESPONSE:\n", response)

                results = extract_json(response)

                # =========================
                # SAFE MAP (FIXED TYPE HANDLING)
                # =========================
                result_map = {}

                for r in results:
                    if "source_id" in r and "tech_stack" in r:
                        try:
                            sid = str(r["source_id"]).strip()
                            result_map[sid] = r["tech_stack"]
                        except:
                            continue

                # =========================
                # DB UPDATE (TYPE SAFE)
                # =========================
                for job in batch:

                    sid = str(job["source_id"]).strip()

                    if sid in result_map:

                        cursor.execute("""
                            UPDATE jobs
                            SET tech_stack = ?
                            WHERE CAST(source_id AS TEXT) = ?
                        """, (result_map[sid], sid))

                        print(f"Updated {sid}")
                        total_updated += 1

                conn.commit()

                # =========================
                # TOKEN ESTIMATION
                # =========================
                total_tokens += len(prompt.split()) * 4
                total_tokens += len(response.split()) * 4

                success = True
                break

            except Exception as e:
                print(f"[Batch {i//BATCH_SIZE}] attempt {attempt+1} failed: {e}")
                time.sleep(RETRY_DELAY)

        if not success:
            print(f"[Batch {i//BATCH_SIZE}] skipped")

    elapsed = (time.time() - start_time) * 1000

    print("\n===== FINAL =====")
    print("tokens:", total_tokens)
    print("time_ms:", round(elapsed, 2))
    print("rows_updated:", total_updated)

    conn.close()


if __name__ == "__main__":
    tag_data("data/jobs_d1.db")
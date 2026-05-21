import sqlite3
import time
import json
from typing import Dict, List

from prompt_model import prompt_model


# =========================
# CONFIG
# =========================
BATCH_SIZE = 2
MODEL_NAME = "llama3.1"

MAX_RETRIES = 3
RETRY_DELAY = 3


# =========================
# TOKEN ESTIMATION
# =========================
def estimate_tokens(text: str) -> int:
    return len(text.split()) * 4


# =========================
# CLEAN TEXT
# =========================
def clean_text(text: str) -> str:
    if not text:
        return ""

    # remove weird spacing/newlines
    text = " ".join(text.split())

    # keep only first 120 words
    text = " ".join(text.split()[:120])

    return text


# =========================
# PROMPT BUILDER
# =========================
def build_prompt(batch: List[Dict]) -> str:

    prompt = """
You are a job skill extraction system.

Extract ONLY technical skills from the job descriptions.

Return STRICT VALID JSON ONLY.

Output format:
[
  {
    "source_id": 123,
    "tech_stack": "Python, SQL, Docker"
  }
]

Rules:
- Output MUST start with [
- Output MUST end with ]
- No markdown
- No explanations
- No extra text
- tech_stack must be comma-separated
"""

    for job in batch:

        prompt += f"""

ID: {job['source_id']}
TITLE: {clean_text(job['job_title'])}
DESCRIPTION: {clean_text(job['description'])}
"""

    return prompt


# =========================
# QUALITY METRICS
# =========================
def compute_quality(results):

    duplicate_count = 0
    total_tags = 0

    for r in results:

        tags = [
            t.strip().lower()
            for t in r["tech_stack"].split(",")
            if t.strip()
        ]

        total_tags += len(tags)
        duplicate_count += len(tags) - len(set(tags))

    duplicate_rate = (
        duplicate_count / total_tags * 100
        if total_tags > 0 else 0
    )

    return {
        "duplicate_count": duplicate_count,
        "duplicate_rate": duplicate_rate
    }


# =========================
# MAIN FUNCTION
# =========================
def tag_data(db_url: str):

    start_time = time.time()

    total_input_tokens = 0
    total_output_tokens = 0
    total_updated = 0

    try:
        conn = sqlite3.connect(db_url)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

    except Exception as e:
        print(f"Database error: {e}")
        return

    try:

        cursor.execute("""
            SELECT source_id, job_title, description
            FROM jobs
            WHERE tech_stack IS NULL OR tech_stack = ''
        """)

        rows = cursor.fetchall()

        if not rows:

            elapsed = (time.time() - start_time) * 1000

            print("No data to tag")
            print(f"Total tokens used: 0, took {elapsed:.3f}ms")

            return

        jobs = [dict(r) for r in rows]

        # =========================
        # BATCH PROCESSING
        # =========================
        for batch_index in range(0, len(jobs), BATCH_SIZE):

            batch = jobs[batch_index:batch_index + BATCH_SIZE]

            prompt = build_prompt(batch)

            success = False

            for attempt in range(1, MAX_RETRIES + 1):

                try:

                    response_text = prompt_model(
                        MODEL_NAME,
                        prompt
                    )

                    # =========================
                    # RESPONSE VALIDATION
                    # =========================
                    if not response_text:
                        raise ValueError("Empty model response")

                    # remove markdown if exists
                    response_text = (
                        response_text
                        .replace("```json", "")
                        .replace("```", "")
                        .strip()
                    )

                    # DEBUG PRINT
                    print("\n===== RAW RESPONSE =====")
                    print(response_text)
                    print("========================\n")

                    # basic JSON validation
                    if not response_text.startswith("["):
                        raise ValueError(
                            "Model did not return JSON array"
                        )

                    # parse JSON
                    try:
                        results = json.loads(response_text)

                    except json.JSONDecodeError:
                        print("\nINVALID JSON RESPONSE:")
                        print(response_text)
                        raise

                    # ensure list
                    if not isinstance(results, list):
                        raise ValueError(
                            "Response is not a JSON list"
                        )

                    # ensure correct batch size
                    if len(results) != len(batch):
                        raise ValueError(
                            "Mismatch between batch size and response"
                        )

                    # validate fields
                    for item in results:

                        if "source_id" not in item:
                            raise ValueError(
                                "Missing source_id field"
                            )

                        if "tech_stack" not in item:
                            raise ValueError(
                                "Missing tech_stack field"
                            )

                    # =========================
                    # TOKEN TRACKING
                    # =========================
                    total_input_tokens += estimate_tokens(prompt)

                    total_output_tokens += estimate_tokens(
                        response_text
                    )

                    # =========================
                    # QUALITY METRICS
                    # =========================
                    quality = compute_quality(results)

                    print("Quality Metrics:", quality)

                    # =========================
                    # DB UPDATE
                    # =========================
                    for item in results:

                        cursor.execute("""
                            UPDATE jobs
                            SET tech_stack = ?
                            WHERE source_id = ?
                        """, (
                            item["tech_stack"],
                            item["source_id"]
                        ))

                        print(
                            f"Analyzed Job "
                            f"{item['source_id']}: "
                            f"{item['tech_stack']}"
                        )

                        total_updated += 1

                    conn.commit()

                    success = True
                    break

                except Exception as e:

                    print(
                        f"[Batch {batch_index // BATCH_SIZE}] "
                        f"Attempt {attempt} failed: {e}"
                    )

                    time.sleep(RETRY_DELAY)

            if not success:

                print(
                    f"[Batch {batch_index // BATCH_SIZE}] "
                    f"skipped after retries"
                )

        elapsed = (time.time() - start_time) * 1000

        total_tokens = (
            total_input_tokens +
            total_output_tokens
        )

        # =========================
        # FINAL SUMMARY
        # =========================
        print("\n===== SUMMARY =====")

        print(
            f"Total tokens used: "
            f"{total_tokens}, "
            f"took {elapsed:.3f}ms"
        )

        return {
            "tokens_used": total_tokens,
            "time_ms": elapsed,
            "rows_updated": total_updated
        }

    except Exception as e:

        print(f"Unexpected error: {e}")

    finally:
        conn.close()


# =========================
# RUN DIRECTLY
# =========================
if __name__ == "__main__":

    tag_data("data/jobs_d1.db")
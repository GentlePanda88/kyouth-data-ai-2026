# Day 2: Cleans/Validates to data/2_silver/

from pathlib import Path
from bs4 import BeautifulSoup
from pydantic import BaseModel, ValidationError
import json
import re

# -----------------------------
# Pydantic Model
# -----------------------------
class JobListing(BaseModel):
    source_id: str
    job_title: str
    company: str
    description: str


# -----------------------------
# Text Cleaning Helper
# -----------------------------
def clean_text(text: str) -> str:
    if not text:
        return ""
    return text.strip()


# -----------------------------
# Extract data from HTML
# -----------------------------
def extract_job_data(html_content: str):

    soup = BeautifulSoup(html_content, "html.parser")

    # ---------------------------------
    # SOURCE ID from og:url
    # ---------------------------------
    source_id = ""

    og_url = soup.find("meta", property="og:url")

    if og_url and og_url.get("content"):
        url = og_url["content"].rstrip("/")
        source_id = url.split("/")[-1]

    # ---------------------------------
    # Job Title
    # ---------------------------------
    job_title = ""

    title_tag = soup.find(attrs={"data-automation": "job-detail-title"})

    if title_tag:
        job_title = clean_text(
            title_tag.get_text(separator=" ", strip=True)
        )

    # ---------------------------------
    # Company
    # ---------------------------------
    company = ""

    company_tag = soup.find(attrs={"data-automation": "advertiser-name"})

    if company_tag:
        company = clean_text(
            company_tag.get_text(separator=" ", strip=True)
        )

    # ---------------------------------
    # Description
    # ---------------------------------
    description = ""

    desc_tag = soup.find(attrs={"data-automation": "jobAdDetails"})

    if desc_tag:
        description = clean_text(
            desc_tag.get_text(separator=" ", strip=True)
        )

    return {
        "source_id": source_id,
        "job_title": job_title,
        "company": company,
        "description": description,
    }


# -----------------------------
# Main Processing Function
# -----------------------------
def process_all_html(input_dir, output_dir):

    print("\n🥈 Silver: Starting processing...\n")

    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Idempotency
    output_path.mkdir(parents=True, exist_ok=True)

    # Handle missing folder
    if not input_path.exists():
        print("⚠️ Input directory missing:", input_dir)
        return

    files = list(input_path.glob("*.html"))

    if not files:
        print("⚠️ No HTML files found.")
        return

    total = len(files)
    processed = 0
    skipped = 0

    for file in files:

        try:
            html_content = file.read_text(
                encoding="utf-8"
            )

            data = extract_job_data(html_content)

            # ---------------------------------
            # Missing field checks
            # ---------------------------------
            missing = False

            for key, value in data.items():
                if not value:
                    print(f"⚠️ Missing {key} in: {file.name}")
                    missing = True

            if missing:
                skipped += 1
                continue

            # ---------------------------------
            # Validate with Pydantic
            # ---------------------------------
            job = JobListing(**data)

            # ---------------------------------
            # Save JSON
            # ---------------------------------
            output_file = (
                output_path / f"{file.stem}.json"
            )

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(
                    job.model_dump(),
                    f,
                    ensure_ascii=False,
                    indent=2,
                )

            print(f"✅ Processed: {file.name}")
            processed += 1

        except ValidationError as e:
            print(f"⚠️ Validation failed: {file.name}")
            print(e)
            skipped += 1

        except Exception as e:
            print(f"⚠️ Error processing {file.name}: {e}")
            skipped += 1

    # ---------------------------------
    # Summary
    # ---------------------------------
    print("\n📊 Silver Summary:")
    print(
        f"Total: {total} | "
        f"Processed: {processed} | "
        f"Skipped: {skipped}"
    )


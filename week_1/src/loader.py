 #Day 3: Loads to data/3_gold/

from pathlib import Path
import sqlite3
import json


DB_NAME = "jobs.db"


def create_table(cursor):

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            source_id TEXT PRIMARY KEY,
            job_title TEXT,
            company TEXT,
            description TEXT,
            tech_stack TEXT
        )
        """
    )


def load_all_jsons(input_dir, output_dir):

    print("\n🥇 Gold: Starting database loading...\n")

    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # ---------------------------------
    # Idempotency
    # ---------------------------------
    output_path.mkdir(parents=True, exist_ok=True)

    # ---------------------------------
    # Handle missing input folder
    # ---------------------------------
    if not input_path.exists():
        print("⚠️ Input directory missing:", input_dir)
        return

    files = list(input_path.glob("*.json"))

    if not files:
        print("⚠️ No JSON files found.")
        return

    # ---------------------------------
    # Create database
    # ---------------------------------
    db_path = output_path / DB_NAME

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    create_table(cursor)

    total = len(files)
    inserted = 0
    skipped = 0

    # ---------------------------------
    # Process JSON files
    # ---------------------------------
    for file in files:

        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # ---------------------------------
            # INSERT OR IGNORE prevents duplicates
            # ---------------------------------
            cursor.execute(
                """
                INSERT OR IGNORE INTO jobs (
                    source_id,
                    job_title,
                    company,
                    description,
                    tech_stack
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    data["source_id"],
                    data["job_title"],
                    data["company"],
                    data["description"],
                    data.get("tech_stack"),
                ),
            )

            # ---------------------------------
            # Detect inserted vs skipped
            # ---------------------------------
            if cursor.rowcount == 0:
                print(f"⏭️ Skipped (duplicate): {file.name}")
                skipped += 1

            else:
                print(f"✅ Inserted: {file.name}")
                inserted += 1

        except Exception as e:
            print(f"⚠️ Failed loading {file.name}: {e}")

    # ---------------------------------
    # Save changes
    # ---------------------------------
    connection.commit()
    connection.close()

    # ---------------------------------
    # Summary
    # ---------------------------------
    print("\n📊 Gold Summary:")
    print(
        f"Total: {total} | "
        f"Inserted: {inserted} | "
        f"Skipped: {skipped}"
    )

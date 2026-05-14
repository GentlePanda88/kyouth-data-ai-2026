# Day 4: Quality checks on Gold layer

from pathlib import Path
import sqlite3

def run_data_profile(db_path):

    db_path = Path(db_path)

    # ---------------------------------
    # Handle missing DB
    # ---------------------------------
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return

    # ---------------------------------
    # Connect DB
    # ---------------------------------
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # ---------------------------------
    # Total records
    # ---------------------------------
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM jobs
        """
    )

    total_records = cursor.fetchone()[0]

    # ---------------------------------
    # Null / empty counts
    # ---------------------------------
    cursor.execute(
        """
        SELECT
            SUM(
                CASE
                    WHEN job_title IS NULL
                    OR job_title = ''
                    THEN 1
                    ELSE 0
                END
            ),

            SUM(
                CASE
                    WHEN company IS NULL
                    OR company = ''
                    THEN 1
                    ELSE 0
                END
            ),

            SUM(
                CASE
                    WHEN description IS NULL
                    OR description = ''
                    THEN 1
                    ELSE 0
                END
            )

        FROM jobs
        """
    )

    missing_job_title, missing_company, missing_description = cursor.fetchone()

    # ---------------------------------
    # Average description length
    # ---------------------------------
    cursor.execute(
        """
        SELECT AVG(LENGTH(description))
        FROM jobs
        """
    )

    avg_desc_length = cursor.fetchone()[0]

    # ---------------------------------
    # Shortest description
    # ---------------------------------
    cursor.execute(
        """
        SELECT
            source_id,
            job_title,
            LENGTH(description) AS desc_length

        FROM jobs

        ORDER BY desc_length ASC

        LIMIT 1
        """
    )

    shortest = cursor.fetchone()

    # ---------------------------------
    # Longest description
    # ---------------------------------
    cursor.execute(
        """
        SELECT
            source_id,
            job_title,
            LENGTH(description) AS desc_length

        FROM jobs

        ORDER BY desc_length DESC

        LIMIT 1
        """
    )

    longest = cursor.fetchone()

    connection.close()

    # ---------------------------------
    # Print report
    # ---------------------------------
    print("\n--- 🔍 DATA QUALITY REPORT ---")

    print(f"📈 Total Records: {total_records}")

    print(
        "❓ Missing Values -> "
        f"job_title: {missing_job_title}, "
        f"company: {missing_company}, "
        f"description: {missing_description}"
    )

    print(
        f"📝 Avg Description Length: "
        f"{round(avg_desc_length)} chars"
    )

    print(
        f"⚠️ Shortest Description: "
        f"{shortest[2]} chars"
    )

    print(
        f"   ↳ source_id: {shortest[0]} "
        f"| job_title: {shortest[1]}"
    )

    print(
        f"🚨 Longest Description: "
        f"{longest[2]} chars"
    )

    print(
        f"   ↳ source_id: {longest[0]} "
        f"| job_title: {longest[1]}"
    )

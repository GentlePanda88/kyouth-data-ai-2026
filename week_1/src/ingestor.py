#Day 1: Extracts to data/1_bronze/
from pathlib import Path
import email
import quopri


def extract_html_from_mhtml(file_path: Path):
    """Extract decoded HTML from MHTML file"""

    try:
        with open(file_path, "rb") as f:
            msg = email.message_from_binary_file(f)

        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if content_type == "text/html" and "attachment" not in content_disposition:
                payload = part.get_payload(decode=True)

                if payload:
                    # decode quoted-printable safely
                    html = quopri.decodestring(payload).decode("utf-8", errors="ignore")
                    return html

        return None

    except Exception as e:
        print(f"⚠️ Error reading {file_path.name}: {e}")
        return None


def ingest_all_mhtml(input_dir: str, output_dir: str):

    print("🔥 ingest_all_mhtml() STARTED")

    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # 🧠 Idempotency: create folder if missing
    output_path.mkdir(parents=True, exist_ok=True)

    print("INPUT PATH:", input_path.resolve())
    print("FILES FOUND:", len(list(input_path.glob('*.mhtml'))))

    # 🧠 Handle missing input folder safely
    if not input_path.exists():
        print("⚠️ Input directory does not exist:", input_dir)
        return

    files = list(input_path.glob("*.mhtml"))

    if not files:
        print("⚠️ No MHTML files found in:", input_dir)
        return

    total = len(files)
    extracted = 0
    failed = 0

    print("\n🥉 Bronze: Starting ingestion...\n")

    for file in files:
        html = extract_html_from_mhtml(file)

        if html:
            output_file = output_path / f"{file.stem}.html"
            output_file.write_text(html, encoding="utf-8")

            print(f"✅ Extracted: {file.name}")
            extracted += 1
        else:
            print(f"⚠️ No HTML content found in: {file.name}")
            failed += 1

    print("\n📊 Bronze Summary:")
    print(f"Total: {total} | Extracted: {extracted} | Failed: {failed}")
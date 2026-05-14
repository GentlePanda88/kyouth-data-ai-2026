***Job Posting Data Pipeline Project***

#Project description 
-> This project is a local data engineering pipeline that processes raw `.mhtml` job posting files into a structured SQLite database using a Medallion Architecture approach.

-> The main goal of this project is to simulate how modern data platforms handle ingestion, transformation, validation, and storage of data using ETL concepts and orchestration practices commonly used in industry systems.

-> The pipeline follows multiple stages, where;

1. '0_source/' - the original source files (MHTML)
2. '1_bronze/' - raw extracted HTML files
3. '2_silver/' - the cleaned and transformed structured data, contains JSON files
4. '3_gold/' - final SQLite warehouse layer for analytics or querying


#Setup Instructions

Make sure the followings are installed on your system:
- Python 3.11 or newer
- Git
- uv package manager

1. Clone the repository
git clone <your-repository-url>
cd <your-project-folder>

2. Install uv

- for (windows) - use PowerShell, paste the following code

powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

- for (macOS/Linux), paste the following code

curl -LsSf https://astral.sh/uv/install.sh | sh

i. verify installation:

uv --version

3. Create Virtual Environment, paste the following

uv venv

i. to activate virtual environment:

(Windows) - use Powershell

.venv\Scripts\activate

(macOS/Linux)

source .venv/bin/activate

4. Install dependencies (If using pyproject.toml)

uv sync

#Usage (2 options either full pipeline or individual)

I. Run Full Pipeline - to execute the full ETL pipeline: (paste the command in Terminal)

python main.py all

or 

python week_1/main.py all

-> This command will:
1. Extract raw .mhtml files into Bronze layer
2. Clean & transform data into Silver layer
3. Load processed data into SQLite Gold warehouse
4. Run profiling or quality checks

II. Run Individual Modules

- Run Extractor

python main.py ingest

or

python week_1/main.py ingest

- Run Processor

python main.py process

or

python week_1/main.py process

- Run Loader

python main.py load

or 

python week_1/main.py load

- Run Data Profiling

python main.py profile

or

python week_1/main.py profile

#Expected Inputs & Outputs

1. Input - place raw .mhtml files inside:

0_source/

2. Output

(Bronze Layer) - raw extracted HTML:

1_bronze/

(Silver Layer) - clean structured JSON data

2_silver/

(Gold Layer) - SQLite warehouse database

3_gold/jobs.db

#Example Workflow

python main.py all

or

python week_1/main.py all

-> Expected Output

[INFO] Extracting source files...
[INFO] Processing HTML files...
[INFO] Loading data into SQLite...
[INFO] Running data quality profiling...
[SUCCESS] Pipeline completed successfully.

***Technical Reflections***

#Module 1: The Extractor (Medallion & Lakehouses)

Why is it useful to keep the original raw HTML files instead of directly inserting processed data into the database? What problems become easier to debug or recover from?

Answer: Keeping the original raw HTML files gives us a reliable backup of the source data and allows the pipeline to be rerun whenever the transformation logic changes. If data corruption, parsing errors, or incorrect transformations occur, developers can always refer back to the untouched source files for debugging and recovery.

#Module 2: Treatmant Plant (ETL vs ELT & Scale)

Why do cloud systems prefer loading raw data first before cleaning it (ELT)? What problems happen when processing files sequentially, and how does distributed processing help?

Answer: Cloud systems favor ELT because modern cloud warehouses like Snowflake and BigQuery are built to handle large-scale transformations directly within the platform. By loading raw data first, teams can keep complete datasets intact while applying various transformations at a later stage, eliminating the need to repeatedly pull data from the source.

#Module 3: The Blueprint & The Vault (Storage & Contracts)

What should happen if an important field like job_title disappears? Why fail early instead of silently inserting nulls into DB? How does INSERT OR IGNORE help prevent duplicate records?

Answer: If a critical field like job_title is missing, the pipeline should immediately flag it as an error rather than quietly inserting incomplete records. Catching the problem early prevents bad or incomplete data from spreading into dashboards, reports, or other systems where it becomes much harder to spot and fix later.

INSERT OR IGNORE helps keep the data consistent by preventing the same record from being inserted more than once if the pipeline runs again. This ensures the database remains clean and makes it safer to retry the loading process without worrying about duplicate entries.

#Module 4: The QA Inspector & Orchestrator

What happens if processor.py crashes halfway? How are automated orchestration tools more reliable than manual retries with Python scripts?

Answer: If processor.py crashes midway, the pipeline may be left in an incomplete state where some files have been processed and others have not. Manually rerunning it without proper tracking can lead to inconsistencies, duplicate entries, or skipped files.

Automated tools like Airflow break large scripts into smaller, separate tasks. If one task fails, the tool tracks the exact error, saves logs, and keeps unrelated tasks running. Instead of manual fixes, it uses automatic retries and alerts to heal from temporary errors. This ensures safe reruns without breaking your data or workflows.


#Technologies Used

-> Python
-> SQLite
-> uv
-> JSON
-> ETL Pipeline Concepts
-> Medallion Architecture
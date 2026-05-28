FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source files
COPY main.py .
COPY find_skill_gaps.py .
COPY prompt_model.py .
COPY tag_data.py .
COPY jobs.db .

# Copy env (or pass at runtime via --env-file)
COPY .env .

EXPOSE 8001

# host.docker.internal lets the container reach Ollama on your machine's localhost
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

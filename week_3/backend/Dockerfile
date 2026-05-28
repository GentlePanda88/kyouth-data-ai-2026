FROM python:3.14

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
COPY .env .

EXPOSE 8001

# OLLAMA_HOST is overridden in docker-compose.yml to reach host machine
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

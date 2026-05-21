import os
import time
import requests
from dotenv import load_dotenv

from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# =========================
# OLLAMA MODELS
# =========================
OLLAMA_MODELS = {
    "llama3.1",
    "phi3",
    "deepseek-r1:1.5b"
}

# =========================
# GEMINI MODELS
# =========================
GEMINI_MODELS = {
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-3-flash-preview",
    "gemini-3.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-3.1-flash-lite-preview",
    "gemini-flash-latest"
}

MAX_RETRIES = 3
RETRY_DELAY = 2

OLLAMA_URL = "http://localhost:11434/api/generate"


# =========================
# NORMALIZER
# =========================
def normalize_model(model: str) -> str:
    return model.replace("models/", "").strip()


# =========================
# ERROR CHECK
# =========================
def is_quota_error(error: str) -> bool:
    return "429" in str(error) or "RESOURCE_EXHAUSTED" in str(error)


# =========================
# GEMINI CALL
# =========================
def prompt_gemini(model: str, prompt: str) -> str:

    for attempt in range(1, MAX_RETRIES + 1):

        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            return response.text.strip()

        except Exception as e:
            print(f"[Gemini Error] {model} attempt={attempt}: {e}")

            if is_quota_error(str(e)):
                print("[Gemini] Quota hit → switching to Ollama")
                return None

            time.sleep(RETRY_DELAY)

    return None


# =========================
# OLLAMA CALL (FIXED)
# =========================
def prompt_ollama(model: str, prompt: str) -> str:

    for attempt in range(1, MAX_RETRIES + 1):

        try:
            r = requests.post(
                OLLAMA_URL,
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0
                    }
                },
                timeout=(10, 300)
            )

            if r.status_code != 200:
                raise Exception(f"HTTP {r.status_code}")

            response = r.json().get("response", "").strip()

            # IMPORTANT: avoid returning broken values
            if not response:
                raise Exception("Empty response from Ollama")

            return response

        except Exception as e:
            print(f"[Ollama Error] {model} attempt={attempt}: {e}")
            time.sleep(RETRY_DELAY)

    return None


# =========================
# ROUTER
# =========================
def prompt_model(model: str, prompt: str) -> str:

    model = normalize_model(model)

    # =========================
    # GEMINI PATH
    # =========================
    if model in GEMINI_MODELS:

        result = prompt_gemini(model, prompt)

        # fallback to Ollama
        if result is None:
            print("[Router] Falling back to Ollama...")
            result = prompt_ollama("llama3.1", prompt)

            # second fallback (optional safety)
            if result is None:
                return "[Error] Both Gemini and Ollama failed"

        return result


    # =========================
    # OLLAMA PATH
    # =========================
    if model in OLLAMA_MODELS:

        result = prompt_ollama(model, prompt)

        if result is None:
            return "[Error] Ollama failed after retries"

        return result


    return f"[Error] Unknown model: {model}"


# =========================
# CLI TEST
# =========================
if __name__ == "__main__":

    import sys

    if len(sys.argv) < 3:
        print("Usage: uv run prompt_model.py <model> <prompt>")
        exit()

    model = sys.argv[1]
    prompt = " ".join(sys.argv[2:])

    print("\n--- RESPONSE ---\n")
    print(prompt_model(model, prompt))
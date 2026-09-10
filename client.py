import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import random
import time
from datetime import datetime, timezone
from openai import APITimeoutError, APIStatusError
load_dotenv()

client = OpenAI(
    base_url=os.environ["LLM_BASE_URL"],
    api_key=os.environ["LLM_API_KEY"],
    timeout=30.0,
    max_retries=0,
)

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "llm", "src", "prompts", "enrich-v1.md")

def load_prompt():
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()

def call_model(book_input: dict) -> str:
    system_prompt = load_prompt()
    user_message = json.dumps(book_input)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    return _call_with_retries(messages)


def _call_with_retries(messages, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            start = time.time()
            response = client.chat.completions.create(
                model=os.environ["LLM_MODEL"],
                temperature=0,
                messages=messages,
            )
            duration_ms = (time.time() - start) * 1000
            log_call(
                model=os.environ["LLM_MODEL"],
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                duration_ms=round(duration_ms, 2),
                repaired=False
            )
            return response.choices[0].message.content
            
           
        except APITimeoutError:
            if attempt == max_attempts - 1:
                raise
            wait = (2 ** attempt) + random.uniform(0, 0.5)
            time.sleep(wait)
        except APIStatusError as e:
            if e.status_code == 429 or e.status_code >= 500:
                if attempt == max_attempts - 1:
                    raise
                wait = (2 ** attempt) + random.uniform(0, 0.5)
                time.sleep(wait)
            else:
                raise
def call_model_repair(book_input: dict, broken_output: str, error_message: str) -> str:
    system_prompt = load_prompt()
    user_message = json.dumps(book_input)

    repair_message = (
        f"Your previous answer was rejected for this reason: {error_message}\n"
        f"Your previous answer was: {broken_output}\n"
        f"Return only corrected JSON matching the schema."
    )

    response = client.chat.completions.create(
        model=os.environ["LLM_MODEL"],
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": broken_output},
            {"role": "user", "content": repair_message},
        ],
    )
    return response.choices[0].message.content

def parse_model_json(raw_text: str) -> dict:
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())

def log_call(model, input_tokens, output_tokens, duration_ms, repaired):
    os.makedirs("llm/logs", exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt_version": "enrich-v1",
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "duration_ms": duration_ms,
        "repaired": repaired
    }
    with open("llm/logs/calls.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
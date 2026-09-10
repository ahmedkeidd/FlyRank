import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url=os.environ["LLM_BASE_URL"],
    api_key=os.environ["LLM_API_KEY"],
)

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "llm", "src", "prompts", "enrich-v1.md")

def load_prompt():
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()

def call_model(book_input: dict) -> str:
    system_prompt = load_prompt()
    user_message = json.dumps(book_input)

    response = client.chat.completions.create(
        model=os.environ["LLM_MODEL"],
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content
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
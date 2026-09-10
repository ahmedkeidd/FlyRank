# Put an LLM Behind Your API — FlyRank Internship A17

A `POST /enrich` endpoint that takes a scraped book record (title + description)
and returns a validated category, one-sentence summary, and quality flags —
chaining directly onto the scraper built in Assignment A9.

## What it does

Given a book's title and optional description, the endpoint asks an LLM to classify
it into one of five categories, write a one-sentence summary, and flag any data
quality issues (missing description, generic title, etc.) — returning clean,
schema-validated JSON every time, never raw model text.

## Run it

```bash
# from the FlyRank root
uvicorn main:app --reload --port 8000
```

## Example request

```bash
curl.exe -X POST http://localhost:8000/enrich -H "Content-Type: application/json" -d "{\"title\": \"The Great Gatsby\", \"description\": \"A novel about wealth, love, and the American Dream.\"}"
```

Example response:
```json
{"category": "fiction", "summary": "A story of love and ambition in 1920s America.", "quality_flags": []}
```

## Job card

See [JOB-CARD.md](./JOB-CARD.md) for the full input/output contract, closed lists, and "must never" rules.

## Provider & environment variables

- **Provider:** OpenRouter (free tier)
- **Model:** `openrouter/free`
- Required env vars (see `.env.example` at project root):
  - `LLM_BASE_URL=https://openrouter.ai/api/v1`
  - `LLM_API_KEY=<your key>`
  - `LLM_MODEL=openrouter/free`

## Eval result

**Score: 8/8** — run on 2026-09-11, prompt version `enrich-v1`.

All 8 hand-labelled test cases (in `evals/cases.json`) passed, including an
ambiguous case (missing description) and an empty-description edge case.

## Cost log (sample)

```json
{"timestamp": "2026-09-10T23:23:47.755128+00:00", "prompt_version": "enrich-v1", "model": "openrouter/free", "input_tokens": 414, "output_tokens": 231, "duration_ms": 9884.0, "repaired": false}
```

**Estimate for 10,000 requests/day:** ~4.14M input tokens + ~2.31M output tokens
per day at this rate. On OpenRouter's free tier this isn't billed, but on a paid
tier this would be the main driver of cost — output tokens are typically priced
higher than input.

## Reliability features

- **Timeout:** 30 seconds (SDK default of 10 minutes overridden)
- **Retries:** manual exponential backoff with jitter, only on timeouts, 429, and 5xx — never on 400/401/403 (a bad key stays a bad key)
- **Repair retry:** one repair attempt if the model's output fails schema validation, before quarantining
- **Kill switch:** `LLM_ENABLED=false` disables the model call entirely and returns a clean 503
- **Stub mode:** `LLM_STUB=1` skips the model and returns a fixed valid response, for testing without spending quota

## What I'd fix with another day

Add prompt-injection test cases to the eval set, since book descriptions are
scraped from the web and could theoretically contain adversarial text.
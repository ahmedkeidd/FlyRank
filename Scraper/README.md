# The Polite Scraper — FlyRank Internship A9

A small scraping pipeline that downloads the first 3 catalogue pages of
[Books to Scrape](https://books.toscrape.com), visits all 60 book detail pages,
and turns the raw HTML into clean, validated JSON records.

## Target classification

- **Site:** Books to Scrape (https://books.toscrape.com)
- **Why:** it's a public sandbox built specifically for practicing scraping — confirmed on toscrape.com.
- **Scope:** first 3 catalogue pages only (60 books total)
- **Data collected:** title, price, availability, rating, description, product URL
- **robots.txt check:** https://books.toscrape.com/robots.txt returned 404 — no robots file found. A missing file is not permission, just an absence of rules, so I'm sticking to the sandbox's stated purpose and the assignment's 3-page scope.
- **Note:** I will not reuse this code on another site without checking its rules and terms first.

## How to run

```bash
cd Scraper
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python src/main.py
```

Output lands in `output/books.json` and `output/run-report.json`.

## Record schema

| Field | Type | Notes |
|---|---|---|
| title | string | |
| product_url | string | absolute URL, used as canonical identity |
| price_text | string | raw text, e.g. "£51.77" |
| price_gbp | float | normalized number, e.g. 51.77 |
| availability_text | string | e.g. "In stock (22 available)" |
| rating_text | string | e.g. "Three" |
| description | string or null | null when the book has no description |
| source_page | string | which catalogue page this book was found on |
| fetched_at | string | ISO timestamp of when the record was fetched |

## Politeness rules

- Sends an identifying user-agent: `FlyRankInternshipA9/1.0 (+https://github.com/ahmedkeidd/FlyRank)`
- 10-second timeout on every request
- 0.5s delay between real requests (cached pages skip the delay)
- Checks status code before parsing — only 200 is treated as success
- Caches every page in `cache/` so repeated runs during development don't hit the site again

## Why no browser was needed

The data is already present in the HTML the server sends back — a browser would only add cost (memory, time) with no benefit here.

## Sample run report

```json
{
  "start_time": "2026-08-19T11:14:03.271280+00:00",
  "duration_seconds": 3.0342,
  "pages_fetched": 61,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1
}
```
(This run included one deliberately broken URL to prove failure handling — the 60 real records still succeeded.)

## Limitations

- No retry/backoff logic yet (planned for next week's assignment, A16)
- Only handles the first 3 catalogue pages by design, not the full site

## Ethics note

Only scraping a sandbox built for this purpose. I use an official API when one exists, never bypass logins/paywalls/blocks, and only collect what's needed for the task.

I will not reuse this code on another site without checking its rules and terms first.
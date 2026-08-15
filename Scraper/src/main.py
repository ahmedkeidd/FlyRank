import requests
import os
from pathlib import Path

USER_AGENT = "FlyRankInternshipA9/1.0 (+https://github.com/ahmedkeidd/FlyRank)"
CACHE_DIR = Path(__file__).parent.parent / "cache"
TIMEOUT = 10  # seconds

def fetch_page(url, cache_filename):
    CACHE_DIR.mkdir(exist_ok=True)
    cache_path = CACHE_DIR / cache_filename

    if cache_path.exists():
        html = cache_path.read_text(encoding="utf-8")
        print(f"CACHE HIT: {cache_filename} ({len(html)} bytes)")
        return html

    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=TIMEOUT)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch {url}: status {response.status_code}")

    html = response.text
    cache_path.write_text(html, encoding="utf-8")
    print(f"FETCH: {cache_filename} ({len(html)} bytes)")
    return html

if __name__ == "__main__":
    fetch_page("https://books.toscrape.com/catalogue/page-1.html", "catalogue-page-1.html")
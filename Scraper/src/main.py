import requests
from pathlib import Path

USER_AGENT = "FlyRankInternshipA9/1.0 (+https://github.com/ahmedkeidd/FlyRank)"
CACHE_DIR = Path(__file__).parent.parent / "cache"
TIMEOUT = 10

CACHE_DIR.mkdir(exist_ok=True)
cache_path = CACHE_DIR / "catalogue-page-1.html"

if cache_path.exists():
    html = cache_path.read_text(encoding="utf-8")
    print(f"CACHE HIT ({len(html)} bytes)")
else:
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(
        "https://books.toscrape.com/catalogue/page-1.html",
        headers=headers,
        timeout=TIMEOUT
    )
    html = response.text
    cache_path.write_text(html, encoding="utf-8")
    print(f"FETCH ({len(html)} bytes)")
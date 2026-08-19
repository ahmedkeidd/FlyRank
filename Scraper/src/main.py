import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from pydantic import BaseModel, ValidationError
from typing import Optional

class BookRecord(BaseModel):
    title: str
    product_url: str
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: Optional[str]
    source_page: str
    fetched_at: str

USER_AGENT = "FlyRankInternshipA9/1.0 (+https://github.com/ahmedkeidd/FlyRank)"
CACHE_DIR = Path(__file__).parent.parent / "cache"
TIMEOUT = 10

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
    response.encoding = "utf-8"   
    html = response.text
    cache_path.write_text(html, encoding="utf-8")
    print(f"FETCH: {cache_filename} ({len(html)} bytes)")
    time.sleep(0.5)
    return html

def get_next_page_url(soup, current_url):
    next_link = soup.select_one("li.next a")
    if next_link is None:
        return None
    return urljoin(current_url, next_link["href"])

all_book_urls = []
current_url = "https://books.toscrape.com/catalogue/page-1.html"
page_num = 1

while current_url and page_num <= 3:
    html = fetch_page(current_url, f"catalogue-page-{page_num}.html")
    soup = BeautifulSoup(html, "html.parser")

    book_links = soup.select("article.product_pod h3 a")
    book_urls = [urljoin(current_url, link["href"]) for link in book_links]
    for url in book_urls:
        all_book_urls.append((url, current_url))  # store pair: (book_url, source_page)

    current_url = get_next_page_url(soup, current_url)
    page_num += 1

unique_urls = list(set(url for url, source in all_book_urls))

print(f"catalogue_pages={page_num - 1}")
print(f"discovered={len(all_book_urls)}")
print(f"unique_urls={len(unique_urls)}")

from datetime import datetime, timezone

def parse_price(price_text):
    cleaned = price_text.replace("£", "").strip()
    return float(cleaned)

def extract_book(book_url, source_page):
    book_html = fetch_page(book_url, book_url.rstrip("/").split("/")[-2] + ".html")
    book_soup = BeautifulSoup(book_html, "html.parser")

    title = book_soup.select_one("h1").text
    price_text = book_soup.select_one("p.price_color").text
    availability_text = book_soup.select_one("p.availability").text.strip()

    rating_tag = book_soup.select_one("p.star-rating")
    rating_text = rating_tag["class"][1]

    description_tag = book_soup.select_one("#product_description ~ p")
    description = description_tag.text if description_tag else None

    price_text = book_soup.select_one("p.price_color").text
    price_gbp = parse_price(price_text)

    return {
        "title": title,
        "product_url": book_url,
        "price_text": price_text,
        "price_gbp": price_gbp,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }


valid_records = []
invalid_records = []

for url, source_page in all_book_urls:
    raw = extract_book(url, source_page)
    try:
        validated = BookRecord(**raw)
        valid_records.append(validated.model_dump())
    except ValidationError as e:
        invalid_records.append({"url": url, "reason": str(e)})

print(f"valid={len(valid_records)}")
print(f"invalid={len(invalid_records)}")
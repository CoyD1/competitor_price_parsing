import re

import httpx
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def extract_price_from_html(html: str, price_selector: str) -> int:
    soup = BeautifulSoup(html, "html.parser")
    price_element = soup.select_one(price_selector)

    if not price_element:
        raise ValueError("Price element not found")
    
    price_text = price_element.get_text(strip=True)
    price_digits = re.sub(r"\D", "", price_text)

    if not price_digits:
        raise ValueError("Price text does not contain digits")
    
    return int(price_digits)

async def fetch_price_from_url(url: str, price_selector: str) -> int:
    async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
        response = await client.get(url, headers=DEFAULT_HEADERS)

    response.raise_for_status()

    return extract_price_from_html(response.text, price_selector)
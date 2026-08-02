import re
import asyncio 

import httpx
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from pathlib import Path

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

async def fetch_html_from_url(url: str) -> httpx.Response:
    async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
        response = await client.get(url, headers=DEFAULT_HEADERS)

    response.raise_for_status()

    return response

def fetch_html_with_browser_sync(url: str) -> str:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False, slow_mo=300)
        page = browser.new_page(extra_http_headers=DEFAULT_HEADERS,
                                viewport={"width": 1440, "height": 900},
        )

        page.goto(url, wait_until="networkidle", timeout=30000)
        page.screenshot(path="debug_dns.png", full_page=True)

        page.wait_for_timeout(10000)
        html = page.content()
        Path("debug_dns.html").write_text(html, encoding="utf-8")
        browser.close()

        return html

async def fetch_html_with_browser(url: str) -> str:
    return await asyncio.to_thread(fetch_html_with_browser_sync, url)

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
    response = await fetch_html_from_url(url)

    return extract_price_from_html(response.text, price_selector)
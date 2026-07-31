import re

from bs4 import BeautifulSoup


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
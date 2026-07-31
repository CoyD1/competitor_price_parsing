import pytest

from parser.price_parser import extract_price_from_html


def test_extract_price_from_html_by_class_selector():
    html = """
    <html>
      <body>
        <span class="product-price">12 990</span>
      </body>
    </html>
    """

    price = extract_price_from_html(html, ".product-price")

    assert price == 12990


def test_extract_price_from_html_with_extra_text():
    html = """
    <html>
      <body>
        <span class="product-price">Price: 15 500 rub</span>
      </body>
    </html>
    """

    price = extract_price_from_html(html, ".product-price")

    assert price == 15500


def test_extract_price_from_html_raises_when_selector_not_found():
    html = """
    <html>
      <body>
        <span class="other-price">12 990</span>
      </body>
    </html>
    """

    with pytest.raises(ValueError, match="Price element not found"):
        extract_price_from_html(html, ".product-price")


def test_extract_price_from_html_raises_when_price_has_no_digits():
    html = """
    <html>
      <body>
        <span class="product-price">not available</span>
      </body>
    </html>
    """

    with pytest.raises(ValueError, match="Price text does not contain digits"):
        extract_price_from_html(html, ".product-price")
"""Website scraping service."""

import re
import urllib3

import requests
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def scrape_website(url: str) -> str:
    """Download a webpage and return cleaned text content."""
    try:
        response = requests.get(
            url,
            timeout=10,
            verify=False,
            headers={
                "User-Agent": "Mozilla/5.0",
            },
        )
        response.raise_for_status()
    except Exception:
        return ""

    soup = BeautifulSoup(response.text, "html.parser")
    elements = soup.find_all(["p", "h1", "h2", "h3", "li", "article"])
    raw_text = " ".join(element.get_text(separator=" ", strip=True) for element in elements)
    cleaned_text = re.sub(r"\s+", " ", raw_text).strip()
    return cleaned_text

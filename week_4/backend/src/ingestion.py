from urllib.parse import quote_plus

import feedparser
import httpx
from bs4 import BeautifulSoup

SUPPORTED_TICKERS = {
    "1155": "Maybank",
    "5347": "Tenaga Nasional",
    "1295": "Public Bank",
    "1023": "CIMB Group",
    "5183": "Petronas Chemicals",
    "5225": "IHH Healthcare",
    "1066": "RHB Bank",
    "5819": "Hong Leong Bank",
    "6888": "Axiata Group",
    "6012": "Maxis",
    "4197": "Sime Darby",
    "5168": "Hartalega",
}


def is_supported(ticker: str) -> bool:
    return ticker in SUPPORTED_TICKERS


def get_company_name(ticker: str) -> str:
    return SUPPORTED_TICKERS.get(ticker, "Unknown Company")


def fetch_articles(ticker: str, max_articles: int = 5) -> list[dict]:
    """
    Fetch and clean news articles for a given Bursa ticker.
    Returns a list of dicts with keys: source, headline, text
    """
    company = get_company_name(ticker)
    query = quote_plus(f"{company} Bursa Malaysia stock")
    url = f"https://news.google.com/rss/search?q={query}&hl=en-MY&gl=MY&ceid=MY:en"

    feed = feedparser.parse(url)

    if not feed.entries:
        return []

    articles = []
    for entry in feed.entries[:max_articles]:
        try:
            headline = entry.get("title", "").strip()
            source = entry.get("source", {}).get("title", "Google News")

            # Use RSS summary first, fall back to fetching full article
            summary = entry.get("summary", "")
            summary_text = clean_html(summary)

            # Try to get full article text
            link = entry.get("link", "")
            full_text = fetch_article_text(link) if link else ""

            # Use whichever is longer
            text = full_text if len(full_text) > len(summary_text) else summary_text

            if headline and len(text) > 50:
                articles.append({
                    "source": source,
                    "headline": headline,
                    "text": text,
                })
        except Exception:
            continue

    return articles


def clean_html(html: str) -> str:
    """Strip HTML tags and return plain text."""
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(strip=True)


def fetch_article_text(url: str) -> str:
    """
    Fetch and clean the main text content from a news article URL.
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = httpx.get(
            url, headers=headers, timeout=10, follow_redirects=True
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()

        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text(strip=True) for p in paragraphs)

        return text[:3000]

    except Exception:
        return ""
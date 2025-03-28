import os
import pytest
from scraipe.scrapers.multi_scraper import MultiScraper
from scraipe.scrapers.telegram_scraper import TelegramScraper
from scraipe.scrapers.news_scraper import NewsScraper
from scraipe.scrapers.default_scraper import DefaultScraper
from scraipe.classes import ScrapeResult
from unittest.mock import MagicMock


TEST_TELEGRAM_URL = "https://t.me/TelegramTips/516"

@pytest.fixture
def mock_telegram_scraper():
    # Attempt to create a live Telegram scraper
    name = os.environ.get("TELEGRAM_NAME")
    api_id = os.environ.get("TELEGRAM_API_ID")
    api_hash = os.environ.get("TELEGRAM_API_HASH")
    phone_number = os.environ.get("TELEGRAM_PHONE_NUMBER")

    if all([name, api_id, api_hash, phone_number]):
        try:
            scraper = TelegramScraper(name, api_id, api_hash, phone_number)
            yield scraper
            scraper.disconnect()
            return
        except Exception as e:
            print(f"Failed to create live Telegram scraper: {e}")

    # Fallback to mock scraper
    class MockTelegramScraper:
        def scrape(self, url):
            if "valid" in url:
                return ScrapeResult(link=url, scrape_success=True, content="Mocked Telegram content")
            return ScrapeResult(link=url, scrape_success=False, scrape_error="Invalid Telegram link")
    
    yield MockTelegramScraper()

@pytest.fixture
def mock_news_scraper():
    class MockNewsScraper:
        def scrape(self, url):
            if "news" in url:
                return ScrapeResult(link=url, scrape_success=True, content="News content")
            return ScrapeResult(link=url, scrape_success=False, scrape_error="Not a news link")
    return MockNewsScraper()

@pytest.fixture
def mock_default_scraper():
    class MockDefaultScraper:
        def scrape(self, url):
            return ScrapeResult(link=url, scrape_success=True, content="Default content")
    return MockDefaultScraper()

@pytest.fixture
def multi_scraper(mock_telegram_scraper, mock_news_scraper, mock_default_scraper):
    return MultiScraper(
        telegram_scraper=mock_telegram_scraper,
        news_scraper=mock_news_scraper,
        default_scraper=mock_default_scraper
    )

def test_telegram_scraper(multi_scraper):
    if isinstance(multi_scraper.telegram_scraper, TelegramScraper):
        url = TEST_TELEGRAM_URL
    else:
        url = "https://t.me/valid"
    result = multi_scraper.scrape(url)
    assert result.success
    assert len(result.content) > 0

def test_news_scraper(multi_scraper):
    url = "https://example.com/news"
    result = multi_scraper.scrape(url)
    assert result.success
    assert result.content == "News content"

def test_default_scraper(multi_scraper):
    url = "https://example.com/other"
    result = multi_scraper.scrape(url)
    assert result.success
    assert result.content == "Default content"
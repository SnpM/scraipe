import re
import pytest
from scraipe.extended.telegram_news_scraper import TelegramNewsScraper
from scraipe.classes import ScrapeResult, IScraper


# Dummy telegram scraper that returns success.
class DummyTelegramScraper(IScraper):
    def scrape(self, url: str):
        return ScrapeResult.succeed(url, "Telegram content")
    def __str__(self):
        return "DummyTelegramScraper"
    async def async_scrape(self, url: str):
        return self.scrape(url)

# Dummy news scraper that returns success.
class DummyNewsScraper(IScraper):
    def scrape(self, url: str):
        return ScrapeResult.succeed(url, "News content")
    def __str__(self):
        return "DummyNewsScraper"
    async def async_scrape(self, url: str):
        return self.scrape(url)

# Dummy aiohttp scraper that returns success.
class DummyAiohttpScraper(IScraper):
    def scrape(self, url: str):
        return ScrapeResult.succeed(url, "Aiohttp content")
    def __str__(self):
        return "DummyAiohttpScraper"
    async def async_scrape(self, url: str):
        return self.scrape(url)

# Dummy failure scraper that always fails.
class DummyFailureScraper(IScraper):
    def scrape(self, url: str):
        return ScrapeResult.fail(url, "failed")
    def __str__(self):
        return "DummyFailureScraper"
    async def async_scrape(self, url: str):
        return self.scrape(url)

def test_telegram_rule_success():
    # URL matching telegram rule.
    url = "https://t.me/username/1234"
    scraper = TelegramNewsScraper(
        telegram_scraper=DummyTelegramScraper(),
        news_scraper=DummyNewsScraper(),
        text_scraper=DummyAiohttpScraper()
    )
    result = scraper.scrape(url)
    assert result.scrape_success
    assert result.content == "Telegram content"

def test_news_rule_success():
    # Non-telegram URL: telegram rule is not triggered.
    url = "http://news.example.com/article"
    scraper = TelegramNewsScraper(
        telegram_scraper=DummyFailureScraper(),
        news_scraper=DummyNewsScraper(),
        text_scraper=DummyAiohttpScraper()
    )
    result = scraper.scrape(url)
    assert result.scrape_success
    assert result.content == "News content"

def test_aiohttp_fallback():
    # Both telegram and news fail; fallback to aiohttp scraper.
    url = "http://news.example.com/article"
    scraper = TelegramNewsScraper(
        telegram_scraper=DummyFailureScraper(),
        news_scraper=DummyFailureScraper(),
        text_scraper=DummyAiohttpScraper(),
        debug=True,
    )
    result = scraper.scrape(url)
    assert result.scrape_success
    assert result.content == "Aiohttp content"
    # Check that errors from failing scrapers are present.
    assert "DummyFailureScraper[FAIL]: failed" in result.scrape_error
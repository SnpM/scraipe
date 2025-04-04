import os
import pytest
import asyncio
from scraipe.extras import MultiScraper
from scraipe.extras import TelegramScraper
from scraipe.classes import ScrapeResult
from scraipe.extras.multi_scraper import MultiScraper
from unittest.mock import MagicMock


TEST_TELEGRAM_URL = "https://t.me/TelegramTips/516"

# Dummy scrapers for testing
class DummyTelegramScraper:
    async def async_scrape(self, url: str) -> ScrapeResult:
        return ScrapeResult.success(link=url, content="telegram content")

class DummyNewsScraperSuccess:
    async def async_scrape(self, url: str) -> ScrapeResult:
        return ScrapeResult.success(link=url, content="news content")

class DummyNewsScraperFail:
    async def async_scrape(self, url: str) -> ScrapeResult:
        return ScrapeResult.fail(link=url, error="news scrape failed")

class DummyDefaultScraper:
    async def async_scrape(self, url: str) -> ScrapeResult:
        return ScrapeResult.success(link=url, content="default content")

@pytest.mark.asyncio
async def test_telegram_scrape_success():
    scraper = MultiScraper(telegram_scraper=DummyTelegramScraper())
    result = await scraper.async_scrape("https://t.me/somechannel")
    # Expect telegram branch to return success
    assert result.scrape_success
    assert result.content == "telegram content"

@pytest.mark.asyncio
async def test_telegram_scrape_failure():
    # No telegram scraper provided, so telegram branch should return failure.
    scraper = MultiScraper()
    result = await scraper.async_scrape("https://t.me/somechannel")
    assert not result.scrape_success
    assert result.scrape_error == "Telegram scraper not configured."

@pytest.mark.asyncio
async def test_news_scrape_success():
    # Provide a news scraper that succeeds.
    scraper = MultiScraper(telegram_scraper=DummyTelegramScraper(), news_scraper=DummyNewsScraperSuccess())
    result = await scraper.async_scrape("https://news.example.com/article")
    assert result.scrape_success
    assert result.content == "news content"

@pytest.mark.asyncio
async def test_default_scrape_fallback():
    # When news scraping fails, default scraper should be used.
    scraper = MultiScraper(news_scraper=DummyNewsScraperFail(), default_scraper=DummyDefaultScraper())
    result = await scraper.async_scrape("https://example.com/page")
    assert result.scrape_success
    assert result.content == "default content"
    

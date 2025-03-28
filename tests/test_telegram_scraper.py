import pytest
from scraipe.scrapers.telegram_scraper import TelegramScraper
from scraipe.classes import ScrapeResult
from unittest.mock import AsyncMock, patch, MagicMock

TEST_URL = "https://t.me/TelegramTips/516"

@pytest.fixture
def live_scraper():
    # Load telethon credentials from the environment
    import os
    name = os.environ.get("TELEGRAM_NAME")
    api_id = os.environ.get("TELEGRAM_API_ID")
    api_hash = os.environ.get("TELEGRAM_API_HASH")
    phone_number = os.environ.get("TELEGRAM_PHONE_NUMBER")
    if not all([name, api_id, api_hash, phone_number]):
        return None
    scraper =  TelegramScraper(name, api_id, api_hash, phone_number)
    yield scraper
    scraper.disconnect()

@pytest.fixture
def mock_scraper():
    with patch("scraipe.scrapers.telegram_scraper.TelegramClient") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_client.connect = AsyncMock()
        mock_client.get_entity = AsyncMock()
        mock_client.get_messages = AsyncMock()
        scraper = TelegramScraper("mock_name", "mock_api_id", "mock_api_hash", "mock_phone_number")
        scraper.client = mock_client
        yield scraper
        scraper.disconnect()

def test_live_scrape_valid_url(live_scraper):
    if live_scraper is None:
        pytest.skip("Live scraper credentials are not set in the environment.")
    url = TEST_URL
    result = live_scraper.scrape(url)
    assert isinstance(result, ScrapeResult)
    assert result.scrape_success
    assert result.link == url
    assert result.content is not None

def test_live_scrape_invalid_url(live_scraper):
    if live_scraper is None:
        pytest.skip("Live scraper credentials are not set in the environment.")
    url = "https://example.com/invalid"
    result = live_scraper.scrape(url)
    assert isinstance(result, ScrapeResult)
    assert not result.scrape_success
    assert "not a telegram link" in result.scrape_error

def test_live_scrape_nonexistent_message(live_scraper):
    if live_scraper is None:
        pytest.skip("Live scraper credentials are not set in the environment.")
    url = TEST_URL.replace("516", "1000000")
    result = live_scraper.scrape(url)
    assert isinstance(result, ScrapeResult)
    assert result.scrape_success == False
    assert result.content is None

def test_mock_scrape_valid_url(mock_scraper):
    mock_scraper.client.get_entity.return_value = MagicMock(restricted=False)
    mock_scraper.client.get_messages.return_value = MagicMock(message="Mocked message content")
    url = "https://t.me/mock_channel/123"
    result = mock_scraper.scrape(url)
    assert isinstance(result, ScrapeResult)
    assert result.scrape_success
    assert result.link == url
    assert result.content == "Mocked message content"

def test_mock_scrape_restricted_entity(mock_scraper):
    mock_scraper.client.get_entity.return_value = MagicMock(restricted=True)
    url = "https://t.me/mock_channel/123"
    result = mock_scraper.scrape(url)
    assert isinstance(result, ScrapeResult)
    assert not result.scrape_success
    assert "restricted" in result.scrape_error

def test_mock_scrape_nonexistent_message(mock_scraper):
    mock_scraper.client.get_entity.return_value = MagicMock(restricted=False)
    mock_scraper.client.get_messages.return_value = None
    url = "https://t.me/mock_channel/10000000"
    result = mock_scraper.scrape(url)
    assert isinstance(result, ScrapeResult)
    assert result.scrape_success == False
    assert result.content is None


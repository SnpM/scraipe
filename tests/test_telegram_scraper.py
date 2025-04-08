import pytest
from scraipe.extended.telegram_message_scraper import TelegramMessageScraper
from scraipe.classes import ScrapeResult
from unittest.mock import AsyncMock, patch, MagicMock

TARGET_MODULE = TelegramMessageScraper.__module__

TEST_URL = "https://t.me/TelegramTips/515"


@pytest.fixture
def live_scraper():
    # Load telethon credentials from the environment
    import os
    name = os.environ.get("TELEGRAM_NAME")
    api_id = os.environ.get("TELEGRAM_API_ID")
    api_hash = os.environ.get("TELEGRAM_API_HASH")
    phone_number = os.environ.get("TELEGRAM_PHONE_NUMBER")
    if not all([name, api_id, api_hash, phone_number]):
        pytest.skip("Live scraper credentials are not set in the environment.")
    scraper =  TelegramMessageScraper(name, api_id, api_hash, phone_number)
    yield scraper
    scraper.disconnect()

@pytest.fixture
def mock_scraper():
    with patch(TARGET_MODULE + ".Client") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)  # added for async context manager
        mock_client.__aexit__ = AsyncMock(return_value=None)            # added for async context manager
        mock_client.start = AsyncMock()
        mock_client.connect = AsyncMock(return_value=True)             # NEW: add async connect
        mock_client.disconnect = AsyncMock(return_value=None)          # NEW: add async disconnect
        mock_client.get_chat = AsyncMock()
        mock_client.get_messages = AsyncMock()
        scraper = TelegramMessageScraper("mock_name", "mock_api_id", "mock_api_hash", "mock_phone_number")
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
    url = TEST_URL.replace("515", "1000000")
    result = live_scraper.scrape(url)
    assert isinstance(result, ScrapeResult)
    assert result.scrape_success == False
    assert result.content is None

def test_mock_scrape_valid_url(mock_scraper):
    mock_scraper.client.get_chat.return_value = MagicMock(restricted=False)
    mock_scraper.client.get_messages.return_value.text = "Mocked message content"
    url = "https://t.me/mock_channel/123"
    result = mock_scraper.scrape(url)
    assert isinstance(result, ScrapeResult)
    assert result.scrape_success
    assert result.link == url
    assert result.content == "Mocked message content"

def test_mock_scrape_restricted_entity(mock_scraper):
    mock_scraper.client.get_chat.return_value = MagicMock(restricted=True)
    url = "https://t.me/mock_channel/123"
    result = mock_scraper.scrape(url)
    assert isinstance(result, ScrapeResult)
    assert not result.scrape_success
    assert "restricted" in result.scrape_error

def test_mock_scrape_nonexistent_message(mock_scraper):
    mock_scraper.client.get_chat.return_value = MagicMock(restricted=False)
    mock_scraper.client.get_messages.side_effect = Exception("Message not found")
    url = "https://t.me/mock_channel/10000000"
    result = mock_scraper.scrape(url)
    assert isinstance(result, ScrapeResult)
    assert result.scrape_success == False
    assert result.content is None


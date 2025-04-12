import pytest
from scraipe.extended.telegram_message_scraper import TelegramMessageScraper
from scraipe.classes import ScrapeResult
from unittest.mock import AsyncMock, patch, MagicMock
import os

TARGET_MODULE = TelegramMessageScraper.__module__

TEST_URL = "https://t.me/TelegramTips/515"


@pytest.fixture
def live_scraper():
    # Load telethon credentials from the environment
    import os
    session_name = "telegram_tests"
    api_id = os.environ.get("TELEGRAM_API_ID")
    api_hash = os.environ.get("TELEGRAM_API_HASH")
    phone_number = os.environ.get("TELEGRAM_PHONE_NUMBER")
    if not all([session_name, api_id, api_hash, phone_number]):
        pytest.skip("Live scraper credentials are not set in the environment.")
    scraper = TelegramMessageScraper(api_id, api_hash, phone_number, session_name=session_name)
    yield scraper
    scraper.disconnect()

@pytest.fixture
def mock_scraper():
    with patch(TARGET_MODULE + ".TelegramClient") as MockClient:  # modified patch target
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)  # added for async context manager
        mock_client.__aexit__ = AsyncMock(return_value=None)            # added for async context manager
        mock_client.start = AsyncMock()
        mock_client.connect = AsyncMock(return_value=True)             # NEW: add async connect
        mock_client.disconnect = AsyncMock(return_value=None)          # NEW: add async disconnect
        mock_client.get_entity = AsyncMock()
        mock_client.get_messages = AsyncMock()
        mock_client.is_user_authorized = AsyncMock(return_value=True)  # Mocking is_user_authorized to always return True
        
        # Patch TelegramMessageScraper.authenticate to do nothing
        with patch(TARGET_MODULE + ".TelegramMessageScraper.authenticate", return_value=True):
            scraper = TelegramMessageScraper("mock_name", "mock_api_id", "mock_api_hash", "mock_phone_number")
            scraper.session_string = ""
            scraper.client = mock_client
            yield scraper
            scraper.disconnect()

def test_live_scrape_valid_url(request,live_scraper):
    skip_if_no_capture(request)
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
    mock_scraper.client.get_entity.return_value = MagicMock(restricted=False)
    mock_scraper.client.get_messages.return_value.message = "Mocked message content"
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
    mock_scraper.client.get_messages.side_effect = Exception("Message not found")
    url = "https://t.me/mock_channel/10000000"
    result = mock_scraper.scrape(url)
    assert isinstance(result, ScrapeResult)
    assert result.scrape_success == False
    assert result.content is None
    
def skip_if_no_capture(request):
    import sys, _io
    capture_option = request.config.option.capture
    if capture_option != "no":
        pytest.skip("The -s flag is not set. Test requires interaction.")

@pytest.mark.skipif(os.environ.get("QR") is None, reason="QR is not set")    
def test_qrcode_login(request):
    skip_if_no_capture(request)
        
    # Load telethon credentials from the environment
    api_id = os.environ.get("TELEGRAM_API_ID")
    api_hash = os.environ.get("TELEGRAM_API_HASH")
    phone_number = os.environ.get("TELEGRAM_PHONE_NUMBER")
    if not all([api_id, api_hash, phone_number]):
        pytest.skip("Live scraper credentials are not set in the environment.")
        
    scraper = TelegramMessageScraper(api_id, api_hash, phone_number, session_name=None, use_qr_login=True)
    scrape_result = scraper.scrape(TEST_URL)
    assert scrape_result.scrape_success
    
@pytest.mark.asyncio
@pytest.mark.skipif(os.environ.get("QR") is None, reason="QR is not set")
async def test_qrcode_login_async(request):
    skip_if_no_capture(request)
        
    # Load telethon credentials from the environment
    api_id = os.environ.get("TELEGRAM_API_ID")
    api_hash = os.environ.get("TELEGRAM_API_HASH")
    phone_number = os.environ.get("TELEGRAM_PHONE_NUMBER")
    if not all([api_id, api_hash, phone_number]):
        pytest.skip("Live scraper credentials are not set in the environment.")

    scraper = TelegramMessageScraper(api_id, api_hash, phone_number, session_name=None, use_qr_login=True, sync_auth=False)
    url = scraper.get_qr_url()
    import qrcode
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.make(fit=True)
    print("Scan from Telegram app for the test:")
    qr.print_ascii()
    
    import asyncio
    acc = 0
    while not scraper.is_authenticated():
        POLL_INTERVAL = .1
        await asyncio.sleep(POLL_INTERVAL)
        acc += POLL_INTERVAL
        if acc > 15:
            raise TimeoutError("QR code login timed out.")
    
    scrape_result = scraper.scrape(TEST_URL)
    assert scrape_result.scrape_success
    
    
# @pytest.mark.asyncio
# async def test_telethon_client():
#     from telethon import TelegramClient
#     from telethon.sessions import StringSession
#     name = os.environ.get("TELEGRAM_NAME")
#     api_id = os.environ.get("TELEGRAM_API_ID")
#     api_hash = os.environ.get("TELEGRAM_API_HASH")
#     phone_number = os.environ.get("TELEGRAM_PHONE_NUMBER")
#     if not all([name, api_id, api_hash, phone_number]):
#         pytest.skip("Live scraper credentials are not set in the environment.")

#     session = StringSession()
#     client = TelegramClient(session, api_id=int(api_id), api_hash=api_hash)
#     await client.connect()
#     if not await client.is_user_authorized():
#         pytest.skip("Telethon client not authorized.")
#     await client.disconnect()
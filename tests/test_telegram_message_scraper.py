import pytest
from scraipe.extended.telegram_message_scraper import TelegramMessageScraper, AuthState, LoginType, QrLoginContext
from scraipe.classes import ScrapeResult
from unittest.mock import AsyncMock, patch, MagicMock
import os
import asyncio

from tests.common import skip_if_no_capture

TARGET_MODULE = TelegramMessageScraper.__module__

TEST_URL = "https://t.me/TelegramTips/515"

IMAGE_URL = "https://t.me/binancesignals/45"


@pytest.fixture
def live_scraper(request):
    # Load telethon credentials from the environment
    import os
    session_name = "telegram_tests"
    api_id = os.environ.get("TELEGRAM_API_ID")
    api_hash = os.environ.get("TELEGRAM_API_HASH")
    phone_number = os.environ.get("TELEGRAM_PHONE_NUMBER")
    if not all([session_name, api_id, api_hash, phone_number]):
        pytest.skip("Live scraper credentials are not set in the environment.")
    scraper = TelegramMessageScraper(api_id, api_hash, phone_number, session_name=session_name, sync_auth=True, defer_auth=True)
    
    if scraper.requires_interaction():
        skip_if_no_capture(request)
        
    scraper.authenticate()
        
    yield scraper

@pytest.fixture
def mock_scraper():
    # Create a mock telethon.TelegramClient
    
    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client) 
    mock_client.__aexit__ = AsyncMock(return_value=None)    
    mock_client.start = AsyncMock()
    mock_client.connect = AsyncMock(return_value=True)           
    mock_client.disconnect = AsyncMock(return_value=None)
    mock_client.get_entity = AsyncMock()
    mock_client.get_messages = AsyncMock()
    mock_client.is_user_authorized = AsyncMock(return_value=True)
    mock_client.is_connected = AsyncMock(return_value=False)
    
    # Patch TelegramMessageScraper.authenticate to do nothing
    with patch(TARGET_MODULE + ".TelegramMessageScraper.authenticate", return_value=AuthState.AUTHENTICATED):
        # Patch function to return the mock client
        with patch(TARGET_MODULE + ".TelegramMessageScraper._authenticated_client", return_value=mock_client):
            scraper = TelegramMessageScraper(api_id="mock_api_id",api_hash= "mock_api_hash", phone_number="mock_phone_number")
            scraper.session_string = ""
            scraper.client = mock_client
            yield scraper

def test_live_scrape_valid_url(request,live_scraper):
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
    assert result.scrape_error is not None

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
    
def test_image_message_live(live_scraper):
    if live_scraper is None:
        pytest.skip("Live scraper credentials are not set in the environment.")
    url = IMAGE_URL
    result = live_scraper.scrape(url)
    assert isinstance(result, ScrapeResult)
    assert result.scrape_success
    assert result.link == url
    assert result.content is not None
    

@pytest.mark.skipif(os.environ.get("QR") is None, reason="QR environment flag is not set")    
def test_qrcode_login(request):
    skip_if_no_capture(request)
        
    # Load telethon credentials from the environment
    api_id = os.environ.get("TELEGRAM_API_ID")
    api_hash = os.environ.get("TELEGRAM_API_HASH")
    phone_number = os.environ.get("TELEGRAM_PHONE_NUMBER")
    if not all([api_id, api_hash, phone_number]):
        pytest.skip("Live scraper credentials are not set in the environment.")
        
    scraper = TelegramMessageScraper(api_id, api_hash, phone_number, session_name=None, login_type=LoginType.QRCode)
    scrape_result = scraper.scrape(TEST_URL)
    assert scrape_result.scrape_success
    
@pytest.mark.asyncio
@pytest.mark.skipif(os.environ.get("QR") is None, reason="QR environment flag is not set")
async def test_qrcode_login_async(request):
    skip_if_no_capture(request)
        
    # Load telethon credentials from the environment
    api_id = os.environ.get("TELEGRAM_API_ID")
    api_hash = os.environ.get("TELEGRAM_API_HASH")
    phone_number = os.environ.get("TELEGRAM_PHONE_NUMBER")
    if not all([api_id, api_hash, phone_number]):
        pytest.skip("Live scraper credentials are not set in the environment.")

    scraper = TelegramMessageScraper(api_id, api_hash, phone_number, session_name=None,
                                    login_type=LoginType.QRCode,
                                    sync_auth=False)
    login_context: QrLoginContext = scraper.login_context
    url = login_context.get_qr_url()
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
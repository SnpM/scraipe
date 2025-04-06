import pytest
from unittest.mock import patch, MagicMock, AsyncMock  # added import for asynchronous mocks
from scraipe.defaults.TextScraper import TextScraper
from scraipe import ScrapeResult, AnalysisResult

TARGET_MODULE = TextScraper.__module__


def test_default_headers():
    scraper = TextScraper()
    assert scraper.headers == {"User-Agent": TextScraper.DEFAULT_USER_AGENT}


def test_custom_headers():
    custom_headers = {"User-Agent": "CustomAgent/1.0"}
    scraper = TextScraper(headers=custom_headers)
    assert scraper.headers == custom_headers


@patch("aiohttp.ClientSession")
def test_scrape_success(mock_session_cls):
    # Create an async mock response
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.text = AsyncMock(return_value="Mocked response content")
    # Create a mock session whose get returns an async context manager yielding mock_response
    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response
    mock_session_cls.return_value.__aenter__.return_value = mock_session

    scraper = TextScraper()
    scrape_result: ScrapeResult = scraper.scrape("https://google.com")
    assert scrape_result.scrape_success, f"Scrape failed: {scrape_result.scrape_error}"
    assert scrape_result.content == "Mocked response content"


@patch("aiohttp.ClientSession")
def test_scrape_failure(mock_session_cls):
    # Setup mock session to raise an exception on get call
    mock_session = MagicMock()
    mock_session.get.side_effect = Exception("Request failed")
    mock_session_cls.return_value.__aenter__.return_value = mock_session

    scraper = TextScraper()
    result = scraper.scrape("https://invalid-url-aoietasdnlkbxjcnweaituh.com")
    assert result.scrape_success == False


def test_scrape_google():
    # Check if connection to google succeeds
    import requests
    if not requests.get("https://www.google.com").status_code == 200:
        pytest.skip("Could not connect to google.com")
        return

    scraper = TextScraper()
    result = scraper.scrape("https://www.google.com")
    assert result.scrape_success
    assert isinstance(result.content, str)
    assert len(result.content) > 0
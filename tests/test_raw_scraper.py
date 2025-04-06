import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from scraipe.defaults.raw_scraper import RawScraper
from scraipe import ScrapeResult

@pytest.mark.asyncio
async def test_default_headers():
    scraper = RawScraper()
    assert scraper.headers == {"User-Agent": RawScraper.DEFAULT_USER_AGENT}

@pytest.mark.asyncio
async def test_custom_headers():
    custom_headers = {"User-Agent": "CustomAgent/1.0"}
    scraper = RawScraper(headers=custom_headers)
    assert scraper.headers == custom_headers

@pytest.mark.asyncio
@patch("aiohttp.ClientSession")
async def test_scrape_success(mock_session_cls):
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.text = AsyncMock(return_value="Mocked raw content")
    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response
    mock_session_cls.return_value.__aenter__.return_value = mock_session

    scraper = RawScraper()
    result: ScrapeResult = await scraper.async_scrape("https://example.com")
    assert result.scrape_success, f"Scrape failed: {result.scrape_error}"
    assert result.content == "Mocked raw content"

@pytest.mark.asyncio
@patch("aiohttp.ClientSession")
async def test_scrape_non_200(mock_session_cls):
    mock_response = MagicMock()
    mock_response.status = 404
    mock_response.text = AsyncMock(return_value="Not Found")
    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response
    mock_session_cls.return_value.__aenter__.return_value = mock_session

    scraper = RawScraper()
    result: ScrapeResult = await scraper.async_scrape("https://example.com")
    assert not result.scrape_success
    assert "Status code: 404" in result.scrape_error

@pytest.mark.asyncio
@patch("aiohttp.ClientSession")
async def test_scrape_exception(mock_session_cls):
    mock_session = MagicMock()
    mock_session.get.side_effect = Exception("Request failed")
    mock_session_cls.return_value.__aenter__.return_value = mock_session

    scraper = RawScraper()
    result: ScrapeResult = await scraper.async_scrape("https://example.com")
    assert not result.scrape_success
    assert "Request failed" in result.scrape_error
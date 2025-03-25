import pytest
from unittest.mock import patch, MagicMock
from scraipe.scrapers.default_scraper import DefaultScraper
from scraipe import ScrapeResult,AnalysisResult


def test_default_headers():
    scraper = DefaultScraper()
    assert scraper.headers == {"User-Agent": DefaultScraper.DEFAULT_USER_AGENT}


def test_custom_headers():
    custom_headers = {"User-Agent": "CustomAgent/1.0"}
    scraper = DefaultScraper(headers=custom_headers)
    assert scraper.headers == custom_headers


@patch("scraipe.scrapers.default_scraper.requests.get")
def test_scrape_success(mock_get):
    mock_response = MagicMock()
    mock_response.text = "Mocked response content"
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    scraper = DefaultScraper()
    scrape_result:ScrapeResult = scraper.scrape("https://google.com")
    assert scrape_result.success, f"Scrape failed: {scrape_result.error}"
    assert scrape_result.content == "Mocked response content"
    mock_get.assert_called_once_with("https://google.com", headers=scraper.headers)


@patch("scraipe.scrapers.default_scraper.requests.get")
def test_scrape_failure(mock_get):
    mock_get.side_effect = Exception("Request failed")

    scraper = DefaultScraper()
    result = scraper.scrape("https://invalid-url-aoietasdnlkzbxjcnweaituh.com")
    assert result.success == False
    
def test_scrape_google():
    # Check if connection to google succeeds
    import requests
    if not requests.get("https://www.google.com").status_code == 200:
        pytest.skip("Could not connect to google.com")
        return
        
    scraper = DefaultScraper()
    result = scraper.scrape("https://www.google.com")
    assert result.success
    assert isinstance(result.content, str)
    assert len(result.content) > 0
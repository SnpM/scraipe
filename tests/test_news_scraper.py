import pytest
from unittest.mock import patch, Mock
from scraipe.extras.news_scraper import NewsScraper
from scraipe.classes import ScrapeResult

TARGET_MODULE = NewsScraper.__module__

@pytest.fixture
def scraper():
    return NewsScraper()

@patch(f"{TARGET_MODULE}.requests.get")
def test_scrape_success(mock_get, scraper):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>Sample content</body></html>"
    mock_get.return_value = mock_response

    with patch(f"{TARGET_MODULE}.trafilatura.extract", return_value="Extracted content"):
        result = scraper.scrape("http://example.com")
        assert result.scrape_success is True
        assert result.content == "Extracted content"
        assert result.link == "http://example.com"

@patch(f"{TARGET_MODULE}.requests.get")
def test_scrape_failure_status_code(mock_get, scraper):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    result = scraper.scrape("http://example.com")
    assert result.scrape_success is False
    assert result.content is None
    assert "Status code: 404" in result.scrape_error

@patch(f"{TARGET_MODULE}.requests.get")
def test_scrape_failure_exception(mock_get, scraper):
    mock_get.side_effect = Exception("Connection error")

    result = scraper.scrape("http://example.com")
    assert result.scrape_success is False
    assert result.content is None
    assert "Error: Connection error" in result.scrape_error

def test_scrape_apnews_article_real_request(scraper):
    url = "https://apnews.com/article/book-review-david-szalay-flesh-b05fbda57b6123de8eddd931bae3e3fc"
    crib = "When that relationship ends in tragedy and violence"
    # Ensure connection works; if not, skip
    import requests
    try:
        response = requests.get(url)
        if response.status_code != 200:
            pytest.skip(f"Failed to connect to {url}. Status code: {response.status_code}")
    except requests.RequestException as e:
        pytest.skip(f"Failed to connect to {url}. Error: {e}")
    result = scraper.scrape(url)
    assert result.scrape_success is True
    assert crib in result.content
    assert result.link == url


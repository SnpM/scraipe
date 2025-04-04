import pytest
from scraipe.defaults.example_scraper import ExampleScraper

def test_scrape_success():
    # ...existing test setup...
    url = "http://example.com"
    scraper = ExampleScraper()
    result = scraper.scrape(url)
    # Assertions to verify scraper behavior
    assert result.link == url
    assert url in result.content
    # ...additional assertions if needed...

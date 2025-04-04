import asyncio
import pytest
from scraipe.classes import ScrapeResult
from scraipe.async_classes import IAsyncScraper

# Dummy subclass with a concrete implementation for testing
class DummyScraper(IAsyncScraper):
    async def async_scrape(self, url: str) -> ScrapeResult:
        # Dummy implementation returning a simple ScrapeResult
        return ScrapeResult.success(link=url, content=f"content for {url}")

@pytest.mark.asyncio
async def test_async_scrape():
    scraper = DummyScraper()
    url = "http://example.com"
    result = await scraper.async_scrape(url)
    assert result.link == url
    assert result.content == f"content for {url}"

def test_scrape():
    scraper = DummyScraper()
    url = "http://example.com/sync"
    result = scraper.scrape(url)
    assert result.link == url
    assert result.content == f"content for {url}"

def test_scrape_multiple():
    scraper = DummyScraper()
    urls = ["http://example.com/sync1", "http://example.com/sync2"]
    results = {}
    for url, result in scraper.scrape_multiple(urls):
        results[url] = result
    
    assert len(results) == len(urls)
    assert set(results.keys()) == set(urls)
    for url in urls:
        assert results[url].link == url
        assert results[url].content == f"content for {url}"
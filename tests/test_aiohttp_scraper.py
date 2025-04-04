import pytest
from aioresponses import aioresponses
from scraipe.extended.aiohttp_scraper import AiohttpScraper
from scraipe.classes import ScrapeResult

@pytest.mark.asyncio
async def test_async_scrape_success():
    url = "http://example.com"
    html = "<html><body><p>Test Content</p></body></html>"
    scraper = AiohttpScraper()
    
    with aioresponses() as m:
        m.get(url, status=200, body=html)
        result: ScrapeResult = await scraper.async_scrape(url)
    
    # Check if the scrape is successful and content is parsed (bs4 removes extra newlines)
    assert result.scrape_success is True
    assert "Test Content" in result.content

@pytest.mark.asyncio
async def test_async_scrape_non_200():
    url = "http://example.com/404"
    scraper = AiohttpScraper()
    
    with aioresponses() as m:
        m.get(url, status=404, body="Not Found")
        result: ScrapeResult = await scraper.async_scrape(url)
    
    # Check if the scrape fails due to non-200 status code
    assert result.scrape_success is False
    assert "Status code: 404" in result.scrape_error

@pytest.mark.asyncio
async def test_async_scrape_exception():
    url = "http://example.com/error"
    scraper = AiohttpScraper()
    
    with aioresponses() as m:
        m.get(url, exception=Exception("Test Exception"))
        result: ScrapeResult = await scraper.async_scrape(url)
    
    # Check if the scrape fails due to exception
    assert result.scrape_success is False
    assert "Test Exception" in result.scrape_error
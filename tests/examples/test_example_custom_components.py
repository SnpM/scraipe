import pytest
import asyncio
from examples.example_custom_components import ExampleScraper, AsyncExampleScraper, AsyncExampleAnalyzer

def test_scrape_success():
    # ...existing test setup...
    url = "http://example.com"
    scraper = ExampleScraper()
    result = scraper.scrape(url)
    # Assertions to verify scraper behavior
    assert result.link == url
    assert url in result.content
    # ...additional assertions if needed...

def test_analyze_success():
    # ...existing test setup...
    url = "http://example.com"
    scraper = ExampleScraper()
    result = scraper.scrape(url)
    # Assertions to verify scraper behavior
    assert result.link == url
    assert url in result.content
    # ...additional assertions if needed...

@pytest.mark.asyncio
async def test_async_scrape_success():
    url = "http://example.com"
    scraper = AsyncExampleScraper()
    result = await scraper.async_scrape(url)
    # Assertions to verify async scraper behavior
    assert result.link == url
    assert url in result.content

@pytest.mark.asyncio
async def test_async_analyze_success():
    content = "hello world"
    analyzer = AsyncExampleAnalyzer()
    result = await analyzer.async_analyze(content)
    # Verify that the content was reversed in the output
    assert result.output.get("reversed_content") == content[::-1]
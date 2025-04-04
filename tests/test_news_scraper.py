import pytest
from scraipe.extended.news_scraper import NewsScraper
import trafilatura

@pytest.mark.asyncio
async def test_async_scrape_success(monkeypatch):
    # ...existing setup...
    scraper = NewsScraper()
    async def dummy_get_site_html(url: str):
        return "<html>dummy content</html>"
    scraper.get_site_html = dummy_get_site_html

    def dummy_extract(html, url, output_format):
        return "extracted text"
    monkeypatch.setattr(trafilatura, "extract", dummy_extract)

    result = await scraper.async_scrape("http://dummy.url")
    # Assuming ScrapeResult.success sets content to the extracted text.
    assert result.content == "extracted text"
    # ...additional assertions as needed...

@pytest.mark.asyncio
async def test_async_scrape_fail_get_html(monkeypatch):
    # ...existing setup...
    scraper = NewsScraper()
    async def dummy_get_site_html(url: str):
        raise Exception("network error")
    scraper.get_site_html = dummy_get_site_html

    result = await scraper.async_scrape("http://dummy.url")
    # Expect error message from the inner try-except
    assert "Failed to get page" in result.scrape_error

@pytest.mark.asyncio
async def test_async_scrape_fail_no_content(monkeypatch):
    # ...existing setup...
    scraper = NewsScraper()
    async def dummy_get_site_html(url: str):
        return "<html>dummy content</html>"
    scraper.get_site_html = dummy_get_site_html

    def dummy_extract(html, url, output_format):
        return None
    monkeypatch.setattr(trafilatura, "extract", dummy_extract)

    result = await scraper.async_scrape("http://dummy.url")
    # Expect error message indicating no content was extracted
    assert "No content extracted" in result.scrape_error

def test_live_scrape():
    url = "https://apnews.com/article/book-review-david-szalay-flesh-b05fbda57b6123de8eddd931bae3e3fc"
    begin_crib = "Istvan, the protagonist in David Szalay’s new novel"
    end_crib = "letting these simple interactions tell a tragic story."
    scraper = NewsScraper()
    result = scraper.scrape(url)  # synchronous scrape() call
    assert result.scrape_success
    
    assert begin_crib in result.content
    assert end_crib in result.content
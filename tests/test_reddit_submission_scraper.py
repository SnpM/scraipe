import os
import pytest
import pytest_asyncio
from asyncpraw import Reddit
from scraipe.extended.reddit_submission_scraper import RedditSubmissionScraper
from scraipe.classes import ScrapeResult

@pytest_asyncio.fixture
async def live_scraper():
    """Load Reddit credentials from the environment."""
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    
    if not all([client_id, client_secret]):
        pytest.skip("Live Reddit credentials are not set in the environment.")
    
    scraper = RedditSubmissionScraper(
        client_id=client_id,
        client_secret=client_secret,
        comment_inclusion='both')
    yield scraper

@pytest.mark.asyncio
async def test_reddit_post_scraper(live_scraper:RedditSubmissionScraper):
    # Test the RedditPostScraper on a real Reddit post.
    url = "https://www.reddit.com/r/test/comments/lb7prn/back_when_dinosaurs_existed_there_used_to_be/"
    # Instantiate the scraper with both comment content and metadata.
    
    result: ScrapeResult = await live_scraper.async_scrape(url)
    
    print(result)
    
    # Verify that the scrape result points back to the original URL.
    assert result.link == url
    # Ensure that metadata contains a title.
    assert "title" in result.metadata and result.metadata["title"]
    # Ensure that content is non-empty.
    assert result.content
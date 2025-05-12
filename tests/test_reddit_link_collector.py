import pytest
from unittest.mock import AsyncMock, MagicMock
from scraipe.extended.reddit_link_collector import RedditLinkCollector
from asyncpraw import Reddit
import os
import pytest_asyncio

# fixture that loads credentials from the environment
@pytest_asyncio.fixture
async def live_reddit():
    """Load Reddit credentials from the environment."""
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    user_agent = "scraipe reddit integration by u/PeterTigerr"
    
    if not all([client_id, client_secret]):
        pytest.skip("Live Reddit credentials are not set in the environment.")
    
    reddit = Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )
    try:
        yield reddit
    finally:
        # Close the Reddit client
        await reddit.close()

@pytest.mark.asyncio
async def test_live_collect_links(live_reddit:Reddit):
    """Test live link collection."""
    
    collector = RedditLinkCollector(
        client=live_reddit,
        subreddits="python",
        limit=5,
        sorts="top"
    )
    
    links = set()
    async for link in collector.async_collect_links():
        print(link)
        links.add(link)
    
    assert len(links) == 5
    
def test_live_collect_links_sync(live_reddit:Reddit):
    """Test live link collection."""
    
    collector = RedditLinkCollector(
        client=live_reddit,
        subreddits="python",
        limit=5,
        sorts="top"
    )
    
    links = set()
    for link in collector.collect_links():
        print(link)
        links.add(link)
    
    assert len(links) == 5
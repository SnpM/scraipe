import asyncio
from typing import AsyncIterable, Iterable, Sequence, Union, Literal

from scraipe.async_classes import IAsyncLinkCollector
from asyncpraw import Reddit
from asyncpraw.models import Subreddit, Submission

from scraipe.async_util import AsyncManager

import logging
import time

SortType = Literal["hot", "new", "top", "rising", "controversial"]

TopTimeFilter = Union[None, Literal["all", "day", "hour", "month", "week", "year"]]

USER_AGENT = "Scraipe RedditLinkCollector (by u/PeterTigerr)"

class RedditLinkCollector(IAsyncLinkCollector):
    """
    Collects submission links from Reddit subreddits using asyncpraw.
    """
    
    client_id: str
    client_secret: str
    user_agent: str
    subreddits: list[str]
    sorts: list[SortType]
    max_age: int
    limit: int
    time_filter: TopTimeFilter
    
    def __init__(
        self,
        client_id:str,
        client_secret:str,
        subreddits: Union[str, Sequence[str]],
        limit: int = 100,
        sorts: Union[SortType, Sequence[SortType]] = "new",
        max_age: int = 0,
        top_time_filter: TopTimeFilter=None,  # only for "top"
    ):
        """
        Args:
            client:          An asyncpraw Reddit client.
            subreddits:      One subreddit or a list of subreddit names.
            limit:           Max posts per subreddit per sort.
            sorts:           One or more of "hot", "new", "top", "rising", "controversial".
            max_age:         Maximum age of posts to collect (in seconds). If 0, no limit.
            time_filter:     One of "all","day","hour","month","week","year" (only for "top").
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = USER_AGENT
        
        # normalize to list[str]
        if isinstance(subreddits, str):
            self.subreddits = [subreddits]
        else:
            self.subreddits = list(subreddits)  # assume all items are str

        # normalize sorts
        if isinstance(sorts, str):
            self.sorts = [sorts]
        else:
            self.sorts = list(sorts)

        self.limit = limit
        self.max_age = max_age
        self.time_filter = top_time_filter

    async def async_collect_links(self) -> AsyncIterable[str]:
        """
        Asynchronously yield URLs from each subreddit × sort combination.
        Fetches each subreddit in parallel for maximum throughput.
        """
        client = Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent,
        )
        
        async with client:
            async def fetch_for_sub(sub_name: str) -> list[str]:
                sub: Subreddit = await client.subreddit(sub_name)
                collected: list[str] = []
                now = time.time()
                for sort in self.sorts:
                    assert sort in ["hot", "new", "top", "rising", "controversial"], f"Invalid sort: {sort}"
                    listing_coro = getattr(sub, sort, None)
                    kwargs = {"limit": self.limit}
                    if sort == "top" and self.time_filter:
                        kwargs["time_filter"] = self.time_filter

                    async for submission in listing_coro(**kwargs):
                        submission: Submission
                        suffix = submission.permalink
                        link = f"https://reddit.com{suffix}"
                        
                        age = now - submission.created_utc
                        if self.max_age > 0 and age > self.max_age:
                            if sort == "new":
                                break
                            continue
                        collected.append(link)
                return collected

            # schedule one fetch task per subreddit
            tasks = [fetch_for_sub(name) for name in self.subreddits]
                        
            runs = AsyncManager.get_executor().run_multiple_async(tasks)
            async for output, error in runs:
                if error:
                    logging.error(f"This is bad: {error}")
                    continue
                output: list[str]
                for url in output:
                    yield url
        
import asyncio
from typing import AsyncIterable, Iterable, Sequence, Union, Literal

from scraipe.async_classes import IAsyncLinkCollector
from asyncpraw import Reddit
from asyncpraw.models import Subreddit, Submission

from scraipe.async_util import AsyncManager

import logging

SortType = Literal["hot", "new", "top", "rising", "controversial"]

class RedditLinkCollector(IAsyncLinkCollector):
    """
    Collects submission links from Reddit subreddits using asyncpraw.
    """
    def __init__(
        self,
        client: Reddit,
        subreddits: Union[str, Sequence[str]],
        limit: int = 100,
        sorts: Union[SortType, Sequence[SortType]] = "new",
        time_filter: Union[None, Literal["all", "day", "hour", "month", "week", "year"]] = None,  # only for "top"
    ):
        """
        Args:
            client:          An asyncpraw Reddit client.
            subreddits:      One subreddit or a list of subreddit names.
            limit:           Max posts per subreddit per sort.
            sorts:           One or more of "hot", "new", "top", "rising", "controversial".
            time_filter:     One of "all","day","hour","month","week","year" (only for "top").
        """
        self.client = client
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
        self.time_filter = time_filter

    async def async_collect_links(self) -> AsyncIterable[str]:
        """
        Asynchronously yield URLs from each subreddit × sort combination.
        Fetches each subreddit in parallel for maximum throughput.
        """
        async def fetch_for_sub(sub_name: str) -> list[str]:
            print("Event loop of fetch_for_sub:", id(asyncio.get_event_loop()))
            sub: Subreddit = await self.client.subreddit(sub_name)
            collected: list[str] = []

            for sort in self.sorts:
                # get the method (fallback to hot if misspelled)
                listing_coro = getattr(sub, sort, sub.hot)
                kwargs = {"limit": self.limit}
                if sort == "top" and self.time_filter:
                    kwargs["time_filter"] = self.time_filter

                async for submission in listing_coro(**kwargs):
                    submission: Submission
                    suffix = submission.permalink
                    link = f"https://reddit.com{suffix}"
                    collected.append(link)
            return collected

        # schedule one fetch task per subreddit
        tasks = [fetch_for_sub(name) for name in self.subreddits]
        
        print("Event loop of async_collect_links:", id(asyncio.get_event_loop()))
        
        runs = AsyncManager.get_executor().run_multiple_async(tasks)
        async for output, error in runs:
            if error:
                logging.error(f"This is bad: {error}")
                continue
            output: list[str]
            for url in output:
                yield url
    
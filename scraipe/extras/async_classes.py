from abc import abstractmethod
from typing import Generator, Tuple
from scraipe.classes import IScraper, ScrapeResult
from scraipe.extras.async_util import AsyncManager
import asyncio

class AsyncScraperBase(IScraper):
    @abstractmethod
    async def async_scrape(self, url: str) -> ScrapeResult:
        """
        Asynchronously scrape the given URL.
        
        Args:
            url (str): The URL to scrape.
        
        Returns:
            ScrapeResult: The result of the scrape.
        """
        raise NotImplementedError("Subclasses must implement this method.")
    
    def scrape(self, url: str) -> ScrapeResult:
        """
        Synchronously scrape the given URL. Wraps async_scrape().
        
        Args:
            url (str): The URL to scrape.
        
        Returns:
            ScrapeResult: The result of the scrape.
        """
        return AsyncManager.run(self.async_scrape, url)
    
    def scrape_multiple(self, urls) -> Generator[Tuple[str, ScrapeResult], None, None]:
        """
        Asynchronously scrape multiple URLs and yield results. Blocks until all results are available.
        
        Args:
            urls (list): A list of URLs to scrape.
        
        Returns:
            Generator[Tuple[str, ScrapeResult], None, None]: A generator yielding tuples of URL and ScrapeResult.
        """
        def make_task(url):
            async def task():
                return url, await self.async_scrape(url)
            return task
        tasks = [make_task(url) for url in urls]
        for result in AsyncManager.run_multiple(tasks):
            yield result
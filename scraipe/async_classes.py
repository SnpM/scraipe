from abc import abstractmethod
from typing import Generator, Tuple
from scraipe.classes import IScraper, ScrapeResult, IAnalyzer, AnalysisResult
from scraipe.async_util import AsyncManager

class IAsyncScraper(IScraper):
    """
    Base class for asynchronous scrapers. Implements the IScraper interface.
    This class provides a synchronous wrapper around the asynchronous scraping method.
    Subclasses must implement the async_scrape() method.
    """
    max_workers:int = 10
    def __init__(self, max_workers: int=10):
        """
        Initialize the IAsyncScraper with a maximum number of concurrent workers.
        
        Args:
            max_workers (int): The maximum number of concurrent workers.
        """
        self.max_workers = max_workers
    
    @abstractmethod
    async def async_scrape(self, link: str) -> ScrapeResult:
        """
        Asynchronously scrape the given URL.
        
        Args:
            link (str): The URL to scrape.
        
        Returns:
            ScrapeResult: The result of the scrape.
        """
        raise NotImplementedError("Subclasses must implement this method.")
    
    def scrape(self, link: str) -> ScrapeResult:
        """
        Synchronously scrape the given URL. Wraps async_scrape().
        
        Args:
            link (str): The link to scrape.
        
        Returns:
            ScrapeResult: The result of the scrape.
        """
        return AsyncManager.get_executor().run(self.async_scrape(link))
    
    def scrape_multiple(self, links) -> Generator[Tuple[str, ScrapeResult], None, None]:
        """
        Asynchronously scrape multiple URLs and yield results in synchronous context.
        Blocks while waiting for results.
        
        Args:
            urls (list): A list of URLs to scrape.
        
        Returns:
            Generator[Tuple[str, ScrapeResult], None, None]: A generator yielding tuples of URL and ScrapeResult.
        """
        def make_task(link):
            async def task():
                return link, await self.async_scrape(link)
            return task()
        tasks = [make_task(link) for link in links]
        return AsyncManager.get_executor().run_multiple(tasks, self.max_workers)
            
class IAsyncAnalyzer(IAnalyzer):
    """
    Base class for asynchronous analyzers. Implements the IAnalyzer interface.
    This class provides a synchronous wrapper around the asynchronous analysis method.
    Subclasses must implement the async_analyze() method.
    """
    max_workers:int = 10
    def __init__(self, max_workers: int = 10):
        """
        Initialize the IAsyncAnalyzer with a maximum number of concurrent workers.
        
        Args:
            max_workers (int): The maximum number of concurrent workers.
        """
        self.max_workers = max_workers

    @abstractmethod
    async def async_analyze(self, content: str) -> AnalysisResult:
        """
        Asynchronously analyze the given content.

        Args:
            content (str): The content to analyze.

        Returns:
            AnalysisResult: The result of the analysis.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def analyze(self, content: str) -> AnalysisResult:
        """
        Synchronously analyze the given content. Wraps async_analyze().

        Args:
            content (str): The content to analyze.

        Returns:
            AnalysisResult: The result of the analysis.
        """
        return AsyncManager.get_executor().run(self.async_analyze(content))
    
    def analyze_multiple(self, contents: dict) -> "Generator[Tuple[str, AnalysisResult], None, None]":
        """
        Asynchronously analyze multiple contents and yield results in synchronous context.
        Blocks while waiting for results.

        Args:
            contents (dict): A dictionary of contents to analyze, with keys as identifiers and values as content.

        Returns:
            Generator[Tuple[str, AnalysisResult], None, None]: A generator yielding tuples of identifier and AnalysisResult.
        """
        def make_task(link, content):
            async def task():
                return link, await self.async_analyze(content)
            return task()
        tasks = [make_task(link, content) for link, content in contents.items()]
        return AsyncManager.get_executor().run_multiple(tasks, self.max_workers)

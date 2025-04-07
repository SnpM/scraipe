from scraipe import ScrapeResult
from scraipe.async_classes import IAsyncScraper
import aiohttp

class RawScraper(IAsyncScraper):
    """Asynchronous scraper that retrieves webpage content in raw text format. The scraper performs no cleaning or parsing of the content.

    Uses aiohttp to perform HTTP GET requests.

    Attributes:
        DEFAULT_USER_AGENT (str): Default User-Agent string for HTTP requests.
        headers (dict): HTTP headers used during the requests.
    """
    
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    headers: dict = {"User-Agent": DEFAULT_USER_AGENT}
    """Headers to be used in the HTTP requests. Defaults to a standard User-Agent header."""
    
    def __init__(self, headers=None):
        """
        Initializes a RawScraper instance.

        Args:
            headers (dict, optional): Custom headers for HTTP requests.
                                      Defaults to None, which uses the class-defined headers.
        """
        self.headers = headers or RawScraper.headers
        
    async def async_scrape(self, url: str) -> ScrapeResult:
        """Scrape a webpage asynchronously and return its raw text content.

        Args:
            url (str): URL of the webpage to be scraped.

        Returns:
            ScrapeResult: Result containing the URL, raw text content, success flag, and error message if applicable.
        """
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return ScrapeResult.fail(url, f"Failed to scrape {url}. Status code: {response.status}")
                    text = await response.text()
                    return ScrapeResult.succeed(url, text)
        except Exception as e:
            return ScrapeResult.fail(url, f"Failed to scrape {url}. Error: {e}")
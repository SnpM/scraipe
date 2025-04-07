import aiohttp
import trafilatura
from scraipe.classes import ScrapeResult
from scraipe.async_classes import IAsyncScraper

class NewsScraper(IAsyncScraper):
    """A scraper that uses aiohttp and trafilatura to extract article content.
    
    Retrieves HTML content from a given URL and extracts the main article text 
    using the trafilatura library. Handles HTTP errors by raising exceptions or 
    returning a failed ScrapeResult.
    """
    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/58.0.3029.110 Safari/537.36"
    )

    def __init__(self, headers=None):
        self.headers = headers or {"User-Agent": NewsScraper.DEFAULT_USER_AGENT}
        
    async def get_site_html(self, url: str):
        """Retrieve HTML content from the specified URL using aiohttp.
        
        Parameters:
            url (str): The URL of the webpage to scrape.
        
        Returns:
            str: The HTML content of the webpage.
        
        Raises:
            Exception: If the HTTP response status is not 200.
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to scrape {url}. Status code: {response.status}")
                return await response.text()

    async def async_scrape(self, url: str) -> ScrapeResult:
        """Asynchronously scrape the specified URL and extract its content.
        
        Parameters:
            url (str): The URL to scrape and extract content from.
        
        Returns:
            ScrapeResult: A success result with the extracted text if successful,
            or a failure result containing an error message on failure.
        """
        try:
            try:
                html = await self.get_site_html(url)
            except Exception as e:
                return ScrapeResult.fail(url,f"Failed to get page: {e}")
            
            content = trafilatura.extract(
                html,
                url=url,
                output_format="txt"
            )
            if not content:
                return ScrapeResult.fail(url,f"No content extracted from {url}."
                )
            return ScrapeResult.succeed(url,content)
        except Exception as e:
            return ScrapeResult.fail(url,f"Exception while scraping {url}: {e}")
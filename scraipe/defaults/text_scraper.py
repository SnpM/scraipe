from scraipe import ScrapeResult
from scraipe.async_classes import IAsyncScraper
from bs4 import BeautifulSoup
import aiohttp

class TextScraper(IAsyncScraper):
    """Asynchronous text scraper that extracts visible text from HTML.

    Fetches webpage content using aiohttp and parses the HTML with BeautifulSoup. Strips HTML tags.
    
    Attributes:
        DEFAULT_USER_AGENT (str): Default User-Agent string for HTTP requests.
        headers (dict): HTTP headers used in fetching the webpage content.
    """
    
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    headers: dict = {"User-Agent": DEFAULT_USER_AGENT}
    """Headers to be used in the HTTP requests. Defaults to a standard User-Agent header."""
    
    def __init__(self, headers=None):
        """
        Initializes the TextScraper with optional custom HTTP headers.
        
        :param headers: A dictionary of HTTP headers to use in asynchronous requests. If not provided,
                        defaults to a standard User-Agent header.
        """
        self.headers = headers or TextScraper.headers
        
    async def async_scrape(self, url: str) -> ScrapeResult:
        """Scrape a webpage asynchronously and extract visible text.

        Args:
            url (str): URL of the webpage to be scraped.

        Returns:
            ScrapeResult: Result containing the URL, extracted text content, success flag, and error if any.
        """
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return ScrapeResult.fail(url, f"Failed to scrape {url}. Status code: {response.status}")                        
                    text = await response.text()
                    # Use bs4 to extract the text from the html
                    soup = BeautifulSoup(text, "html.parser")
                    content = soup.get_text()
                    content = "\n".join([line for line in content.split("\n") if line.strip() != ""])
                    return ScrapeResult.succeed(url, content)
        except Exception as e:
            return ScrapeResult.fail(url, f"Failed to scrape {url}. Error: {e}")
from scraipe import ScrapeResult
from scraipe.async_classes import IAsyncScraper
from bs4 import BeautifulSoup
import aiohttp

class TextScraper(IAsyncScraper):
    """Pulls the content of a webpage and returns the html-stripped text.
    
    This asynchronous scraper utilizes aiohttp for HTTP requests and BeautifulSoup to parse HTML.
    It fetches the webpage content, parses out HTML tags, removes extra whitespace, and returns a
    ScrapeResult object indicating the success or failure of the scraping process.
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
        """
        Asynchronously scrapes the given URL by making an HTTP GET request and processing the HTML content.
        
        :param url: The URL to scrape.
        :return: A ScrapeResult object containing:
                 - link: the provided URL,
                 - content: the text extracted from the HTML (if successful),
                 - scrape_success: a boolean indicating if the operation succeeded,
                 - scrape_error: an error message if the scrape failed.
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
                    return ScrapeResult.success(url, content)
        except Exception as e:
            return ScrapeResult.fail(url, f"Failed to scrape {url}. Error: {e}")
import aiohttp
from bs4 import BeautifulSoup
from scraipe.classes import ScrapeResult
from scraipe.async_classes import IAsyncScraper

class AiohttpScraper(IAsyncScraper):
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    
    def __init__(self, headers=None, max_workers: int = 10):
        super().__init__(max_workers)
        self.headers = headers or {"User-Agent": AiohttpScraper.DEFAULT_USER_AGENT}
    
    async def async_scrape(self, url: str) -> ScrapeResult:
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return ScrapeResult.fail(url,f"Failed to scrape {url}. Status code: {response.status}")                        
                    text = await response.text()
                    # Use bs4 to extract the text from the html
                    soup = BeautifulSoup(text, "html.parser")
                    content = soup.get_text()
                    content = "\n".join([line for line in content.split("\n") if line.strip() != ""])
                    return ScrapeResult.success(url, content)
        except Exception as e:
            return ScrapeResult.fail(url, f"Failed to scrape {url}. Error: {e}")
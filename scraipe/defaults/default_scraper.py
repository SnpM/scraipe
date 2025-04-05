from scraipe.classes import IScraper, ScrapeResult
import requests
from bs4 import BeautifulSoup

class DefaultScraper(IScraper):
    """The default scraper that pulls the content of a webpage using requests and filters out html tags."""
    
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    def __init__(self, headers=None):
        self.headers = headers or {"User-Agent": DefaultScraper.DEFAULT_USER_AGENT}
    
    def scrape(self, url:str)->ScrapeResult:
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                return ScrapeResult(
                    link=url,
                    content=None,
                    scrape_success=False, 
                    scrape_error=f"Failed to scrape {url}. Status code: {response.status_code}")
            text = response.text
            # Use bs4 to extract the text from the html
            soup = BeautifulSoup(text, "html.parser")
            content = soup.get_text()
            # Remove multiple consecutive lines
            content = "\n".join([line for line in content.split("\n") if line.strip() != ""])
            
            return ScrapeResult(link=url, content=content, scrape_success=True)
        except Exception as e:
            return ScrapeResult(link=url,scrape_success=False, scrape_error=f"Failed to scrape {url}. Error: {e}")
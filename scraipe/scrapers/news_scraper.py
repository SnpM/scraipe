from scraipe.classes import IScraper, ScrapeResult
import requests
from bs4 import BeautifulSoup
from newspaper import Article

class NewsScraper(IScraper):
    """A scraper that uses the newspaper3k library to extract article content."""
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    def __init__(self, headers=None):
        self.headers = headers or {"User-Agent": NewsScraper.DEFAULT_USER_AGENT}
    
    def scrape(self, url:str)->ScrapeResult:
        try:
            article = Article(url)
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                return ScrapeResult(
                    link=url,
                    content=None,
                    scrape_success=False, 
                    scrape_error=f"Failed to scrape {url}. Status code: {response.status_code}")
            text = response.text
            article.set_html(text)
            article.parse()
            content = article.text
            if not content:
                return ScrapeResult(link=url, scrape_success=False, scrape_error=f"Failed to news from {url}. No content found.")
            return ScrapeResult(link=url, content=content, scrape_success=True)
        except Exception as e:
            return ScrapeResult(link=url,scrape_success=False, scrape_error=f"Failed to scrape {url}. Error: {e}")
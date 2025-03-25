from scraipe.classes import IScraper, ScrapeResult
import requests
from bs4 import BeautifulSoup
from newspaper import Article

class NewsScraper(IScraper):
    """A scraper that uses the newspaper3k library to scrape news articles."""
    def scrape(self, url:str)->ScrapeResult:
        try:
            article = Article(url)
            article.download()
            article.parse()
            content = article.text
            return ScrapeResult(link=url, content=content, success=True)
        except Exception as e:
            return ScrapeResult(link=url,success=False, error=f"Failed to scrape {url}. Error: {e}")
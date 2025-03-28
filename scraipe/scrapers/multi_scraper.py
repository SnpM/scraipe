from scraipe.classes import IScraper, ScrapeResult
import requests
from bs4 import BeautifulSoup
from newspaper import Article
from scraipe.scrapers.telegram_scraper import TelegramScraper
from scraipe.scrapers.default_scraper import DefaultScraper
from scraipe.scrapers.news_scraper import NewsScraper

class MultiScraper(IScraper):
    """A scraper that picks the best scraper approach for telegram, news, and default webpages."""
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

    def __init__(self,
        telegram_scraper:TelegramScraper=None,
        news_scraper:NewsScraper=None,
        default_scraper:DefaultScraper=None
    ):
        self.telegram_scraper = telegram_scraper
        if self.telegram_scraper is None:
            print("Telegram scraper not provided. Telegram scraping will not work.")
        self.news_scraper = news_scraper or NewsScraper()
        self.default_scraper = default_scraper or DefaultScraper()
    
    def scrape(self, url:str)->ScrapeResult:
        # Check if the url is a telegram link
        if url.startswith("https://t.me/"):
            if self.telegram_scraper is None:
                return ScrapeResult(link=url, scrape_success=False, scrape_error="Telegram scraper not configured.")
            return self.telegram_scraper.scrape(url)
        # Attempt news scraping
        result = self.news_scraper.scrape(url)
        if result.scrape_success:
            return result
        # Use default scraper as fallback
        return self.default_scraper.scrape(url)
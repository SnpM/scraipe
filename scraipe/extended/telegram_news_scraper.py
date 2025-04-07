from scraipe.defaults.multi_scraper import MultiScraper, IngressRule
from scraipe.classes import IScraper
from scraipe.extended.news_scraper import NewsScraper
from scraipe.defaults.text_scraper import TextScraper

class TelegramNewsScraper(MultiScraper):
    """
    A multi-scraper that processes Telegram message links and news content.
    
    This scraper uses a dedicated telegram_scraper for Telegram links and falls back to 
    news_scraper for general news links and to text_scraper for text content. If news_scraper 
    or text_scraper are not provided, default configurations will be used.
    """
    
    def __init__(
        self,
        telegram_scraper: IScraper,
        news_scraper: IScraper = None,
        text_scraper: IScraper = None,
        **kwargs
    ):
        """
        Initialize the TelegramNewsScraper.
        
        Parameters:
            telegram_scraper (IScraper): Scraper instance for processing Telegram links.
            news_scraper (IScraper, optional): Scraper instance for processing news links. 
                Defaults to NewsScraper() if not provided.
            text_scraper (IScraper, optional): Scraper instance for text content scraping. 
                Defaults to TextScraper if not provided.
            **kwargs: Additional keyword arguments passed to the parent MultiScraper.
        
        Raises:
            ValueError: If telegram_scraper is None.
        """
        if telegram_scraper is None:
            raise ValueError("telegram_scraper cannot be automatically configured without credentials. Please provide a valid scraper.")
        if news_scraper is None:
            news_scraper = NewsScraper()
        if text_scraper is None:
            text_scraper = TextScraper()
        ingress_rules = [
            # Match telegram message links
            # e.g. https://t.me/username/1234
            IngressRule(
                r"t.me/\w+/\d+",
                scraper=telegram_scraper
            ),
            # Match all links
            IngressRule(
                r".*",
                scraper=news_scraper
            ),
            # Fallback to aiohttp scraper
            IngressRule(
                r".*",
                scraper=text_scraper
            )
        ]
        super().__init__(
            ingress_rules=ingress_rules,
            **kwargs
        )
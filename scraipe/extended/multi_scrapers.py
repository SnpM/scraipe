from scraipe.extended.multi_scraper import MultiScraper, IngressRule
from scraipe.classes import IScraper

class TelegramNewsScraper(MultiScraper):
    """A multiscraper for telegram and news links. Falls back to AiohttpScraper."""
    def __init__(
        self,
        telegram_scraper: IScraper,
        news_scraper: IScraper = None,
        aiohttp_scraper: IScraper = None,
        **kwargs
    ):
        if telegram_scraper is None:
            raise ValueError("telegram_scraper cannot be automatically configured without credentials. Please provide a valid scraper.")
        if news_scraper is None:
            news_scraper = telegram_scraper
        if aiohttp_scraper is None:
            aiohttp_scraper = telegram_scraper
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
                scraper=aiohttp_scraper
            )
        ]
        super().__init__(
            ingress_rules=ingress_rules,
            **kwargs
        )
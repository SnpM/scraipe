from scraipe.defaults.multi_scraper import MultiScraper, IngressRule
from scraipe.classes import IScraper

class TelegramNewsScraper(MultiScraper):
    """A multiscraper for telegram and news links. Falls back to TextScraper."""
    def __init__(
        self,
        telegram_scraper: IScraper,
        news_scraper: IScraper = None,
        text_scraper: IScraper = None,
        **kwargs
    ):
        if telegram_scraper is None:
            raise ValueError("telegram_scraper cannot be automatically configured without credentials. Please provide a valid scraper.")
        if news_scraper is None:
            news_scraper = telegram_scraper
        if text_scraper is None:
            text_scraper = telegram_scraper
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
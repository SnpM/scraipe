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
        ingress_rules = [
            IngressRule(
                r"t.me/\w+/\d+",
                scraper=telegram_scraper
            ),
            IngressRule(
                r".*",
                scraper=news_scraper
            ),
        ]
        super().__init__(
            ingress_rules=ingress_rules,
            fallback_scraper=aiohttp_scraper,
            **kwargs
        )
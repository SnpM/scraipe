import unittest
import re
from scraipe.extras.multi_scrapers import TelegramNewsScraper
from scraipe.extras.multi_scraper import IngressRule
from scraipe.classes import IScraper, ScrapeResult

# ...existing imports...

# Dummy scraper that implements IScraper
class DummyScraper(IScraper):
    def scrape(self, url: str) -> ScrapeResult:
        return ScrapeResult.success(url, "dummy content")

class TestTelegramNewsScraper(unittest.TestCase):
    def test_ingress_rules_and_fallback(self):
        telegram_scraper = DummyScraper()
        news_scraper = DummyScraper()
        aiohttp_scraper = DummyScraper()
        
        scraper = TelegramNewsScraper(telegram_scraper, news_scraper, aiohttp_scraper)
        
        # Verify fallback_scraper is set correctly
        self.assertEqual(scraper.fallback_scraper, aiohttp_scraper)
        
        # Check ingress rules
        self.assertEqual(len(scraper.ingress_rules), 2)
        self.assertTrue(
            isinstance(scraper.ingress_rules[0].match, re.Pattern) and 
            scraper.ingress_rules[0].match.pattern == IngressRule.Patterns.TELEGRAM_MESSAGE.pattern
        )
        self.assertEqual(scraper.ingress_rules[0].scraper, telegram_scraper)
        
        self.assertTrue(
            isinstance(scraper.ingress_rules[1].match, re.Pattern) and 
            scraper.ingress_rules[1].match.pattern == IngressRule.Patterns.ALL.pattern
        )
        self.assertEqual(scraper.ingress_rules[1].scraper, news_scraper)

if __name__ == '__main__':
    unittest.main()

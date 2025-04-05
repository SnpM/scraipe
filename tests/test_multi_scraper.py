import re
import asyncio
import unittest

from scraipe.extended.multi_scraper import MultiScraper, IngressRule
from scraipe.classes import IScraper, ScrapeResult

# Dummy ScrapeResult for testing purposes
class DummyScrapeResult:
    def __init__(self, url, scrape_success, scrape_error, data):
        self.url = url
        self.scrape_success = scrape_success
        self.scrape_error = scrape_error
        self.data = data
    @classmethod
    def fail(cls, url, message):
        return cls(url, False, message, None)

# Dummy scraper that always succeeds
class DummySuccessScraper(IScraper):
    def scrape(self, url: str):
        return DummyScrapeResult(url, True, "", "success")
    def __str__(self):
        return "DummySuccessScraper"

# Dummy scraper that always fails
class DummyFailureScraper(IScraper):
    def scrape(self, url: str):
        return DummyScrapeResult(url, False, "failed", None)
    def __str__(self):
        return "DummyFailureScraper"

# Override ScrapeResult for testing if needed
# (Assuming MultiScraper uses the attributes: scrape_success and scrape_error)

class TestMultiScraper(unittest.TestCase):
    def test_rule_success(self):
        # When the URL matches an ingress rule that uses a successful scraper
        url = "http://example.com/match"
        rules = [
            IngressRule(re.compile(r"match"), DummySuccessScraper()),
            IngressRule(re.compile(r"fail"), DummyFailureScraper()) 
        ]
        ms = MultiScraper(rules, preserve_errors=False)
        result = asyncio.run(ms.async_scrape(url))
        self.assertTrue(result.scrape_success)
        self.assertEqual(result.data, "success")
    
    
    def test_preserve_errors(self):
        # When all scrapers fail and preserve_errors is True,
        # the returned error should contain concatenated messages.
        url = "http://example.com/fail"
        rule1 = IngressRule(re.compile(r"fail"), DummyFailureScraper())
        rule2 = IngressRule(re.compile(r"fail"), DummyFailureScraper())
        ms = MultiScraper([rule1, rule2], preserve_errors=True, error_delimiter="|")
        result = asyncio.run(ms.async_scrape(url))
        self.assertFalse(result.scrape_success)
        self.assertIn("DummyFailureScraper: failed", result.scrape_error)
        # Expect errors from all failed attempts (at least two occurrences)
        self.assertTrue(result.scrape_error.count("DummyFailureScraper: failed") >= 2)

if __name__ == '__main__':
    unittest.main()

import re
import asyncio

from scraipe.defaults.multi_scraper import MultiScraper, IngressRule
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

def test_rule_success():
    # When the URL matches an ingress rule that uses a successful scraper
    url = "http://example.com/match"
    rules = [
        IngressRule(re.compile(r"match"), DummySuccessScraper()),
        IngressRule(re.compile(r"fail"), DummyFailureScraper()) 
    ]
    ms = MultiScraper(rules, debug=False)
    result = asyncio.run(ms.async_scrape(url))
    assert result.scrape_success
    assert result.data == "success"

def test_debug_flag():
    # When all scrapers fail and preserve_errors is True,
    # the returned error should contain concatenated messages.
    url = "http://example.com/fail"
    rule1 = IngressRule(re.compile(r"fail"), DummyFailureScraper())
    rule2 = IngressRule(re.compile(r"fail"), DummyFailureScraper())
    ms = MultiScraper([rule1, rule2], debug=True, debug_delimiter="|")
    result = asyncio.run(ms.async_scrape(url))
    
    print(result.error)
    assert not result.scrape_success
    assert "DummyFailureScraper[FAIL]: failed" in result.scrape_error
    # Expect errors from all failed attempts (at least two occurrences)
    assert len(re.findall(r"DummyFailureScraper.{0,10}failed", result.scrape_error)) >= 2

import re
import pytest
from scraipe.defaults.multi_scraper import MultiScraper, IngressRule
from scraipe.classes import ScrapeResult
from scraipe import IScraper
from scraipe.async_classes import IAsyncScraper  # added import

# Dummy scraper that always returns success.
class DummySuccessScraper(IScraper):
    def scrape(self, url: str) -> ScrapeResult:
        return ScrapeResult.succeed(url, "Dummy succeeded")
    def get_expected_link_format(self):
        return r"success"

# Dummy scraper that always returns failure.
class DummyFailScraper(IScraper):
    def scrape(self, url: str) -> ScrapeResult:
        return ScrapeResult.fail(url, "Dummy failed")
    def get_expected_link_format(self):
        return r"fail"

def test_single_success_rule():
    scraper = DummySuccessScraper()
    rule = IngressRule(scraper.get_expected_link_format(), scraper)
    ms = MultiScraper([rule], debug=True)
    url = "http://example.com/success"
    result = ms.scrape(url)
    assert result.scrape_success is True
    assert "SUCCESS" in result.scrape_error

def test_single_fail_rule():
    scraper = DummyFailScraper()
    rule = IngressRule(scraper.get_expected_link_format(), scraper)
    ms = MultiScraper([rule], debug=False)
    url = "http://example.com/fail"
    result = ms.scrape(url)
    # When scraper fails, MultiScraper returns a failure result indicating no successful scrape.
    assert result.scrape_success is False
    assert "No scraper could handle" in result.scrape_error

def test_no_matching_rule():
    # Rule pattern that does not match the URL.
    scraper = DummySuccessScraper()
    rule = IngressRule(r"nomatch", scraper)
    ms = MultiScraper([rule], debug=True)
    url = "http://example.com/success"
    result = ms.scrape(url)
    assert result.scrape_success is False
    assert "No scraper could handle" in result.scrape_error

def test_multiple_rules_second_matches():
    # First rule does not match; second rule matches and returns success.
    scraper_fail = DummyFailScraper()
    scraper_success = DummySuccessScraper()
    rule_fail = IngressRule(r"nomatch", scraper_fail)
    rule_success = IngressRule(scraper_success.get_expected_link_format(), scraper_success)
    ms = MultiScraper([rule_fail, rule_success], debug=True)
    url = "http://example.com/success"
    result = ms.scrape(url)
    assert result.scrape_success is True
    assert "SUCCESS" in result.scrape_error

def test_async_and_sync_scrapers():
    class AsyncDummySuccessScraper(IAsyncScraper):
        async def async_scrape(self, url: str) -> ScrapeResult:
            return ScrapeResult.succeed(url, "Async Dummy succeeded")
        def get_expected_link_format(self):
            return r"async"
    # Use existing sync dummy scraper for failure
    scraper_sync_fail = DummyFailScraper()
    rule_sync_fail = IngressRule(scraper_sync_fail.get_expected_link_format(), scraper_sync_fail)
    scraper_async = AsyncDummySuccessScraper()
    rule_async = IngressRule(scraper_async.get_expected_link_format(), scraper_async)
    ms = MultiScraper([rule_sync_fail, rule_async], debug=True)
    url = "http://example.com/async"
    result = ms.scrape(url)
    assert result.scrape_success is True
    assert "[SUCCESS]" in result.scrape_error
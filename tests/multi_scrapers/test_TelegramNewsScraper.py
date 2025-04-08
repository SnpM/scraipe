import re
import pytest
from scraipe import IScraper

# Dummy scraper to simulate IScraper behavior
class DummyScraper (IScraper):
    def __init__(self, name, ret_val):
        self.name = name
        self.ret_val = ret_val
        self.called = False

    def scrape(self, url):
        self.called = True
        return f"{self.name} scraped {url} with result: {self.ret_val}"

# Helper to simulate MultiScraper routing through ingress_rules
def dummy_scrape(url, ingress_rules):
    for rule in ingress_rules:
        if re.search(rule.match, url):
            return rule.scraper.scrape(url)
    return None

def test_telegram_news_scraper_init_error():
    from scraipe.extended.telegram_news_scraper import TelegramNewsScraper
    with pytest.raises(ValueError):
        TelegramNewsScraper(telegram_scraper=None)

def test_telegram_news_scraper_routing():
    from scraipe.extended.telegram_news_scraper import TelegramNewsScraper
    telegram_dummy = DummyScraper("telegram", "telegram_result")
    news_dummy = DummyScraper("news", "news_result")
    text_dummy = DummyScraper("text", "text_result")

    scraper = TelegramNewsScraper(
        telegram_scraper=telegram_dummy,
        news_scraper=news_dummy,
        text_scraper=text_dummy
    )

    # Test that a telegram link routes to the telegram scraper
    telegram_url = "https://t.me/username/1234"
    result = dummy_scrape(telegram_url, scraper.ingress_rules)
    assert "telegram" in result

    # Test that a non-telegram link routes to the news scraper
    news_url = "https://example.com/article"
    result = dummy_scrape(news_url, scraper.ingress_rules)
    assert "news" in result

def test_fallback_rule():
    from scraipe.extended.telegram_news_scraper import TelegramNewsScraper
    telegram_dummy = DummyScraper("telegram", "telegram_result")
    news_dummy = DummyScraper("news", "news_result")
    text_dummy = DummyScraper("text", "text_result")

    scraper = TelegramNewsScraper(
        telegram_scraper=telegram_dummy,
        news_scraper=news_dummy,
        text_scraper=text_dummy
    )
    generic_url = "https://anotherexample.com"
    result = dummy_scrape(generic_url, scraper.ingress_rules)
    # With current routing, since the telegram rule does not match, news should be selected.
    assert "news" in result
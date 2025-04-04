from scraipe.classes import IScraper, ScrapeResult
class ExampleScraper(IScraper):
    """A minimal scraper implementation for example."""
    def scrape(self, url:str)->ScrapeResult:
        # Fail if url is malicious!
        if "hacker" in url:
            return ScrapeResult.fail(url, "Hacker detected!")
        # Simulate a successful scrape; simply returns the url
        content = f"I'm simply returning the {url}"
        return ScrapeResult.success(url, content)
from scraipe.classes import IScraper, ScrapeResult
class ExampleScraper(IScraper):
    """A minimal scraper implementation for example."""
    def scrape(self, url:str)->ScrapeResult:
        # Simulate scraping by returning a predefined string
        content = f"I'm simply returning the {url} :p"
        return ScrapeResult.success(url, content)
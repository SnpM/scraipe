#============================================================
# ExampleScraper
#============================================================
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
    
#============================================================
# ExampleAnalyzer
#============================================================
from scraipe.classes import IAnalyzer, AnalysisResult
class ExampleAnalyzer(IAnalyzer):
    """A minimal analyzer implementation for example."""
    def analyze(self, content: str) -> AnalysisResult:
        # Fail if content is malicious!
        if "hacker" in content:
            return AnalysisResult.fail("Hacker detected!")
        # Simulate a successful analysis; reverses the content
        result = content[::-1]
        output = {"reversed_content": result}
        return AnalysisResult.success(output)
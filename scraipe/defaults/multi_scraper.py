from scraipe.classes import IScraper, ScrapeResult
from scraipe.async_classes import IAsyncScraper

from typing import List, cast, final
import re

@final
class IngressRule():
    """
    A rule that defines how to handle a specific type of URL.
    It contains a match string and a scraper to use for that match.
    """
    match:str
    scraper:IScraper
    def __init__(self,
                 match:str|re.Pattern,
                 scraper:IScraper):
        """
        Initialize the IngressRule with a match string and a scraper.
        Args:
            match (str|re.Pattern): The regex pattern to match against URLs.
            scraper (IScraper): The scraper to use for this match.
        """
        if isinstance(match, str):
            self.match = re.compile(match)
        elif isinstance(match, re.Pattern):
            self.match = match
        assert isinstance(self.match, re.Pattern), "self.match must be a regex pattern"
        
        assert isinstance(scraper, IScraper), "scraper must be an instance of IScraper"
        self.scraper = scraper
    def __str__(self):
        return f"IngressRule(match={self.match}, scraper={self.scraper})"
    def __repr__(self):
        return self.__str__()

class MultiScraper(IAsyncScraper):
    """A scraper that uses multiple ingress rules to determine how to scrape a link."""
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        
    ingress_rules: List[IngressRule]
    def __init__(self,
        ingress_rules: List[IngressRule],
        preserve_errors: bool = False,
        error_delimiter: str = "; "
    ):
        """
        Initialize the MultiScraper with ingress rules.

        Args:
            ingress_rules (list[IngressRule]): A list of ingress rules.
            preserve_errors (bool, optional): Whether to preserve errors from the ingress chain when the scrape is successful.
            error_delimiter (str, optional): The delimiter to use for concatenating error messages.
        """
        super().__init__()
        assert isinstance(ingress_rules, list), "ingress_rules must be a list of IngressRule"
        assert all(isinstance(rule, IngressRule) for rule in ingress_rules), "All items in ingress_rules must be IngressRule instances"
        self.ingress_rules = ingress_rules
        assert isinstance(preserve_errors, bool), "preserve_errors must be a boolean"
        self.preserve_errors = preserve_errors
        assert isinstance(error_delimiter, str), "error_delimiter must be a string"
        self.error_delimiter = error_delimiter

    async def async_scrape(self, url: str) -> ScrapeResult:
        """
        Scrape the given URL using the appropriate scraper based on ingress rules.

        Args:
            url (str): The URL to scrape.

        Returns:
            ScrapeResult: The result of the scrape.
        """
        ingress_chain_fails = []        
        def use_scraper(scraper: IScraper) -> ScrapeResult:
            """Use the provided scraper to scrape the URL and save the error message if it fails."""
            if isinstance(scraper, IAsyncScraper):
                async_scraper = cast(IAsyncScraper, scraper)
                result = async_scraper.async_scrape(url)
            else:
                result = scraper.scrape(url)
            if not result.scrape_success:
                ingress_chain_fails.append(f"{scraper}: {result.scrape_error}")
            return result
                
        successful_result = None
        # Attempt to scrape using each ingress rule
        for rule in self.ingress_rules:
            if re.search(rule.match, url):
                # If the rule matches, use the associated scraper
                result = use_scraper(rule.scraper)
                if result.scrape_success:
                    successful_result = result
                    break
        
        if successful_result:
            if self.preserve_errors:
                # Even if successful, store the failure messages for debugging
                result.scrape_error = self.error_delimiter.join(ingress_chain_fails)
            return result

        # If ingress rules don't succeed, return a failure result
        result = ScrapeResult.fail(url, f"No scraper could handle {url}: ")
        result.scrape_error += self.error_delimiter.join(ingress_chain_fails)
        return result
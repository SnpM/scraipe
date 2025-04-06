from scraipe.classes import IScraper, ScrapeResult
from scraipe.async_classes import IAsyncScraper

from typing import List, cast, final
import re

@final
class IngressRule():
    """
    A rule that defines how to handle a specific type of URL.

    Attributes:
        match (re.Pattern): A compiled regular expression used to match URLs.
        scraper (IScraper): An instance of a scraper to be used when the URL matches.

    Methods:
        __init__(match: str | re.Pattern, scraper: IScraper):
            Initializes the ingress rule by compiling the match string if needed and setting the scraper.
        __str__():
            Returns a human-readable string representation of the ingress rule.
        __repr__():
            Returns a string representation of the ingress rule.
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
    """
    A scraper that uses multiple ingress rules to determine how to scrape a link.

    Attributes:
        DEFAULT_USER_AGENT (str): Default User-Agent used for HTTP requests.
        ingress_rules (List[IngressRule]): A list of ingress rule instances.
        debug (bool): Indicates whether debug mode is enabled.
        debug_delimiter (str): The delimiter used to join debug log messages.

    Methods:
        __init__(ingress_rules: List[IngressRule], debug: bool = False, debug_delimiter: str = "; "):
            Initializes the MultiScraper with a list of ingress rules and optional debug settings.
        async_scrape(url: str) -> ScrapeResult:
            Asynchronously scrapes the given URL using the first matching ingress rule.
            Returns a ScrapeResult indicating success or failure.
    """
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        
    ingress_rules: List[IngressRule]
    def __init__(self,
        ingress_rules: List[IngressRule],
        debug: bool = False,
        debug_delimiter: str = "; "
    ):
        """
        Initialize the MultiScraper with ingress rules.

        Args:
            ingress_rules (list[IngressRule]): A list of ingress rules.
            
        """
        super().__init__()
        assert isinstance(ingress_rules, list), "ingress_rules must be a list of IngressRule"
        assert all(isinstance(rule, IngressRule) for rule in ingress_rules), "All items in ingress_rules must be IngressRule instances"
        self.ingress_rules = ingress_rules
        assert isinstance(debug, bool), "debug must be a boolean"
        self.debug = debug
        assert isinstance(debug_delimiter, str), "debug_delimtier must be a string"
        self.debug_delimiter = debug_delimiter

    async def async_scrape(self, url: str) -> ScrapeResult:
        """
        Scrape the given URL using the appropriate scraper based on ingress rules.

        Args:
            url (str): The URL to scrape.

        Returns:
            ScrapeResult: The result of the scrape.
        """
        debug_chain = []      
        async def use_scraper(scraper: IScraper) -> ScrapeResult:
            """Use the provided scraper to scrape the URL and save the error message if it fails."""
            if isinstance(scraper, IAsyncScraper):
                async_scraper = cast(IAsyncScraper, scraper)
                result = await async_scraper.async_scrape(url)
            else:
                result = scraper.scrape(url)
            if result.scrape_success:
                # Log the successful scrape
                debug_chain.append(f"{scraper}[SUCCESS]")
            else:
                # If the scraper fails, append the error message to the debug chain
                debug_chain.append(f"{scraper}[FAIL]: {result.scrape_error}")
            return result
                
        successful_result = None
        # Attempt to scrape using each ingress rule
        for rule in self.ingress_rules:
            if re.search(rule.match, url):
                # If the rule matches, use the associated scraper
                result = await use_scraper(rule.scraper)
                if result.scrape_success:
                    successful_result = result
                    break
        
        if successful_result:
            if self.debug:
                # Even if successful, store the debug chain in result
                successful_result.scrape_error = self.debug_delimiter.join(debug_chain)
            return successful_result

        # If ingress rules don't succeed, return a failure result
        error_message = f"No scraper could handle {url}{self.debug_delimiter}{self.debug_delimiter.join(debug_chain)}"
        result = ScrapeResult.fail(url, error_message)
        return result
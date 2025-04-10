from scraipe.classes import IScraper, ScrapeResult
from scraipe.async_classes import IAsyncScraper
from scraipe.async_util import AsyncManager
from concurrent.futures import Future

from typing import List, cast, final, Tuple
import re
from pydantic import BaseModel

@final
class IngressRule():
    """
    A rule that defines how to handle a specific type of URL.

    Attributes:
        match (re.Pattern): A compiled regular expression used to match URLs.
        scraper (IScraper): An instance of a scraper to be used when the URL matches.
    """
    pattern: str|re.Pattern
    scraper: IScraper
    exclusive: bool = False
    def __init__(self,
                 pattern: str | re.Pattern,
                 scraper: IScraper,
                 exclusive: bool = False):
        """
        Initialize the IngressRule with a match string and a scraper.
        Args:
            match (str|re.Pattern): The regex pattern to match against URLs.
            scraper (IScraper): The scraper to use for this match.
            exclusive (bool): If True, this rule is exclusive and no other rules will be processed if it matches.
        """
        if isinstance(pattern, str):
            try:
                self.pattern = re.compile(pattern)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {pattern}") from e
        elif isinstance(pattern, re.Pattern):
            self.pattern = pattern
        else:
            raise ValueError("match must be a string or a compiled regex pattern")
        
        self.scraper = scraper
        
        self.exclusive = exclusive
    def __str__(self):
        return f"IngressRule(match={self.pattern}, scraper={self.scraper})"
    def __repr__(self):
        return self.__str__()
    @staticmethod
    def from_scraper(scraper:IScraper, exclusive:bool = False) -> 'IngressRule':
        """
        Create an IngressRule from a scraper instance and its expected link format.

        Args:
            scraper (IScraper): The scraper to use for this rule.
            exclusive (bool): If True, this rule is exclusive and no other rules will be processed if it matches.

        Returns:
            IngressRule: An IngressRule instance with a match that always returns True.
        """
        match = scraper.get_expected_link_format()
        if match is None:
            match = r".*"
        return IngressRule(match, scraper, exclusive=exclusive)

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
            ingress_rules (list[IngressRule]): A list of IngressRule instances. None items are omited.
            debug (bool, optional): Enable debug mode. Defaults to False.
            debug_delimiter (str, optional): Delimiter for joining debug log messages. Defaults to "; ".
        """
        super().__init__()
        assert isinstance(ingress_rules, list), "ingress_rules must be a list of IngressRule"
        assert all(rule is None or isinstance(rule, IngressRule) for rule in ingress_rules), "All items in ingress_rules must be IngressRule instances"
        
        # Omit None items from ingress_rules
        self.ingress_rules = [rule for rule in ingress_rules if rule is not None]
        
        assert isinstance(debug, bool), "debug must be a boolean"
        self.debug = debug
        assert isinstance(debug_delimiter, str), "debug_delimiter must be a string"
        self.debug_delimiter = debug_delimiter
        
    async def _run_scraper(self, link:str, scraper:IScraper) -> ScrapeResult:
        if isinstance(scraper, IAsyncScraper):
            async_scraper = cast(IAsyncScraper, scraper)
            result = await async_scraper.async_scrape(link)
        else:
            result = scraper.scrape(link)
        return result
    
    
    async def _process_rules(self, rules:List[IngressRule], url:str) -> List[Tuple[IngressRule,ScrapeResult]]:
        """Returns a ScrapeResult if a run succeeded; else None"""
        process_results = []
        for rule in rules:
            if re.search(rule.pattern, url):
                # If the rule matches, use the associated scraper
                result = await self._run_scraper(url, rule.scraper)
                process_results.append((rule,result))
                # Stop processing after first success
                if result.success or rule.exclusive:
                    break
        return process_results
    
    def _compile_results(self, url:str, process_results:List[Tuple[IngressRule,ScrapeResult]]) -> ScrapeResult:
        # Construct debug message from results
        debug_chain = []
        for process_result in process_results:
            result = process_result[1]
            rule = process_result[0]
            if result.scrape_success:
                debug_chain.append(f"{rule.scraper.__class__.__name__}[SUCCESS]")
            else:
                debug_chain.append(f"{rule.scraper.__class__.__name__}[FAIL]: {result.scrape_error}")    
        debug_message =  self.debug_delimiter.join(debug_chain)
        
        for process_result in process_results:
            result = process_result[1]
            if result.success:
                # Add debug info to error
                if self.debug:
                    result.scrape_error = debug_message
                # Return the successful ScrapeResult
                return result
        # No successful results; return failure
        error_message = f"No scraper could handle link{self.debug_delimiter}{debug_message}"
        result = ScrapeResult.fail(url, error_message)
        return result
        

    async def async_scrape(self, url: str) -> ScrapeResult:
        """
        Scrape the given URL using the appropriate scraper based on ingress rules.

        Args:
            url (str): The URL to scrape.

        Returns:
            ScrapeResult: The result of the scrape.
        """
        process_results = await self._process_rules(rules=self.ingress_rules, url=url)
        return self._compile_results(url, process_results)

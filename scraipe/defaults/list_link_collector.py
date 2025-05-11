from scraipe.classes import ILinkCollector

from typing import Iterable

class ListTargeter(ILinkCollector):
    """
    A simple implementation of ITargeter that returns a predefined list of links.
    
    Attributes:
        links (list): A list of URLs to scrape.
    """
    
    def __init__(self, links: Iterable[str]):
        """
        Initialize the ListTargeter with a list of links.
        
        Args:
            links (list): A list of URLs to scrape.
        """
        self.links = list(links)
    
    def collect_links(self) -> Iterable[str]:
        """
        Returns the collection of links to scrape.
        Returns:
            Iterable[str]: A list of URLs to scrape.
        """
        return self.links
    
    
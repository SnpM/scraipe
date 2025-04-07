"""
This package contains default implementations for scrapers and analyzers.
"""

# Default scrapers
from scraipe.defaults.text_scraper import TextScraper
from scraipe.defaults.raw_scraper import RawScraper
from scraipe.defaults.multi_scraper import MultiScraper, IngressRule

# Default analyzers
from scraipe.defaults.text_stats_analyzer import TextStatsAnalyzer
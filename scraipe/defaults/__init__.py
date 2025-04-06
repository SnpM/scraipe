"""
This package contains default implementations of scrapers and analyzers.

Modules:
    - text_scraper: Extracts visible text from HTML content.
    - raw_scraper: Retrieves raw webpage content.
    - text_stats_analyzer: Analyzes text statistics such as word count and sentence count.
"""

# Default scrapers
from scraipe.defaults.text_scraper import TextScraper
from scraipe.defaults.raw_scraper import RawScraper

# Default analyzers
from scraipe.defaults.text_stats_analyzer import TextStatsAnalyzerthe
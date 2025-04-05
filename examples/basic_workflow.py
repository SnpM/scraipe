# Import necessary components from scraipe
from scraipe.defaults.default_scraper import DefaultScraper
from scraipe.defaults.text_stats_analyzer import TextStatsAnalyzer
from scraipe.workflow import Workflow

# Initialize the default scraper and analyzer
scraper = DefaultScraper()
analyzer = TextStatsAnalyzer()

# Create the workflow instance
workflow = Workflow(scraper, analyzer)
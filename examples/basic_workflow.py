# Import necessary components from scraipe
from scraipe.defaults.default_scraper import DefaultScraper
from scraipe.defaults.text_stats_analyzer import TextStatsAnalyzer
from scraipe.workflow import Workflow

# Initialize the default scraper and analyzer
scraper = DefaultScraper()
analyzer = TextStatsAnalyzer()

# Create the workflow instance
workflow = Workflow(scraper, analyzer)

# List urls to scrape
urls = [
    "https://example.com",
    "https://rickandmortyapi.com/api/character/1",
    "https://ckaestne.github.io/seai/"
]

# Run the workflow
workflow.scrape(urls)
workflow.analyze()

# Print the results
results = workflow.export()
print(results)
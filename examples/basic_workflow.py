# Import necessary components from scraipe
from scraipe.defaults import DefaultScraper
from scraipe.defaults import TextStatsAnalyzer
from scraipe import Workflow

# Initialize the scraper and analyzer
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
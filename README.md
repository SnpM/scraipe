# Scraipe

Scraipe is a high performance asynchronous scraping and analysis framework that leverages Large Language Models (LLMs) to extract structured information.

## Installation

Ensure you have Python 3.10+ installed. Install Scraipe with powerful scrapers and analyzers:
```bash
pip install scraipe[extras]
```

## Features
- **High Performance**: IO-bound tasks such as scraping and querying LLMs are fully asynchronous under the hood.
- **Custom Scraping**: Scraipe comes with 
- **LLM Analysis:** Process text using OpenAI’s API with built-in validation via Pydantic.
- **Workflow Management:** Combine scraping and analysis in a single workflow--ideal for work in Jupyter notebooks.

## Usage Example

1. **Setup:**
   - Import the required modules:
   ```python
   from scraipe import Workflow
   from scraipe.extras import NewsScraper, OpenAiAnalyzer
   ```
   
2. **Configure Scraper and Analyzer:**
   ```python
   # Configure the scraper
   scraper = NewsScraper()
   
   # Define an instruction and optional Pydantic schema for the analyzer
   instruction = '''
   Extract a list of celebrities mentioned in the article text.
   Return a JSON dictionary with the schema: {"celebrities": ["celebrity1", "celebrity2", ...]}
   '''
   
   from pydantic import BaseModel
   from typing import List
   class ExpectedOutput(BaseModel):
       celebrities: List[str]
   
   analyzer = OpenAiAnalyzer("YOUR_OPENAI_API_KEY", instruction, pydantic_schema=ExpectedOutput)
   ```
   
3. **Use the Workflow:**
   ```python
   workflow = Workflow(scraper, analyzer)
   
   # Provide a list of URLs to scrape
   news_links = ["https://example.com/article1", "https://example.com/article2"]
   workflow.scrape(news_links)
   
   # Analyze the scraped content
   workflow.analyze()
   
   # Export results as a CSV file
   export_df = workflow.export()
   export_df.to_csv('celebrities.csv', index=False)
   ```
   
## Contributing

Contributions are welcome. Please open an issue or submit a pull request for improvements.

## License
This project is licensed under the MIT License.

## Maintainer
This project is maintained by [Nibs](https://github.com/SnpM)
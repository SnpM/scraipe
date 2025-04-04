# Scraipe

Scraipe is a high performance asynchronous scraping and analysis framework that leverages Large Language Models (LLMs) to extract structured information.

## Installation

Ensure you have Python 3.10+ installed. Install Scraipe with all built-in scrapers/analyzers:
```bash
pip install scraipe[extended]
```

Alternatively, install the core library and develop your own scrapers/analyzers with:
```bash
pip install scraipe
```

## Features
- **Versatile Scraping**: Leverage custom scrapers that handle Telegram messages, news articles, and links that require multiple ingress rules.
- **LLM Analysis:** Process text using OpenAI models with built-in Pydantic validation.
- **Workflow Management:** Combine scraping and analysis in a single fault-tolerant workflow--ideal for Jupyter notebooks.
- **High Performance**: Asynchronous IO-bound tasks are seamlessly integrated in the synchronous API.
- **Modular**: Extend the framework with new scrapers or analyzers as your data sources evolve.
- **Customizable Ingress**: Easily define and update rules to route different types of links to their appropriate scrapers.
- **Detailed Logging**: Monitor scraping and analysis operations through comprehensive logging for improved debugging and transparency.

## Usage Example

1. **Setup:**
   - Import the required modules:
   ```python
   from scraipe import Workflow
   from scraipe.extended import NewsScraper, OpenAiAnalyzer
   ```
   
2. **Configure Scraper and Analyzer:**
   ```python
   # Configure the scraper
   scraper = NewsScraper()
   
   # Define an instruction for the analyzer
   instruction = '''
   Extract a list of celebrities mentioned in the article text.
   Return a JSON dictionary with the schema: {"celebrities": ["celebrity1", "celebrity2", ...]}
   '''   
   analyzer = OpenAiAnalyzer("YOUR_OPENAI_API_KEY", instruction)
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
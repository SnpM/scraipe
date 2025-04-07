# Scraipe

Scraipe is a high performance asynchronous scraping and analysis framework that leverages Large Language Models (LLMs) to extract structured information.

## Features
- **Versatile Scraping**: Leverage custom scrapers that handle Telegram messages, news articles, and links that require multiple ingress rules.
- **LLM Analysis:** Process text using OpenAI models with built-in Pydantic validation.
- **Workflow Management:** Combine scraping and analysis in a single fault-tolerant workflow--ideal for Jupyter notebooks.
- **High Performance**: Asynchronous IO-bound tasks are seamlessly integrated in the synchronous API.
- **Modular**: Extend the framework with new scrapers or analyzers as your data sources evolve.
- **Customizable Ingress**: Easily define and update rules to route different types of links to their appropriate scrapers.
- **Detailed Logging**: Monitor scraping and analysis operations through comprehensive logging for improved debugging and transparency.

## Installation

Ensure you have Python 3.10+ installed. Install Scraipe with all built-in scrapers/analyzers:
```bash
pip install scraipe[extended]
```

Alternatively, install the core library and develop your own scrapers/analyzers with:
```bash
pip install scraipe
```

## Example Usage

   ```python
    # Import components from scraipe
    from scraipe.defaults import TextScraper
    from scraipe.defaults import TextStatsAnalyzer
    from scraipe import Workflow

    # Initialize the scraper and analyzer
    scraper = TextScraper()
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
    ```
   
## Contributing

Contributions are welcome. Please open an issue or submit a pull request for improvements.

## License
This project is licensed under the MIT License.

## Maintainer
This project is maintained by [nibs](https://github.com/SnpM).
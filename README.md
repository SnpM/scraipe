# Scraipe
[![pypi](https://img.shields.io/pypi/v/scraipe.svg)](https://pypi.python.org/pypi/scraipe)
[![versions](https://img.shields.io/pypi/pyversions/scraipe.svg)](https://github.com/snpm/scraipe)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/SnpM/scraipe/blob/main/LICENSE)

Scraping and analysis framework. Under development.

## Features
- **Versatile Scraping**: Leverage custom scrapers that handle Telegram messages, news articles, and links that require multiple ingress rules.
- **LLM Analysis:** Process text using OpenAI models with built-in Pydantic validation.
- **Workflow Management:** Combine scraping and analysis in a single fault-tolerant workflow--ideal for Jupyter notebooks.
- **High Performance**: Asynchronous IO-bound tasks are seamlessly integrated in the synchronous API.
- **Modular**: Extend the framework with new scrapers or analyzers as your data sources evolve.
- **Customizable Ingress**: Easily define rules to dynamically route different links to their appropriate scrapers.
- **Detailed Logging**: Monitor scraping and analysis operations through robust errors for improved debugging and transparency.

Check out [the demo](https://scraipe.streamlit.app/).

## Help

See [documentation](https://scraipe.readthedocs.io/en/latest/) for details.

## Installation

Ensure you are using Python>=3.10. Install Scraipe and all built-in scrapers/analyzers:
```bash
pip install scraipe[extended]
```

Alternatively, install the core library with:
```bash
pip install scraipe
```

## Example

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

Run `poetry install --with dev,docs --extras extended` to install all dependences for the project.

## Maintainer
This project is maintained by [nibs](https://github.com/SnpM).

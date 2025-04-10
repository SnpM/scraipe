# Scraipe

**Scraipe** is a high performance scraping and analysis framework.

---

## Why use Scraipe?

- **Versatile Scraping**: Scraipe integrates popular libraries such as `aiohttp`, `trafilatura`, and `telethon` to efficiently scrape diverse documents.f
- **Speed**: Run batches of asynchronous IO-bound tasks in parallel through a simple synchronous API.
- **Customization**: Scraipe's modular architecture allows you to easily extend or create new scrapers and analyzers.
- **LLM Analysis**: Use LLM models to extract structured information from unstructured content.
- **Pydantic Validation**: Ensure the format of component and LLM outputs with built-in Pydantic integration.
- **Workflow Management**: Streamline scraping and analysis in one fault-tolerant workflow.
- **Jupyter Friendly**: Scraipe workflows are ergonomic in the notebook environment.


---

## Quick Start

1. **Installation**

   Install Scraipe with full features:

   ```bash
   pip install scraipe[extended]
   ```

   Or install the core package to build your own components:
   
   ```bash
   pip install scraipe
   ```
2. **Example Usage**
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

---

## Explore

Check out these awesome resources to starting cooking.

- [Basic Workflow](./get_started/basic_workflow.md)
- [Custom Scrapers and Analyzers](./advanced_usage/custom_components.md)
- [MultiScraper for dynamic link routing](./advanced_usage/multi_scraper_guide.md)
- [Using LLM Analyzers for intelligent feature extraction](./get_started/using_llm_analyzers.md)
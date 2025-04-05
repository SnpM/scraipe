---
title: Welcome to Scraipe
---

# Scraipe Documentation

Welcome to the official documentation for **Scraipe**, a high performance scraping and analysis framework with built-in LLM integration.

---

## Why use Scraipe?

- **Versatile Scraping**: Efficient scrapers for Telegram messages, news articles, and more.
- **Asynchronous Performance**: Leverage async IO-bound tasks through a simple, synchronous API.
- **Customization**: Scraipe's modular architecture allows you to easily extend or create new scrapers and analyzers.
- **LLM-powered Analysis**: Seamless integration with OpenAI models plus built-in Pydantic validation of LLM outputs.
- **Workflow Management**: Streamline scraping and analysis in one fault-tolerant workflow.
- **Jupyter Friendly**: Scraipe workflows are ergonomic in the notebook environment.


---

## Quick Start

1. **Installation**

   Install Scraipe with full features:

   ```bash
   pip install scraipe[extended]
   ```

   Or install the core package to build your own extensions:
   
   ```bash
   pip install scraipe
   ```

2. **Example Usage**

    ```python
    from scraipe import Workflow
    from scraipe.extended import NewsScraper, OpenAiAnalyzer

    # 1. Initialize your scraper
    scraper = NewsScraper()

    # 2. Define an instruction for the analyzer
    instruction = '''
    Extract a list of celebrities mentioned in the article text.
    Return a JSON dictionary with the schema: {"celebrities": ["celebrity1", "celebrity2", ...]}
    '''
    analyzer = OpenAiAnalyzer("YOUR_OPENAI_API_KEY", instruction)

    # 3. Create and run your workflow
    workflow = Workflow(scraper, analyzer)
    news_links = ["https://example.com/article1", "https://example.com/article2"]
    workflow.scrape(news_links)
    workflow.analyze()

    # 4. Export results
    export_df = workflow.export()
    export_df.to_csv('celebrities.csv', index=False)
    ```

---

## Getting Help

If you encounter any issues or have questions, please visit our [GitHub repository](https://github.com/SnpM/scraipe) and open an issue.

Happy scraping and analyzing!

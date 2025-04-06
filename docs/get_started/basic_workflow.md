# Creating a Basic Workflow

For background, Scraipe uses interfaces to define scraping and analysis logic:

- [`IScraper`][scraipe.classes.IScraper]: Fetches and extracts content from a link.
- [`IAnalyzer`][scraipe.classes.IAnalyzer]: Extracts structured information from content (e.g., with an LLM)

The [`Workflow`][scraipe.workflow.Workflow] class orchestrates scrapers and analyzers in one persistent process.

Check out [celebrities_example.ipynb](https://github.com/SnpM/scraipe/blob/main/examples/celebrities_example.ipynb) for an advanced workflow using [`NewsScraper`][scraipe.extended.NewsScraper] and [`OpenAiAnalyzer`][scraipe.extended.OpenAiAnalyzer]. Continue reading for a basic example.

## Setup

Make sure scraipe is installed. Scraipe requires python 3.10 or greater.

```
%pip install scraipe
```

## Basic Example

Our basic workflow will use two standard components:

- [`TextScraper`][scraipe.defaults.TextScraper]: gets the content of a website and strips out html tags.
- [`TextStatsAnalyzer`][scraipe.defaults.TextStatsAnalyzer]: computes word and sentence statistics.

[]()

1. Import dependencies.

    ```python
    # Import necessary components from scraipe
    from scraipe.defaults.default_scraper import TextScraper
    from scraipe.defaults.text_stats_analyzer import TextStatsAnalyzer
    from scraipe.workflow import Workflow
    ```

2. Configure the workflow.

    ```python
    # Initialize the scraper and analyzer
    scraper = TextScraper()
    analyzer = TextStatsAnalyzer()

    # Create the workflow instance
    workflow = Workflow(scraper, analyzer)
    ```

3. Run the workflow on links.

    ```python
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

Running [our workflow script](https://github.com/SnpM/scraipe/blob/main/examples/basic_workflow.py) will print a Pandas dataframe containing text stats for each link.

```bash
$ python basic_workflow.py 
Scraping: 100%|█████████████████████████████████████████████████████████████████| 3/3 [00:00<00:00, 12.59link/s]
Analyzing: 100%|██████████████████████████████████████████████████████████████| 3/3 [00:00<00:00, 1065.08item/s]
                                          link  word_count  character_count  sentence_count  average_word_length
0  https://rickandmortyapi.com/api/character/1         366             2719              58             5.669399
1             https://ckaestne.github.io/seai/        2426            15878              96             5.298434
2                          https://example.com          30              206               3             5.600000
```

## Conclusion

We created a basic workflow to orchestrate web scraping and text stats extraction. Next up, check out [bundled scrapers and analyzers](./bundled_components.md) or learn how to [create custom components](../advanced_usage/custom_components.md) for your project's specific needs.